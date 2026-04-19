"""
model.py - Core ML Engine for InsightEngine
RFM Calculation, Preprocessing, Clustering, and Churn Prediction
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, silhouette_score
from sklearn.utils import resample
import warnings
warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────
# 1. DATA LOADING & CLEANING
# ─────────────────────────────────────────────

def load_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Accepts a raw DataFrame and returns a cleaned version.
    Handles common column name variations from different datasets.
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Map common column name variants
    col_map = {
        "invoiceno":    "invoice_no",
        "invoice_no":   "invoice_no",
        "stockcode":    "stock_code",
        "description":  "description",
        "quantity":     "quantity",
        "invoicedate":  "invoice_date",
        "invoice_date": "invoice_date",
        "unitprice":    "unit_price",
        "unit_price":   "unit_price",
        "customerid":   "customer_id",
        "customer_id":  "customer_id",
        "country":      "country",
    }
    df.rename(columns={c: col_map[c] for c in df.columns if c in col_map}, inplace=True)

    # Drop rows with missing customer_id
    df.dropna(subset=["customer_id"], inplace=True)
    df["customer_id"] = df["customer_id"].astype(str).str.strip()

    # Parse invoice date — try multiple formats for compatibility with pandas 2.x and 3.x
    # Handles: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD HH:MM:SS, etc.
    for fmt in [None, "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"]:
        try:
            if fmt:
                parsed = pd.to_datetime(df["invoice_date"], format=fmt, errors="coerce")
            else:
                parsed = pd.to_datetime(df["invoice_date"], errors="coerce", dayfirst=False)
            # Use this parse if most rows succeeded
            success_rate = parsed.notna().mean()
            if success_rate > 0.8:
                df["invoice_date"] = parsed
                break
        except Exception:
            continue
    df.dropna(subset=["invoice_date"], inplace=True)

    # Remove returns / cancellations (invoice starting with C)
    if "invoice_no" in df.columns:
        df = df[~df["invoice_no"].astype(str).str.startswith("C")]

    # Remove non-positive quantity / price
    if "quantity" in df.columns:
        df = df[df["quantity"] > 0]
    if "unit_price" in df.columns:
        df = df[df["unit_price"] > 0]

    # Compute total price per row
    if "quantity" in df.columns and "unit_price" in df.columns:
        df["total_price"] = df["quantity"] * df["unit_price"]

    df.reset_index(drop=True, inplace=True)
    return df


# ─────────────────────────────────────────────
# 2. RFM FEATURE ENGINEERING
# ─────────────────────────────────────────────

def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Recency, Frequency, Monetary values per customer.
    Returns a DataFrame indexed by customer_id.
    """
    snapshot_date = df["invoice_date"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("customer_id").agg(
        recency   = ("invoice_date",  lambda x: (snapshot_date - x.max()).days),
        frequency = ("invoice_no",    "nunique"),
        monetary  = ("total_price",   "sum"),
    ).reset_index()

    rfm["monetary"] = rfm["monetary"].round(2)
    return rfm


# ─────────────────────────────────────────────
# 3. FEATURE SCALING
# ─────────────────────────────────────────────

def scale_rfm(rfm: pd.DataFrame):
    """
    Applies StandardScaler to RFM columns.
    Returns (scaled_array, scaler_object, rfm_df_with_scores).
    """
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[["recency", "frequency", "monetary"]])
    return rfm_scaled, scaler


# ─────────────────────────────────────────────
# 4. ELBOW METHOD
# ─────────────────────────────────────────────

def elbow_inertia(rfm_scaled: np.ndarray, max_k: int = 10):
    """Returns list of inertia values for k = 2..max_k."""
    inertias = []
    k_range = range(2, max_k + 1)
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(rfm_scaled)
        inertias.append(km.inertia_)
    return list(k_range), inertias


def best_k_from_elbow(inertias: list, k_range: list) -> int:
    """
    Auto-detects optimal k using the 'knee' heuristic (largest drop ratio).
    """
    drops = [inertias[i - 1] - inertias[i] for i in range(1, len(inertias))]
    ratios = [drops[i] / (drops[i - 1] + 1e-9) for i in range(1, len(drops))]
    best_idx = int(np.argmin(ratios)) + 2   # offset: k starts at 2
    return k_range[min(best_idx, len(k_range) - 1)]


# ─────────────────────────────────────────────
# 5. K-MEANS CLUSTERING
# ─────────────────────────────────────────────

def run_kmeans(rfm_scaled: np.ndarray, n_clusters: int):
    """Fits KMeans and returns (model, labels, silhouette_score)."""
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(rfm_scaled)
    sil = silhouette_score(rfm_scaled, labels)
    return km, labels, round(sil, 4)


# ─────────────────────────────────────────────
# 6. AUTOMATED SEGMENT LABELING
# ─────────────────────────────────────────────

def label_segments(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Rule-based labeling on raw RFM values.
    Returns rfm with a new 'segment' column.
    """
    r_33  = rfm["recency"].quantile(0.33)
    r_66  = rfm["recency"].quantile(0.66)
    f_33  = rfm["frequency"].quantile(0.33)
    f_66  = rfm["frequency"].quantile(0.66)
    m_33  = rfm["monetary"].quantile(0.33)
    m_66  = rfm["monetary"].quantile(0.66)

    def _label(row):
        r, f, m = row["recency"], row["frequency"], row["monetary"]

        if r <= r_33 and f >= f_66 and m >= m_66:
            return "Champions"
        elif r <= r_33 and f >= f_33:
            return "Loyal Customers"
        elif r <= r_33 and f < f_33:
            return "Recent Customers"
        elif r_33 < r <= r_66 and f >= f_33 and m >= m_33:
            return "Potential Loyalists"
        elif r_33 < r <= r_66 and f < f_33:
            return "Promising"
        elif r > r_66 and f >= f_66:
            return "At Risk"
        elif r > r_66 and f_33 <= f < f_66:
            return "Needs Attention"
        elif r > r_66 and f < f_33 and m >= m_66:
            return "Cant Lose Them"
        elif r > r_66 and f < f_33 and m < m_33:
            return "Lost"
        else:
            return "Hibernating"

    rfm["segment"] = rfm.apply(_label, axis=1)
    return rfm


# ─────────────────────────────────────────────
# 7. CHURN PREDICTION (Logistic Regression)
# ─────────────────────────────────────────────

def build_churn_model(rfm: pd.DataFrame):
    """
    Trains a Logistic Regression churn model.
    Churn = 1 if recency > 90 days (heuristic label).
    Returns (model, X_test, y_test, report_dict, rfm_with_churn).
    """
    rfm = rfm.copy()
    rfm["churn"] = (rfm["recency"] > 90).astype(int)

    features = ["recency", "frequency", "monetary"]
    X = rfm[features]
    y = rfm["churn"]

    # Handle class imbalance via upsampling minority
    data = rfm[features + ["churn"]]
    majority = data[data.churn == 0]
    minority = data[data.churn == 1]

    if len(minority) < 5:
        # Not enough churners — return dummy model
        rfm["churn_prob"]    = 0.0
        rfm["churn_predict"] = 0
        return None, None, None, None, rfm

    minority_up = resample(minority, replace=True, n_samples=len(majority), random_state=42)
    balanced    = pd.concat([majority, minority_up])

    X_bal = balanced[features]
    y_bal = balanced["churn"]

    scaler  = StandardScaler()
    X_sc    = scaler.fit_transform(X_bal)
    X_all_sc = scaler.transform(X)

    X_tr, X_te, y_tr, y_te = train_test_split(X_sc, y_bal, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
    model.fit(X_tr, y_tr)

    y_pred   = model.predict(X_te)
    report   = classification_report(y_te, y_pred, output_dict=True, zero_division=0)

    probs = model.predict_proba(X_all_sc)[:, 1]
    rfm["churn_prob"]    = probs.round(4)
    rfm["churn_predict"] = (probs >= 0.5).astype(int)

    return model, scaler, X_te, y_te, report, rfm


# ─────────────────────────────────────────────
# 8. FULL PIPELINE RUNNER
# ─────────────────────────────────────────────

def run_full_pipeline(raw_df: pd.DataFrame, n_clusters: int = None):
    """
    Orchestrates the complete ML pipeline.

    Returns a dict with:
        df_clean, rfm, rfm_labeled, rfm_scaled,
        km_model, labels, silhouette,
        churn_model, churn_scaler, churn_report,
        k_range, inertias, n_clusters
    """
    # Clean
    df_clean = load_and_clean_data(raw_df)

    # RFM
    rfm = compute_rfm(df_clean)

    # Scale
    rfm_scaled, _ = scale_rfm(rfm)

    # Elbow
    k_range, inertias = elbow_inertia(rfm_scaled, max_k=10)

    # Choose k
    if n_clusters is None:
        n_clusters = best_k_from_elbow(inertias, k_range)
    n_clusters = max(2, min(n_clusters, 10))

    # KMeans
    km_model, labels, sil = run_kmeans(rfm_scaled, n_clusters)
    rfm["cluster"] = labels

    # Segment labels
    rfm_labeled = label_segments(rfm)

    # Churn
    result = build_churn_model(rfm_labeled)
    if len(result) == 6:
        churn_model, churn_scaler, X_te, y_te, churn_report, rfm_labeled = result
    else:
        churn_model = churn_scaler = X_te = y_te = churn_report = None

    return {
        "df_clean":     df_clean,
        "rfm":          rfm_labeled,
        "rfm_scaled":   rfm_scaled,
        "km_model":     km_model,
        "labels":       labels,
        "silhouette":   sil,
        "churn_model":  churn_model,
        "churn_scaler": churn_scaler,
        "churn_report": churn_report,
        "k_range":      k_range,
        "inertias":     inertias,
        "n_clusters":   n_clusters,
    }

# 🔮 InsightEngine
### Customer Segmentation & Intelligent Marketing System

> An end-to-end machine learning dashboard that segments customers using RFM analysis + K-Means clustering, predicts churn risk with Logistic Regression, and generates personalized marketing campaigns — all in a beautiful interactive Streamlit UI.

---

## 🧠 How It Works (One Line)
**Data → RFM → Clustering → Segment Labels → Churn Prediction → Campaign Engine → Dashboard**

---

## 🚀 Features

| Feature | Description |
|---|---|
| 📊 RFM Analysis | Recency · Frequency · Monetary profiling per customer |
| 🤖 K-Means Clustering | Auto elbow detection + silhouette scoring |
| 🏷️ Smart Segment Labels | 10 business-meaningful segments (Champions, At Risk, Lost, etc.) |
| 🔮 Churn Prediction | Logistic Regression with class balancing |
| 📣 Campaign Generator | Dynamic personalized messages + discount logic |
| 🧠 Decision Engine | Per-customer actionable ML recommendations |
| 🌙 Dark/Light Mode | Toggle between pastel light and dark themes |
| ⬇️ Export | Download full segmented dataset + campaigns as CSV |

---

## 📁 Project Structure

```
customer-segmentation-project/
│
├── data.csv           # (Optional) Your transaction dataset
├── app.py             # Streamlit dashboard (main entry point)
├── model.py           # ML engine: RFM, KMeans, Churn model
├── utils.py           # Campaign generator, decision engine, segment metadata
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

---

## ⚙️ Setup & Run (Local)

### 1. Clone / download the project
```bash
cd customer-segmentation-project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 📂 Dataset Format

Upload any CSV with these columns (case-insensitive):

| Column | Description |
|---|---|
| `CustomerID` | Unique customer identifier |
| `InvoiceNo` | Invoice/order number |
| `InvoiceDate` | Date of transaction |
| `Quantity` | Items purchased |
| `UnitPrice` | Price per item |

**Compatible with the [UCI Online Retail Dataset](https://archive.ics.uci.edu/ml/datasets/Online+Retail) from Kaggle.**

> No dataset? Use the built-in **Sample Data** option in the sidebar — it generates 400 customers with 3000 synthetic transactions instantly.

---

## 🗂️ Customer Segments

| Segment | Description | Priority |
|---|---|---|
| 🏆 Champions | Bought recently, buy often, spend the most | High |
| 💚 Loyal Customers | Regular buyers with good spend | High |
| 🌱 Recent Customers | New buyers, not frequent yet | Medium |
| ⭐ Potential Loyalists | Recent with avg frequency | Medium |
| 🌟 Promising | New, low spend | Medium |
| ⚠️ Needs Attention | Mid recency, need re-engagement | Medium |
| 🔴 At Risk | Once-valuable, haven't returned | Critical |
| 🆘 Can't Lose Them | High-value, long absent | Critical |
| 😴 Hibernating | Low recency + low frequency | Low |
| 💤 Lost | Lowest scores across RFM | Low |

---

## 🌐 Deployment on Render

1. Push code to a GitHub repository
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Click **Deploy**

---

## 🧰 Tech Stack

- **Frontend:** Streamlit + Plotly + Custom CSS
- **ML:** scikit-learn (KMeans, LogisticRegression, StandardScaler)
- **Data:** pandas, numpy
- **Deployment:** Render (free tier)

---

## 👨‍💻 For Viva / Presentation

**Problem:** Businesses fail to use transaction data for personalized marketing, treating all customers the same.

**Solution:** InsightEngine automates customer intelligence:
1. Loads & cleans transaction data
2. Computes RFM (Recency, Frequency, Monetary) per customer
3. Scales features with StandardScaler
4. Applies K-Means clustering with automatic elbow detection
5. Labels clusters with business-meaningful segment names
6. Trains Logistic Regression for churn prediction
7. Decision engine combines segment + churn → actionable strategy
8. Dynamic campaign generator creates personalized messages
9. Streamlit dashboard ties everything together in real-time

**Key Insight:** Combining unsupervised learning (clustering) + supervised learning (churn prediction) + rule-based logic (campaign engine) creates a powerful, interpretable business decision system.

---

*Built with ❤️ using Python, Streamlit, and scikit-learn*

"""
app.py — InsightEngine v3
Premium redesign: no sidebar, everything centered, rich dark/light mode,
all tabs fully working (campaigns, churn, decision engine, export).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io, random

from model import run_full_pipeline
from utils import (
    get_segment_meta, generate_campaign,
    decision_engine, segment_summary,
    SEGMENT_META, DISCOUNT_BY_SEGMENT,
)

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="InsightEngine", page_icon="🔮", layout="wide")

# ═══════════════════════════════════════════════════════════════
# THEME DEFINITIONS
# ═══════════════════════════════════════════════════════════════
LIGHT = {
    "mode":        "light",
    "bg":          "#F7F3EE",
    "bg_deep":     "#EFE9E0",
    "card":        "#FFFFFF",
    "card2":       "#FAF7F4",
    "border":      "#E0D8CE",
    "border2":     "#CEC4B8",
    "text":        "#1E1A16",
    "text2":       "#3D3630",
    "muted":       "#8C7E72",
    "rose":        "#C25878",
    "rose_soft":   "#F2CBD6",
    "teal":        "#2D8F7B",
    "teal_soft":   "#C3EDE5",
    "amber":       "#C07830",
    "amber_soft":  "#F5DFB8",
    "violet":      "#6B50A0",
    "violet_soft": "#DDD4F5",
    "success":     "#2D8F5A",
    "danger":      "#C03A3A",
    "warn":        "#C07830",
    "plot_paper":  "rgba(255,255,255,0)",
    "plot_bg":     "rgba(247,243,238,0.6)",
    "grid":        "#E0D8CE",
    "toggle_bg":   "#E0D8CE",
    "toggle_knob": "#FFFFFF",
}
DARK = {
    "mode":        "dark",
    "bg":          "#161412",
    "bg_deep":     "#1E1C19",
    "card":        "#242220",
    "card2":       "#2C2A27",
    "border":      "#3A3733",
    "border2":     "#4A4743",
    "text":        "#F0EBE4",
    "text2":       "#C8C0B6",
    "muted":       "#7A7268",
    "rose":        "#E8789A",
    "rose_soft":   "#3D2030",
    "teal":        "#4DBFA8",
    "teal_soft":   "#1A3530",
    "amber":       "#E8A050",
    "amber_soft":  "#3A2A10",
    "violet":      "#9B80D8",
    "violet_soft": "#2A2040",
    "success":     "#50C880",
    "danger":      "#E86060",
    "warn":        "#E8A050",
    "plot_paper":  "rgba(0,0,0,0)",
    "plot_bg":     "rgba(36,34,32,0.6)",
    "grid":        "#3A3733",
    "toggle_bg":   "#4DBFA8",
    "toggle_knob": "#161412",
}

def T():
    return DARK if st.session_state.get("dark", False) else LIGHT

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
def init():
    defaults = {"dark": False, "pipeline": None, "src": None, "camp": None, "ran": False}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════
# CSS — FULL COVERAGE, NO SIDEBAR, CENTERED
# ═══════════════════════════════════════════════════════════════
def css(t):
    dm = t["mode"] == "dark"
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,900;1,9..144,400&family=Cabinet+Grotesk:wght@400;500;600;700;800&display=swap');

/* ── TOTAL BACKGROUND TAKEOVER ── */
html, body, #root,
.stApp, [data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, section.main,
div.stApp, div[class^="appview"],
[data-testid="stHeader"] {{
    background: {t['bg']} !important;
    font-family: 'Cabinet Grotesk', sans-serif !important;
}}

/* kill sidebar entirely */
[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="collapsedControl"] {{ display: none !important; }}

/* main block — defined above in header section */

/* ── TYPOGRAPHY ── */
*, *::before, *::after {{ box-sizing: border-box; }}
h1,h2,h3,h4,h5,h6 {{
    font-family: 'Fraunces', serif !important;
    color: {t['text']} !important;
}}
p, span, div, label, li, td, th, button {{
    font-family: 'Cabinet Grotesk', sans-serif !important;
    color: {t['text']} !important;
}}

/* ── TABS ── */
[data-baseweb="tab-list"] {{
    background: {t['card2']} !important;
    border-radius: 16px !important;
    padding: 5px !important;
    border: 1px solid {t['border']} !important;
    gap: 2px !important;
}}
[data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 12px !important;
    color: {t['muted']} !important;
    font-family: 'Cabinet Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    padding: 0.4rem 1rem !important;
    border: none !important;
    transition: all 0.2s !important;
    letter-spacing: 0.01em !important;
}}
[data-baseweb="tab"]:hover {{
    background: {t['border']} !important;
    color: {t['text']} !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    background: {t['rose']} !important;
    color: #fff !important;
    box-shadow: 0 3px 12px {t['rose']}55 !important;
}}
[data-baseweb="tab-panel"] {{
    background: transparent !important;
    padding-top: 1.5rem !important;
}}

/* ── INPUTS ── */
[data-baseweb="select"]>div,
[data-testid="stSelectbox"]>div>div,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-baseweb="input"],
[data-baseweb="input"]>div {{
    background: {t['card2']} !important;
    border: 1.5px solid {t['border']} !important;
    border-radius: 12px !important;
    color: {t['text']} !important;
    font-family: 'Cabinet Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
}}
[data-baseweb="select"]>div:focus-within,
[data-testid="stTextInput"] input:focus {{
    border-color: {t['rose']} !important;
    box-shadow: 0 0 0 3px {t['rose']}22 !important;
}}
[data-baseweb="select"] span {{ color: {t['text']} !important; }}
[data-baseweb="menu"], [data-baseweb="popover"]>div {{
    background: {t['card']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,{0.3 if dm else 0.12}) !important;
}}
[data-baseweb="menu"] li {{ color: {t['text']} !important; }}
[data-baseweb="menu"] li:hover {{ background: {t['card2']} !important; }}

/* ── RADIO ── */
[data-testid="stRadio"] label {{
    background: {t['card2']} !important;
    border: 1.5px solid {t['border']} !important;
    border-radius: 10px !important;
    padding: 0.45rem 1rem !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}}
[data-testid="stRadio"] label:hover {{
    border-color: {t['rose']} !important;
    background: {t['rose_soft']} !important;
}}
[data-testid="stRadio"] [aria-checked="true"] label {{
    border-color: {t['rose']} !important;
    background: {t['rose_soft']} !important;
    color: {t['rose']} !important;
}}

/* ── CHECKBOX ── */
[data-testid="stCheckbox"] label {{ font-weight: 600 !important; }}

/* ── FILE UPLOADER — hide internal label to prevent duplicate text ── */
[data-testid="stFileUploader"] {{
    background: {t['card2']} !important;
    border: 2px dashed {t['border2']} !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}}
[data-testid="stFileUploader"] * {{ color: {t['muted']} !important; }}
[data-testid="stFileUploader"]:hover {{
    border-color: {t['rose']} !important;
}}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p,
[data-testid="stFileUploader"] > div > label {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}

/* ── BUTTONS ── */
.stButton>button {{
    background: {t['rose']} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.65rem 1.8rem !important;
    font-family: 'Cabinet Grotesk', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.22s !important;
    box-shadow: 0 4px 16px {t['rose']}44 !important;
}}
.stButton>button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px {t['rose']}66 !important;
    background: {t['rose']}dd !important;
}}

/* Download button */
[data-testid="stDownloadButton"]>button {{
    background: transparent !important;
    color: {t['rose']} !important;
    border: 2px solid {t['rose']} !important;
    box-shadow: none !important;
    border-radius: 12px !important;
}}
[data-testid="stDownloadButton"]>button:hover {{
    background: {t['rose']} !important;
    color: #fff !important;
    transform: translateY(-1px) !important;
}}

/* ── ALERTS ── */
[data-testid="stAlert"] {{
    background: {t['card2']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 12px !important;
}}
[data-testid="stAlert"] * {{ color: {t['text']} !important; }}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {{
    background: {t['card']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}}

/* ── SPINNER ── */
[data-testid="stSpinner"]>div>div {{
    border-color: {t['rose']} transparent transparent transparent !important;
}}

/* ── STREAMLIT HEADER & TOP SPACING ── */
[data-testid="stHeader"] {{
    background: {t['bg']} !important;
    border-bottom: 1px solid {t['border']} !important;
    z-index: 999 !important;
}}

/* Push content below the fixed header */
.main .block-container,
[data-testid="stMainBlockContainer"],
[data-testid="block-container"] {{
    background: {t['bg']} !important;
    max-width: 1200px !important;
    padding: 4.5rem 2rem 5rem !important;
    margin: 0 auto !important;
}}

/* ── FIXED THEME TOGGLE (top-right, always visible) ── */
#ie-toggle-fixed {{
    position: fixed;
    top: 10px;
    right: 16px;
    z-index: 9999;
}}
#ie-toggle-fixed button {{
    background: {t['card']} !important;
    color: {t['text']} !important;
    border: 1.5px solid {t['border']} !important;
    border-radius: 999px !important;
    padding: 5px 14px !important;
    font-family: 'Cabinet Grotesk', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15) !important;
    transition: all 0.2s !important;
    white-space: nowrap !important;
    height: 32px !important;
    line-height: 1 !important;
}}
#ie-toggle-fixed button:hover {{
    border-color: {t['rose']} !important;
    color: {t['rose']} !important;
    background: {t['rose_soft']} !important;
}}

/* hide the old toggle column button */
.toggle-col .stButton>button {{
    display: none !important;
}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:{t['bg']}; }}
::-webkit-scrollbar-thumb {{ background:{t['border2']}; border-radius:3px; }}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer {{ visibility:hidden; }}

/* ══════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════ */

/* Nav bar */
.ie-nav {{
    display:flex; align-items:center; justify-content:space-between;
    padding: 1.2rem 0 1rem;
    border-bottom: 1px solid {t['border']};
    margin-bottom: 2rem;
}}
.ie-logo {{
    font-family:'Fraunces',serif;
    font-size:1.6rem; font-weight:900;
    background: linear-gradient(135deg,{t['rose']},{t['violet']});
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text;
    display:inline-block;
    line-height:1.3;
    padding-bottom:0.15em;
    overflow:visible;
}}
.ie-logo-sub {{
    font-size:0.72rem; color:{t['muted']}; font-weight:600;
    letter-spacing:0.08em; text-transform:uppercase;
    margin-top:0.1rem;
}}

/* Hero */
.ie-hero {{
    text-align:center; padding:3rem 1rem 2.8rem;
    background: linear-gradient(180deg, {t['card']}00 0%, {t['card']}66 100%);
    border-radius:24px; margin-bottom:1.5rem;
    position:relative; overflow:visible;
}}
.ie-hero::before {{
    content:'';
    position:absolute; inset:0;
    background: radial-gradient(ellipse 70% 50% at 50% 0%, {t['rose']}18 0%, transparent 70%),
                radial-gradient(ellipse 50% 40% at 80% 80%, {t['violet']}12 0%, transparent 60%),
                radial-gradient(ellipse 40% 40% at 20% 70%, {t['teal']}10 0%, transparent 60%);
    pointer-events:none;
    border-radius:24px;
}}
.ie-hero-title {{
    font-family:'Fraunces',serif;
    font-size:clamp(2.5rem,6vw,4rem);
    font-weight:900;
    background: linear-gradient(135deg,{t['rose']},{t['violet']},{t['teal']});
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text;
    display:inline-block;
    line-height:1.25;
    padding-bottom:0.18em;
    margin-bottom:0.6rem;
    position:relative;
    overflow:visible;
}}
.ie-hero-sub {{
    font-size:1.1rem; color:{t['muted']}; max-width:520px;
    margin:0 auto 2rem; font-weight:500; line-height:1.6; position:relative;
}}

/* Config panel */
.ie-config {{
    background:{t['card']};
    border:1px solid {t['border']};
    border-radius:20px;
    padding:1.8rem 2rem;
    margin-bottom:1.5rem;
    position:relative;
}}
.ie-config-title {{
    font-family:'Fraunces',serif;
    font-size:1.1rem; font-weight:700;
    color:{t['text']}; margin-bottom:1.2rem;
    display:flex; align-items:center; gap:0.5rem;
}}

/* Feature flip cards */
.ie-flip-grid {{
    display:grid; grid-template-columns:repeat(4,1fr); gap:1.2rem;
    margin:0 0 1.5rem;
}}
@media(max-width:800px){{ .ie-flip-grid{{grid-template-columns:repeat(2,1fr);}} }}
.ie-flip {{
    height:190px; perspective:1000px; cursor:pointer;
}}
.ie-flip-inner {{
    width:100%; height:100%; position:relative;
    transition:transform 0.6s cubic-bezier(.4,0,.2,1);
    transform-style:preserve-3d;
}}
.ie-flip:hover .ie-flip-inner {{ transform:rotateY(180deg); }}
.ie-flip-f,.ie-flip-b {{
    position:absolute; inset:0;
    border-radius:16px; border:1px solid {t['border']};
    backface-visibility:hidden; -webkit-backface-visibility:hidden;
    display:flex; flex-direction:column; align-items:center;
    justify-content:center; padding:1.2rem;
    text-align:center;
}}
.ie-flip-f {{
    background:{t['card']};
    box-shadow:0 2px 16px rgba(0,0,0,{0.18 if dm else 0.06});
}}
.ie-flip-b {{
    background:linear-gradient(145deg,{t['card2']},{t['card']});
    transform:rotateY(180deg);
    border-color:{t['rose']}44;
}}
.ie-flip-icon {{ font-size:2.2rem; margin-bottom:0.5rem; }}
.ie-flip-title {{
    font-family:'Fraunces',serif; font-size:1rem; font-weight:700;
    color:{t['text']}; margin-bottom:0.2rem;
}}
.ie-flip-hint {{ font-size:0.7rem; color:{t['muted']}; }}
.ie-flip-bh {{
    font-family:'Fraunces',serif; font-size:0.88rem;
    color:{t['rose']}; font-weight:700; margin-bottom:0.4rem;
}}
.ie-flip-bt {{ font-size:0.76rem; color:{t['text2']}; line-height:1.6; }}

/* Stat cards */
.ie-stats-grid {{
    display:grid; grid-template-columns:repeat(5,1fr); gap:1rem;
    margin:0 0 1.5rem;
}}
@media(max-width:900px){{ .ie-stats-grid{{grid-template-columns:repeat(3,1fr);}} }}
.ie-stat {{
    background:{t['card']};
    border:1px solid {t['border']};
    border-radius:16px; padding:1.1rem 1rem;
    text-align:center; position:relative; overflow:hidden;
    transition:transform 0.2s, box-shadow 0.2s;
}}
.ie-stat:hover {{
    transform:translateY(-2px);
    box-shadow:0 8px 24px rgba(0,0,0,{0.18 if dm else 0.08});
}}
.ie-stat::before {{
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background:var(--accent,{t['rose']});
    border-radius:16px 16px 0 0;
}}
.ie-stat-val {{
    font-family:'Fraunces',serif; font-size:1.9rem; line-height:1;
    color:var(--accent,{t['rose']}); margin-bottom:0.25rem;
}}
.ie-stat-lbl {{
    font-size:0.68rem; color:{t['muted']};
    text-transform:uppercase; letter-spacing:0.08em; font-weight:700;
}}

/* Section heading */
.ie-sh {{
    font-family:'Fraunces',serif; font-size:1.3rem; color:{t['text']};
    margin:1.8rem 0 0.9rem; padding-bottom:0.5rem;
    border-bottom:2px solid {t['border']};
    display:flex; align-items:center; gap:0.5rem;
}}

/* Cards */
.ie-card {{
    background:{t['card']};
    border:1px solid {t['border']};
    border-radius:16px; padding:1.3rem 1.5rem;
    margin-bottom:0.8rem;
    box-shadow:0 2px 12px rgba(0,0,0,{0.14 if dm else 0.04});
}}

/* Campaign box */
.ie-camp {{
    background:{t['card2']};
    border:1px solid {t['border']};
    border-left:4px solid {t['rose']};
    border-radius:14px; padding:1.2rem 1.4rem;
    line-height:1.8; font-size:0.97rem; color:{t['text']};
    margin:0.5rem 0 0.8rem;
}}
.ie-camp-meta {{ font-size:0.74rem; color:{t['muted']}; margin-bottom:0.4rem; letter-spacing:0.04em; }}
.ie-camp-sub {{ font-weight:800; font-size:0.88rem; color:{t['text2']}; margin-bottom:0.55rem; }}

/* Rec items */
.ie-rec {{
    background:{t['card2']};
    border-left:3px solid {t['teal']};
    border-radius:8px; padding:0.6rem 1rem;
    margin:0.35rem 0; font-size:0.86rem; color:{t['text']};
}}

/* Risk bar */
.ie-rbar {{ background:{t['border']}; border-radius:999px; height:8px; overflow:hidden; margin:0.25rem 0 0.8rem; }}
.ie-rbar-f {{ height:8px; border-radius:999px; transition:width 0.5s; }}

/* Segment pill */
.ie-pill {{
    display:inline-flex; align-items:center; gap:0.3rem;
    padding:0.25rem 0.8rem; border-radius:999px;
    font-size:0.78rem; font-weight:700; border:1px solid;
}}

/* Info strip */
.ie-strip {{
    background:{t['card']};
    border:1px solid {t['border']};
    border-radius:50px;
    padding:0.5rem 1.5rem;
    display:flex; gap:2rem; align-items:center; flex-wrap:wrap;
    margin-bottom:1.2rem; font-size:0.82rem;
}}

/* Toggle button pill override */
.toggle-col .stButton>button {{
    background:{t['card2']} !important;
    color:{t['text']} !important;
    border:1.5px solid {t['border']} !important;
    border-radius:999px !important;
    padding:0.3rem 1rem !important;
    font-size:0.78rem !important;
    font-weight:700 !important;
    box-shadow:none !important;
    height:32px !important;
    letter-spacing:0.02em !important;
}}
.toggle-col .stButton>button:hover {{
    border-color:{t['rose']} !important;
    color:{t['rose']} !important;
    background:{t['rose_soft']} !important;
    transform:none !important;
    box-shadow:none !important;
}}

/* Step pills on hero */
.ie-steps {{
    display:flex; gap:0.8rem; justify-content:center;
    flex-wrap:wrap; margin-bottom:1.5rem; position:relative;
}}
.ie-step {{
    display:flex; align-items:center; gap:0.5rem;
    background:{t['card']}; border:1px solid {t['border']};
    border-radius:999px; padding:0.45rem 1.1rem;
    font-size:0.82rem; font-weight:700; color:{t['text2']};
}}
.ie-step-num {{
    width:20px; height:20px; border-radius:50%;
    background:{t['rose']}; color:#fff;
    font-size:0.72rem; font-weight:800;
    display:flex; align-items:center; justify-content:center;
}}

/* Pulse dot */
@keyframes pulse {{
    0%,100%{{opacity:1;transform:scale(1);}}
    50%{{opacity:0.6;transform:scale(1.4);}}
}}
.pulse {{ animation:pulse 2s ease-in-out infinite; display:inline-block; }}

/* Fade in */
@keyframes fadeUp {{
    from{{opacity:0;transform:translateY(16px);}}
    to{{opacity:1;transform:translateY(0);}}
}}
.fade-up {{ animation:fadeUp 0.5s ease forwards; }}

/* Stagger children */
.stagger>*:nth-child(1){{animation-delay:0.05s;}}
.stagger>*:nth-child(2){{animation-delay:0.1s;}}
.stagger>*:nth-child(3){{animation-delay:0.15s;}}
.stagger>*:nth-child(4){{animation-delay:0.2s;}}
.stagger>*:nth-child(5){{animation-delay:0.25s;}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def plo(t, title="", h=360):
    return dict(
        paper_bgcolor=t["plot_paper"], plot_bgcolor=t["plot_bg"],
        font=dict(family="Cabinet Grotesk", color=t["text"], size=11),
        title=dict(text=title, font=dict(family="Fraunces", size=14, color=t["text"])),
        height=h, margin=dict(l=16,r=16,t=44 if title else 16,b=16),
        xaxis=dict(gridcolor=t["grid"], zerolinecolor=t["grid"], color=t["muted"]),
        yaxis=dict(gridcolor=t["grid"], zerolinecolor=t["grid"], color=t["muted"]),
        legend=dict(bgcolor=t["card"], bordercolor=t["border"], borderwidth=1,
                    font=dict(color=t["text"], size=10)),
    )

def stat(val, lbl, accent):
    return f"""<div class="ie-stat" style="--accent:{accent}">
        <div class="ie-stat-val">{val}</div>
        <div class="ie-stat-lbl">{lbl}</div>
    </div>"""

def seg_colors(rfm, col="segment"):
    return {s: SEGMENT_META.get(s,{}).get("color","#AAA") for s in rfm[col].unique()}

def make_sample():
    rng = np.random.default_rng(42)
    custs = [f"C{str(i).zfill(4)}" for i in range(1,501)]
    base  = pd.Timestamp("2022-01-01")
    rows  = []
    prods = [("P001","Widget Pro",24.99),("P002","Bundle Kit",49.99),("P003","Starter Pack",14.99),
             ("P004","Premium Set",89.99),("P005","Classic Item",9.99),("P006","Deluxe Bundle",129.99)]
    for _ in range(4000):
        c=rng.choice(custs); p=prods[rng.integers(0,len(prods))]
        rows.append({"InvoiceNo":f"INV{rng.integers(10000,99999)}","StockCode":p[0],
                     "Description":p[1],"Quantity":int(rng.integers(1,20)),
                     "InvoiceDate":(base+pd.Timedelta(days=int(rng.integers(0,730)))).strftime("%Y-%m-%d"),
                     "UnitPrice":p[2],"CustomerID":c,
                     "Country":rng.choice(["UK","Germany","France","Spain","Italy"])})
    return pd.DataFrame(rows)

# ═══════════════════════════════════════════════════════════════
# NAV BAR — logo left, toggle right (fully visible, pill-shaped)
# ═══════════════════════════════════════════════════════════════
def nav(t):
    tog_label = "☀️ Light" if t["mode"] == "dark" else "🌙 Dark"

    # Two-column layout: logo left, toggle right
    logo_col, gap_col, tog_col = st.columns([7, 2, 1])

    with logo_col:
        st.markdown(f"""
        <div style="padding:0.6rem 0 0.5rem;">
            <div class="ie-logo">🔮 InsightEngine</div>
            <div class="ie-logo-sub">Customer Intelligence &amp; Marketing System</div>
        </div>
        """, unsafe_allow_html=True)

    with tog_col:
        # Unique CSS class for this specific button
        st.markdown('<div class="ie-tog-wrap">', unsafe_allow_html=True)
        if st.button(tog_label, key="tog"):
            st.session_state.dark = not st.session_state.dark
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="border-bottom:1px solid {t["border"]};margin-bottom:1.5rem;margin-top:0.3rem;"></div>',
                unsafe_allow_html=True)

    # Style ONLY the toggle button via its wrapper class
    st.markdown(f"""
    <style>
    .ie-tog-wrap {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding-top: 0.7rem;
    }}
    .ie-tog-wrap .stButton > button {{
        background: {t['card']} !important;
        color: {t['text']} !important;
        border: 1.5px solid {t['border']} !important;
        border-radius: 999px !important;
        padding: 0 14px !important;
        font-family: 'Cabinet Grotesk', sans-serif !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 8px rgba(0,0,0,{0.18 if t['mode']=='dark' else 0.1}) !important;
        height: 30px !important;
        min-height: 30px !important;
        line-height: 28px !important;
        letter-spacing: 0.02em !important;
        transform: none !important;
        width: auto !important;
        min-width: 80px !important;
        background-image: none !important;
        white-space: nowrap !important;
    }}
    .ie-tog-wrap .stButton > button:hover {{
        border-color: {t['rose']} !important;
        color: {t['rose']} !important;
        background: {t['rose_soft']} !important;
        transform: none !important;
        box-shadow: 0 1px 8px rgba(0,0,0,{0.18 if t['mode']=='dark' else 0.1}) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# WELCOME PAGE
# ═══════════════════════════════════════════════════════════════
def welcome(t):
    st.markdown(f"""
    <div class="ie-hero fade-up">
        <div class="ie-hero-title">🔮 InsightEngine</div>
        <div class="ie-hero-sub">
            Transform raw transaction data into customer intelligence —<br>
            segment, predict churn, and generate campaigns automatically.
        </div>
        <div class="ie-steps">
            <div class="ie-step"><div class="ie-step-num">1</div>Choose Data Source</div>
            <div class="ie-step"><div class="ie-step-num">2</div>Configure Model</div>
            <div class="ie-step"><div class="ie-step-num">3</div>Run Analysis</div>
            <div class="ie-step"><div class="ie-step-num">4</div>Explore Insights</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature flip cards
    cards = [
        ("📊","RFM Analysis","hover to explore →","Recency · Frequency · Monetary",
         "Profiles every customer across 3 key behaviour dimensions. The foundation of every smart segmentation decision."),
        ("🤖","ML Clustering","hover to explore →","K-Means + Auto Elbow",
         "Finds the optimal number of clusters automatically, then groups customers into distinct behaviour profiles — validated by silhouette scoring."),
        ("🔮","Churn Prediction","hover to explore →","Logistic Regression",
         "Estimates each customer's probability of leaving. Identifies at-risk revenue before it walks out the door."),
        ("📣","Campaign Engine","hover to explore →","30+ Dynamic Templates",
         "Generates personalised messages per segment with auto-adjusted discounts, urgency levels, and delivery channel recommendations."),
    ]
    html = '<div class="ie-flip-grid stagger">'
    for ic,ti,hi,bh,bt in cards:
        html += f"""<div class="ie-flip fade-up">
          <div class="ie-flip-inner">
            <div class="ie-flip-f">
              <div class="ie-flip-icon">{ic}</div>
              <div class="ie-flip-title">{ti}</div>
              <div class="ie-flip-hint">{hi}</div>
            </div>
            <div class="ie-flip-b">
              <div class="ie-flip-bh">{bh}</div>
              <div class="ie-flip-bt">{bt}</div>
            </div>
          </div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # ── Pipeline steps strip (replaces the blank box) ──
    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};border-radius:16px;
                padding:1.1rem 1.6rem;margin:0 0 1.4rem;display:flex;align-items:center;
                gap:0;flex-wrap:wrap;justify-content:center;">
        <span style="font-size:0.75rem;font-weight:800;color:{t['muted']};text-transform:uppercase;
                     letter-spacing:0.1em;margin-right:1rem;">Pipeline</span>
        {"".join([
            f'<span style="display:inline-flex;align-items:center;gap:0.4rem;">'
            f'<span style="background:{c}22;border:1px solid {c}66;color:{c};border-radius:999px;'
            f'padding:0.25rem 0.85rem;font-size:0.78rem;font-weight:700;white-space:nowrap;">{step}</span>'
            + (f'<span style="color:{t["border2"]};font-size:1rem;margin:0 0.1rem;">›</span>' if i < 4 else '')
            + '</span>'
            for i,(step,c) in enumerate([
                ("Data", t["rose"]),
                ("RFM", t["amber"]),
                ("K-Means", t["teal"]),
                ("Segments", t["violet"]),
                ("Churn Model", t["rose"]),
            ])
        ])}
        <span style="color:{t['border2']};font-size:1rem;margin:0 0.1rem;">›</span>
        <span style="background:{t['teal']}22;border:1px solid {t['teal']}66;color:{t['teal']};
                     border-radius:999px;padding:0.25rem 0.85rem;font-size:0.78rem;font-weight:700;">
            Decision Engine
        </span>
        <span style="color:{t['border2']};font-size:1rem;margin:0 0.1rem;">›</span>
        <span style="background:{t['violet']}22;border:1px solid {t['violet']}66;color:{t['violet']};
                     border-radius:999px;padding:0.25rem 0.85rem;font-size:0.78rem;font-weight:700;">
            Dashboard
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Configure & Run panel — use st.container, not open/close HTML divs ──
    with st.container(border=True):
        st.markdown(f'<div style="font-family:\'Fraunces\',serif;font-size:1.05rem;font-weight:700;color:{t["text"]};margin-bottom:1rem;">⚙️ Configure &amp; Run</div>', unsafe_allow_html=True)

        col_src, col_set, col_run = st.columns([2, 2, 1.2])
        with col_src:
            st.markdown(f'<div style="font-size:0.78rem;color:{t["muted"]};font-weight:700;margin-bottom:0.4rem;text-transform:uppercase;letter-spacing:0.07em;">📁 Data Source</div>', unsafe_allow_html=True)
            src = st.radio("", ["📊 Sample Data","📤 Upload CSV"], label_visibility="collapsed", key="src_r", horizontal=True)

            uploaded = None
            if "Upload" in src:
                uploaded = st.file_uploader(
                    "Upload your dataset CSV",
                    type=["csv"],
                    label_visibility="hidden",
                    key="uploader"
                )
                st.markdown(f'<div style="font-size:0.72rem;color:{t["muted"]};margin-top:0.3rem;">Required columns: CustomerID · InvoiceDate · InvoiceNo · Quantity · UnitPrice</div>', unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style="background:{t['bg_deep']};border:1px solid {t['border']};
                    border-radius:10px;padding:0.65rem 1rem;margin-top:0.3rem;font-size:0.78rem;color:{t['muted']};">
                    500 customers · 4,000 transactions · Synthetic retail dataset</div>""",
                    unsafe_allow_html=True)

        with col_set:
            st.markdown(f'<div style="font-size:0.78rem;color:{t["muted"]};font-weight:700;margin-bottom:0.4rem;text-transform:uppercase;letter-spacing:0.07em;">⚙️ Model Settings</div>', unsafe_allow_html=True)
            auto_k = st.checkbox("Auto-detect clusters (Elbow method)", value=True, key="auto_k")
            n_clusters = None
            if not auto_k:
                n_clusters = st.slider("Clusters (k)", 2, 10, 4, key="k_sl")

        with col_run:
            st.markdown('<div style="height:1.9rem;"></div>', unsafe_allow_html=True)
            run_btn = st.button("🚀 Run Analysis", use_container_width=True, key="run_hero")

    # Three bottom info cards
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:0.5rem;" class="fade-up">
        <div class="ie-card" style="border-top:3px solid {t['rose']};">
            <div style="font-size:1.3rem;margin-bottom:0.4rem;">🎯</div>
            <div style="font-family:'Fraunces',serif;font-size:0.95rem;font-weight:700;margin-bottom:0.3rem;">10 Segment Labels</div>
            <div style="font-size:0.78rem;color:{t['muted']};">Champions · Loyal · At Risk · Hibernating · Lost — auto-assigned using rule-based RFM thresholds.</div>
        </div>
        <div class="ie-card" style="border-top:3px solid {t['teal']};">
            <div style="font-size:1.3rem;margin-bottom:0.4rem;">📈</div>
            <div style="font-family:'Fraunces',serif;font-size:0.95rem;font-weight:700;margin-bottom:0.3rem;">7 Analytics Tabs</div>
            <div style="font-size:0.78rem;color:{t['muted']};">Overview · Segments · Churn · Campaigns · Decision Engine · RFM Analysis · Export all in one dashboard.</div>
        </div>
        <div class="ie-card" style="border-top:3px solid {t['violet']};">
            <div style="font-size:1.3rem;margin-bottom:0.4rem;">⬇️</div>
            <div style="font-family:'Fraunces',serif;font-size:0.95rem;font-weight:700;margin-bottom:0.3rem;">Full CSV Export</div>
            <div style="font-size:0.78rem;color:{t['muted']};">Every customer's segment, churn score, campaign message, discount & channel in one download.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return src, uploaded, n_clusters, run_btn

# ═══════════════════════════════════════════════════════════════
# TAB: OVERVIEW
# ═══════════════════════════════════════════════════════════════
def tab_overview(p, t):
    rfm = p["rfm"]
    has_churn = "churn_predict" in rfm.columns

    # KPI row
    total_rev  = rfm["monetary"].sum()
    avg_rec    = rfm["recency"].mean()
    churn_rate = rfm["churn_predict"].mean()*100 if has_churn else 0

    kpis = [
        (f"{len(rfm):,}",            "Total Customers", t["rose"]),
        (f"£{total_rev:,.0f}",       "Total Revenue",   t["teal"]),
        (f"{avg_rec:.0f}d",          "Avg Recency",     t["amber"]),
        (str(p["n_clusters"]),       "Clusters",        t["violet"]),
        (f"{churn_rate:.1f}%",       "Churn Risk",      t["danger"]),
    ]
    html = '<div class="ie-stats-grid stagger fade-up">'
    for v,l,c in kpis:
        html += stat(v,l,c)
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # Charts row 1
    c1,c2 = st.columns(2)
    with c1:
        sc = rfm["segment"].value_counts().reset_index()
        sc.columns = ["segment","count"]
        clrs = [SEGMENT_META.get(s,{}).get("color","#AAA") for s in sc["segment"]]
        fig = go.Figure(go.Pie(
            labels=sc["segment"], values=sc["count"], hole=0.56,
            marker=dict(colors=clrs, line=dict(color=t["bg"],width=2)),
            textinfo="percent", textfont=dict(size=10),
            hovertemplate="<b>%{label}</b><br>%{value} customers (%{percent})<extra></extra>",
        ))
        fig.update_layout(**plo(t,"Customer Segment Distribution",360))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        rev = rfm.groupby("segment")["monetary"].sum().reset_index().sort_values("monetary")
        clrs2=[SEGMENT_META.get(s,{}).get("color","#AAA") for s in rev["segment"]]
        fig = go.Figure(go.Bar(
            x=rev["monetary"], y=rev["segment"], orientation="h",
            marker=dict(color=clrs2,line=dict(width=0)),
            text=rev["monetary"].apply(lambda x:f"£{x:,.0f}"),
            textposition="outside", textfont=dict(color=t["muted"],size=9),
            hovertemplate="<b>%{y}</b><br>£%{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(**plo(t,"Revenue Contribution by Segment",360))
        st.plotly_chart(fig, use_container_width=True)

    # Charts row 2: freq distribution + avg monetary by segment
    c3,c4 = st.columns(2)
    with c3:
        fig = px.histogram(rfm, x="frequency", nbins=30,
            color_discrete_sequence=[t["rose"]],
            labels={"frequency":"Purchase Frequency"})
        fig.update_layout(**plo(t,"Purchase Frequency Distribution",300))
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        avg_m = rfm.groupby("segment")["monetary"].mean().reset_index().sort_values("monetary",ascending=True)
        clrs3 = [SEGMENT_META.get(s,{}).get("color","#AAA") for s in avg_m["segment"]]
        fig = go.Figure(go.Bar(
            x=avg_m["segment"], y=avg_m["monetary"],
            marker=dict(color=clrs3, line=dict(width=0)),
            text=avg_m["monetary"].apply(lambda x:f"£{x:,.0f}"),
            textposition="outside", textfont=dict(color=t["muted"],size=9),
        ))
        fig.update_layout(**plo(t,"Avg Revenue per Customer by Segment",300))
        fig.update_xaxes(tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    # 3D scatter
    st.markdown('<div class="ie-sh">🧭 RFM 3D Cluster Map</div>', unsafe_allow_html=True)
    cmap = seg_colors(rfm)
    fig = px.scatter_3d(rfm, x="recency",y="frequency",z="monetary",
        color="segment", color_discrete_map=cmap, opacity=0.8,
        labels={"recency":"Recency (days)","frequency":"Frequency","monetary":"Monetary (£)"},
        hover_data={"customer_id":True})
    fig.update_traces(marker=dict(size=3.5))
    fig.update_layout(
        paper_bgcolor=t["plot_paper"], plot_bgcolor=t["plot_bg"],
        font=dict(family="Cabinet Grotesk",color=t["text"],size=10),
        height=500, margin=dict(l=0,r=0,t=20,b=0),
        scene=dict(
            xaxis=dict(backgroundcolor=t["card2"],gridcolor=t["grid"],color=t["muted"]),
            yaxis=dict(backgroundcolor=t["card2"],gridcolor=t["grid"],color=t["muted"]),
            zaxis=dict(backgroundcolor=t["card2"],gridcolor=t["grid"],color=t["muted"]),
        ),
        legend=dict(bgcolor=t["card"],bordercolor=t["border"],borderwidth=1,font=dict(color=t["text"],size=9)),
    )
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# TAB: SEGMENTS
# ═══════════════════════════════════════════════════════════════
def tab_segments(p, t):
    rfm = p["rfm"]
    st.markdown('<div class="ie-sh">🗂️ Segment Deep-Dive</div>', unsafe_allow_html=True)

    segs = sorted(rfm["segment"].unique())
    sel  = st.selectbox("Select a segment:", segs, key="seg_sel")
    meta = get_segment_meta(sel)
    sdf  = rfm[rfm["segment"]==sel]

    # Header card
    st.markdown(f"""
    <div class="ie-card" style="border-left:5px solid {meta['color']};">
        <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
            <span style="font-size:2.8rem;line-height:1;">{meta['emoji']}</span>
            <div style="flex:1;">
                <div style="font-family:'Fraunces',serif;font-size:1.4rem;font-weight:700;color:{t['text']};">{sel}</div>
                <div style="font-size:0.85rem;color:{t['muted']};margin-top:0.15rem;">{meta['description']}</div>
            </div>
            <div style="background:{meta['color']}33;border:1px solid {meta['color']}88;border-radius:999px;
                        padding:0.3rem 1rem;font-size:0.8rem;font-weight:700;color:{meta['color']};">
                Priority: {meta['priority']}
            </div>
        </div>
        <div style="margin-top:0.9rem;background:{t['bg_deep']};border-radius:10px;padding:0.7rem 1rem;font-size:0.86rem;">
            <strong>📌 Recommended Action:</strong> {meta['action']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs for segment
    html = '<div class="ie-stats-grid stagger">'
    avg_churn = float(sdf["churn_prob"].mean()) if "churn_prob" in sdf.columns else 0
    for v,l,c in [
        (f"{len(sdf):,}","Customers",meta["color"]),
        (f"{sdf['recency'].mean():.0f}d","Avg Recency",t["amber"]),
        (f"{sdf['frequency'].mean():.1f}","Avg Frequency",t["teal"]),
        (f"£{sdf['monetary'].mean():,.0f}","Avg Revenue",t["violet"]),
        (f"{avg_churn*100:.1f}%","Avg Churn Risk",t["danger"]),
    ]:
        html += stat(v,l,c)
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # Distributions
    c1,c2,c3 = st.columns(3)
    for col,fld,lbl in zip([c1,c2,c3],
        ["recency","frequency","monetary"],["Recency (days)","Frequency","Monetary (£)"]):
        fig=px.histogram(sdf,x=fld,nbins=20,color_discrete_sequence=[meta["color"]],labels={fld:lbl})
        fig.update_layout(**plo(t,lbl,240))
        col.plotly_chart(fig,use_container_width=True)

    # All-segment comparison table
    st.markdown('<div class="ie-sh">📋 All Segments at a Glance</div>', unsafe_allow_html=True)
    summary_rows = []
    for s in sorted(rfm["segment"].unique()):
        sd = rfm[rfm["segment"]==s]
        m  = get_segment_meta(s)
        cr = float(sd["churn_prob"].mean())*100 if "churn_prob" in sd.columns else 0
        summary_rows.append({
            "Segment": f"{m['emoji']} {s}",
            "Customers": len(sd),
            "Avg Recency (d)": round(sd["recency"].mean(),1),
            "Avg Frequency":   round(sd["frequency"].mean(),1),
            "Avg Revenue £":   round(sd["monetary"].mean(),2),
            "Churn Risk %":    round(cr,1),
            "Priority":        m["priority"],
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    # Customer table
    st.markdown('<div class="ie-sh">👥 Individual Customers</div>', unsafe_allow_html=True)
    dcols = ["customer_id","recency","frequency","monetary"]
    if "churn_prob" in sdf.columns:
        dcols += ["churn_prob","churn_predict"]
    st.dataframe(sdf[dcols].sort_values("monetary",ascending=False).reset_index(drop=True),
        use_container_width=True, height=320)

# ═══════════════════════════════════════════════════════════════
# TAB: CHURN
# ═══════════════════════════════════════════════════════════════
def tab_churn(p, t):
    rfm = p["rfm"]
    st.markdown('<div class="ie-sh">🔮 Churn Prediction Model</div>', unsafe_allow_html=True)

    if "churn_prob" not in rfm.columns:
        st.warning("⚠️ Churn model could not be trained — not enough data variety in this dataset.")
        return

    rep = p.get("churn_report") or {}
    acc = rep.get("accuracy",0)
    pr  = rep.get("1",{}).get("precision",0)
    rc  = rep.get("1",{}).get("recall",0)
    f1  = rep.get("1",{}).get("f1-score",0)

    html = '<div class="ie-stats-grid stagger">'
    for v,l,c in [
        (f"{acc*100:.1f}%","Accuracy",t["teal"]),
        (f"{pr*100:.1f}%","Precision",t["rose"]),
        (f"{rc*100:.1f}%","Recall",t["amber"]),
        (f"{f1*100:.1f}%","F1-Score",t["violet"]),
        (f"{rfm['churn_predict'].mean()*100:.1f}%","Predicted Churn",t["danger"]),
    ]:
        html += stat(v,l,c)
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ie-card" style="border-left:4px solid {t['teal']};margin-bottom:0.5rem;">
        <div style="font-family:'Fraunces',serif;font-size:1rem;font-weight:700;margin-bottom:0.4rem;">How Churn is Predicted</div>
        <div style="font-size:0.85rem;color:{t['muted']};line-height:1.7;">
            A <strong>Logistic Regression</strong> model is trained on RFM features (Recency, Frequency, Monetary).
            Customers inactive for <strong>&gt;90 days</strong> are labelled as churned for training.
            Class imbalance is handled via upsampling. Each customer receives a probability score (0–1).
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        fig=px.histogram(rfm,x="churn_prob",nbins=30,color_discrete_sequence=[t["rose"]],
            labels={"churn_prob":"Churn Probability"})
        fig.update_layout(**plo(t,"Churn Probability Distribution",320))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        sc=rfm.groupby("segment")["churn_prob"].mean().reset_index()
        sc.columns=["segment","avg"]; sc=sc.sort_values("avg")
        clrs=[SEGMENT_META.get(s,{}).get("color","#AAA") for s in sc["segment"]]
        fig=go.Figure(go.Bar(x=sc["avg"],y=sc["segment"],orientation="h",
            marker=dict(color=clrs,line=dict(width=0)),
            text=sc["avg"].apply(lambda x:f"{x*100:.1f}%"),
            textposition="outside",textfont=dict(color=t["muted"],size=9)))
        fig.update_layout(**plo(t,"Avg Churn Risk by Segment",320))
        st.plotly_chart(fig,use_container_width=True)

    # Elbow curve
    st.markdown('<div class="ie-sh">📐 Elbow Curve — Optimal Cluster Selection</div>', unsafe_allow_html=True)
    kr,inr,bk = p["k_range"],p["inertias"],p["n_clusters"]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=kr,y=inr,mode="lines+markers",
        line=dict(color=t["rose"],width=2.5),
        marker=dict(color=t["rose"],size=9,line=dict(color=t["card"],width=2)),
        hovertemplate="k=%{x}<br>Inertia=%{y:,.0f}<extra></extra>"))
    fig.add_vline(x=bk,line_dash="dash",line_color=t["teal"],line_width=2,
        annotation_text=f"  Best k={bk}",annotation_font=dict(color=t["teal"],size=12))
    fig.update_layout(**plo(t,"",300))
    st.plotly_chart(fig,use_container_width=True)

    # High risk table
    st.markdown('<div class="ie-sh">🚨 High-Risk Customers (Churn ≥ 60%)</div>', unsafe_allow_html=True)
    hr=rfm[rfm["churn_prob"]>=0.6].sort_values("churn_prob",ascending=False)
    if hr.empty:
        st.success("✅ No customers with churn probability ≥ 60% in this dataset.")
    else:
        st.markdown(f'<div style="font-size:0.84rem;color:{t["muted"]};margin-bottom:0.5rem;"><span class="pulse">🔴</span> {len(hr)} customers at elevated churn risk</div>', unsafe_allow_html=True)
        dcols=["customer_id","segment","recency","frequency","monetary","churn_prob"]
        st.dataframe(hr[dcols].reset_index(drop=True),use_container_width=True,height=300)

# ═══════════════════════════════════════════════════════════════
# TAB: CAMPAIGNS
# ═══════════════════════════════════════════════════════════════
def tab_campaigns(p, t):
    rfm = p["rfm"]
    st.markdown('<div class="ie-sh">📣 Campaign Generator</div>', unsafe_allow_html=True)

    left, right = st.columns([1,1.6])
    with left:
        st.markdown(f'<div style="font-size:0.78rem;color:{t["muted"]};font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.3rem;">Select Segment</div>', unsafe_allow_html=True)
        segs    = sorted(rfm["segment"].unique())
        sel_seg = st.selectbox("",segs,key="camp_seg",label_visibility="collapsed")

        st.markdown(f'<div style="font-size:0.78rem;color:{t["muted"]};font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin:0.7rem 0 0.3rem;">Customer Preview Name</div>', unsafe_allow_html=True)
        cname = st.text_input("","Alex",key="camp_name",label_visibility="collapsed")

        avg_ch = 0.0
        if "churn_prob" in rfm.columns:
            avg_ch = float(rfm[rfm["segment"]==sel_seg]["churn_prob"].mean())

        rc = t["danger"] if avg_ch>=0.6 else (t["warn"] if avg_ch>=0.35 else t["success"])
        st.markdown(f"""
        <div style="margin:0.9rem 0 1.2rem;">
            <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:0.2rem;">
                <span style="color:{t['muted']};font-weight:700;">Avg Segment Churn Risk</span>
                <strong style="color:{rc};">{avg_ch*100:.1f}%</strong>
            </div>
            <div class="ie-rbar"><div class="ie-rbar-f" style="width:{avg_ch*100:.1f}%;background:{rc};"></div></div>
        </div>
        """, unsafe_allow_html=True)

        meta = get_segment_meta(sel_seg)
        st.markdown(f"""
        <div style="background:{t['bg_deep']};border:1px solid {t['border']};border-radius:12px;padding:0.8rem 1rem;margin-bottom:1rem;font-size:0.82rem;">
            <div style="font-weight:700;color:{t['text']};margin-bottom:0.25rem;">{meta['emoji']} {sel_seg}</div>
            <div style="color:{t['muted']};">{meta['description']}</div>
            <div style="margin-top:0.4rem;font-size:0.78rem;"><strong>Action:</strong> {meta['action']}</div>
            <div style="margin-top:0.3rem;font-size:0.78rem;"><strong>Discount:</strong> {DISCOUNT_BY_SEGMENT.get(sel_seg,20)}% off</div>
        </div>
        """, unsafe_allow_html=True)

        gen = st.button("✨ Generate Campaign", use_container_width=True, key="camp_gen")
        if gen:
            st.session_state.camp = generate_campaign(sel_seg, cname, avg_ch)

    with right:
        res = st.session_state.get("camp")
        if res:
            m2 = get_segment_meta(res["segment"])
            st.markdown(f"""
            <div class="ie-card" style="border-left:5px solid {m2['color']};">
                <div class="ie-camp-meta">{res['urgency']} &nbsp;·&nbsp; {res['channel']}</div>
                <div class="ie-camp-sub">📧 {res['subject']}</div>
                <div class="ie-camp">{res['message']}</div>
                <div style="display:flex;gap:1rem;align-items:center;margin-top:0.5rem;flex-wrap:wrap;">
                    <div style="font-size:0.82rem;color:{t['muted']};">
                        Discount: <strong style="color:{m2['color']}">{res['discount']}% OFF</strong>
                    </div>
                    <div class="ie-pill" style="background:{m2['color']}22;border-color:{m2['color']}66;color:{m2['color']};">
                        {m2['emoji']} {res['segment']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Regenerate",key="camp_regen"):
                st.session_state.camp = generate_campaign(sel_seg, cname, avg_ch)
                st.rerun()
        else:
            st.markdown(f"""
            <div style="background:{t['card']};border:1px solid {t['border']};border-radius:16px;
                        padding:3rem 2rem;text-align:center;height:100%;">
                <div style="font-size:2.5rem;margin-bottom:0.6rem;">✨</div>
                <div style="font-family:'Fraunces',serif;font-size:1.1rem;color:{t['text']};margin-bottom:0.4rem;">Ready to Generate</div>
                <div style="font-size:0.85rem;color:{t['muted']};">Choose a segment, enter a name,<br>then click <strong style="color:{t['rose']};">Generate Campaign</strong></div>
            </div>
            """, unsafe_allow_html=True)

    # All-segment overview table
    st.markdown('<div class="ie-sh">📋 Campaign Playbook — All Segments</div>', unsafe_allow_html=True)
    rows=[]
    for seg in sorted(rfm["segment"].unique()):
        ac=float(rfm[rfm["segment"]==seg]["churn_prob"].mean()) if "churn_prob" in rfm.columns else 0.0
        c=generate_campaign(seg,"Customer",ac,variant=0)
        m=get_segment_meta(seg)
        rows.append({
            "Segment":f"{m['emoji']} {seg}",
            "Customers":int((rfm["segment"]==seg).sum()),
            "Priority":m["priority"],
            "Discount":f"{c['discount']}%",
            "Avg Churn Risk":f"{ac*100:.1f}%",
            "Urgency":c["urgency"],
            "Channel":c["channel"],
        })
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

# ═══════════════════════════════════════════════════════════════
# TAB: DECISION ENGINE
# ═══════════════════════════════════════════════════════════════
def tab_decision(p, t):
    rfm = p["rfm"]
    st.markdown('<div class="ie-sh">🧠 Decision Engine</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.86rem;color:{t["muted"]};margin-bottom:1rem;">Select any customer to get ML-powered, personalised recommendations combining segment + churn data.</div>', unsafe_allow_html=True)

    cids = rfm["customer_id"].tolist()
    sel  = st.selectbox("Customer ID:",cids,key="dec_cid")
    row  = rfm[rfm["customer_id"]==sel].iloc[0]
    cp   = float(row.get("churn_prob",0.0))
    seg  = row["segment"]
    mon  = float(row["monetary"])
    freq = int(row["frequency"])
    rec  = int(row["recency"])
    meta = get_segment_meta(seg)
    rc   = t["danger"] if cp>=0.6 else (t["warn"] if cp>=0.35 else t["success"])

    # Profile
    st.markdown(f"""
    <div class="ie-card" style="border-left:5px solid {meta['color']};">
        <div style="display:flex;gap:1.8rem;flex-wrap:wrap;align-items:center;">
            <div><div style="font-size:0.66rem;color:{t['muted']};text-transform:uppercase;letter-spacing:.08em;font-weight:700;">Customer ID</div>
                 <div style="font-size:1.2rem;font-weight:800;color:{t['text']};font-family:'Fraunces',serif;">{sel}</div></div>
            <div><div style="font-size:0.66rem;color:{t['muted']};text-transform:uppercase;letter-spacing:.08em;font-weight:700;">Segment</div>
                 <div style="font-size:1rem;">{meta['emoji']} {seg}</div></div>
            <div><div style="font-size:0.66rem;color:{t['muted']};text-transform:uppercase;letter-spacing:.08em;font-weight:700;">Last Purchase</div>
                 <div style="font-size:1rem;">{rec} days ago</div></div>
            <div><div style="font-size:0.66rem;color:{t['muted']};text-transform:uppercase;letter-spacing:.08em;font-weight:700;">Orders</div>
                 <div style="font-size:1rem;">{freq}</div></div>
            <div><div style="font-size:0.66rem;color:{t['muted']};text-transform:uppercase;letter-spacing:.08em;font-weight:700;">Lifetime Value</div>
                 <div style="font-size:1rem;">£{mon:,.2f}</div></div>
            <div><div style="font-size:0.66rem;color:{t['muted']};text-transform:uppercase;letter-spacing:.08em;font-weight:700;">Churn Risk</div>
                 <div style="font-size:1rem;font-weight:800;color:{rc};">{cp*100:.1f}%</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_r,col_g = st.columns([1.3,1])
    with col_r:
        dec = decision_engine(seg,cp,mon,freq)
        st.markdown(f'<div style="font-family:\'Fraunces\',serif;font-size:1rem;font-weight:700;margin:0.6rem 0 0.4rem;color:{t["text"]};">🎯 AI Recommendations</div>', unsafe_allow_html=True)
        for item in dec["recommendations"]:
            st.markdown(f'<div class="ie-rec">{item}</div>', unsafe_allow_html=True)
    with col_g:
        fig=go.Figure(go.Indicator(
            mode="gauge+number", value=round(cp*100,1),
            title=dict(text="Churn Risk",font=dict(family="Fraunces",size=13,color=t["text"])),
            number=dict(suffix="%",font=dict(color=t["text"],family="Fraunces",size=28)),
            gauge=dict(
                axis=dict(range=[0,100],tickcolor=t["muted"],tickfont=dict(color=t["muted"])),
                bar=dict(color=t["rose"]), bgcolor=t["card2"], borderwidth=0,
                steps=[
                    dict(range=[0,40],  color=t["card2"]),
                    dict(range=[40,70], color="rgba(192,120,48,0.15)" if t["mode"]=="light" else "rgba(232,160,80,0.15)"),
                    dict(range=[70,100],color="rgba(192,58,58,0.15)"  if t["mode"]=="light" else "rgba(232,96,96,0.15)"),
                ],
                threshold=dict(line=dict(color=t["danger"],width=3),thickness=0.78,value=70),
            ),
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",font=dict(color=t["text"]),
            height=260,margin=dict(l=20,r=20,t=30,b=10))
        st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="ie-sh">📣 Personalised Campaign for This Customer</div>', unsafe_allow_html=True)
    camp=generate_campaign(seg,f"Customer {sel}",cp)
    st.markdown(f"""
    <div class="ie-camp">
        <div class="ie-camp-meta">{camp['urgency']} &nbsp;·&nbsp; {camp['channel']}</div>
        <div class="ie-camp-sub">📧 {camp['subject']}</div>
        {camp['message']}
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB: RFM ANALYSIS
# ═══════════════════════════════════════════════════════════════
def tab_rfm(p, t):
    rfm = p["rfm"]
    st.markdown('<div class="ie-sh">📈 RFM Feature Analysis</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        corr=rfm[["recency","frequency","monetary"]].corr()
        # Use [[position, color]] format — the only format Plotly accepts for custom colorscales
        mid_color = "rgb(22,20,18)" if t["mode"]=="dark" else "rgb(247,243,238)"
        corr_scale = [
            [0.0,  t["rose"]],
            [0.5,  mid_color],
            [1.0,  t["teal"]],
        ]
        fig=px.imshow(corr, text_auto=".2f",
            color_continuous_scale=corr_scale,
            zmin=-1, zmax=1)
        fig.update_layout(**plo(t,"RFM Correlation Heatmap",320))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        metric=st.selectbox("Box plot metric:",["recency","frequency","monetary"],key="rfm_m")
        cmap=seg_colors(rfm)
        fig=px.box(rfm,x="segment",y=metric,color="segment",color_discrete_map=cmap)
        fig.update_layout(**plo(t,f"{metric.title()} Distribution by Segment",320))
        fig.update_xaxes(tickangle=-35)
        st.plotly_chart(fig,use_container_width=True)

    c3,c4=st.columns(2)
    with c3:
        fig=px.scatter(rfm,x="recency",y="monetary",color="segment",
            size="frequency",color_discrete_map=cmap,opacity=0.75,
            hover_data=["customer_id","frequency"],
            labels={"recency":"Recency (days)","monetary":"Monetary (£)"})
        fig.update_layout(**plo(t,"Recency vs Monetary (size = frequency)",380))
        st.plotly_chart(fig,use_container_width=True)
    with c4:
        fig=px.scatter(rfm,x="frequency",y="monetary",color="segment",
            size="recency",color_discrete_map=cmap,opacity=0.75,
            hover_data=["customer_id","recency"],
            labels={"frequency":"Frequency","monetary":"Monetary (£)"})
        fig.update_layout(**plo(t,"Frequency vs Monetary (size = recency)",380))
        st.plotly_chart(fig,use_container_width=True)

    # RFM score distributions
    st.markdown('<div class="ie-sh">📊 Individual RFM Metric Distributions</div>', unsafe_allow_html=True)
    c5,c6,c7=st.columns(3)
    for col,fld,lbl,clr in zip([c5,c6,c7],
        ["recency","frequency","monetary"],
        ["Recency (days)","Purchase Frequency","Monetary Value (£)"],
        [t["rose"],t["teal"],t["amber"]]):
        fig=px.histogram(rfm,x=fld,nbins=25,color_discrete_sequence=[clr],labels={fld:lbl})
        fig.update_layout(**plo(t,lbl,250))
        col.plotly_chart(fig,use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# TAB: EXPORT
# ═══════════════════════════════════════════════════════════════
def tab_export(p, t):
    rfm = p["rfm"]
    st.markdown('<div class="ie-sh">⬇️ Export Results</div>', unsafe_allow_html=True)

    with st.spinner("Preparing export files..."):
        exp=rfm.copy()
        exp["campaign_subject"]     = exp.apply(lambda r: generate_campaign(r["segment"],f"Customer {r['customer_id']}",float(r.get("churn_prob",0)))["subject"],axis=1)
        exp["campaign_message"]     = exp.apply(lambda r: generate_campaign(r["segment"],f"Customer {r['customer_id']}",float(r.get("churn_prob",0)))["message"],axis=1)
        exp["recommended_discount"] = exp["segment"].map(DISCOUNT_BY_SEGMENT)
        exp["recommended_channel"]  = exp.apply(lambda r: generate_campaign(r["segment"],"X",float(r.get("churn_prob",0)))["channel"],axis=1)
        exp["priority"]             = exp["segment"].map(lambda s: get_segment_meta(s)["priority"])

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.2rem;">
        <div class="ie-card" style="text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:0.3rem;">📊</div>
            <div style="font-family:'Fraunces',serif;font-size:0.95rem;font-weight:700;margin-bottom:0.2rem;">Full Results</div>
            <div style="font-size:0.76rem;color:{t['muted']};margin-bottom:0.8rem;">{len(exp)} customers · All fields + campaigns</div>
        </div>
        <div class="ie-card" style="text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:0.3rem;">📋</div>
            <div style="font-family:'Fraunces',serif;font-size:0.95rem;font-weight:700;margin-bottom:0.2rem;">Segment Summary</div>
            <div style="font-size:0.76rem;color:{t['muted']};margin-bottom:0.8rem;">{rfm['segment'].nunique()} segments · Avg metrics</div>
        </div>
        <div class="ie-card" style="text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:0.3rem;">🚨</div>
            <div style="font-family:'Fraunces',serif;font-size:0.95rem;font-weight:700;margin-bottom:0.2rem;">High-Risk Customers</div>
            <div style="font-size:0.76rem;color:{t['muted']};margin-bottom:0.8rem;">{len(rfm[rfm.get('churn_prob',pd.Series([0]*len(rfm))) >= 0.6] if 'churn_prob' in rfm.columns else pd.DataFrame())} churn-risk records</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    b1=io.StringIO(); exp.to_csv(b1,index=False)
    sm=segment_summary(rfm); b2=io.StringIO(); sm.to_csv(b2,index=False)

    hr=rfm[rfm["churn_prob"]>=0.6] if "churn_prob" in rfm.columns else pd.DataFrame()
    b3=io.StringIO()
    if not hr.empty:
        hr_exp=hr.copy()
        hr_exp["campaign"]=hr_exp.apply(lambda r:generate_campaign(r["segment"],f"Customer {r['customer_id']}",float(r["churn_prob"]))["message"],axis=1)
        hr_exp.to_csv(b3,index=False)

    c1,c2,c3=st.columns(3)
    with c1:
        st.download_button("⬇️ Full Results CSV",b1.getvalue(),"insightengine_results.csv","text/csv",use_container_width=True)
    with c2:
        st.download_button("⬇️ Segment Summary CSV",b2.getvalue(),"insightengine_summary.csv","text/csv",use_container_width=True)
    with c3:
        if not hr.empty:
            st.download_button("⬇️ High-Risk Customers CSV",b3.getvalue(),"insightengine_highrisk.csv","text/csv",use_container_width=True)
        else:
            st.info("No high-risk customers to export.")

    st.markdown('<div class="ie-sh">👀 Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(exp.head(25),use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    init()
    t = T()
    css(t)
    nav(t)

    pipeline = st.session_state.get("pipeline")

    if pipeline is None:
        # Welcome / config page
        src, uploaded, n_clusters, run_btn = welcome(t)

        if run_btn:
            with st.spinner("⚙️ Running ML pipeline — this takes a few seconds..."):
                try:
                    if "Upload" in src and uploaded is not None:
                        raw = pd.read_csv(uploaded)
                        st.session_state.src = uploaded.name
                    else:
                        raw = make_sample()
                        st.session_state.src = "sample_data.csv"
                    pl = run_full_pipeline(raw, n_clusters=n_clusters)
                    st.session_state.pipeline = pl
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Pipeline error: {e}")
                    st.exception(e)
    else:
        rfm = pipeline["rfm"]
        src_name = st.session_state.get("src","data")

        # Info strip
        st.markdown(f"""
        <div class="ie-strip fade-up">
            <span>📁 <strong style="color:{t['rose']}">{src_name}</strong></span>
            <span style="color:{t['muted']}">👥 <strong style="color:{t['text']}">{len(rfm):,}</strong> customers</span>
            <span style="color:{t['muted']}">🎯 <strong style="color:{t['text']}">{pipeline['n_clusters']}</strong> clusters</span>
            <span style="color:{t['muted']}">📐 Silhouette <strong style="color:{t['text']}">{pipeline['silhouette']}</strong></span>
            <span style="color:{t['muted']}">🗂️ <strong style="color:{t['text']}">{rfm['segment'].nunique()}</strong> segments</span>
        </div>
        """, unsafe_allow_html=True)

        # Reset button
        rcol1,rcol2 = st.columns([9,1])
        with rcol2:
            if st.button("↩ Reset",key="reset_btn"):
                st.session_state.pipeline = None
                st.session_state.camp     = None
                st.rerun()
        # Style reset as outline
        st.markdown(f"""
        <style>
        div[data-testid="column"]:last-child .stButton>button {{
            background:transparent !important;
            color:{t['muted']} !important;
            border:1.5px solid {t['border']} !important;
            border-radius:10px !important;
            font-size:0.8rem !important;
            padding:0.3rem 0.8rem !important;
            box-shadow:none !important;
            height:32px !important;
        }}
        div[data-testid="column"]:last-child .stButton>button:hover {{
            color:{t['text']} !important;
            border-color:{t['text']} !important;
            transform:none !important;
        }}
        </style>
        """, unsafe_allow_html=True)

        tabs = st.tabs([
            "📊 Overview",
            "🗂️ Segments",
            "🔮 Churn",
            "📣 Campaigns",
            "🧠 Decision Engine",
            "📈 RFM Analysis",
            "⬇️ Export",
        ])
        with tabs[0]: tab_overview(pipeline,t)
        with tabs[1]: tab_segments(pipeline,t)
        with tabs[2]: tab_churn(pipeline,t)
        with tabs[3]: tab_campaigns(pipeline,t)
        with tabs[4]: tab_decision(pipeline,t)
        with tabs[5]: tab_rfm(pipeline,t)
        with tabs[6]: tab_export(pipeline,t)

if __name__ == "__main__":
    main()
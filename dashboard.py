import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LeadLens · Intelligence Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, .stApp {
    background: #0b0f1a !important;
    color: #e2e8f0 !important;
    font-family: 'Sora', sans-serif;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d1221 !important;
    border-right: 1px solid #1e293b !important;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }
section[data-testid="stSidebar"] .sidebar-title {
    font-size: 22px; font-weight: 700;
    color: #f8fafc !important; letter-spacing: -0.5px;
}
section[data-testid="stSidebar"] hr {
    border-color: #1e293b !important;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* ── Radio buttons in sidebar ── */
.stRadio > label { color: #64748b !important; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.stRadio div[role="radiogroup"] label {
    color: #94a3b8 !important;
    font-size: 14px !important;
    padding: 8px 12px;
    border-radius: 8px;
    transition: background 0.15s;
}
.stRadio div[role="radiogroup"] label:hover { background: #1e293b !important; }

/* ── Page header ── */
.page-header {
    display: flex; align-items: flex-start;
    gap: 16px; margin-bottom: 2rem;
}
.page-header-badge {
    display: inline-block;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: white; font-size: 11px; font-weight: 600;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 6px;
}
.page-title {
    font-size: 32px; font-weight: 700; color: #f8fafc;
    letter-spacing: -0.8px; line-height: 1.2; margin: 0;
}
.page-sub { color: #64748b; font-size: 14px; margin-top: 4px; }

/* ── Divider ── */
.divider {
    border: none; border-top: 1px solid #1e293b;
    margin: 1.5rem 0;
}

/* ── KPI Cards ── */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 1.5rem; }
.kpi-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.kpi-card.blue::before  { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.kpi-card.purple::before{ background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.kpi-card.green::before { background: linear-gradient(90deg, #10b981, #34d399); }
.kpi-card.amber::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.kpi-card.red::before   { background: linear-gradient(90deg, #ef4444, #f87171); }
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
.kpi-icon { font-size: 22px; margin-bottom: 10px; }
.kpi-label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px; }
.kpi-value { font-size: 28px; font-weight: 700; color: #f8fafc; letter-spacing: -0.5px; font-family: 'JetBrains Mono', monospace; }
.kpi-delta { font-size: 12px; margin-top: 4px; }
.kpi-delta.pos { color: #34d399; }
.kpi-delta.neg { color: #f87171; }
.kpi-delta.neu { color: #94a3b8; }

/* ── Section titles ── */
.section-label {
    font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px;
    color: #475569; margin-bottom: 6px;
}
.section-title {
    font-size: 18px; font-weight: 600; color: #f1f5f9; margin-bottom: 1rem; letter-spacing: -0.3px;
}

/* ── Insight cards ── */
.insight-card {
    border-radius: 12px; padding: 16px 18px;
    border: 1px solid; margin-bottom: 10px;
    display: flex; gap: 12px; align-items: flex-start;
}
.insight-card.good  { background: #022c22; border-color: #065f46; }
.insight-card.bad   { background: #2d0a0a; border-color: #7f1d1d; }
.insight-card.warn  { background: #261a00; border-color: #78350f; }
.insight-card.info  { background: #0c1a2e; border-color: #1e3a5f; }
.insight-card .icon { font-size: 20px; flex-shrink: 0; margin-top: 2px; }
.insight-card .body {}
.insight-card .title { font-weight: 600; font-size: 14px; color: #f1f5f9; margin-bottom: 3px; }
.insight-card .desc  { font-size: 13px; color: #94a3b8; line-height: 1.5; }

/* ── Recommendation pills ── */
.rec-pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: #1e293b; border: 1px solid #334155;
    color: #cbd5e1; font-size: 13px;
    padding: 8px 14px; border-radius: 24px; margin: 4px;
}
.rec-pill .badge {
    background: #3b82f6; color: white;
    font-size: 10px; font-weight: 700;
    padding: 2px 7px; border-radius: 12px;
    text-transform: uppercase; letter-spacing: 0.5px;
}
.rec-pill .badge.high   { background: #ef4444; }
.rec-pill .badge.medium { background: #f59e0b; }
.rec-pill .badge.low    { background: #10b981; }

/* ── Risk items ── */
.risk-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; border-radius: 10px;
    background: #111827; border: 1px solid #1e293b; margin-bottom: 8px;
}
.risk-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.risk-dot.high   { background: #ef4444; box-shadow: 0 0 8px #ef4444; }
.risk-dot.medium { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
.risk-dot.low    { background: #10b981; box-shadow: 0 0 8px #10b981; }
.risk-text { font-size: 13px; color: #cbd5e1; flex: 1; }
.risk-level { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.risk-level.high   { color: #f87171; }
.risk-level.medium { color: #fbbf24; }
.risk-level.low    { color: #34d399; }

/* ── Prediction card ── */
.pred-card {
    background: linear-gradient(135deg, #0f172a, #1e1b4b);
    border: 1px solid #312e81; border-radius: 16px; padding: 22px;
}
.pred-title { font-size: 16px; font-weight: 600; color: #a5b4fc; margin-bottom: 4px; }
.pred-value { font-size: 36px; font-weight: 700; color: #e0e7ff; font-family: 'JetBrains Mono', monospace; letter-spacing: -1px; }
.pred-note  { font-size: 12px; color: #6366f1; margin-top: 6px; }

/* ── Info page ── */
.info-section {
    background: #111827; border: 1px solid #1e293b;
    border-radius: 16px; padding: 24px; margin-bottom: 16px;
}
.info-section h3 { color: #e2e8f0; font-size: 16px; font-weight: 600; margin-top: 0; }
.feature-tag {
    display: inline-block; background: #1e293b; color: #94a3b8;
    font-size: 12px; padding: 4px 10px; border-radius: 6px; margin: 3px;
}

/* ── Plotly chart backgrounds ── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── Streamlit native elements ── */
.stProgress > div > div > div { background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important; }
.stProgress > div > div { background: #1e293b !important; }
div[data-testid="stFileUploader"] {
    background: #111827; border: 2px dashed #1e293b;
    border-radius: 14px; padding: 12px;
}
div[data-testid="stFileUploader"]:hover { border-color: #3b82f6; }
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    font-family: 'Sora', sans-serif !important;
}
.stNumberInput input, .stSelectbox select, .stTextInput input {
    background: #111827 !important; color: #e2e8f0 !important;
    border: 1px solid #1e293b !important; border-radius: 10px !important;
}
.stDataFrame { border-radius: 10px; overflow: hidden; }
.stExpander { background: #111827 !important; border: 1px solid #1e293b !important; border-radius: 12px !important; }
label, .stSelectbox label, .stNumberInput label { color: #94a3b8 !important; font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Sora, sans-serif"),
    xaxis=dict(gridcolor="#1e293b", linecolor="#1e293b", showgrid=True),
    yaxis=dict(gridcolor="#1e293b", linecolor="#1e293b", showgrid=True),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e293b"),
)
PALETTE = ["#3b82f6","#8b5cf6","#10b981","#f59e0b","#ef4444","#06b6d4","#ec4899","#84cc16"]

def kpi(col, icon, label, value, delta_text="", delta_pos=None, color="blue"):
    pos = "pos" if delta_pos else ("neg" if delta_pos is False else "neu")
    col.markdown(f"""
<div class='kpi-card {color}'>
  <div class='kpi-icon'>{icon}</div>
  <div class='kpi-label'>{label}</div>
  <div class='kpi-value'>{value}</div>
  <div class='kpi-delta {pos}'>{delta_text}</div>
</div>""", unsafe_allow_html=True)


def insight(kind, icon, title, desc):
    st.markdown(f"""
<div class='insight-card {kind}'>
  <div class='icon'>{icon}</div>
  <div class='body'>
    <div class='title'>{title}</div>
    <div class='desc'>{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)


def risk_item(level, text):
    st.markdown(f"""
<div class='risk-item'>
  <div class='risk-dot {level}'></div>
  <div class='risk-text'>{text}</div>
  <div class='risk-level {level}'>{level.upper()}</div>
</div>""", unsafe_allow_html=True)


@st.cache_data
def load_data(file):
    if file.name.lower().endswith("csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    cols_lower = {c.strip().lower(): c for c in df.columns}

    def find(*keys):
        for k in keys:
            for col_l, col_orig in cols_lower.items():
                if k in col_l:
                    return col_orig
        return None

    status_col = find("status", "stage", "state")
    source_col = find("source", "channel", "medium", "campaign")
    rev_col    = find("revenue", "amount", "value", "deal", "sale")
    date_col   = find("date", "created", "time", "closed")
    cost_col   = find("cost", "spend", "budget", "expense")
    region_col = find("region", "area", "territory", "location", "city", "country")
    owner_col  = find("owner", "rep", "agent", "assignee", "salesperson")

    # Normalise status
    if status_col:
        df[status_col] = df[status_col].astype(str).str.strip().str.lower()

    # Parse dates
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    return df, status_col, source_col, rev_col, date_col, cost_col, region_col, owner_col


def fmt_inr(n):
    if n >= 1_00_00_000:
        return f"₹{n/1_00_00_000:.2f}Cr"
    elif n >= 1_00_000:
        return f"₹{n/1_00_000:.1f}L"
    elif n >= 1_000:
        return f"₹{n/1_000:.1f}K"
    return f"₹{n:,.0f}"


def is_won(series):
    return series.isin(["won","closed","converted","sale","deal","yes","true","1","success","complete","completed"])


def simple_forecast(series_vals, periods=3):
    """Dead-simple linear extrapolation."""
    x = np.arange(len(series_vals))
    if len(x) < 2:
        return [series_vals[-1]] * periods
    m, b = np.polyfit(x, series_vals, 1)
    future = [max(0, m * (len(x) + i) + b) for i in range(periods)]
    return future


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🔬 LeadLens</div>", unsafe_allow_html=True)
    st.markdown("<small style='color:#475569'>AI-Powered Lead Intelligence</small>", unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "NAVIGATE",
        ["📊 Dashboard", "💡 Insights & AI", "🗺️ Channel Deep-Dive", "📈 Predictions", "⚠️ Risks", "ℹ️ How It Works"],
        label_visibility="visible",
    )

    st.markdown("---")
    st.markdown("""
<small style='color:#475569;line-height:1.8'>
<b style='color:#64748b'>SUPPORTED COLUMNS</b><br>
Status / Stage<br>
Source / Channel<br>
Revenue / Amount<br>
Date / Created<br>
Cost / Spend<br>
Region / Territory<br>
Owner / Rep<br>
<i>…any CSV or XLSX</i>
</small>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HOW IT WORKS PAGE
# ─────────────────────────────────────────────
if page == "ℹ️ How It Works":
    st.markdown("""
<div class='page-header'>
  <div>
    <div class='page-badge' style='display:inline-block;background:linear-gradient(135deg,#3b82f6,#8b5cf6);color:white;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px'>Guide</div>
    <div class='page-title' style='font-size:32px;font-weight:700;color:#f8fafc;letter-spacing:-0.8px'>How LeadLens Works</div>
    <div class='page-sub' style='color:#64748b;font-size:14px;margin-top:4px'>Upload any CSV or Excel file — the dashboard auto-detects columns and builds your full analysis.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    cols = st.columns(2)

    with cols[0]:
        st.markdown("""
<div class='info-section'>
<h3>🎯 What this dashboard does</h3>
<p style='color:#94a3b8;font-size:14px;line-height:1.8'>
LeadLens ingests any sales/lead CSV or Excel file and automatically:
</p>
<ul style='color:#94a3b8;font-size:14px;line-height:2'>
  <li>Detects your column types (status, source, revenue, date, cost…)</li>
  <li>Calculates conversion rates, ROI, revenue, and pipeline velocity</li>
  <li>Identifies your best and worst performing channels</li>
  <li>Runs trend analysis and generates 3-period revenue forecasts</li>
  <li>Surfaces automated insights, recommendations, and risks</li>
</ul>
</div>

<div class='info-section'>
<h3>📊 Dashboard Sections</h3>
<span class='feature-tag'>📊 Dashboard — KPIs & overview</span>
<span class='feature-tag'>💡 Insights & AI — Patterns & recs</span>
<span class='feature-tag'>🗺️ Channel Deep-Dive — Source analysis</span>
<span class='feature-tag'>📈 Predictions — Revenue forecast</span>
<span class='feature-tag'>⚠️ Risks — Concentration & exposure</span>
</div>
""", unsafe_allow_html=True)

    with cols[1]:
        st.markdown("""
<div class='info-section'>
<h3>📁 Accepted File Formats</h3>
<p style='color:#94a3b8;font-size:14px;line-height:1.8'>
Upload <b style='color:#e2e8f0'>.csv</b> or <b style='color:#e2e8f0'>.xlsx</b> files. The dashboard works with any column names — it uses fuzzy matching to find relevant columns automatically.
</p>
<h3 style='margin-top:16px'>🔎 Auto-detected Columns</h3>
<table style='width:100%;font-size:13px;color:#94a3b8;border-collapse:collapse'>
  <tr><td style='padding:6px;border-bottom:1px solid #1e293b;color:#e2e8f0'>Status/Stage</td><td style='padding:6px;border-bottom:1px solid #1e293b'>Won, Lost, Closed, Open…</td></tr>
  <tr><td style='padding:6px;border-bottom:1px solid #1e293b;color:#e2e8f0'>Source/Channel</td><td style='padding:6px;border-bottom:1px solid #1e293b'>Organic, Paid, Referral…</td></tr>
  <tr><td style='padding:6px;border-bottom:1px solid #1e293b;color:#e2e8f0'>Revenue/Amount</td><td style='padding:6px;border-bottom:1px solid #1e293b'>Deal value, sale amount…</td></tr>
  <tr><td style='padding:6px;border-bottom:1px solid #1e293b;color:#e2e8f0'>Date/Created</td><td style='padding:6px;border-bottom:1px solid #1e293b'>Close date, created date…</td></tr>
  <tr><td style='padding:6px;border-bottom:1px solid #1e293b;color:#e2e8f0'>Cost/Spend</td><td style='padding:6px;border-bottom:1px solid #1e293b'>Marketing spend, budget…</td></tr>
  <tr><td style='padding:6px;color:#e2e8f0'>Region/Owner</td><td style='padding:6px'>Territory, sales rep…</td></tr>
</table>
</div>
<div class='info-section'>
<h3>⚡ Tips for best results</h3>
<ul style='color:#94a3b8;font-size:14px;line-height:2'>
  <li>Include a <b style='color:#e2e8f0'>Status</b> column with "Won"/"Lost" values for conversion metrics</li>
  <li>Add a <b style='color:#e2e8f0'>Date</b> column to unlock trend charts & forecasting</li>
  <li>Include <b style='color:#e2e8f0'>Cost</b> to see ROI per channel</li>
  <li>Works with <b style='color:#e2e8f0'>any domain</b>: SaaS, e-commerce, real estate, agencies…</li>
</ul>
</div>
""", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
#  FILE UPLOAD (shown on all other pages)
# ─────────────────────────────────────────────
st.markdown("""
<div class='page-header'>
  <div>
    <div style='display:inline-block;background:linear-gradient(135deg,#3b82f6,#8b5cf6);color:white;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px'>Lead Intelligence</div>
    <div style='font-size:32px;font-weight:700;color:#f8fafc;letter-spacing:-0.8px'>LeadLens Dashboard</div>
    <div style='color:#64748b;font-size:14px;margin-top:4px'>Upload your data · Get instant AI-powered insights</div>
  </div>
</div>
""", unsafe_allow_html=True)

file = st.file_uploader("", type=["csv", "xlsx"], label_visibility="collapsed")

if not file:
    st.markdown("""
<div style='text-align:center;padding:60px 20px'>
  <div style='font-size:48px;margin-bottom:16px'>📂</div>
  <div style='font-size:18px;color:#64748b;margin-bottom:8px'>Drop your CSV or Excel file above to get started</div>
  <div style='font-size:13px;color:#475569'>Supports any sales, lead, or marketing dataset</div>
</div>
""", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────
df, status_col, source_col, rev_col, date_col, cost_col, region_col, owner_col = load_data(file)

total      = len(df)
converted  = is_won(df[status_col]).sum() if status_col else 0
revenue    = df[rev_col].sum() if rev_col else 0
cost       = df[cost_col].sum() if cost_col else 0
conv_rate  = (converted / total * 100) if total else 0
roi        = ((revenue - cost) / cost * 100) if cost > 0 else 0
avg_deal   = (df.loc[is_won(df[status_col]), rev_col].mean() if (status_col and rev_col) else
              (df[rev_col].mean() if rev_col else 0)) or 0


# ═══════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════
if page == "📊 Dashboard":

    # ── KPIs ──
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "📋", "Total Leads", f"{total:,}", "dataset size", None, "blue")
    kpi(c2, "✅", "Converted", f"{converted:,}", f"{conv_rate:.1f}% rate", conv_rate > 20, "green")
    kpi(c3, "💰", "Revenue", fmt_inr(revenue), "gross", None, "purple")
    kpi(c4, "📊", "ROI", f"{roi:.1f}%" if cost > 0 else "N/A", "on spend" if cost > 0 else "add cost col", roi > 100 if cost > 0 else None, "amber")
    kpi(c5, "🎯", "Avg Deal", fmt_inr(avg_deal) if avg_deal else "N/A", "per won lead", None, "blue")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main charts ──
    left, right = st.columns([1.6, 1])

    with left:
        if date_col and rev_col:
            st.markdown("<div class='section-title'>Revenue Over Time</div>", unsafe_allow_html=True)
            tmp = df.dropna(subset=[date_col, rev_col]).copy()
            tmp["month"] = tmp[date_col].dt.to_period("M").astype(str)
            trend = tmp.groupby("month")[rev_col].sum().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend["month"], y=trend[rev_col],
                mode="lines+markers",
                line=dict(color="#3b82f6", width=2.5),
                marker=dict(color="#3b82f6", size=6),
                fill="tozeroy",
                fillcolor="rgba(59,130,246,0.08)",
                name="Revenue"
            ))
            fig.update_layout(**CHART_LAYOUT, height=280)
            st.plotly_chart(fig, use_container_width=True)

        elif source_col:
            st.markdown("<div class='section-title'>Channel Performance</div>", unsafe_allow_html=True)
            data = df[source_col].value_counts().reset_index()
            data.columns = ["Channel", "Leads"]
            fig = px.bar(data, x="Channel", y="Leads", text="Leads",
                         color="Channel", color_discrete_sequence=PALETTE)
            fig.update_traces(textposition="outside")
            fig.update_layout(**CHART_LAYOUT, height=280, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with right:
        if status_col:
            st.markdown("<div class='section-title'>Lead Status Split</div>", unsafe_allow_html=True)
            vc = df[status_col].value_counts().reset_index()
            vc.columns = ["Status", "Count"]
            fig = px.pie(vc, names="Status", values="Count",
                         color_discrete_sequence=PALETTE,
                         hole=0.55)
            fig.update_traces(textinfo="percent+label", textfont_size=12)
            fig.update_layout(**CHART_LAYOUT, height=280,
                              showlegend=False,
                              annotations=[dict(text=f"{total}", x=0.5, y=0.5,
                                                font=dict(size=24, color="#f8fafc"), showarrow=False)])
            st.plotly_chart(fig, use_container_width=True)

    # ── Conversion by source ──
    if source_col and status_col:
        st.markdown("<div class='section-title'>Conversion Rate by Channel</div>", unsafe_allow_html=True)
        perf = df.groupby(source_col).agg(
            Leads=(source_col, "count"),
            Won=(status_col, lambda x: is_won(x).sum())
        ).reset_index()
        perf["Rate %"] = (perf["Won"] / perf["Leads"] * 100).round(1)
        perf = perf.sort_values("Rate %", ascending=True)

        fig = go.Figure(go.Bar(
            x=perf["Rate %"], y=perf[source_col],
            orientation="h",
            text=[f"{v}%" for v in perf["Rate %"]],
            textposition="outside",
            marker=dict(
                color=perf["Rate %"],
                colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#10b981"]],
                showscale=False,
            )
        ))
        fig.update_layout(**CHART_LAYOUT, height=max(220, len(perf)*40))
        st.plotly_chart(fig, use_container_width=True)

    # ── Goal tracker ──
    st.markdown("<div class='section-title'>Goal Tracker</div>", unsafe_allow_html=True)
    g1, g2 = st.columns([2, 1])
    with g1:
        target = st.number_input("Set Revenue Target", value=int(revenue * 1.3) or 50000,
                                 step=10000, format="%d")
    progress = min((revenue / target * 100) if target else 0, 100)
    with g2:
        remaining = max(target - revenue, 0)
        st.markdown(f"""
<div class='kpi-card green' style='margin-top:28px'>
  <div class='kpi-label'>Remaining to Goal</div>
  <div class='kpi-value' style='font-size:20px'>{fmt_inr(remaining)}</div>
</div>""", unsafe_allow_html=True)
    st.progress(int(progress))
    st.caption(f"**{progress:.1f}%** of ₹{target:,} achieved")

    # ── Raw data ──
    with st.expander("📄 View Raw Data"):
        st.dataframe(df, use_container_width=True)


# ═══════════════════════════════════════════════════════
#  PAGE: INSIGHTS & AI
# ═══════════════════════════════════════════════════════
elif page == "💡 Insights & AI":
    st.markdown("<div class='page-title' style='font-size:26px;font-weight:700;color:#f8fafc;margin-bottom:1.5rem'>Insights & Recommendations</div>", unsafe_allow_html=True)

    ins_col, rec_col = st.columns(2)

    with ins_col:
        st.markdown("<div class='section-title'>🔍 Auto-Generated Insights</div>", unsafe_allow_html=True)

        if status_col and total > 0:
            if conv_rate >= 30:
                insight("good", "🏆", "Excellent Conversion Rate",
                        f"Your {conv_rate:.1f}% conversion rate is well above the 20% industry benchmark. Your qualifying process is working.")
            elif conv_rate >= 15:
                insight("warn", "⚡", "Moderate Conversion Rate",
                        f"At {conv_rate:.1f}%, there's room to improve. Consider tightening ICP criteria or improving follow-up sequences.")
            else:
                insight("bad", "🚨", "Low Conversion Rate",
                        f"Only {conv_rate:.1f}% of leads convert. Investigate drop-off stages and consider lead scoring to prioritise high-intent prospects.")

        if source_col and status_col:
            perf = df.groupby(source_col).agg(
                leads=(source_col,"count"),
                won=(status_col, lambda x: is_won(x).sum())
            )
            perf["rate"] = perf["won"] / perf["leads"]
            best = perf["rate"].idxmax()
            worst = perf["rate"].idxmin()
            best_r = perf.loc[best, "rate"] * 100
            worst_r = perf.loc[worst, "rate"] * 100

            insight("good", "🔥", f"Top Channel: {best}",
                    f"{best} converts at {best_r:.1f}% — your highest-performing source. Double budget here for fastest returns.")
            insight("bad", "📉", f"Underperforming: {worst}",
                    f"{worst} has only {worst_r:.1f}% conversion. Audit the lead quality or pause spending until root cause is found.")

            # volume vs quality
            top_vol = perf["leads"].idxmax()
            top_vol_rate = perf.loc[top_vol, "rate"] * 100
            if top_vol != best:
                insight("warn", "⚖️", "Volume ≠ Quality Mismatch",
                        f"{top_vol} sends the most leads but converts at only {top_vol_rate:.1f}%. High volume from poor sources inflates pipeline and wastes sales time.")

        if rev_col and source_col:
            rev_by_src = df.groupby(source_col)[rev_col].sum()
            top_rev_src = rev_by_src.idxmax()
            insight("good", "💎", f"Revenue Champion: {top_rev_src}",
                    f"{top_rev_src} generates {fmt_inr(rev_by_src[top_rev_src])} in revenue — your highest-value channel.")

        if cost_col and source_col:
            grp = df.groupby(source_col).agg(Rev=(rev_col,"sum"), Cost=(cost_col,"sum")) if rev_col else None
            if grp is not None:
                grp["CPL"] = grp["Cost"] / df.groupby(source_col).size()
                most_exp = grp["CPL"].idxmax()
                insight("warn", "💸", f"Highest CPL: {most_exp}",
                        f"Cost per lead from {most_exp} is the highest in your mix. Evaluate whether the conversion rate justifies the spend.")

        if date_col and rev_col:
            tmp = df.dropna(subset=[date_col, rev_col])
            tmp = tmp.copy(); tmp["month"] = tmp[date_col].dt.to_period("M").astype(str)
            monthly = tmp.groupby("month")[rev_col].sum()
            if len(monthly) >= 2:
                delta = monthly.iloc[-1] - monthly.iloc[-2]
                pct = delta / monthly.iloc[-2] * 100 if monthly.iloc[-2] else 0
                kind = "good" if delta > 0 else "bad"
                emoji = "📈" if delta > 0 else "📉"
                insight(kind, emoji, "Month-on-Month Revenue",
                        f"Last month vs previous: {'+' if delta >= 0 else ''}{fmt_inr(delta)} ({pct:+.1f}%).")

    with rec_col:
        st.markdown("<div class='section-title'>🧠 Recommendations</div>", unsafe_allow_html=True)

        recs = []

        if conv_rate < 20 and status_col:
            recs.append(("HIGH", "Implement lead scoring immediately — rank prospects by intent signals to focus rep time on likely converters."))

        if source_col and status_col:
            perf = df.groupby(source_col).agg(leads=(source_col,"count"), won=(status_col, lambda x: is_won(x).sum()))
            perf["rate"] = perf["won"]/perf["leads"]
            best_ch = perf["rate"].idxmax()
            recs.append(("HIGH", f"Scale {best_ch} — reallocate 30–40% of underperforming channel budget here for quick conversion wins."))
            worst_ch = perf["rate"].idxmin()
            recs.append(("MEDIUM", f"A/B test {worst_ch} messaging or pause it for 30 days. Measure pipeline impact."))

        if roi < 100 and cost_col:
            recs.append(("HIGH", f"ROI is {roi:.0f}% — below 100% breakeven. Reduce CAC or increase average deal size via upsell/bundling."))

        if avg_deal and rev_col:
            recs.append(("MEDIUM", f"Current avg deal is {fmt_inr(avg_deal)}. Add a premium tier or annual billing option to lift this by 20–30%."))

        if date_col:
            recs.append(("LOW", "Set up automated drip sequences for leads older than 14 days. Nurture converts stale pipeline into closed deals."))

        recs.append(("LOW", "Build a referral programme targeting your Won customers. Referred leads typically convert 3–5× faster."))
        recs.append(("MEDIUM", "Segment leads by company size / industry if data is available. Personalised outreach lifts open rates by 40–60%."))

        priority_map = {"HIGH": "high", "MEDIUM": "medium", "LOW": "low"}
        for priority, text in recs:
            badge_cls = priority_map[priority]
            st.markdown(f"""
<div class='rec-pill' style='display:flex;align-items:flex-start;width:100%;border-radius:12px;padding:12px 16px;margin-bottom:8px'>
  <span class='badge {badge_cls}' style='flex-shrink:0;margin-top:2px'>{priority}</span>
  <span style='margin-left:10px;color:#cbd5e1;font-size:13px;line-height:1.5'>{text}</span>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  PAGE: CHANNEL DEEP-DIVE
# ═══════════════════════════════════════════════════════
elif page == "🗺️ Channel Deep-Dive":
    st.markdown("<div class='page-title' style='font-size:26px;font-weight:700;color:#f8fafc;margin-bottom:1.5rem'>Channel Deep-Dive</div>", unsafe_allow_html=True)

    if not source_col:
        st.warning("No Source/Channel column detected in your dataset.")
        st.stop()

    channels = df[source_col].value_counts().index.tolist()
    selected = st.multiselect("Filter channels", channels, default=channels)
    dff = df[df[source_col].isin(selected)]

    top, bot = st.columns(2)

    with top:
        st.markdown("<div class='section-title'>Lead Volume by Channel</div>", unsafe_allow_html=True)
        vc = dff[source_col].value_counts().reset_index()
        vc.columns = ["Channel", "Leads"]
        fig = px.bar(vc, x="Channel", y="Leads", text="Leads",
                     color="Channel", color_discrete_sequence=PALETTE)
        fig.update_traces(textposition="outside")
        fig.update_layout(**CHART_LAYOUT, height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with bot:
        if rev_col:
            st.markdown("<div class='section-title'>Revenue by Channel</div>", unsafe_allow_html=True)
            rv = dff.groupby(source_col)[rev_col].sum().reset_index()
            rv.columns = ["Channel", "Revenue"]
            rv = rv.sort_values("Revenue", ascending=False)
            fig = px.bar(rv, x="Channel", y="Revenue", text=rv["Revenue"].apply(fmt_inr),
                         color="Channel", color_discrete_sequence=PALETTE)
            fig.update_traces(textposition="outside")
            fig.update_layout(**CHART_LAYOUT, height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    if status_col:
        st.markdown("<div class='section-title'>Conversion Funnel by Channel</div>", unsafe_allow_html=True)
        funnel = dff.groupby(source_col).agg(
            Leads=(source_col,"count"),
            Won=(status_col, lambda x: is_won(x).sum())
        ).reset_index()
        funnel["Lost"] = funnel["Leads"] - funnel["Won"]
        funnel["Rate %"] = (funnel["Won"] / funnel["Leads"] * 100).round(1)

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Won", x=funnel[source_col], y=funnel["Won"],
                             marker_color="#10b981", text=funnel["Won"], textposition="inside"))
        fig.add_trace(go.Bar(name="Lost/Open", x=funnel[source_col], y=funnel["Lost"],
                             marker_color="#ef4444", text=funnel["Lost"], textposition="inside"))
        fig.update_layout(**CHART_LAYOUT, barmode="stack", height=320,
                          legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    if rev_col and cost_col:
        st.markdown("<div class='section-title'>ROI by Channel</div>", unsafe_allow_html=True)
        roi_df = dff.groupby(source_col).agg(Rev=(rev_col,"sum"), Cost=(cost_col,"sum")).reset_index()
        roi_df["ROI %"] = ((roi_df["Rev"] - roi_df["Cost"]) / roi_df["Cost"].replace(0, np.nan) * 100).round(1)
        roi_df = roi_df.dropna(subset=["ROI %"]).sort_values("ROI %", ascending=False)
        fig = px.bar(roi_df, x=source_col, y="ROI %", text="ROI %",
                     color="ROI %", color_continuous_scale=["#ef4444","#f59e0b","#10b981"])
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(**CHART_LAYOUT, height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Summary table
    st.markdown("<div class='section-title'>Channel Summary Table</div>", unsafe_allow_html=True)
    summary = dff.groupby(source_col).agg(Leads=(source_col,"count")).reset_index()
    if status_col:
        summary["Won"] = dff.groupby(source_col).apply(lambda x: is_won(x[status_col]).sum()).values
        summary["Conv %"] = (summary["Won"]/summary["Leads"]*100).round(1)
    if rev_col:
        summary["Revenue"] = dff.groupby(source_col)[rev_col].sum().values
        summary["Revenue"] = summary["Revenue"].apply(fmt_inr)
    if cost_col:
        summary["Cost"] = dff.groupby(source_col)[cost_col].sum().values
        summary["Cost"] = summary["Cost"].apply(fmt_inr)
    st.dataframe(summary.sort_values("Leads", ascending=False), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════
#  PAGE: PREDICTIONS
# ═══════════════════════════════════════════════════════
elif page == "📈 Predictions":
    st.markdown("<div class='page-title' style='font-size:26px;font-weight:700;color:#f8fafc;margin-bottom:1.5rem'>Predictions & Forecasting</div>", unsafe_allow_html=True)

    if not date_col:
        st.warning("No Date column found. Add a date column to your dataset to enable predictions.")
        st.stop()

    if not rev_col:
        st.warning("No Revenue column found. Forecasting requires a revenue column.")
        st.stop()

    tmp = df.dropna(subset=[date_col, rev_col]).copy()
    tmp["month"] = tmp[date_col].dt.to_period("M").astype(str)
    monthly = tmp.groupby("month")[rev_col].sum().reset_index()
    monthly.columns = ["Month", "Revenue"]

    if len(monthly) < 2:
        st.warning("Need at least 2 months of data to generate predictions.")
        st.stop()

    # Forecast next 3 months
    future_rev = simple_forecast(monthly["Revenue"].tolist(), periods=3)
    last_month_dt = pd.Period(monthly["Month"].iloc[-1], freq="M")
    future_months = [(last_month_dt + i).strftime("%Y-%m") for i in range(1, 4)]

    # KPIs
    f1, f2, f3 = st.columns(3)
    for col_ui, month, val in zip([f1,f2,f3], future_months, future_rev):
        col_ui.markdown(f"""
<div class='pred-card'>
  <div class='pred-title'>Predicted: {month}</div>
  <div class='pred-value'>{fmt_inr(val)}</div>
  <div class='pred-note'>Linear trend projection</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart: actual + forecast
    st.markdown("<div class='section-title'>Revenue Trend + 3-Month Forecast</div>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Revenue"],
        name="Actual", mode="lines+markers",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=6),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.07)"
    ))
    fig.add_trace(go.Scatter(
        x=future_months, y=future_rev,
        name="Forecast", mode="lines+markers",
        line=dict(color="#8b5cf6", width=2.5, dash="dot"),
        marker=dict(size=8, symbol="diamond"),
        fill="tozeroy", fillcolor="rgba(139,92,246,0.07)"
    ))
    fig.update_layout(**CHART_LAYOUT, height=340)
    st.plotly_chart(fig, use_container_width=True)

    # Lead trend
    if status_col:
        st.markdown("<div class='section-title'>Monthly Lead Volume & Conversions</div>", unsafe_allow_html=True)
        tmp2 = df.dropna(subset=[date_col]).copy()
        tmp2["month"] = tmp2[date_col].dt.to_period("M").astype(str)
        lead_trend = tmp2.groupby("month").agg(
            Leads=("month","count"),
            Won=(status_col, lambda x: is_won(x).sum())
        ).reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=lead_trend["month"], y=lead_trend["Leads"],
                              name="Total Leads", marker_color="#1e40af", opacity=0.8))
        fig2.add_trace(go.Bar(x=lead_trend["month"], y=lead_trend["Won"],
                              name="Converted", marker_color="#10b981"))
        fig2.update_layout(**CHART_LAYOUT, barmode="overlay", height=300)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
<div class='info-section' style='background:#111827;border:1px solid #1e293b;border-radius:12px;padding:16px;margin-top:8px'>
<p style='color:#64748b;font-size:13px;margin:0'>
⚠️ <b style='color:#94a3b8'>Forecast disclaimer:</b> Predictions are based on linear trend extrapolation from your historical data. They do not account for seasonality, market changes, or pipeline events. Use as a directional guide, not a financial projection.
</p>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  PAGE: RISKS
# ═══════════════════════════════════════════════════════
elif page == "⚠️ Risks":
    st.markdown("<div class='page-title' style='font-size:26px;font-weight:700;color:#f8fafc;margin-bottom:1.5rem'>Risk Analysis</div>", unsafe_allow_html=True)

    r1, r2 = st.columns(2)

    with r1:
        st.markdown("<div class='section-title'>🚨 Identified Risks</div>", unsafe_allow_html=True)

        # Channel concentration
        if source_col:
            vc = df[source_col].value_counts(normalize=True) * 100
            top_share = vc.iloc[0]
            top_src = vc.index[0]
            if top_share > 60:
                risk_item("high",
                    f"Channel concentration: {top_src} drives {top_share:.0f}% of leads. Single-source dependency creates fragility.")
            elif top_share > 40:
                risk_item("medium",
                    f"Moderate concentration: {top_src} accounts for {top_share:.0f}% of leads. Diversify to reduce exposure.")
            else:
                risk_item("low",
                    f"Good channel diversification — top source ({top_src}) is only {top_share:.0f}% of pipeline.")

        # Conversion risk
        if status_col:
            if conv_rate < 10:
                risk_item("high",
                    f"Critical conversion rate: {conv_rate:.1f}%. Pipeline is not converting — revenue target will be missed without intervention.")
            elif conv_rate < 20:
                risk_item("medium",
                    f"Below-benchmark conversion ({conv_rate:.1f}%). Industry average is ~20–25%. Sales process needs review.")
            else:
                risk_item("low",
                    f"Healthy conversion rate ({conv_rate:.1f}%). Monitor to ensure it stays above 20%.")

        # ROI risk
        if cost_col:
            if roi < 0:
                risk_item("high",
                    f"Negative ROI ({roi:.1f}%). You are spending more than you are earning. Immediate action required.")
            elif roi < 50:
                risk_item("medium",
                    f"Low ROI ({roi:.1f}%). Business is marginally profitable. Review cost allocation per channel.")
            else:
                risk_item("low",
                    f"Positive ROI ({roi:.1f}%). Profitable operations — maintain cost discipline.")

        # Revenue concentration
        if source_col and rev_col:
            rev_share = df.groupby(source_col)[rev_col].sum()
            top_rev_share = rev_share.max() / rev_share.sum() * 100 if rev_share.sum() > 0 else 0
            if top_rev_share > 70:
                risk_item("high",
                    f"Revenue concentration: {top_rev_share:.0f}% of revenue from one channel. Losing this source could be catastrophic.")
            elif top_rev_share > 50:
                risk_item("medium",
                    f"Revenue dependency: {top_rev_share:.0f}% from top channel. Diversify revenue sources.")

        # Date staleness
        if date_col:
            latest = df[date_col].dropna().max()
            if pd.Timestamp.now() - latest > pd.Timedelta(days=60):
                risk_item("medium",
                    f"Data freshness: most recent entry is {latest.strftime('%b %d, %Y')}. Pipeline data may be stale.")
            else:
                risk_item("low", "Data is recent and likely reflects current pipeline.")

        # Low data volume
        if total < 50:
            risk_item("medium",
                f"Small sample ({total} leads). Metrics and predictions may not be statistically reliable. Collect more data.")
        else:
            risk_item("low", f"Sufficient data volume ({total} leads) for reliable analysis.")

    with r2:
        st.markdown("<div class='section-title'>📊 Risk Heatmap</div>", unsafe_allow_html=True)

        risk_data = {
            "Risk Area": ["Channel Concentration", "Conversion Rate", "ROI / Profitability",
                          "Revenue Concentration", "Data Freshness", "Sample Size"],
            "Level": [0, 0, 0, 0, 0, 0],
        }

        if source_col:
            vc = df[source_col].value_counts(normalize=True) * 100
            risk_data["Level"][0] = 3 if vc.iloc[0] > 60 else (2 if vc.iloc[0] > 40 else 1)

        if status_col:
            risk_data["Level"][1] = 3 if conv_rate < 10 else (2 if conv_rate < 20 else 1)

        if cost_col:
            risk_data["Level"][2] = 3 if roi < 0 else (2 if roi < 50 else 1)

        if source_col and rev_col:
            rv = df.groupby(source_col)[rev_col].sum()
            sh = rv.max() / rv.sum() * 100 if rv.sum() > 0 else 0
            risk_data["Level"][3] = 3 if sh > 70 else (2 if sh > 50 else 1)

        if date_col:
            latest = df[date_col].dropna().max()
            days_old = (pd.Timestamp.now() - latest).days
            risk_data["Level"][4] = 2 if days_old > 60 else 1

        risk_data["Level"][5] = 2 if total < 50 else 1

        risk_df = pd.DataFrame(risk_data)
        risk_df["Color"] = risk_df["Level"].map({1:"#10b981", 2:"#f59e0b", 3:"#ef4444"})
        risk_df["Label"] = risk_df["Level"].map({1:"LOW", 2:"MEDIUM", 3:"HIGH"})

        fig = go.Figure(go.Bar(
            x=risk_df["Level"],
            y=risk_df["Risk Area"],
            orientation="h",
            marker=dict(color=risk_df["Color"]),
            text=risk_df["Label"],
            textposition="inside",
            textfont=dict(color="white", size=12, family="Sora"),
        ))
        fig.update_layout(**CHART_LAYOUT, height=380,
                          xaxis=dict(showgrid=False, showticklabels=False, range=[0,3.5]))
        st.plotly_chart(fig, use_container_width=True)

        # Overall risk score
        avg_risk = sum(risk_data["Level"]) / len(risk_data["Level"])
        overall = "HIGH" if avg_risk > 2.2 else ("MEDIUM" if avg_risk > 1.4 else "LOW")
        color = "#ef4444" if overall == "HIGH" else ("#f59e0b" if overall == "MEDIUM" else "#10b981")

        st.markdown(f"""
<div style='text-align:center;padding:20px;background:#111827;border:1px solid #1e293b;border-radius:14px;margin-top:8px'>
  <div style='font-size:13px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Overall Risk Score</div>
  <div style='font-size:42px;font-weight:700;color:{color};font-family:JetBrains Mono'>{overall}</div>
  <div style='font-size:12px;color:#475569;margin-top:6px'>{avg_risk:.1f} / 3.0</div>
</div>""", unsafe_allow_html=True)

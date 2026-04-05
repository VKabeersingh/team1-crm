import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(page_title="Lead Intelligence", layout="wide")

# ================= THEME =================
st.markdown("""
<style>
/* Base */
.stApp {
    background: #f8fafc;
    color: #0f172a;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}

/* Cards */
.card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    transition: all 0.2s ease;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
}

/* KPI */
.kpi {
    font-size: 28px;
    font-weight: 600;
}
.kpi-label {
    color: #64748b;
    font-size: 14px;
}

/* Section Titles */
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 10px;
}

/* Insight Cards */
.insight-good {
    background: #ecfdf5;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #bbf7d0;
}
.insight-bad {
    background: #fef2f2;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #fecaca;
}

/* Buttons / inputs */
.stButton>button {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
@st.cache_data
def load(file):
    df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)

    cols = {c.lower(): c for c in df.columns}

    def find(keys):
        for k in keys:
            for col in cols:
                if k in col:
                    return cols[col]
        return None

    return df, find(["status"]), find(["source"]), find(["rev","amount"]), find(["date"]), find(["cost"])


# ================= SIDEBAR =================
st.sidebar.title("📊 Lead Intelligence")

page = st.sidebar.radio("", ["Dashboard", "Info"])

if page == "Info":
    st.title("Product Guide")

    st.markdown("""
### What this tool does
- Analyze lead performance  
- Identify best & worst channels  
- Track revenue and ROI  
- Visualize funnel & trends  

### Required columns
- Status (Won/Lost)
- Source (Channel)
- Revenue
- Cost (optional)
- Date (optional)

### Use cases
- Marketing teams  
- Agencies  
- Startups  

""")
    st.stop()

# ================= MAIN =================
st.title("Lead Intelligence Dashboard")

file = st.file_uploader("Upload your dataset", type=["csv","xlsx"])

if file:
    df, status_col, source_col, rev_col, date_col, cost_col = load(file)

    if status_col:
        df[status_col] = df[status_col].astype(str).str.lower()

    # ================= KPIs =================
    total = len(df)
    converted = df[status_col].isin(["won","closed"]).sum() if status_col else 0
    revenue = df[rev_col].sum() if rev_col else 0
    cost = df[cost_col].sum() if cost_col else 0

    conv_rate = (converted / total * 100) if total else 0
    roi = ((revenue - cost) / cost * 100) if cost > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"<div class='card'><div class='kpi'>{total}</div><div class='kpi-label'>Leads</div></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><div class='kpi'>{conv_rate:.1f}%</div><div class='kpi-label'>Conversion</div></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'><div class='kpi'>₹{revenue:,.0f}</div><div class='kpi-label'>Revenue</div></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='card'><div class='kpi'>{roi:.1f}%</div><div class='kpi-label'>ROI</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= CHART =================
    if source_col:
        st.markdown("<div class='section-title'>Channel Performance</div>", unsafe_allow_html=True)

        data = df[source_col].value_counts().reset_index()
        data.columns = [source_col, "Leads"]

        fig = px.bar(
            data,
            x=source_col,
            y="Leads",
            text="Leads",
            color=source_col,
            color_discrete_sequence=px.colors.sequential.Purples
        )

        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # ================= INSIGHTS =================
    st.markdown("<div class='section-title'>Insights</div>", unsafe_allow_html=True)

    if source_col and status_col:
        perf = df.groupby(source_col).agg(
            leads=(source_col,"count"),
            conv=(status_col, lambda x: x.isin(["won","closed"]).sum())
        ).reset_index()

        perf["rate"] = perf["conv"] / perf["leads"]

        best = perf.sort_values("rate", ascending=False).iloc[0]
        worst = perf.sort_values("rate").iloc[0]

        c1, c2 = st.columns(2)

        c1.markdown(f"<div class='insight-good'>🔥 Best: <b>{best[source_col]}</b> ({best['rate']*100:.1f}%)</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='insight-bad'>❌ Worst: <b>{worst[source_col]}</b> ({worst['rate']*100:.1f}%)</div>", unsafe_allow_html=True)

    # ================= GOAL =================
    st.markdown("<div class='section-title'>Goal Tracking</div>", unsafe_allow_html=True)

    target = st.number_input("Revenue Target", value=50000)

    progress = (revenue / target * 100) if target else 0
    progress = min(progress, 100)

    st.progress(int(progress))
    st.caption(f"{progress:.1f}% achieved")

    # ================= DATA =================
    with st.expander("View Data"):
        st.dataframe(df)

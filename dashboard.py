import streamlit as st
import pandas as pd
import plotly.express as px

# ================= PAGE =================
st.set_page_config(page_title="Lead Intelligence Pro+", layout="wide")

# ================= THEME =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #ffffff, #f5f3ff);
    color: #1e1b4b;
}

/* Cards */
.card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #e9d5ff;
    box-shadow: 0 10px 25px rgba(124,58,237,0.08);
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-4px);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #ede9fe;
}

/* Titles */
h1, h2, h3 {
    color: #5b21b6;
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

    return df, find(["status"]), find(["source"]), find(["rev","amount"]), find(["date"]), find(["cost","spend"])


# ================= SIDEBAR =================
st.sidebar.title("📘 Dashboard Guide")

page = st.sidebar.radio("Navigate", ["Dashboard", "Info"])

if page == "Info":
    st.title("📊 What This Dashboard Does")

    st.markdown("""
### ✅ Insights You Get
- Conversion Rate  
- Best & Worst Lead Sources  
- Revenue Analysis  
- ROI Tracking  
- Funnel Visualization  
- Trends over time  
- Revenue per Lead  

---

### 📥 Required Data Columns

| Column Type | Example |
|------------|--------|
| Status     | Won, Lost |
| Source     | Instagram, Google |
| Revenue    | 5000 |
| Cost       | 2000 |
| Date       | 2025-01-01 |

---

### ⚡ Tips
- Use clean data (no blanks)
- Keep status consistent (won/lost)
- Add cost for ROI accuracy

---

### 🎯 Best Use Cases
- Marketing Analysis  
- Lead Tracking  
- Startup Growth Monitoring  
- Agency Reporting  

""")
    st.stop()

# ================= MAIN =================
st.title("🚀 Lead Intelligence Pro+")

file = st.file_uploader("Upload Dataset", type=["csv", "xlsx"])

if file:
    df, status_col, source_col, rev_col, date_col, cost_col = load(file)

    # Clean
    if status_col:
        df[status_col] = df[status_col].astype(str).str.lower().str.strip()

    # ================= KPIs =================
    total = len(df)
    converted = df[status_col].isin(["won","converted","closed"]).sum() if status_col else 0
    revenue = df[rev_col].sum() if rev_col else 0
    cost = df[cost_col].sum() if cost_col else 0

    conv_rate = (converted / total * 100) if total else 0
    roi = ((revenue - cost) / cost * 100) if cost > 0 else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f"<div class='card'><h2>{total}</h2><p>Leads</p></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><h2>{conv_rate:.1f}%</h2><p>Conversion</p></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'><h2>₹{revenue:,.0f}</h2><p>Revenue</p></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='card'><h2>{roi:.1f}%</h2><p>ROI</p></div>", unsafe_allow_html=True)

    st.divider()

    # ================= COLORS =================
    if source_col:
        unique_sources = df[source_col].unique()
        color_map = {src: px.colors.qualitative.Bold[i % len(px.colors.qualitative.Bold)]
                     for i, src in enumerate(unique_sources)}

    # ================= CHART =================
    if source_col:
        data = df[source_col].value_counts().reset_index()
        data.columns = [source_col, "Leads"]

        fig = px.bar(
            data,
            x=source_col,
            y="Leads",
            color=source_col,
            color_discrete_map=color_map,
            text="Leads"
        )

        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

    # ================= REVENUE =================
    if source_col and rev_col:
        rev = df.groupby(source_col)[rev_col].sum().reset_index()

        fig = px.pie(
            rev,
            names=source_col,
            values=rev_col,
            color=source_col,
            color_discrete_map=color_map
        )

        fig.update_traces(textinfo="percent+label")

        st.plotly_chart(fig, use_container_width=True)

    # ================= INSIGHTS =================
    st.subheader("🧠 Smart Insights")

    if source_col and status_col:
        perf = df.groupby(source_col).agg(
            leads=(source_col,"count"),
            conversions=(status_col, lambda x: x.isin(["won","converted","closed"]).sum())
        ).reset_index()

        perf["rate"] = perf["conversions"] / perf["leads"]

        best = perf.sort_values("rate", ascending=False).iloc[0]
        worst = perf.sort_values("rate").iloc[0]

        st.success(f"🔥 Best: {best[source_col]} ({best['rate']*100:.1f}%)")
        st.error(f"❌ Worst: {worst[source_col]} ({worst['rate']*100:.1f}%)")

    # ================= GOAL =================
    st.subheader("🎯 Goal Tracker")

    target = st.number_input("Set Target", value=50000)

    progress = (revenue / target * 100) if target else 0
    progress = min(progress, 100)

    st.progress(int(progress))
    st.write(f"{progress:.1f}% achieved")

    # ================= ANIMATION FEEL =================
    st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        animation: fadeIn 0.8s ease-in;
    }
    @keyframes fadeIn {
        from {opacity:0; transform:translateY(10px);}
        to {opacity:1; transform:translateY(0);}
    }
    </style>
    """, unsafe_allow_html=True)

    # ================= DATA =================
    with st.expander("📂 Data"):
        st.dataframe(df)

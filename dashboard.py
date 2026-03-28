import streamlit as st
import pandas as pd
import plotly.express as px

# ================= PAGE =================
st.set_page_config(page_title="Lead Intelligence Pro", layout="wide")

# ================= GLASS UI =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255,255,255,0.2);
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(12px);
}

.block-container {
    padding: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
@st.cache_data
def load(file):
    df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)

    status = next((c for c in df.columns if "status" in c.lower()), None)
    source = next((c for c in df.columns if "source" in c.lower()), None)
    revenue = next((c for c in df.columns if "rev" in c.lower() or "amount" in c.lower()), None)
    date = next((c for c in df.columns if "date" in c.lower()), None)
    cost = next((c for c in df.columns if "cost" in c.lower() or "spend" in c.lower()), None)

    if date:
        df[date] = pd.to_datetime(df[date], errors='coerce')

    return df, status, source, revenue, date, cost

# ================= APP =================
st.title("🚀 Lead Intelligence Pro")

file = st.file_uploader("Upload Dataset", type=["csv", "xlsx"])

if file:
    df, status_col, source_col, rev_col, date_col, cost_col = load(file)

    # ================= SIDEBAR =================
    with st.sidebar:
        st.header("⚙️ Control Panel")

        chart_type = st.selectbox("Chart Type", ["Pie", "Bar", "Line"])

        if source_col:
            sources = st.multiselect("Filter Source", df[source_col].unique(), default=df[source_col].unique())
            df = df[df[source_col].isin(sources)]

        if status_col:
            status = st.multiselect("Filter Status", df[status_col].unique(), default=df[status_col].unique())
            df = df[df[status_col].isin(status)]

    # ================= KPIs =================
    total = len(df)

    converted = len(df[df[status_col].astype(str).str.lower() == "won"]) if status_col else 0

    revenue = df[rev_col].sum() if rev_col else 0
    cost = df[cost_col].sum() if cost_col else 0

    conv_rate = (converted / total * 100) if total else 0
    roi = ((revenue - cost) / cost * 100) if cost else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leads", total)
    c2.metric("Conversion %", f"{conv_rate:.1f}%")
    c3.metric("Revenue", f"${revenue:,.0f}")
    c4.metric("ROI", f"{roi:.1f}%")

    st.divider()

    # ================= CHARTS =================
    col1, col2, col3 = st.columns(3)

    if source_col:
        with col1:
            lead_dist = df[source_col].value_counts().reset_index()
            lead_dist.columns = [source_col, "Leads"]

            if chart_type == "Pie":
                fig = px.pie(lead_dist, names=source_col, values="Leads", hole=0.4)
            elif chart_type == "Bar":
                fig = px.bar(lead_dist, x=source_col, y="Leads")
            else:
                fig = px.line(lead_dist, x=source_col, y="Leads", markers=True)

            st.plotly_chart(fig, use_container_width=True)

    if source_col and rev_col:
        with col2:
            rev_data = df.groupby(source_col)[rev_col].sum().reset_index()

            if chart_type == "Pie":
                fig = px.pie(rev_data, names=source_col, values=rev_col, hole=0.4)
            elif chart_type == "Bar":
                fig = px.bar(rev_data, x=source_col, y=rev_col)
            else:
                fig = px.line(rev_data, x=source_col, y=rev_col)

            st.plotly_chart(fig, use_container_width=True)

    if status_col:
        with col3:
            status_data = df[status_col].value_counts().reset_index()
            status_data.columns = ["Status", "Count"]

            if chart_type == "Pie":
                fig = px.pie(status_data, names="Status", values="Count", hole=0.4)
            elif chart_type == "Bar":
                fig = px.bar(status_data, x="Status", y="Count")
            else:
                fig = px.line(status_data, x="Status", y="Count")

            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ================= FUNNEL =================
    if status_col:
        st.subheader("🎯 Funnel")

        funnel = df[status_col].value_counts().reset_index()
        funnel.columns = ["Stage", "Count"]

        fig = px.funnel(funnel, x="Count", y="Stage")
        st.plotly_chart(fig, use_container_width=True)

    # ================= TREND =================
    if date_col:
        st.subheader("📈 Trend")

        trend = df.groupby(df[date_col].dt.date).size().reset_index(name="Leads")

        fig = px.line(trend, x=date_col, y="Leads")
        st.plotly_chart(fig, use_container_width=True)

    # ================= HEATMAP =================
    if date_col and source_col:
        st.subheader("🔥 Heatmap")

        df["Day"] = df[date_col].dt.day_name()
        heat = df.groupby(["Day", source_col]).size().reset_index(name="Leads")

        fig = px.density_heatmap(heat, x=source_col, y="Day", z="Leads")
        st.plotly_chart(fig, use_container_width=True)

    # ================= COMPARISON =================
    if source_col and rev_col:
        st.subheader("📊 Efficiency")

        comp = df.groupby(source_col).agg({
            rev_col: "sum",
            source_col: "count"
        }).rename(columns={source_col: "Leads"}).reset_index()

        comp["Revenue per Lead"] = comp[rev_col] / comp["Leads"]

        fig = px.bar(comp, x=source_col, y="Revenue per Lead")
        st.plotly_chart(fig, use_container_width=True)

    # ================= INSIGHTS =================
    st.subheader("🧠 Insights")

    if source_col and status_col:
        perf = df.groupby(source_col).agg(
            leads=(source_col, "count"),
            conversions=(status_col, lambda x: x.astype(str).str.lower().eq("won").sum())
        ).reset_index()

        perf["conv_rate"] = perf["conversions"] / perf["leads"]

        best = perf.sort_values("conv_rate", ascending=False).iloc[0]
        worst = perf.sort_values("conv_rate").iloc[0]

        st.success(f"🔥 Best: {best[source_col]} ({best['conv_rate']*100:.1f}%)")
        st.error(f"❌ Worst: {worst[source_col]}")

    if roi < 0:
        st.error("🚨 Losing money")
    elif roi > 100:
        st.success("💰 High ROI")

    # ================= TARGET =================
    st.subheader("🎯 Goal Tracker")

    target = st.number_input("Set Target", value=10000)
    progress = (revenue / target) * 100 if target else 0

    st.progress(min(int(progress), 100))
    st.write(f"{progress:.1f}% achieved")

    # ================= DOWNLOAD =================
    st.subheader("📥 Export")

    st.download_button(
        "Download Filtered Data",
        df.to_csv(index=False),
        file_name="filtered_data.csv"
    )

    # ================= DATA =================
    with st.expander("📂 Data"):
        st.dataframe(df)

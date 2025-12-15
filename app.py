import streamlit as st
import pandas as pd
import plotly.express as px

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Finlytics Dashboard", layout="wide")

# ================= GLOBAL STYLING =================
st.markdown("""
<style>
html, body {
    background-color: #f9fafb;
    color: #111827;
    font-family: "Segoe UI", Arial, sans-serif;
}
.card {
    background-color: #ffffff;
    padding: 24px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    margin-bottom: 30px;
}
.kpi {
    text-align: center;
}
.explain {
    background-color: #fff7ed;
    border-left: 6px solid #ea580c;
    padding: 14px 18px;
    margin-top: 14px;
    font-size: 14px;
    color: #7c2d12;
}
</style>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
df = pd.read_json("csvjson.json")

# ================= DERIVED =================
df["AUM_Bucket"] = pd.cut(
    df["Fund_Net_Assets_USD_M"],
    bins=[0, 5000, 20000, df["Fund_Net_Assets_USD_M"].max()],
    labels=["Small", "Medium", "Large"]
)

# ================= HEADER =================
st.markdown("""
<div style="text-align:center; margin-bottom:35px;">
    <h1 style="font-size:44px; color:#9a3412; font-weight:800;">
        Finlytics Dashboard
    </h1>
    <h3 style="color:#fb923c; font-weight:600;">
        Navigating Tariff Risk & Trade Uncertainty
    </h3>
    <p style="color:#6b7280; font-size:16px;">
        By – <b>Team Finacle</b>
    </p>
</div>
""", unsafe_allow_html=True)

# ================= KPIs =================
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f"<div class='card kpi'><h3>{len(df)}</h3>Total Funds</div>", unsafe_allow_html=True)
k2.markdown(f"<div class='card kpi'><h3>{df['Fund_Net_Assets_USD_M'].sum():,.0f} M</h3>Total AUM</div>", unsafe_allow_html=True)
k3.markdown(f"<div class='card kpi'><h3>{df['Return_1Y_Pct'].mean():.2f}%</h3>Avg 1Y Return</div>", unsafe_allow_html=True)
k4.markdown(f"<div class='card kpi'><h3>{df['Trade_War_Resilience_Score'].mean():.1f}</h3>Avg Resilience</div>", unsafe_allow_html=True)

# ================= FILTERS =================
with st.expander("🔍 Global Filters"):
    c1, c2, c3, c4, c5 = st.columns(5)
    risk = c1.selectbox("Tariff Risk Level", ["All"] + sorted(df["Tariff_Risk_Level"].unique()))
    sector = c2.selectbox("Primary Sector", ["All"] + sorted(df["Primary_Sector"].unique()))
    region = c3.selectbox("Geographic Region", ["All"] + sorted(df["Geographic_Focus"].unique()))
    ftype = c4.selectbox("Fund Type", ["All"] + sorted(df["Fund_Type"].unique()))
    aum = c5.selectbox("AUM Size Bucket", ["All", "Small", "Medium", "Large"])

filtered = df.copy()
if risk != "All": filtered = filtered[filtered["Tariff_Risk_Level"] == risk]
if sector != "All": filtered = filtered[filtered["Primary_Sector"] == sector]
if region != "All": filtered = filtered[filtered["Geographic_Focus"] == region]
if ftype != "All": filtered = filtered[filtered["Fund_Type"] == ftype]
if aum != "All": filtered = filtered[filtered["AUM_Bucket"] == aum]

if filtered.empty:
    st.warning("No data available for selected filters. Showing full dataset.")
    filtered = df.copy()

# ================= HEATMAP =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("Tariff Risk Distribution Across Sectors")

heatmap_data = pd.crosstab(filtered["Primary_Sector"], filtered["Tariff_Risk_Level"])
fig = px.imshow(
    heatmap_data,
    aspect="auto",
    color_continuous_scale=["#fff7ed", "#fb923c", "#9a3412"]
)
fig.update_layout(coloraxis_colorbar=dict(title="Number of Funds"))
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="explain">
Color intensity represents the number of funds in each sector–risk category, not the severity of risk.
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ================= RETURNS SECTION =================
c1, c2 = st.columns(2)

with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Average 1-Year Returns by Tariff Risk")
    avg_ret = filtered.groupby("Tariff_Risk_Level", as_index=False)["Return_1Y_Pct"].mean()
    fig = px.bar(
        avg_ret, x="Tariff_Risk_Level", y="Return_1Y_Pct",
        color="Tariff_Risk_Level",
        color_discrete_map={"Low":"#FDBA74","Medium":"#FB923C","High":"#EA580C"}
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='explain'>Compares performance across tariff risk categories.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Average 1-Year Returns by Region")
    reg_ret = filtered.groupby("Geographic_Focus", as_index=False)["Return_1Y_Pct"].mean()
    fig = px.bar(
        reg_ret, x="Geographic_Focus", y="Return_1Y_Pct",
        color_discrete_sequence=["#FB923C"]
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='explain'>Shows how geography influences returns under tariff pressure.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================= AUM & RESILIENCE =================
c1, c2 = st.columns(2)

with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("AUM vs Tariff Risk")
    fig = px.scatter(
        filtered, x="Tariff_Risk_Score", y="Fund_Net_Assets_USD_M",
        size="Fund_Net_Assets_USD_M", color="Tariff_Risk_Level",
        color_discrete_map={"Low":"#FDBA74","Medium":"#FB923C","High":"#EA580C"}
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='explain'>Shows whether large funds are concentrated in high tariff exposure.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Resilience Score vs Tariff Risk")
    fig = px.scatter(
        filtered, x="Tariff_Risk_Score", y="Trade_War_Resilience_Score",
        color="Fund_Type"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='explain'>Identifies funds that remain resilient despite tariff exposure.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================= VOLATILITY & DRAWDOWN =================
c1, c2 = st.columns(2)

with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Volatility by Sector")
    vol = filtered.groupby("Primary_Sector", as_index=False)["Volatility_1Y_Pct"].mean()
    fig = px.bar(vol, x="Primary_Sector", y="Volatility_1Y_Pct",
                 color_discrete_sequence=["#EA580C"])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='explain'>Higher volatility indicates greater instability.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Drawdown Distribution by Sector")
    dd = filtered.groupby("Primary_Sector", as_index=False)["Max_Drawdown_Pct"].mean()
    fig = px.bar(dd, x="Primary_Sector", y="Max_Drawdown_Pct",
                 color_discrete_sequence=["#FB923C"])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div class='explain'>Shows downside risk across sectors.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================= FUND SCREENER =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("Interactive Fund Screener")
st.dataframe(filtered, use_container_width=True)
st.markdown("<div class='explain'>Final shortlist tool for investment decision-making.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

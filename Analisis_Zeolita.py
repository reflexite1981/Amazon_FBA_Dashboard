#!/usr/bin/env python
# coding: utf-8

# In[304]:


import os
import streamlit as st
import pandas as pd
import plotly.express as px
import re


# In[305]:


# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="Amazon Intelligence",
    layout="wide"
)

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>

/* Fondo */
[data-testid="stAppViewContainer"] {
    background-color: #E5E9F0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #D1D9E6;
    border-right: 2px solid #FF9900;
}

/* Títulos */
h1, h2, h3, h4 {
    color: #111827;
    font-weight: 600;
}

/* KPIs */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 18px;
    border-radius: 14px;
    border-left: 6px solid #FF9900;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.08);
}

/* Tabs */
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 3px solid #FF9900;
    color: #FF9900;
}

/* Plot */
.js-plotly-plot {
    background-color: #FFFFFF !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# DATA
# -------------------------

uploaded_file = st.sidebar.file_uploader(
    "📂 Upload your data",
    type=["csv", "xlsx"]
)

if uploaded_file:

    # 🧠 Detectar tipo de archivo
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif uploaded_file.name.endswith(".xlsx"):

        # 📑 Leer Excel
        excel_file = pd.ExcelFile(uploaded_file)

        # 🟣 PASO 3: selector de hoja
        sheet = st.sidebar.selectbox(
            "📄 Select sheet",
            excel_file.sheet_names
        )

        df = pd.read_excel(uploaded_file, sheet_name=sheet)

    # 🟢 PASO 4: feedback visual
    st.sidebar.success("✅ File loaded successfully")

    # 📊 BONUS PRO (opcional pero recomendable)
    st.sidebar.caption(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")

else:
    st.info("👈 Upload a CSV or Excel file to start analysis")
    st.stop()

df = df.rename(columns={
    "Price  US$": "Price",
    "ASIN Revenue": "Revenue",
    "Fees  US$": "Fees"
})

def clean_money(x):
    if isinstance(x, str):
        x = x.replace('.', '')
        x = x.replace(',', '.')
        x = x.replace('$', '')
    return float(x)

for col in ["Price", "Revenue", "Fees"]:
    df[col] = df[col].apply(clean_money)

# -------------------------
# FEATURES
# -------------------------
df["total_fees"] = df["Fees"] * df["ASIN Sales"]
df["estimated_profit"] = df["Revenue"] - df["total_fees"]
df["profit_margin"] = (df["estimated_profit"] / df["Revenue"]) * 100
def clean_title(title):
    if pd.isna(title):
        return ""
    title = re.sub(r"(for|with|and|the|of|in|on|by)\b", "", title, flags=re.IGNORECASE)
    return " ".join(title.split()[:6])

df["short_title"] = df["Product Details"].apply(clean_title)
display_col = "short_title"

df["opportunity_score"] = df["ASIN Sales"] / (df["Active Sellers"] + 1)

df["competition_level"] = pd.cut(
    df["Active Sellers"],
    bins=[0, 5, 15, 50],
    labels=["Low", "Medium", "High"]
)

df["Ratings"] = df["Ratings"].astype(str).str.replace(',', '.').astype(float)

df["listing_score"] = (
    df["Images"] +
    df["Review Count"] / 100 +
    df["Ratings"]
)

df["product_score"] = (
    df["estimated_profit"] * 0.4 +
    df["ASIN Sales"] * 0.4 -
    df["Active Sellers"] * 0.2
)

# -------------------------
# SIDEBAR
# -------------------------
# -------------------------
# SIDEBAR FILTERS (PRO)
# -------------------------
st.sidebar.header("🔍 Filters")

# 💰 PROFIT
st.sidebar.markdown("### 💰 Profit")

min_profit = st.sidebar.slider(
    "Minimum Profit",
    float(df["estimated_profit"].min()),
    float(df["estimated_profit"].max()),
    float(df["estimated_profit"].min())
)

# 📈 DEMAND
st.sidebar.markdown("### 📈 Demand")

min_sales = st.sidebar.slider(
    "Minimum Sales",
    int(df["ASIN Sales"].min()),
    int(df["ASIN Sales"].max()),
    int(df["ASIN Sales"].min())
)

# 📊 MARGIN (NUEVO 🔥)
st.sidebar.markdown("### 📊 Profitability")

min_margin = st.sidebar.slider(
    "Minimum Margin (%)",
    0,
    100,
    10
)

# 🧠 STRATEGY (NUEVO 🔥)
st.sidebar.markdown("### 🧠 Strategy")

strategy = st.sidebar.selectbox(
    "Select Strategy",
    ["All", "High Profit", "Low Competition", "Balanced"]
)

# -------------------------
# APPLY FILTERS
# -------------------------
df = df[
    (df["estimated_profit"] >= min_profit) &
    (df["ASIN Sales"] >= min_sales) &
    (df["profit_margin"] >= min_margin)
]

# 🎯 Strategy logic
if strategy == "High Profit":
    df = df[df["estimated_profit"] > df["estimated_profit"].median()]

elif strategy == "Low Competition":
    df = df[df["Active Sellers"] < df["Active Sellers"].median()]

elif strategy == "Balanced":
    df = df[
        (df["estimated_profit"] > df["estimated_profit"].median()) &
        (df["Active Sellers"] < df["Active Sellers"].median())
    ]

# 📊 Orden final
df = df.sort_values("product_score", ascending=False)

# 📊 RESULTADOS
st.sidebar.markdown("### 📊 Results")
st.sidebar.metric("Filtered Products", len(df))

# -------------------------
# DATASETS
# -------------------------
top_profit = df.sort_values("estimated_profit", ascending=False).head(10)
loss_products = df[df["estimated_profit"] < 0]
top_opportunities = df.sort_values("opportunity_score", ascending=False).head(10)
top_listing = df.sort_values("listing_score", ascending=False).head(10)
top_sales = df.sort_values("ASIN Sales", ascending=False).head(10)

# -------------------------
# HEADER
# -------------------------
st.markdown(
    '<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:10px;">'
    '<img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="180">'
    '<h1 style="margin:10px 0 5px 0; font-size:34px; color:#0F172A; font-weight:600; text-align:center;">'
    'Intelligence Dashboard</h1>'
    '<p style="margin:0; color:#64748B; font-size:16px; text-align:center;">'
    'Advanced analytics for Amazon FBA sellers</p>'
    '</div>',
    unsafe_allow_html=True
)

# -------------------------
# KPIs
# -------------------------
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"""
<div style="
    padding:15px;
    background:#FFFFFF;
    border-radius:12px;
    border:1px solid #BFC7D5;
    height:130px;
    display:flex;
    flex-direction:column;
    justify-content:center;
">
<h4>📦 Products</h4>
<h2>{len(df)}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style="
    padding:15px;
    background:#FFFFFF;
    border-radius:12px;
    border:1px solid #BFC7D5;
    height:130px;
    display:flex;
    flex-direction:column;
    justify-content:center;
">
<h4 style="margin-bottom:8px;">💰 Total Profit</h4>
<h2>${df['estimated_profit'].sum():,.0f}</h2>
</div>
""", unsafe_allow_html=True)

loss_count = len(loss_products)
total_products = len(df)

loss_pct = (loss_count / total_products * 100) if total_products > 0 else 0

# color dinámico
color = "#DC2626" if loss_pct > 20 else "#F59E0B" if loss_pct > 10 else "#16A34A"

col3.markdown(f"""
<div style="
    padding:15px;
    background:#FFFFFF;
    border-radius:12px;
    border:1px solid #BFC7D5;
    height:130px;
    display:flex;
    flex-direction:column;
    justify-content:center;
">
<h4>⚠️ Loss Products</h4>
<h2>
    {loss_count}
    <span style="font-size:18px; color:{color}; font-weight:600;">
        ({loss_pct:.1f}%)
    </span>
</h2>
</div>
""", unsafe_allow_html=True)

avg_profit = df['estimated_profit'].mean()
color = "#16A34A" if avg_profit > 0 else "#DC2626"

col4.markdown(f"""
<div style="
    padding:15px;
    background:#FFFFFF;
    border-radius:12px;
    border:1px solid #BFC7D5;
    height:130px;
    display:flex;
    flex-direction:column;
    justify-content:center;
">
<h4 style="margin-bottom:8px;">📊 Avg Profit</h4>
<h2 style="color:{color};">${avg_profit:,.0f}</h2>
</div>
""", unsafe_allow_html=True)

st.divider()

# -------------------------
# TABS
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "💰 Profit",
    "🚀 Opportunities",
    "⚔️ Competition",
    "📈 Demand & Listing"
])

# -------------------------
# TAB 1
# -------------------------
with tab1:

    # 🔑 Crear label ASIN + nombre
    top_profit["label"] = top_profit["ASIN"] + " | " + top_profit[display_col]

    # -------------------------
    # 📊 GRÁFICO FULL WIDTH
    # -------------------------
    fig = px.bar(
        top_profit,
        x="label",
        y="estimated_profit",
        color="estimated_profit"
    )

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#111827")
    )

    fig.update_xaxes(tickangle=-30)

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------------------------
    # 🏆 TOP PRODUCTS (ABAJO)
    # -------------------------
    st.markdown("### 🏆 Top Products")

    # 🔑 Agregar ASIN + nombre
    top_profit["label"] = top_profit["ASIN"] + " | " + top_profit[display_col]

    st.dataframe(
        top_profit[["label", "Revenue", "total_fees", "estimated_profit", "profit_margin"]]
        .rename(columns={
        "total_fees": "FBA Fees (excluding COGS, Shipping & Ads)"
    })
    .style
    .background_gradient(cmap="Greens", subset=["estimated_profit"])
    .background_gradient(cmap="Reds", subset=["FBA Fees (excluding COGS, Shipping & Ads)"])
    .background_gradient(cmap="Blues", subset=["profit_margin"])
    .format({
        "Revenue": "${:,.0f}",
        "FBA Fees (excluding COGS, Shipping & Ads)": "${:,.0f}",
        "estimated_profit": "${:,.0f}",
        "profit_margin": "{:.1f}%"
    }),
        use_container_width=True,
        height=400,
        hide_index=True
)

    st.divider()

    # -------------------------
    # 📦 PRODUCT EXPLORER
    # -------------------------
    st.markdown("### 📦 Product Explorer")

    # 👇 CREAR LABEL (ASIN + NOMBRE)
    df["label"] = df["ASIN"] + " | " + df[display_col]

    selected_product = st.selectbox(
        "Select product",
        df["label"]
)
    selected_asin = selected_product.split(" | ")[0]

    product_row = df[df["ASIN"] == selected_asin]
    

    col1, col2 = st.columns(2)

    with col1:
        st.metric("💰 Profit", f"${product_row['estimated_profit'].values[0]:,.0f}")
        st.metric("📈 Sales", int(product_row["ASIN Sales"].values[0]))

    with col2:
        asin = product_row["ASIN"].values[0]
        details = product_row["Product Details"].values[0]

        st.markdown(f"""
        **🔑 ASIN:** {asin}

        {details}
        """)
# -------------------------
# TAB 2
# -------------------------
with tab2:

    fig = px.scatter(
        df,
        x="Active Sellers",
        y="ASIN Sales",
        size="Revenue",
        color="opportunity_score",
        hover_data=[display_col]
    )

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#111827")
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# TAB 3
# -------------------------
with tab3:

    st.markdown("### ⚔️ Competition vs Profit")

    fig = px.scatter(
        df,
        x="Active Sellers",
        y="estimated_profit",
        size="ASIN Sales",
        color="profit_margin",
        hover_data=[display_col],
    )

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#111827")
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption("Top-left = high profit + low competition (best opportunities)")

# -------------------------
# TAB 4
# -------------------------
with tab4:

    # 🔑 Crear labels
    top_sales["label"] = top_sales["ASIN"] + " | " + top_sales[display_col]
    top_listing["label"] = top_listing["ASIN"] + " | " + top_listing[display_col]

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(
            top_sales[["label", "ASIN Sales"]]
            .style.background_gradient(cmap="Blues"),
            use_container_width=True,
            hide_index=True  # 👈 CLAVE
        )

    with col2:
        st.dataframe(
            top_listing[["label", "listing_score"]]
            .style.background_gradient(cmap="Purples"),
            use_container_width=True,
            hide_index=True  # 👈 CLAVE
        )

# -------------------------
# INSIGHTS
# -------------------------
st.divider()

st.markdown("## 🧠 Key Insights")

col1, col2, col3 = st.columns(3)

col1.success(f"Top competitor generates ${top_profit['estimated_profit'].iloc[0]:,.0f}")
col2.warning(f"{len(loss_products)} products are losing money")
col3.info("High demand with moderate competition detected")

best = df.sort_values("product_score", ascending=False).iloc[0]

best_label = f"{best['ASIN']} | {best[display_col]}"

st.success(
    f"🏆 Top performing product: {best_label} | "
    f"Profit: ${best['estimated_profit']:,.0f} | "
    f"Sales: {int(best['ASIN Sales'])}"
)
st.markdown("### 📊 Market Intelligence")

avg_sales = df["ASIN Sales"].mean()
avg_profit = df["estimated_profit"].mean()
avg_sellers = df["Active Sellers"].mean()

signals = []

# 🔴 Saturated + risky
if avg_sales > 300 and avg_profit < 100:
    signals.append(("🔴", "Saturated + risky", "High demand but margins are too low"))

# 🟡 Competitive but viable
if avg_sales > 300 and avg_sellers > 15:
    signals.append(("🟡", "Competitive but viable", "Strong demand but high competition"))

# 🟢 Strong opportunity
if avg_profit > 200 and avg_sellers < 10:
    signals.append(("🟢", "Strong opportunity", "High margins with low competition"))

# 🔵 Hidden opportunity
if avg_profit > 150 and avg_sales < 200:
    signals.append(("🔵", "Hidden opportunity", "Low visibility but good profitability"))

# ⚫ Weak market
if avg_sales < 100:
    signals.append(("⚫", "Weak demand", "Market demand is low"))

# Mostrar insights
if signals:
    for icon, title, desc in signals:
        st.markdown(f"""
        <div style="
            padding:12px;
            margin-bottom:8px;
            background:#FFFFFF;
            border-radius:10px;
            border:1px solid #BFC7D5;
        ">
            <b>{icon} {title}</b><br>
            <span style="color:#475569;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("ℹ️ Market conditions are balanced")
if len(signals) > 1:
    st.info("🧠 Mixed signals detected → fragmented market with both risks and opportunities")
# -------------------------
# 💰 Margin Intelligence
# -------------------------

    st.markdown("### 💰 Profitability Analysis")

    avg_margin = df["profit_margin"].mean()

    if avg_margin < 10:
        st.error("🔴 Low margin market → strong price competition")

    elif avg_margin < 25:
        st.warning("🟡 متوسط margin → optimization required")

    else:
        st.success("🟢 Healthy margins → strong profitability potential")

# -------------------------
# 📦 LISTING INSIGHTS
# -------------------------

    st.markdown("### 📦 Listing Intelligence")

    high_sales = df["ASIN Sales"] > df["ASIN Sales"].median()
    low_sales = df["ASIN Sales"] < df["ASIN Sales"].median()
    high_listing = df["listing_score"] > df["listing_score"].median()
    low_listing = df["listing_score"] < df["listing_score"].median()

    if (high_sales & low_listing).any():
        st.success("🚀 High demand + weak listings → strong optimization opportunity")

    if (low_sales & high_listing).any():
        st.info("🔍 Well-optimized listings but low sales → visibility issue")

    if (high_sales & high_listing).any():
        st.warning("⚠️ High demand + strong listings → competitive market")


# In[ ]:





# In[ ]:





# In[ ]:





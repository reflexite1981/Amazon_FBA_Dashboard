#!/usr/bin/env python
# coding: utf-8

# In[1197]:


import json
from datetime import datetime
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import re
import numpy as np
import streamlit.components.v1 as components
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import Image
from reportlab.platypus import Image, PageBreak
import pdfkit
import base64


# In[1198]:


# -------------------------
# 🔐 AUTH SYSTEM
# -------------------------
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def check_login(username, password):
    users = load_users()

    if username in users:
        if users[username]["password"] == password:

            exp_date = datetime.strptime(users[username]["expires"], "%Y-%m-%d")

            if datetime.now() > exp_date:
                return "expired"

            return "ok"

    return "invalid"

# session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# -------------------------
# UI LOGIN
# -------------------------
if not st.session_state.authenticated:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        # 🔥 HEADER CENTRADO Y ALINEADO CON FORM
        st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="160">
            <h1 style="font-size:30px; color:#0F172A; margin-top:10px; margin-bottom:5px;">
                Market Intelligence Dashboard
            </h1>
            <p style="color:#64748B; font-size:14px;">
                Data-driven insights for strategic decision-making
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Login")

        user = st.text_input("User")
        pwd = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):

            result = check_login(user, pwd)

            if result == "ok":
                st.session_state.authenticated = True
                st.success("Access granted")
                st.rerun()

            elif result == "expired":
                st.error("Your subscription has expired.")
                st.markdown(
                    "**Contact us to renew your access and unlock full insights again.**"
                )

            else:
                st.error("Invalid username or password.")
                st.caption("Please check your details or contact us if you need access.")

    st.stop()

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="Amazon Intelligence",
    layout="wide"
)
# -------------------------
# 🧠 STEP ENGINE
# -------------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if st.session_state.step not in [1, 2, 3]:
    st.stop()
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

if "acos_mode" not in st.session_state:
    st.session_state.acos_mode = "Custom"
# -------------------------
# 🎨 PROGRESS BAR
# -------------------------
def render_progress():
    step = st.session_state.step
    total_steps = 3
    progress = step / total_steps * 100

    html = f"""
    <div style="margin-bottom:25px;">
        <div style="font-size:14px; color:#6B7280; margin-bottom:8px;">
            Step {step} of {total_steps}
        </div>

        <div style="
            width:100%;
            height:12px;
            background:#E5E7EB;
            border-radius:8px;
            overflow:hidden;
        ">
            <div style="
                width:{progress}%;
                height:100%;
                background:#16A34A;
                transition: width 0.4s ease-in-out;
            "></div>
        </div>
    </div>
    """

    components.html(html, height=70)
st.markdown("""
<style>
[data-testid="stMetric"] {
    padding: 8px 12px !important;
}

[data-testid="stMetricDelta"] {
    margin-top: -4px !important;
    font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)
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
    border-left: 4px solid #9CA3AF;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.08);
}

/* 🔥 Tabs */
div[data-testid="stTabs"] {
    gap: 30px !important;
    justify-content: space-between;
}

div[data-testid="stTabs"] button {
    font-size: 25px !important;
    font-weight: 700 !important;
    color: #334155 !important;
    padding: 12px 18px !important;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #FF9900 !important;
    border-bottom: 3px solid #FF9900 !important;
}

/* Plot */
.js-plotly-plot {
    background-color: #FFFFFF !important;
}

/* -------------------------
   🎯 SLIDER (AZUL EJECUTIVO)
------------------------- */

.stSlider > div > div {
    background-color: #E5E7EB !important;
}

.stSlider > div > div > div {
    background: #1E3A8A !important;
}

.stSlider > div > div > div > div {
    background-color: #1E40AF !important;
    border: 2px solid white !important;
}

/* 🎯 VALUE (número del slider) */
.stSlider [data-baseweb="slider"] div {
    color: #111827 !important;
    font-weight: 500 !important;
}

/* 🎯 LIMPIEZA TICKS (0 y 60) */
.stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] * {
    background: transparent !important;
    color: #374151 !important;
    border: none !important;
}

.stSlider span[style*="background"] {
    background: transparent !important;
    color: #374151 !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# DATA (DYNAMIC TITLE)
# -------------------------

if st.session_state.step == 1:

    render_progress()

    st.sidebar.markdown("## Upload Data")

    uploaded_file = st.sidebar.file_uploader(
        "Upload file",
        type=["csv", "xlsx"]
    )

    if uploaded_file:

        # -------------------------
        # 📥 LOAD FILE
        # -------------------------
        if uploaded_file:

            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
        
            elif uploaded_file.name.endswith(".xlsx"):
                excel_file = pd.ExcelFile(uploaded_file)
                sheet = st.sidebar.selectbox("Sheet", excel_file.sheet_names)
                df = pd.read_excel(uploaded_file, sheet_name=sheet)


        # -------------------------
        # 🧹 CLEANING (AHORA SÍ)
        # -------------------------

        # limpiar columnas
        df.columns = df.columns.str.strip()

        # rename robusto
        rename_map = {
            "Price  US$": "Price",
            "Price US$": "Price",
            "ASIN Revenue": "Revenue",
            "Fees  US$": "Fees",
            "Fees US$": "Fees"
        }

        df = df.rename(columns=rename_map)

        # función única (SOLO UNA VEZ)
        def clean_numeric(x):
            try:
                if pd.isna(x):
                    return 0.0
        
                x = str(x).strip()
                x = x.replace("$", "").replace("€", "").replace(" ", "")
        
                # 🔥 CASO 1: formato europeo con miles → 88.805,96
                if "." in x and "," in x:
                    x = x.replace(".", "").replace(",", ".")
        
                # 🔥 CASO 2: decimal con coma (sin miles) → 9080,1 / 11,25
                elif "," in x:
                    x = x.replace(",", ".")
        
                # 🔥 CASO 3: formato US → 1,234.56
                elif "," in x:
                    x = x.replace(",", "")
        
                return float(x)
        
            except:
                return 0.0

        # aplicar cleaning
        for col in ["Revenue", "Fees", "Price", "ASIN Sales", "Parent Level Sales"]:
            if col in df.columns:
                df[col] = df[col].apply(clean_numeric)

        # -------------------------
        # 🚨 VALIDACIÓN
        # -------------------------
        required_cols = ["Revenue", "Fees", "ASIN Sales"]

        missing = [col for col in required_cols if col not in df.columns]

        if missing:
            st.error(f"Missing columns: {missing}")
            st.stop()

        # -------------------------
        # DEBUG (recomendado)
        # -------------------------
        st.write("Columns:", df.columns.tolist())
        st.write(df[["Price", "Revenue", "Fees"]].head())

        # -------------------------
        # SAVE STATE
        # -------------------------
        with st.spinner("Processing data..."):
            st.session_state.df = df
            st.session_state.step = 2
            st.rerun()
    st.stop() 

    
# -------------------------
# STEP 2 — COST STRUCTURE
# -------------------------
if st.session_state.step == 2:

    render_progress()

    st.sidebar.markdown("## Cost Structure")

    cogs = st.sidebar.number_input("COGS per unit ($)", value=0.0, step=0.5)
    shipping = st.sidebar.number_input("Shipping per unit ($)", value=0.0, step=0.5)
    acos = st.sidebar.slider("Ad Spend (ACOS %)", 0, 60, 15)

    col1, col2 = st.sidebar.columns(2)

    if col1.button("Back"):
         st.session_state.step = 1

    if col2.button("Run Analysis"):
        st.session_state.cogs = cogs
        st.session_state.shipping = shipping
        st.session_state.acos = acos
        st.session_state.step = 3
        st.rerun()
    st.stop()


# -------------------------
# STEP 3 — DASHBOARD + LIVE CONTROL
# -------------------------
if st.session_state.step == 3:

    if "df" not in st.session_state:
        st.stop()

    # 🔐 LOGOUT (VA ACÁ)
    st.sidebar.markdown("### Account")

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.step = 1
        st.rerun()
    # 🔄 RESET
    if st.sidebar.button("Upload new file", use_container_width=True):

        for key in ["df", "cogs", "shipping", "acos"]:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state.step = 1
        st.rerun()
    # -------------------------
    # 📊 DATA
    # -------------------------
    df = st.session_state.df

    # -------------------------
    # 💰 COST STRUCTURE (LIVE)
    # -------------------------
    st.sidebar.markdown("## Cost Structure")

    cogs = st.sidebar.number_input(
        "COGS per unit ($)",
        value=st.session_state.cogs,
        step=0.5,
        key="cogs_live"
    )

    shipping = st.sidebar.number_input(
        "Shipping per unit ($)",
        value=st.session_state.shipping,
        step=0.5,
        key="shipping_live"
    )

   
    
    # -------------------------
    # 🚀 ACOS (HYBRID MODE)
    # -------------------------
    st.sidebar.markdown("### Ad Spend Strategy")

    col1, col2 = st.sidebar.columns(2)

    preset_active = st.session_state.get("acos_mode", "Preset") == "Preset"
    custom_active = st.session_state.get("acos_mode", "Preset") == "Custom"
    
    if col1.button("Preset", use_container_width=True, type="primary" if preset_active else "secondary"):
        st.session_state.acos_mode = "Preset"
    
    if col2.button("Custom", use_container_width=True, type="primary" if custom_active else "secondary"):
        st.session_state.acos_mode = "Custom"
    
    mode = st.session_state.acos_mode
    
    if mode == "Custom":
        st.sidebar.markdown(
            "<span style='color:#1E3A8A; font-weight:500;'>Adjust your advertising intensity (ACOS)</span>",
            unsafe_allow_html=True
        )
    
    if mode == "Preset":

        strategy = st.sidebar.selectbox(
            "Strategy",
            ["Conservative (10%)", "Balanced (20%)", "Aggressive (35%)"],
            key="acos_strategy"
        )

        acos = int(strategy.split("(")[1].replace("%)", ""))

    else:

        # 🎯 SLIDER
        acos = st.sidebar.slider(
            "ACOS %",
            0, 60,
            st.session_state.acos,
            key="acos_live"
        )

        # 🔥 👇 ACA VAN LOS TICKS (ESTO TE FALTABA)
        st.sidebar.markdown("""
        <div style="
        display:flex;
        justify-content:space-between;
        font-size:12px;
        color:#6B7280;
        margin-top:-8px;
        padding: 0 4px;
        ">
        <span>0</span>
        <span>10</span>
        <span>20</span>
        <span>30</span>
        <span>40</span>
        <span>50</span>
        <span>60</span>
        </div>
        """, unsafe_allow_html=True)

    # 🔁 SYNC
    st.session_state.acos = acos
    st.session_state.shipping = shipping

 
# -------------------------
# FEATURES
# -------------------------
df["total_fees"] = df["Fees"] * df["ASIN Sales"]
df["estimated_profit"] = df["Revenue"] - df["total_fees"]
df["profit_margin"] = (df["estimated_profit"] / df["Revenue"]) * 100
# -------------------------
# 💰 USER COSTS → REAL PROFIT
# -------------------------

use_real_profit = (cogs > 0) or (shipping > 0) or (acos > 0)

df["cogs_cost"] = cogs * df["ASIN Sales"]
df["shipping_cost"] = shipping * df["ASIN Sales"]
df["ads_cost"] = df["Revenue"] * (acos / 100)

df["real_profit"] = (
    df["Revenue"]
    - df["total_fees"]
    - df["cogs_cost"]
    - df["shipping_cost"]
    - df["ads_cost"]
)

df["real_margin"] = np.where(
    df["Revenue"] > 0,
    (df["real_profit"] / df["Revenue"]) * 100,
    0
)

# -------------------------
# 🧠 ACTIVE LAYER (CLAVE)
# -------------------------

df["active_profit"] = np.where(
    use_real_profit,
    df["real_profit"],
    df["estimated_profit"]
)

df["active_margin"] = np.where(
    use_real_profit,
    df["real_margin"],
    df["profit_margin"]
)


# -------------------------
# 📊 NORMALIZATION (FOR SCORING)
# -------------------------

# evitar división por cero
df["profit_norm"] = df["active_profit"] / df["active_profit"].max() if df["active_profit"].max() > 0 else 0
df["sales_norm"] = df["ASIN Sales"] / df["ASIN Sales"].max() if df["ASIN Sales"].max() > 0 else 0
df["sellers_norm"] = df["Active Sellers"] / df["Active Sellers"].max() if df["Active Sellers"].max() > 0 else 0

# -------------------------
# 📊 ORIGINAL FILTERS
# -------------------------
df_original = df.copy()

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

# -------------------------
# 🧠 RATINGS (fix formato)
# -------------------------
df["Ratings"] = df["Ratings"].astype(str).str.replace(',', '.').astype(float)

# -------------------------
# 🔥 NUEVO: MARKET POWER
# -------------------------
df["review_power"] = (df["Review Count"] ** 0.5) * df["Ratings"]
df["market_dominance"] = df["Review Count"] * df["Ratings"]

# -------------------------
# 📦 LISTING SCORE (MEJORADO)
# -------------------------
df["listing_score"] = (
    df["Images"] +
    df["review_power"]
)

# -------------------------
# 💰 PRODUCT SCORE (igual)
# -------------------------
df["product_score"] = (
    df["profit_norm"] * 0.4 +
    df["sales_norm"] * 0.4 -
    df["sellers_norm"] * 0.2
)
# -------------------------
# 🧠 AUTHORITY (reviews + rating)
# -------------------------
df["authority_score"] = np.log1p(df["Review Count"]) * df["Ratings"]

# -------------------------
# 🚀 MOMENTUM (dinámica del mercado)
# -------------------------
df["momentum_score"] = (
    np.log1p(df["Review velocity"]) * 0.6 +
    np.log1p(df["Recent Purchases"]) * 0.4
)

# -------------------------
# 🛡️ TRUST SIGNALS
# -------------------------
df["buybox_flag"] = df["Buy Box"].astype(str).str.lower().isin(["yes", "true"]).astype(int)
df["bestseller_flag"] = df["Best Seller"].astype(str).str.lower().isin(["yes", "true"]).astype(int)

df["trust_score"] = (
    df["buybox_flag"] * 0.6 +
    df["bestseller_flag"] * 0.4
)

# -------------------------
# 🏆 TRUE MARKET POWER (CORE KPI)
# -------------------------
df["market_power_score"] = (
    df["authority_score"] * 0.5 +
    df["momentum_score"] * 0.3 +
    df["trust_score"] * 0.2
)
# -------------------------
# 📅 CREATION DATE (NUEVO)
# -------------------------
df["Creation Date"] = pd.to_datetime(df["Creation Date"], errors="coerce")

# Edad del producto en días
df["product_age_days"] = (pd.Timestamp.now() - df["Creation Date"]).dt.days

# Edad en meses (más útil)
df["product_age_months"] = df["product_age_days"] / 30

# 🆕 NUEVOS PRODUCTOS
df["is_new"] = df["product_age_months"] <= 6
# 🚀 SALES VELOCITY (NUEVO)
df["sales_velocity"] = df["ASIN Sales"] / (df["product_age_months"] + 1)


# -------------------------
# 🎯 SIDEBAR (SaaS PRO)
# -------------------------
with st.sidebar.expander("Advanced Strategy", expanded=False):

    preset = st.radio(
        "Select your objective",
        ["Find Winners", "Low Risk", "Scale Opportunities", "Custom"],
         index=3 
    )
    

# -------------------------
# 🧠 DEFAULT VALUES
# -------------------------
if preset == "Find Winners":
    min_profit = df["estimated_profit"].median()
    min_sales = df["ASIN Sales"].median()
    min_margin = 25
    strategy = "High Profit"

elif preset == "Low Risk":
    min_profit = df["estimated_profit"].median() * 0.5
    min_sales = df["ASIN Sales"].median()
    min_margin = 20
    strategy = "Balanced"

elif preset == "Scale Opportunities":
    min_profit = df["estimated_profit"].median()
    min_sales = df["ASIN Sales"].median() * 1.2
    min_margin = 15
    strategy = "Low Competition"

else:
    strategy = "All"
    
    st.sidebar.markdown("### Advanced Filters")

    # -------------------------
    # 💰 PROFIT
    # -------------------------
    st.sidebar.markdown("**Profit ($)**")
    
    profit_preset = st.sidebar.radio(
        "Profit preset",
        ["Any", "Low", "Medium", "High"],
        horizontal=True,
        key="profit_preset",
        label_visibility="collapsed"
    )
    
    if profit_preset == "Low":
        min_profit = df["estimated_profit"].quantile(0.25)
    elif profit_preset == "Medium":
        min_profit = df["estimated_profit"].quantile(0.5)
    elif profit_preset == "High":
        min_profit = df["estimated_profit"].quantile(0.75)
    else:
        min_profit = 0
    
    min_profit = st.sidebar.number_input(
        "Custom value",
        value=float(min_profit),
        step=10.0
    )
    
    # -------------------------
    # 📈 SALES
    # -------------------------
    st.sidebar.markdown("**Demand (Units)**")
    
    sales_preset = st.sidebar.radio(
        "Select preset",
        ["Any", "Low", "Medium", "High"],
        horizontal=True,
        key="sales_preset",
        label_visibility="collapsed"
    )
    
    if sales_preset == "Low":
        min_sales = int(df["ASIN Sales"].quantile(0.25))
    elif sales_preset == "Medium":
        min_sales = int(df["ASIN Sales"].quantile(0.5))
    elif sales_preset == "High":
        min_sales = int(df["ASIN Sales"].quantile(0.75))
    else:
        min_sales = 0
    
    min_sales = st.sidebar.number_input(
        "Custom value",
        value=int(min_sales),
        step=10
    )
    
    # -------------------------
    # 📊 MARGIN
    # -------------------------
    st.sidebar.markdown("**Margin (%)**")
    
    margin_preset = st.sidebar.radio(
        "Margin preset",
        ["Any", "Low", "Medium", "High"],
        horizontal=True,
        key="margin_preset",
        label_visibility="collapsed"
    )
    
    if margin_preset == "Low":
        min_margin = 10
    elif margin_preset == "Medium":
        min_margin = 20
    elif margin_preset == "High":
        min_margin = 30
    else:
        min_margin = 0
    
    min_margin = st.sidebar.number_input(
        "Custom value",
        value=int(min_margin),
        step=1
    )

# -------------------------
# 💡 CONTEXTO
# -------------------------
if preset != "Custom":
    st.sidebar.success(f"Preset: {preset}")
# -------------------------
# 🎯 APPLY FILTERS
# -------------------------
df = df[
    (df["active_profit"] >= min_profit) &
    (df["ASIN Sales"] >= min_sales) &
    (df["active_margin"] >= min_margin)
]
# -------------------------
# 🧠 STRATEGY LOGIC
# -------------------------
if not df.empty:

    profit_median = df["active_profit"].median()
    competition_median = df["Active Sellers"].median()

    if strategy == "High Profit":
        df = df[df["active_profit"] >= profit_median]

    elif strategy == "Low Competition":
        df = df[df["Active Sellers"] <= competition_median]

    elif strategy == "Balanced":
        df = df[
            (df["active_profit"] >= profit_median) &
            (df["Active Sellers"] <= competition_median)
        ]

# -------------------------
# 🚨 FALLBACK AUTOMÁTICO
# -------------------------
if df.empty and preset != "Custom":

    st.warning("No products matched this strategy. Expanding criteria...")

    df = df_original.copy()

    df = df[
        (df["active_profit"] >= df["active_profit"].quantile(0.3)) &
        (df["ASIN Sales"] >= df["ASIN Sales"].quantile(0.3))
    ]

# -------------------------
# 📊 SORT
# -------------------------
df = df.sort_values("product_score", ascending=False) if not df.empty else df

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
    border-left: 4px solid #9CA3AF;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.08);
}

/* 🔥 Tabs (FIX DEFINITIVO) */
div[data-testid="stTabs"] button {
    font-size: 23px !important;
    font-weight: 600 !important;
    color: #334155 !important;
    padding: 12px 16px !important;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #FF9900 !important;
    border-bottom: 3px solid #FF9900 !important;
}

/* Plot */
.js-plotly-plot {
    background-color: #FFFFFF !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# 🧩 FUNCTIONS 
# -------------------------
def gap_signal_card(title, gap, is_pct=False):
    is_positive = gap > 0

    text_color = "#166534" if is_positive else "#991B1B"
    border_color = "#BBF7D0" if is_positive else "#FECACA"

    dot = "●"
    value = f"{gap:.1f}%" if is_pct else f"{gap:,.0f}"

    return f"""<div style="
padding:12px;
margin-bottom:4px;
background:#F8FAFC;
border-radius:14px;
border:1px solid #E5E7EB;
border-left: 4px solid {border_color};
box-shadow: 0px 2px 6px rgba(0,0,0,0.03);
height:100%;

display:flex;
flex-direction:column;
justify-content:center;
align-items:flex-start;
">
<div style="font-size:13px; color:#6B7280; margin-bottom:4px;">
{title}
</div>

<div style="font-size:24px; font-weight:700; color:{text_color};">
{dot} {value}
</div>
</div>"""
# -------------------------
# Metric Card
# -------------------------
def metric_card(title, value):
    return f"""<div style="
padding:10px;
margin-bottom:4px;
background:#F8FAFC;
border-radius:14px;
border:1px solid #E5E7EB;
box-shadow: 0px 2px 6px rgba(0,0,0,0.03);
height:100%;

display:flex;
flex-direction:column;
justify-content:center;
align-items:flex-start;
">
<div style="font-size:12px; color:#6B7280; margin-bottom:3px;">
{title}
</div>

<div style="font-size:22px; font-weight:700; color:#111827;">
{value}
</div>
</div>"""
# -------------------------
# DATASETS
# -------------------------
top_profit = df.sort_values("active_profit", ascending=False).head(10)
loss_products = df[df["active_profit"] < 0]
top_opportunities = df.sort_values("opportunity_score", ascending=False).head(10)
top_listing = df.sort_values("listing_score", ascending=False).head(10)
top_sales = df.sort_values("ASIN Sales", ascending=False).head(10)
top_dominance = df.sort_values("market_dominance", ascending=False).head(10)
# -------------------------
# HEADER
# -------------------------
st.markdown("""
<div style="text-align:center; margin-bottom:10px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="180">
</div>

<div style="text-align:center; margin-bottom:20px;">
    <h1 style="font-size:34px; color:#0F172A; margin-bottom:8px;">
        Market Intelligence Dashboard
    </h1>
    <p style="color:#475569; font-size:16px;">
        Data-driven insights for strategic decision-making
    </p>
</div>
""", unsafe_allow_html=True)
# -------------------------
# KPIs
# -------------------------
col1, col2, col3, col4 = st.columns(4)

def kpi_card(title, value, subtitle="", color="#0F172A"):
    return f"""
    <div style="
        padding:22px;
        background:#FFFFFF;
        border-radius:16px;
        border:1px solid #9CA3AF;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
        height:150px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;  /* 👈 CLAVE */
        text-align:center;   /* 👈 CLAVE */
    ">
        <div style="font-size:18px; color:#475569; margin-bottom:8px; font-weight:600;">
            {title}
        </div>
        <div style="font-size:32px; font-weight:700; color:{color};">
            {value}
        </div>
        <div style="font-size:13px; color:#94A3B8; margin-top:6px;">
            {subtitle}
        </div>
    </div>
    """

# KPI 1
col1.markdown(
    kpi_card("Total Products", f"{len(df)}", "Active listings in dataset"),
    unsafe_allow_html=True
)

# KPI 2
col2.markdown(
    kpi_card(
        "Total Estimated Profit",
        f"${df['estimated_profit'].sum():,.0f}",
        "Aggregated across all products",
        "#FF9900"
    ),
    unsafe_allow_html=True
)

# KPI 3
loss_count = len(loss_products)
total_products = len(df)
loss_pct = (loss_count / total_products * 100) if total_products > 0 else 0

color = "#DC2626" if loss_pct > 20 else "#F59E0B" if loss_pct > 10 else "#16A34A"

col3.markdown(
    kpi_card(
        "Loss-Making Products",
        f"{loss_count} ({loss_pct:.1f}%)",
        "Share of unprofitable listings",
        color
    ),
    unsafe_allow_html=True
)

# KPI 4 → REAL PROFIT
real_total = df["real_profit"].sum()
estimated_total = df["estimated_profit"].sum()

impact_pct = (
    (real_total - estimated_total) / estimated_total * 100
    if estimated_total > 0 else 0
)

color = "#16A34A" if real_total > 0 else "#DC2626"

col4.markdown(
    kpi_card(
        "Real Profit",
        f"${real_total:,.0f}",
        f"{impact_pct:.0f}% vs estimated",
        color
    ),
    unsafe_allow_html=True
)

st.divider()
def kpi_card_tab5(title, value, color="#0F172A", subtitle=None):

    subtitle_html = f"""
        <div style="
            font-size:12px;
            color:#6B7280;
            height:18px;  /* 🔥 espacio reservado SIEMPRE */
            margin-top:6px;
        ">
            {subtitle if subtitle else ""}
        </div>
    """

    return f"""
    <div style="
        height:180px;
        width:100%;
        padding:22px;
        background:#FFFFFF;
        border-radius:16px;
        border:1px solid #E5E7EB;
        box-shadow: 0px 6px 18px rgba(0,0,0,0.05);

        display:flex;
        flex-direction:column;
        align-items:center;
        text-align:center;
        box-sizing:border-box;
    ">

        <!-- TITLE -->
        <div style="
            font-size:18px;
            color:#6B7280;
            font-weight:600;
            margin-bottom:8px;
        ">
            {title}
        </div>

        <!-- VALUE -->
        <div style="
            font-size:36px;
            font-weight:700;
            color:{color};
            flex-grow:1;  /* 🔥 centra verticalmente */
            display:flex;
            align-items:center;
        ">
            {value}
        </div>

        <!-- SUBTITLE (SIEMPRE RESERVA ESPACIO) -->
        {subtitle_html}

    </div>
    """
# -------------------------
# STRATEGY CLASSIFICATION
# -------------------------
avg_profit = df["active_profit"].mean()
avg_sellers = df["Active Sellers"].mean()
    
def classify(row):
    if row["active_profit"] > avg_profit and row["Active Sellers"] < avg_sellers:
        return "Scale"
    elif row["active_profit"] > avg_profit:
        return "Defend"
    elif row["Active Sellers"] < avg_sellers:
        return "Optimize"
    else:
        return "Exit"
    
df["strategy_zone"] = df.apply(classify, axis=1)
    
# 🎨 PALETA CONSISTENTE
strategy_colors = {
    "Defend": "#A5B4FC",
    "Scale": "#67E8F9",
    "Optimize": "#FCA5A5",
    "Exit": "#F9A8D4"
}
# -------------------------
# TABS
# -------------------------
tab1, tab2, tab3, tab4, tab5, tab6  = st.tabs([
    "Performance Overview",
    "Market Analysis",
    "Leadership Position",
    "Growth Opportunities",
    "Strategic Decisions",
    "Executive Report"
])

# -------------------------
# TAB 1
# -------------------------
# -------------------------
# 📊 GRÁFICO FULL WIDTH
# -------------------------
with tab1:

    # 🏆 TOP PERFORMER 
    st.markdown("## Top Performer")

    if not df.empty:
        best = df.sort_values("product_score", ascending=False).iloc[0]
        st.markdown(f"**{best['ASIN']} | {best[display_col]}**")

        col1, col2, col3 = st.columns(3)

        col1.metric("Sales", f"{best['ASIN Sales']:,.0f}")
        col2.metric("Profit", f"${best['active_profit']:,.0f}")
        col3.metric("Margin", f"{best['active_margin']:.1f}%")

    else:
        st.warning("No products available")

    st.divider()
    
    # 🔑 Crear label ASIN + nombre
    top_profit["label"] = top_profit["ASIN"] + " | " + top_profit[display_col]

    # 🔥 Limitar a top 10 (más limpio)
    top_profit = top_profit.sort_values("active_profit", ascending=False).head(10)

    # 🔥 Ordenar para gráfico horizontal
    top_profit = top_profit.sort_values("active_profit", ascending=True)

    # 👇 AGREGA ESTO ACÁ
    st.caption("Profit reflects real profitability after all costs (FBA fees, COGS, shipping, and advertising)")
    # -------------------------
    # 📊 GRÁFICO FULL WIDTH (MEJORADO)
    # -------------------------
    fig = px.bar(
        top_profit,
        x="active_profit",
        y="label",
        orientation="h",
        text="active_profit",
        color="active_profit",
        color_continuous_scale=["#DCFCE7", "#16A34A"]
    )

    fig.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    )

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#111827"),
        height=500,
        yaxis_title="",
        xaxis_title="Profit (After Costs)",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------------------------
    # 🏆 TOP PRODUCTS (ABAJO)
    # -------------------------

    st.markdown("### Top Performing Products")

    # 🔑 Agregar ASIN + nombre
    top_profit["label"] = top_profit["ASIN"] + " | " + top_profit[display_col]

    # 🔥 Renombrar columnas (EJECUTIVO)
    top_display = top_profit[[
        "label", 
        "Revenue", 
        "total_fees", 
        "cogs_cost",
        "shipping_cost",
        "ads_cost",
        "estimated_profit",
        "active_profit",
        "active_margin"
    ]].rename(columns={
        "label": "Product",
        "total_fees": "FBA Fees",
        "cogs_cost": "COGS",
        "shipping_cost": "Shipping",
        "ads_cost": "Ads",
        "estimated_profit": "Estimated Profit",
        "active_profit": "Real Profit",
        "active_margin": "Real Margin (%)"
    })

    top_display = top_display.sort_values("Real Profit", ascending=False)
    # 🔥 Tabla final
    st.caption("Profit reflects real profitability after all costs (FBA fees, COGS, shipping, and advertising)")
    st.dataframe(
        top_display
        .style
        .background_gradient(cmap="Purples", subset=["Revenue"])
        .background_gradient(cmap="Greens", subset=["Estimated Profit"])
        .background_gradient(cmap="Greens", subset=["Real Profit"]) 
        .background_gradient(cmap="Reds", subset=["FBA Fees"])
        .background_gradient(cmap="Blues", subset=["Real Margin (%)"])
        .background_gradient(cmap="Reds", subset=["COGS", "Shipping", "Ads"])
        .format({
            "Revenue": "${:,.0f}",
            "FBA Fees": "${:,.0f}",
            "COGS": "${:,.0f}",
            "Shipping": "${:,.0f}",
            "Ads": "${:,.0f}",
            "Estimated Profit": "${:,.0f}",
            "Real Profit": "${:,.0f}",
            "Real Margin (%)": "{:.1f}%"
        }),
        use_container_width=True,
        height=400,
        hide_index=True
    )

    st.divider()
    # -------------------------
    # 🏆 PRODUCT PERFORMANCE OVERVIEW
    # -------------------------
    
    st.markdown("### Product Performance Overview")
    
    # 🏆 Market Leader
    if not df.empty:
        best = df.sort_values("product_score", ascending=False).iloc[0]
        best_label = f"{best['ASIN']} | {best[display_col]}"
    else:
        st.warning("No data available")
        st.stop()

    # -------------------------
    # 🔎 PRODUCT SELECTOR
    # -------------------------
    
    df["label"] = df["ASIN"] + " | " + df[display_col]
    
    # 🎯 Contenedor visual (estilo executive)
    st.markdown("""
    <div style="
    padding:14px;
    margin-bottom:12px;
    background:#F8FAFC;
    border-radius:12px;
    border:1.5px solid #D1D5DB;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.03);
    ">
    <div style="font-size:13px; font-weight:600; margin-bottom:6px; color:#374151;">
    Select your product (ASIN)
    </div>
    """, unsafe_allow_html=True)
    
    selected_product = st.selectbox(
        "Select your product (ASIN)",   # requerido por Streamlit
        df["label"],
        label_visibility="collapsed"    # 👈 no visible pero correcto
    )

    st.markdown("</div>", unsafe_allow_html=True)
    
    # 🎯 Lógica

    if selected_product is not None:
    
        selected_asin = selected_product.split(" | ")[0]
    
        filtered = df[df["ASIN"] == selected_asin]
    
        if not filtered.empty:
            selected_row = filtered.iloc[0]
        else:
            st.warning("Selected product not found")
            st.stop()
    
    else:
        st.warning("No product selected")
        st.stop()

# -------------------------
    # 📊 MARKET AVERAGE
    # -------------------------
    avg_profit = df["active_profit"].mean()
    avg_sales = df["ASIN Sales"].mean()
    avg_margin = df["active_margin"].mean()
    # -------------------------
    # 📊 COMPARACIÓN + MARKET AVERAGE + GAP
    # -------------------------
    if not df.empty:
        best = df.sort_values("product_score", ascending=False).iloc[0]
        
        filtered_selected = df[df["ASIN"] == selected_row["ASIN"]]
    
        if not filtered_selected.empty:
            selected_row = filtered_selected.iloc[0]
        else:
            st.warning("Selected product no longer matches filters")
            st.stop()
    
        # GAP vs LEADER
        profit_gap = selected_row["active_profit"] - best["active_profit"]
        sales_gap = selected_row["ASIN Sales"] - best["ASIN Sales"]
        margin_gap = selected_row["active_margin"] - best["active_margin"]
    
        # GAP vs MARKET AVERAGE (🔥 MOVER ADENTRO)
        profit_gap_avg = selected_row["active_profit"] - avg_profit
        sales_gap_avg = selected_row["ASIN Sales"] - avg_sales
        margin_gap_avg = selected_row["active_margin"] - avg_margin
    
        col1, col2, col3, col4, col5 = st.columns(5)
    
        # 🔎 YOUR PRODUCT
        with col1:
            st.markdown("#### Your Product")
            components.html(metric_card("Profit", f"${selected_row['active_profit']:,.0f}"), height=110)
            components.html(metric_card("Sales", f"{int(selected_row['ASIN Sales'])}"), height=110)
            components.html(metric_card("Margin", f"{selected_row['active_margin']:.1f}%"), height=110)
    
        # 🏆 MARKET LEADER
        with col2:
            st.markdown("#### Market Leader")
            components.html(metric_card("Profit", f"${best['active_profit']:,.0f}"), height=110)
            components.html(metric_card("Sales", f"{int(best['ASIN Sales'])}"), height=110)
            components.html(metric_card("Margin", f"{best['active_margin']:.1f}%"), height=110)
    
        # 📊 AVERAGE
        with col3:
            st.markdown("#### Market Average")
            components.html(metric_card("Profit", f"${avg_profit:,.0f}"), height=110)
            components.html(metric_card("Sales", f"{int(avg_sales) if not pd.isna(avg_sales) else 0}"), height=110)
            components.html(metric_card("Margin", f"{avg_margin:.1f}%"), height=110)
    
        # GAP vs Leader
        with col4:
            st.markdown("#### Gap vs Leader")
            components.html(gap_signal_card("Profit Gap", profit_gap), height=110)
            components.html(gap_signal_card("Sales Gap", sales_gap), height=110)
            components.html(gap_signal_card("Margin Gap", margin_gap, is_pct=True), height=110)
    
        # GAP vs Market
        with col5:
            st.markdown("#### Gap vs Market")
            components.html(gap_signal_card("Profit Gap", profit_gap_avg), height=110)
            components.html(gap_signal_card("Sales Gap", sales_gap_avg), height=110)
            components.html(gap_signal_card("Margin Gap", margin_gap_avg, is_pct=True), height=110)
    
    else:
        st.warning("No data available after filters")
        st.stop()
    # -------------------------
    # 🧠 SMART INTERPRETATION
    # -------------------------
    # -------------------------
    # 🧠 PERFORMANCE INTERPRETATION (SMART COLORS)
    # -------------------------
    # -------------------------
    # 🧠 GAP IMPACT SCORE
    # -------------------------
    leader_impact = abs(profit_gap) + abs(sales_gap) + abs(margin_gap)
    market_impact = abs(profit_gap_avg) + abs(sales_gap_avg) + abs(margin_gap_avg)
    
    st.markdown("### Performance Interpretation")
    
    messages = []
    
    if profit_gap < 0:
        messages.append(
            "Lower profitability vs market leader — review pricing, cost structure, or fees."
        )
    
    if sales_gap < 0:
        messages.append(
            "Lower sales volume indicates weaker demand or visibility — improve ranking, ads, or listing quality."
        )

    if margin_gap < 0:
        messages.append(
            "Lower margin suggests pricing pressure or higher costs — optimization opportunity."
        )
    
    # 🟢 MATCH LEADER (igual al top)
    if profit_gap == 0 and sales_gap == 0:
        insight_text = "Market-leading performance — your product matches the top performer and significantly outperforms the market."
        bg = "#ECFDF5"
        border = "#BBF7D0"
        text = "#065F46"

    # 🚀 OUTPERFORM REAL (mejor que el líder)
    elif profit_gap > 0 and sales_gap > 0:
        insight_text = "Exceptional performance — your product outperforms the market leader across key metrics."
        bg = "#DCFCE7"
        border = "#86EFAC"
        text = "#065F46"
    
    # 🔴 UNDERPERFORM (todo mal)
    elif profit_gap < 0 and sales_gap < 0:

    # 🎯 DECISIÓN: Leader vs Market
        if leader_impact > market_impact:
            insight_text = "Performance gap is driven by a strong market leader — competitive positioning is the main constraint."
        else:
            insight_text = "Structural underperformance — the product is below market benchmarks, indicating issues in demand or profitability."

    # 📊 CONTEXTO POSITIVO
        positives = []
    
        if margin_gap_avg > 0:
            positives.append("healthy margins vs market")
    
        if profit_gap_avg > 0:
            positives.append("above-average profitability")
    
        if positives:
            insight_text += " However, it still shows " + ", ".join(positives) + "."
    
        bg = "#FEF2F2"
        border = "#FECACA"
        text = "#7F1D1D"

    # 🟡 MIXED
    elif messages:
        insight_text = " ".join(messages)
    
        # 📊 CONTEXTO VS MERCADO
        market_context = []
    
        if profit_gap_avg > 0:
            market_context.append("above market average in profitability")
    
        if sales_gap_avg > 0:
            market_context.append("stronger demand vs market")
    
        if margin_gap_avg > 0:
            market_context.append("healthy margin vs competitors")
    
        if market_context:
            insight_text += " The product remains " + ", ".join(market_context) + "."
    
        bg = "#FEFCE8"
        border = "#FEF08A"
        text = "#713F12"

    # 🔵 NEUTRAL (NO TOCAR)
    else:
        insight_text = "Performance is aligned with the market — differentiation opportunities may exist."
        bg = "#E0F2FE"
        border = "#BAE6FD"
        text = "#0C4A6E"

    # 🎨 INSIGHT CARD
    st.markdown(f"""
    <div style="
    padding:16px;
    margin-top:10px;
    background:{bg};
    border-radius:14px;
    border:1px solid {border};
    box-shadow: 0px 2px 6px rgba(0,0,0,0.03);
    font-size:14px;
    color:{text};
    font-weight:500;
    ">
    {insight_text}
    </div>
    """, unsafe_allow_html=True)
# -------------------------
# TAB 2
# -------------------------
# -------------------------
# 📈 DEMAND vs LISTING QUALITY (QUADRANT ANALYSIS)
# -------------------------
with tab2:   
    st.markdown("### Demand vs Listing Quality")
    
    # Promedios (líneas de cuadrante)
    avg_sales = df["ASIN Sales"].mean()
    avg_listing = df["listing_score"].mean()
        
    # Scatter
    fig = px.scatter(
        df,
        x="listing_score",
        y="ASIN Sales",
        size="ASIN Sales",
        color="listing_score",
        labels={
        "listing_score": "Listing Score",
        "ASIN Sales": "Sales"
        },
        hover_data=[display_col],
    )
    
    # -------------------------
    # CUADRANTES
    # -------------------------
    fig.add_vline(
        x=avg_listing,
        line_dash="dash",
        line_color="gray"
    )
        
    fig.add_hline(
        y=avg_sales,
        line_dash="dash",
        line_color="gray"
    )
    
    # -------------------------
    # 🧠 LABELS EN CUADRANTES (PRO)
    # -------------------------
    
    x_min, x_max = df["listing_score"].min(), df["listing_score"].max()
    y_min, y_max = df["ASIN Sales"].min(), df["ASIN Sales"].max()
    
    # centros de cuadrantes
    x_left = (x_min + avg_listing) / 2
    x_right = (avg_listing + x_max) / 2
    y_bottom = (y_min + avg_sales) / 2
    y_top = (avg_sales + y_max) / 2
    
    annotation_style = dict(
        showarrow=False,
        font=dict(size=12, color="rgba(17,24,39,0.5)")  # 👈 suave
    )
    
    fig.add_annotation(x=x_right, y=y_top, text="Scale", **annotation_style)
    fig.add_annotation(x=x_left, y=y_top, text="Opportunity", **annotation_style)
    fig.add_annotation(x=x_right, y=y_bottom, text="Optimize", **annotation_style)
    fig.add_annotation(x=x_left, y=y_bottom, text="Low Priority", **annotation_style)
    
    # Layout
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#111827"),
        xaxis_title="Listing Quality",
        yaxis_title="Sales"
    )
        
    st.plotly_chart(fig, use_container_width=True)
        
    # -------------------------
    # 🧾 MICRO CONTEXTO (CLARO Y RÁPIDO)
    # -------------------------
    st.caption(
        "Top-right: High demand & strong listing | "
        "Top-left: High demand, weak listing (opportunity) | "
        "Bottom-right: Low demand, strong listing | "
        "Bottom-left: Low demand & weak listing"
    )
    
     # -------------------------
    # 🧠 DYNAMIC INTERPRETATION
    # -------------------------
    top_right = df[
        (df["ASIN Sales"] > avg_sales) &
        (df["listing_score"] > avg_listing)
    ]
        
    high_sales_low_listing = df[
        (df["ASIN Sales"] > avg_sales) &
        (df["listing_score"] < avg_listing)
    ]
    
    if len(top_right) > len(df) * 0.3:
        insight = "A strong portion of products combine high demand and high listing quality — the market is competitive and well-optimized."
        
    elif len(high_sales_low_listing) > len(df) * 0.3:
        insight = "Several products show strong demand but weak listing quality — this indicates clear opportunities to improve conversion and capture market share."
        
    else:
        insight = "The market presents a balanced mix of demand and listing quality — opportunities exist both in scaling and optimization."
    
    # -------------------------
    # 💬 OUTPUT FINAL
    # -------------------------
    st.info(
        f"{len(top_right)} products are positioned in the high-demand, high-quality quadrant.\n\n"
        f"{insight}"
    )
    
    # 🔑 Crear labels
    top_sales["label"] = top_sales["ASIN"] + " | " + top_sales[display_col]
    top_listing["label"] = top_listing["ASIN"] + " | " + top_listing[display_col]
    
    st.divider()
    col1, col2 = st.columns(2)
    
    # -------------------------
    # 🚀 SALES LEADERS
    # -------------------------
    with col1:
        st.markdown("### Top Sales Products")
    
        df_display = top_sales[["label", "ASIN Sales"]].copy()
    
        # 👇 convertir a entero
        df_display["ASIN Sales"] = df_display["ASIN Sales"].fillna(0).astype(int)
    
        st.dataframe(
            df_display.rename(columns={
                "label": "Product",
                "ASIN Sales": "Monthly Sales"
            })
            .style.background_gradient(cmap="Blues"),
            use_container_width=True,
            hide_index=True
        )
    
        st.caption("Top products by sales")
    
    # -------------------------
    # 🧠 LISTING LEADERS
    # -------------------------
    with col2:
        st.markdown("### Listing Quality Leaders")
    
        st.dataframe(
            top_listing[["label", "listing_score"]]
            .rename(columns={
                "label": "Product",
                "listing_score": "Listing Score"
            })
            .style.background_gradient(cmap="Purples"),
            use_container_width=True,
            hide_index=True
        )
    
        st.caption("Best optimized listings")
    
    # -------------------------
    # 💎 BEST COMBINED OPPORTUNITIES
    # -------------------------
    st.markdown("### Best Overall Opportunities")
    
    top_combined = df.sort_values(
        ["ASIN Sales", "listing_score"],
        ascending=False
    ).head(5).copy()
    
    # 👇 convertir a entero
    top_combined["ASIN Sales"] = top_combined["ASIN Sales"].fillna(0).astype(int)
    
    top_combined["label"] = top_combined["ASIN"] + " | " + top_combined[display_col]
    
    st.dataframe(
        top_combined[["label", "ASIN Sales", "listing_score"]]
        .rename(columns={
            "label": "Product",
            "ASIN Sales": "Sales",
            "listing_score": "Listing Score"
        })
        .style
        .background_gradient(cmap="Blues", subset=["Sales"])
        .background_gradient(cmap="Purples", subset=["Listing Score"]),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    st.markdown("### Competitive Action Map")

    # -------------------------
    # 📊 ACTION SUMMARY
    # -------------------------
    scale = (df["strategy_zone"]=="Scale").sum()
    defend = (df["strategy_zone"]=="Defend").sum()
    optimize = (df["strategy_zone"]=="Optimize").sum()
    exit_ = (df["strategy_zone"]=="Exit").sum()
    total = len(df)

    # 🔥 CARD FUNCTION (EXECUTIVE STYLE)
    def action_card(title, value, color):
        return f"""
        <div style='
            background:#FFFFFF;
            border-radius:18px;
            border:1px solid #E5E7EB;
            box-shadow: 0px 6px 18px rgba(0,0,0,0.05);
            height:150px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            text-align:center;
            position:relative;
        '>

            <!-- línea superior -->
                <div style='
                position:absolute;
                top:0;
                left:0;
                width:100%;
                height:4px;
                background:{color};
                border-top-left-radius:18px;
                border-top-right-radius:18px;
            '></div>

            <div style='
                font-size:16px;
                color:#6B7280;
                font-weight:600;
                margin-bottom:8px;
            '>
                {title}
            </div>

            <div style='
                font-size:40px;
                font-weight:700;
                color:#111827;
            '>
                {value}
            </div>

        </div>
        """

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        components.html(action_card("Scale", scale, strategy_colors["Scale"]), height=150)

    with col2:
        components.html(action_card("Defend", defend, strategy_colors["Defend"]), height=150)

    with col3:
        components.html(action_card("Optimize", optimize, strategy_colors["Optimize"]), height=150)

    with col4:
        components.html(action_card("Exit", exit_, strategy_colors["Exit"]), height=150)

    # espacio
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # -------------------------
    # 📊 QUADRANT SCATTER
    # -------------------------
    fig = px.scatter(
        df,
        x="Active Sellers",
        y="active_profit",
        size="ASIN Sales",
        color="strategy_zone",
        color_discrete_map=strategy_colors,
        hover_data=[display_col],
    )

    fig.add_vline(x=avg_sellers, line_dash="dash", line_color="gray")
    fig.add_hline(y=avg_profit, line_dash="dash", line_color="gray")

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#111827"),
        xaxis_title="Competition (Active Sellers)",
        yaxis_title="Real Profit"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption("Quadrants show relative positioning based on current filtered dataset")

    # -------------------------
    # 🧠 DYNAMIC SUMMARY
    # -------------------------
    if optimize > total * 0.5:
        insight = "Most products require optimization — margin and conversion improvements are needed."
    elif scale > total * 0.4:
        insight = "A strong portion of the portfolio is ready to scale."
    else:
        insight = "Portfolio shows a balanced mix of growth and optimization opportunities."

    st.info(
        f"This analysis reflects the current filtered dataset, not the full market.\n\n"
        f"{scale} products are ready to scale, "
        f"{defend} require defense, "
        f"{optimize} need optimization, "
        f"and {exit_} may be candidates for exit.\n\n"
        f"{insight}"
    )

    # -------------------------
    # 🔥 TOP SCALE PRODUCTS
    # -------------------------
    st.markdown("### Top Products to Scale")
    
    st.info("Margins reflects your cost structure (Revenue – FBA Fees, COGS, shipping, and advertising costs)")
    
    top_scale = df[df["strategy_zone"]=="Scale"] \
        .sort_values("estimated_profit", ascending=False) \
        .head(5).copy()
    
    # 👇 limpiar datos
    top_scale["ASIN Sales"] = top_scale["ASIN Sales"].fillna(0).astype(int)
    
    if len(top_scale) > 0:
        st.dataframe(
            top_scale[[
                "strategy_zone",
                "label",
                "active_profit",
                "ASIN Sales",
                "active_margin"
            ]]
            .rename(columns={
                "strategy_zone": "Strategy",
                "label": "Product",
                "active_profit": "Profit",
                "ASIN Sales": "Sales",
                "active_margin": "Margin"
            })
            .style
            # 🎯 Strategy colors
            .map(
                lambda x: "color: #16A34A; font-weight:600;" if x == "Scale"
                else "color: #2563EB;" if x == "Defend"
                else "color: #F59E0B;" if x == "Optimize"
                else "color: #DC2626;",
                subset=["Strategy"]
            )
            # 💰 Profit → verde
            .background_gradient(cmap="Greens", subset=["Profit"])
            # 📊 Sales → azul
            .background_gradient(cmap="Blues", subset=["Sales"])
            # 📈 Margin → azul-violeta (más pro que usar Blues)
            .background_gradient(cmap="BuPu", subset=["Margin"])
            # 🎯 formatos
            .format({
                "Profit": "${:,.0f}",
                "Sales": "{:,}",
                "Margin": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No products currently in the Scale category based on selected filters.")


 
# -------------------------
# TAB 3 - LEADERSHIP 
# -------------------------
with tab3:

    st.markdown("### Market Leadership")

    st.caption(
        "Market Power combines review authority, growth momentum, and trust signals "
        "to identify current leaders and emerging competitors."
    )

    # -------------------------
    # 📊 SELLER POWER
    # -------------------------
    seller_power = (
        df.groupby("Seller")["market_power_score"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    total_power = seller_power["market_power_score"].sum()
    seller_power["share"] = seller_power["market_power_score"] / total_power * 100

    # KPIs
    top1 = seller_power.iloc[0]["share"] if not seller_power.empty else 0
    top3 = seller_power.head(3)["share"].sum() if not seller_power.empty else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        components.html(
            kpi_card_tab5("Top Seller Share", f"{top1:.1f}%"),
            height=180
        )
    
    with col2:
        components.html(
            kpi_card_tab5("Top 3 Share", f"{top3:.1f}%"),
            height=180
        )
    
    with col3:
        components.html(
            kpi_card_tab5(
                "Unique Sellers",
                f"{len(seller_power)}",
                subtitle="Some sellers manage multiple listings"
            ),
            height=200
        )
    # -------------------------
    # 📊 CHART
    # -------------------------
    top_sellers = seller_power.head(10)

    fig = px.bar(
        top_sellers.sort_values("share"),
        x="share",
        y="Seller",
        orientation="h",
        text="share",
        color="share",
        color_continuous_scale="Reds"
    )

    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=380,  # 👈 más compacto
        margin=dict(l=20, r=20, t=20, b=20),  # 👈 elimina espacio vacío
        xaxis_title="Market Power Share (%)",
        yaxis_title=""
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------------------------
    # 🧠 MARKET DYNAMICS
    # -------------------------
    leaders = df.sort_values("market_power_score", ascending=False).head(3)
    rising = df.sort_values("momentum_score", ascending=False).head(3)

    st.markdown("### Market Dynamics")

    st.info(
        f"Top seller controls {top1:.1f}% of market power. "
        f"Top 3 sellers control {top3:.1f}%.\n\n"
        f"Leaders are driven by strong review authority, while emerging products show high growth velocity."
    )

    # -------------------------
    # 🚀 RISING PRODUCTS
    # -------------------------
    st.markdown("### Emerging Competitors")
    
    st.markdown("""
        <div style="
        padding:14px;
        margin-top:8px;
        margin-bottom:10px;
        background:#F8FAFC;
        border-radius:10px;
        border-left:5px solid #10B981;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
    ">
    
    <span style="font-size:15px; color:#0F172A; line-height:1.5;">
    <b>Momentum Score</b> reflects real-time market traction based on recent purchase activity 
    and review growth. High momentum products are gaining visibility and may become future leaders.
    </span>
    
    </div>
    """, unsafe_allow_html=True)
    
    # 👇 copy para evitar warnings
    rising = rising.copy()
    
    # 👇 limpiar datos
    rising["Recent Purchases"] = rising["Recent Purchases"].fillna(0).astype(int)
    
    rising["label"] = rising["ASIN"] + " | " + rising[display_col]
    
    st.dataframe(
        rising[[
            "Seller",
            "label",
            "momentum_score",
            "Review velocity",
            "Recent Purchases"
        ]]
        .rename(columns={
            "label": "Product",
            "momentum_score": "Momentum Score"
        })
        .style
        # 💰 momentum → verde (ya lo tenías)
        .background_gradient(cmap="Greens", subset=["Momentum Score"])
        # 📈 review velocity → naranja (actividad / crecimiento)
        .background_gradient(cmap="Oranges", subset=["Review velocity"])
        # 📊 recent purchases → azul (volumen)
        .background_gradient(cmap="Blues", subset=["Recent Purchases"])
        # 🎯 formato
        .format({
            "Recent Purchases": "{:,}"
        }),
        use_container_width=True,
        hide_index=True
    )

    # -------------------------
    # 🏆 TOP PRODUCTS
    # -------------------------
    st.markdown("### Top Market Power Products")
    
    top_power = df.sort_values("market_power_score", ascending=False).head(10).copy()
    
    top_power["label"] = top_power["ASIN"] + " | " + top_power[display_col]
    
    # 👇 limpiar datos
    top_power["Review Count"] = top_power["Review Count"].fillna(0).astype(int)
    
    st.dataframe(
        top_power[[
            "Seller",
            "label",
            "market_power_score",
            "Ratings",
            "Review Count"
        ]]
        .rename(columns={
            "label": "Product",
            "market_power_score": "Market Power"
        })
        .style
        .background_gradient(cmap="Reds", subset=["Market Power"])       # 🔴 fuerte
        .background_gradient(cmap="Blues", subset=["Review Count"])      # 🔵 suave
        .background_gradient(cmap="Greys", subset=["Ratings"], low=0.9, high=1.0)
        .format({
            "Ratings": "{:.2f}",
            "Review Count": "{:,}"
        }),
        use_container_width=True,
        hide_index=True
    )
# -------------------------
# TAB 4 - NEW PRODUCTS
# -------------------------
with tab4:

    st.markdown("### Growth Opportunity Matrix")
    st.caption("Products positioned by profitability and competition level")

    # 🔑 Label
    df["label"] = df["ASIN"] + " | " + df[display_col]

    # 🔥 Líneas promedio (cuadrantes)
    avg_profit = df["active_profit"].mean()
    avg_sellers = df["Active Sellers"].mean()

    fig = px.scatter(
        df,
        x="Active Sellers",
        y="active_profit",
        size="ASIN Sales",
        color="active_profit",
        hover_data={
            "label": True,
            "active_profit": ":,.0f",
            "ASIN Sales": ":,.0f",
            "Active Sellers": True
        },
        color_continuous_scale="greens",
        labels={"active_profit": "Profit"}
    )
    fig.add_vline(x=avg_sellers, line_dash="dash", line_color="gray")
    fig.add_hline(y=avg_profit, line_dash="dash", line_color="gray")

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#111827"),
        height=550,
        xaxis_title="Competition (Active Sellers)",
        yaxis_title="Profit"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # 🧠 INSIGHT INTELIGENTE
    # -------------------------

    top_profit_value = df["active_profit"].max()
    avg_profit = df["active_profit"].mean()
    
    ratio = top_profit_value / avg_profit if avg_profit > 0 else 0
    
    if ratio > 2:
        insight = "The market is highly concentrated, with a dominant product significantly outperforming competitors."
    elif ratio > 1.3:
        insight = "The market shows moderate concentration, with a few leading products outperforming the rest."
    else:
        insight = "The market appears relatively balanced, with no single product dominating performance."

    
    st.markdown(f"""
    <div style="
    padding:18px;
    margin-top:10px;
    background:#FFFFFF;
    border-radius:12px;
    border-left:6px solid #6B7280;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    ">

    <div style="font-size:14px; color:#6B7280; margin-bottom:6px;">
    Market Insight
    </div>

    <div style="font-size:16px; color:#0F172A; line-height:1.5;">
    {insight} The top product generates approximately <b>${top_profit_value:,.0f}</b>, compared to an average of <b>${avg_profit:,.0f}</b>.
    </div>

    </div>
    """, unsafe_allow_html=True)

    # -------------------------
    # 🔥 Interpretación ejecutiva
    # -------------------------
    st.markdown("""
    <div style="
        padding:18px;
        background:#FFFFFF;
        border-radius:14px;
        border:1px solid #E5E7EB;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
        margin-top:10px;
    ">
    
    <div style="
        font-size:16px;
        font-weight:700;
        color:#111827;
        margin-bottom:12px;
    ">
    Quadrant Interpretation
    </div>
    
    <div style="font-size:15px; line-height:1.7;">
    
    <div><span style="color:#166534; font-weight:600;">High Profit / Low Competition</span> — Expansion opportunity with strong margin potential</div>
    
    <div><span style="color:#92400E; font-weight:600;">High Profit / High Competition</span> — Competitive environment requiring differentiation</div>
    
    <div><span style="color:#1E3A8A; font-weight:600;">Low Profit / Low Competition</span> — Niche positioning with optimization potential</div>
    
    <div><span style="color:#7F1D1D; font-weight:600;">Low Profit / High Competition</span> — Low attractiveness with limited upside</div>
    
    </div>
    
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    
    # -------------------------
    # 🚀 HEADER
    # -------------------------
    st.markdown("### Market Entry Opportunities")

    st.caption(
        "Identifies products with strong demand velocity, manageable competition, "
        "and healthy margins — optimal conditions for new market entry."
    )

    # -------------------------
    # 🧠 ENTRY SCORE (TEMPORAL)
    # -------------------------
    entry_df = df.copy()

    entry_df["entry_score"] = (
        entry_df["sales_velocity"] * 0.4 +
        (entry_df["Active Sellers"].max() - entry_df["Active Sellers"]) * 0.3 +
        entry_df["profit_margin"] * 0.3
    )

    # -------------------------
    # 📊 TOP OPPORTUNITIES
    # -------------------------
    top_entry = entry_df.sort_values("entry_score", ascending=False).head(10)

    top_entry["label"] = top_entry["ASIN"] + " | " + top_entry[display_col]

    st.markdown("### Top Entry Opportunities")

    st.dataframe(
        top_entry[[
            "label",
            "sales_velocity",
            "Active Sellers",
            "active_margin"
        ]]
        .rename(columns={
            "label": "Product",
            "sales_velocity": "Demand Speed",
            "Active Sellers": "Competition",
            "active_margin": "Real Margin (%)"
        })
        .style
        .background_gradient(cmap="Greens", subset=["Demand Speed"])
        .background_gradient(cmap="Blues", subset=["Real Margin (%)"])
        .background_gradient(cmap="Oranges", subset=["Competition"])
        .format({
            "Demand Speed": "{:.1f}",
            "Real Margin (%)": "{:.1f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    # -------------------------
    # 🧠 INSIGHT AUTOMÁTICO
    # -------------------------
    if not top_entry.empty:
        best_opportunity = top_entry.iloc[0]

        st.info(
            f"Top opportunity shows strong demand velocity ({best_opportunity['sales_velocity']:.1f}), "
            f"moderate competition ({int(best_opportunity['Active Sellers'])} sellers), "
            f"and solid margins ({best_opportunity['active_margin']:.1f}%)."
        )
    else:
        st.warning("No opportunity data available")
    # -------------------------
    # 🎯 MARKET CONDITION SIGNAL
    # -------------------------
    high_opportunity = entry_df[
        entry_df["entry_score"] > entry_df["entry_score"].quantile(0.75)
    ]

    if len(high_opportunity) > len(df) * 0.3:
        signal = "The market presents multiple entry opportunities with favorable conditions."
    elif len(high_opportunity) > len(df) * 0.1:
        signal = "Selective entry opportunities exist, but require careful positioning."
    else:
        signal = "Entry opportunities are limited — market may be saturated or highly competitive."

    st.markdown("### Market Entry Signal")

    st.markdown(f"""
    <div style="
        padding:14px;
        margin-bottom:10px;
        background:#F0FDF4;
        border-radius:12px;
        border-left:6px solid #16A34A;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    ">

    <span style="color:#166534; font-size:14px;">
    {signal}
    </span>
    
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# TAB 7 - STRATEGY
# -------------------------
with tab5:

    st.markdown("## Business Decisions")

    st.caption(
        "Actionable insights based on current market conditions and portfolio performance"
    )
    col1, col2, col3 = st.columns(3)

    # -------------------------
    # INSIGHTS
    # -------------------------
    st.markdown("## Executive Signals")
    
    col1, col2, col3 = st.columns(3)
    
    # -------------------------
    # 1. 🔥 PROFIT CONCENTRATION
    # -------------------------
    col1.markdown("### Revenue Concentration")
    
    top3_profit = df.sort_values("active_profit", ascending=False).head(3)["active_profit"].sum()
    total_profit = df["active_profit"].sum()
    
    concentration_pct = (top3_profit / total_profit * 100) if total_profit > 0 else 0
    
    if concentration_pct > 60:
        col1.error(
            f"""
    Revenue Concentration Risk

    {concentration_pct:.0f}% of total profit is generated by the top 3 products.
    
    → Action:
    Scale 2–3 mid-performing ASINs with strong margins to reduce dependency on top performers.
    
    → Impact:
    Improves portfolio stability and reduces revenue risk concentration.
    """
        )
    
    elif concentration_pct > 40:
        col1.warning(
            f"""
    Moderate Concentration

    {concentration_pct:.0f}% of profit comes from a limited number of products.
    
    → Action:
    Strengthen secondary products by improving pricing, visibility, and conversion.
    
    → Impact:
    Creates a more balanced revenue distribution and reduces volatility.
    """
        )
    
    else:
        col1.success(
            f"""
    Diversified Portfolio

    Top 3 products represent {concentration_pct:.0f}% of total profit.
    
    → Action:
    Maintain current strategy while selectively scaling top performers.
    
    → Impact:
    Sustainable and resilient portfolio with low dependency risk.
    """
        )

    # -------------------------
    # 2. 💸 PROFIT LEAKAGE
    # -------------------------
    col2.markdown("### Profit Leakage")
    
    loss_products = df[df["active_profit"] < 0]
    loss_pct = (len(loss_products) / len(df) * 100) if len(df) > 0 else 0
    
    if loss_pct > 25:
        col2.error(
            f"""
    Profit Leakage Detected

    {len(loss_products)} products are unprofitable ({loss_pct:.0f}%).
    
    → Action:
    Identify low-performing ASINs and optimize pricing, reduce costs, or discontinue unprofitable listings.
    
    → Impact:
    Improves overall profitability and reallocates capital to high-performing products.
    """
        )
    
    elif loss_pct > 10:
        col2.warning(
            f"""
    Margin Pressure

    {len(loss_products)} products are underperforming ({loss_pct:.0f}%).
    
    → Action:
    Review cost structure, pricing strategy, and advertising efficiency for affected products.
    
    → Impact:
    Increases margin consistency and reduces profit erosion.
    """
        )
    
    else:
        col2.success(
            f"""
    Healthy Margins
    
    Only {len(loss_products)} products are unprofitable ({loss_pct:.0f}%).
    
    → Action:
    Maintain current pricing and cost strategy while monitoring performance.
    
    → Impact:
    Sustains a strong and efficient profit structure.
    """
        )


    # -------------------------
    # 3. 📈 SCALABILITY SIGNAL
    # -------------------------
    col3.markdown("### Scalability")
    
    avg_sales = df["ASIN Sales"].mean()
    avg_sellers = df["Active Sellers"].mean()
    
    if avg_sales > 300 and avg_sellers < 10:
        col3.success(
            f"""
    High Scalability
    
    Strong demand (avg {avg_sales:.0f} sales) with relatively low competition ({avg_sellers:.0f} sellers).
    
    → Action:
    Increase inventory levels and scale advertising to capture additional market share.

    → Impact:
    Accelerates revenue growth and strengthens market position.
    """
        )
    
    elif avg_sales > 300 and avg_sellers > 15:
        col3.warning(
            f"""
    Competitive Market
    
    Strong demand (avg {avg_sales:.0f} sales) but high competition ({avg_sellers:.0f} sellers).
    
    → Action:
    Differentiate through branding, listing optimization, and pricing strategy.
    
    → Impact:
    Improves conversion rate and defends market share in a crowded space.
    """
        )
    
    else:
        col3.info(
            f"""
    Limited Scalability
    
    Moderate demand (avg {avg_sales:.0f} sales) and/or constrained margins.
    
    → Action:
    Focus on niche positioning or optimize margins before scaling.
    
    → Impact:
    Reduces risk and improves efficiency before growth investment.
    """
        )

    # -------------------------
    # 🧠 EXECUTIVE INTERPRETATION (CONSULTOR MODE)
    # -------------------------
    st.markdown("### Executive Interpretation")
    
    # 🎯 PRIORIDAD ESTRATÉGICA (orden importa)
    if concentration_pct > 60:
        title = "High Structural Risk"
        text = "Profit is highly concentrated in a small number of products, creating dependency on top performers and limiting portfolio resilience."
    
    elif loss_pct > 20:
        title = "Profitability Issue"
        text = "A significant portion of the catalog is unprofitable, indicating inefficiencies in pricing, cost structure, or product selection."
    
    elif avg_sales > 300 and avg_sellers < 10:
        title = "Scaling Opportunity"
        text = "The market shows strong demand with manageable competition, creating favorable conditions to scale revenue."
    
    elif avg_sales > 300 and avg_sellers > 15:
        title = "Competitive Pressure"
        text = "Demand is strong but competition is high, limiting scalability and requiring differentiation to sustain growth."
    
    else:
        title = "Balanced Market"
        text = "The market is relatively balanced, with no dominant risks or clear scaling opportunities. Performance depends on execution."

# 🎨 RENDER (CARD EJECUTIVA)
    st.markdown(f"""
    <div style="
    padding:18px;
    background:#FFFFFF;
    border-radius:14px;
    border-left:6px solid #6B7280;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    ">
        
    <div style="
    font-size:16px;
    font-weight:700;
    color:#111827;
    margin-bottom:6px;
    ">
    {title}
    </div>
        
    <div style="
    font-size:14.5px;
    color:#374151;
    line-height:1.5;
    ">
    {text}
    </div>
        
    </div>
    """, unsafe_allow_html=True)

    # -------------------------
    # 📊 MARKET POSITIONING (PRO)
    # -------------------------
    st.markdown("### Market Positioning")
    
    avg_sales = df["ASIN Sales"].mean()
    avg_profit = df["active_profit"].mean()
    avg_sellers = df["Active Sellers"].mean()
    
    signals = []
    
    # Margin compression
    if avg_sales > 300 and avg_profit < 100:
        signals.append((
            "Margin Compression Risk",
            "High demand with low profitability",
            "Indicates strong price competition. Focus on cost reduction or premium positioning.",
            "high"
        ))
    
    # Competitive pressure
    if avg_sales > 300 and avg_sellers > 15:
        signals.append((
            "High Competitive Intensity",
            "Demand is strong but competition is elevated",
            "Sustainable growth requires differentiation, branding, or bundling strategies.",
            "medium"
        ))
    
    # Scale opportunity
    if avg_profit > 200 and avg_sellers < 10:
        signals.append((
            "Scale Opportunity",
            "High profitability with limited competition",
            "Reinvest in inventory and advertising to capture additional market share.",
            "low"
        ))
    
    # Niche efficiency
    if avg_profit > 150 and avg_sales < 200:
        signals.append((
            "Niche Efficiency",
            "Moderate demand with strong margins",
            "Focus on targeted growth and maintain operational efficiency.",
            "low"
        ))

    # 💤 Weak segment
    if avg_sales < 100:
        signals.append((
            "Low ROI Segment",
            "Limited demand across products",
            "Market may not justify further investment.",
            "high"
        ))
    
    # 🎨 PRIORITY COLORS
    priority_colors = {
        "high": "#DC2626",
        "medium": "#F59E0B",
        "low": "#16A34A"
    }

    # -------------------------
    # 🔥 LIMITAR A TOP 2 (MUY PRO)
    # -------------------------
    priority_order = {"high": 0, "medium": 1, "low": 2}
    signals = sorted(signals, key=lambda x: priority_order[x[3]])[:2]
    
    
    # -------------------------
    # RENDER
    # -------------------------
    if signals:
        for title, subtitle, desc, level in signals:
    
            html = f"""
            <div style="
                padding:18px;
                margin-bottom:12px;
                background:#FFFFFF;
                border-radius:14px;
                border-left:6px solid {priority_colors[level]};
                box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
            ">
            
                <div style="
                    font-size:17px;
                    font-weight:700;
                    color:#111827;
                    margin-bottom:6px;
                ">
                    {title}
                </div>
            
                <div style="
                    color:#374151;
                    font-size:14.5px;
                    margin-bottom:6px;
                ">
                    {subtitle}
                </div>
            
                <div style="
                    color:#6B7280;
                    font-size:14px;
                ">
                    {desc}
                </div>
            
            </div>
            """
    
            # 🔥 ESTA LÍNEA FALTABA
            components.html(html, height=130)
    
    else:
        st.info("Market conditions are balanced with no dominant structural risks")
    
    # -------------------------
    # 🧠 INSIGHT CARD (REUSABLE)
    # -------------------------
    def insight_card(text, type_="neutral"):
        
        if type_ == "success":
            bg = "#F0FDF4"
            color = "#166534"
        elif type_ == "warning":
            bg = "#FFFBEB"
            color = "#92400E"
        else:
            bg = "#F9FAFB"
            color = "#111827"
    
        return f"""
        <div style="
            padding:16px;
            background:{bg};
            border-radius:12px;
            border:1px solid #D1D5DB;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
            min-height:90px;
            display:flex;
            align-items:center;
        ">
            <span style="color:{color}; font-size:15.5px; font-weight:500; line-height:1.4;">
                {text}
            </span>
        </div>
        """
    
    # -------------------------
    # 🔥 ROW 1 → Competitive + Portfolio
    # -------------------------
    col1, col2 = st.columns(2)
    
    # ---- Competitive Threat ----
    with col1:
        st.markdown("### Competitive Threat Analysis")
    
        insights = []

        new_products = df[df["is_new"]]
        old_products = df[~df["is_new"]]
        
        if len(new_products) > 0 and len(old_products) > 0:
            avg_new_velocity = new_products["sales_velocity"].mean()
            avg_old_velocity = old_products["sales_velocity"].mean()
        
            if avg_new_velocity > avg_old_velocity:
                insights.append(("warning", "Emerging competitive threat: new entrants are gaining traction and may impact rankings"))
            elif avg_new_velocity < avg_old_velocity:
                insights.append(("success", "Strong market control: existing products dominate new entrants"))
            else:
                insights.append(("info", "Moderate competitive pressure"))
        else:
            insights.append(("info", "Not enough data to evaluate competitive threat"))
        
        for type_, text in insights:
            st.markdown(insight_card(text, type_), unsafe_allow_html=True)
    
    
    # ---- Portfolio Actions ----
    with col2:
        st.markdown("### Portfolio Actions")
    
        insights = []
        low_margin = df[df["active_margin"] < 15]
        high_perf = df[df["active_margin"] > 30]
    
        if len(low_margin) > len(df) * 0.3:
            insights.append(("warning", f"{len(low_margin)} products require margin optimization"))
    
        if len(high_perf) > len(df) * 0.3:
            insights.append(("success", f"{len(high_perf)} products show strong scaling potential"))
    
        if not insights:
            insights.append(("info", "Portfolio performance is balanced"))
    
        for type_, text in insights:
            st.markdown(insight_card(text, type_), unsafe_allow_html=True)
    
    
    # -------------------------
    # 🔥 ROW 2 → Conversion (FULL WIDTH)
    # -------------------------
    st.markdown("### Conversion Performance")
    
    insights = []
    
    high_sales = df["ASIN Sales"] > df["ASIN Sales"].median()
    high_listing = df["listing_score"] > df["listing_score"].median()
    
    high_perf = df[high_sales & high_listing]
    pct = len(high_perf) / len(df) if len(df) > 0 else 0
    
    if pct > 0.3:
        insights.append(("success", f"Strong conversion engine: {pct:.0%} of products perform well"))
    else:
        insights.append(("info", "No dominant conversion pattern"))
    
    for type_, text in insights:
        st.markdown(insight_card(text, type_), unsafe_allow_html=True)
    
    
    # -------------------------
    # 🔥 ROW 3 → 💰 PROFIT ENGINE (FULL WIDTH - FINAL)
    # -------------------------
    st.markdown("### Profit Engine Analysis")
    
    low_margin = df[df["active_margin"] < 15]
    high_margin = df[df["active_margin"] > 30]
    
    low_pct = len(low_margin) / len(df) if len(df) > 0 else 0
    high_pct = len(high_margin) / len(df) if len(df) > 0 else 0
    
    if high_pct > 0.4:
        text = f"Strong profit engine: {high_pct:.0%} of products operate with high margins, supporting scalable and sustainable profitability."
        type_ = "success"
    
    elif low_pct > 0.3:
        text = f"Profitability pressure: {low_pct:.0%} of products have low margins, indicating structural inefficiencies in pricing or cost structure."
        type_ = "warning"
    
    else:
        text = "Balanced profit structure: margins are distributed evenly, with no major risks or strong optimization signals."
        type_ = "info"
    
    st.markdown(insight_card(text, type_), unsafe_allow_html=True)

    # -------------------------
    # CTA CONSULTORIA
    # -------------------------
    
    st.markdown("---")
    
    st.markdown("### Take your results to the next level")
    
    st.write("""
    You've identified key opportunities — but execution is what drives results.
    
    We help Amazon sellers scale profitably with tailored strategies and real-world execution.
    """)
    
    st.link_button("Book a Strategy Call", "mailto:consultora@kpistudio.net")



# -------------------------
# 📄 EXECUTIVE REPORT (PREMIUM FINAL)
# -------------------------
with tab6:

    st.divider()
    st.markdown("## Executive Report")

    st.info("Turn your analysis into a structured market report in one click.")

    if st.button("Generate PDF Report"):

        today = pd.Timestamp.now().strftime("%Y-%m-%d")

        # -------------------------
        # 📊 DATA
        # -------------------------
        avg_profit_val = avg_profit
        avg_margin_val = avg_margin
        avg_sellers_val = avg_sellers
        low_pct_val = low_pct
        high_pct_val = high_pct

        # -------------------------
        # 🧠 SMART INSIGHT
        # -------------------------
        if high_pct_val > 0.6:
            strategy_text = "The market shows strong profitability conditions with a high concentration of scalable products. This indicates a favorable environment for expansion and revenue growth."
        elif high_pct_val > 0.3:
            strategy_text = "The market presents moderate scalability opportunities. Strategic optimization in pricing and cost structure could unlock additional growth."
        else:
            strategy_text = "The market shows limited scalability. Focus should be placed on cost optimization and selective product positioning."

        # -------------------------
        # 🖼️ BANNER BASE64
        # -------------------------
        with open("banner.png", "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()

        banner_base64 = f"data:image/png;base64,{encoded}"

        # -------------------------
        # 🎨 HTML
        # -------------------------
        html = f"""
        <html>
        <head>
        <style>

        body {{
            font-family: Arial, sans-serif;
            margin:0;
            background:#F5F7FA;
        }}

        .banner {{
            width:100%;
        }}

        .container {{
            padding:30px;
        }}

        .title {{
            font-size:28px;
            font-weight:700;
            color:#0F172A;
            margin-bottom:5px;
        }}

        .subtitle {{
            font-size:14px;
            color:#64748B;
            margin-bottom:15px;
        }}

        .gold-line {{
            width:100%;
            height:4px;
            background:#D4AF37;
            margin-bottom:20px;
        }}

        .date {{
            font-size:13px;
            color:#6B7280;
            margin-bottom:15px;
        }}

        /* KPI ROW */
        .kpi-row {{
            display:table;
            width:100%;
            background:#0B1A2B;
            border-radius:16px;
            overflow:hidden;
            margin-bottom:30px;
        }}

        .kpi {{
            display:table-cell;
            text-align:center;
            padding:25px 10px;
            color:#D4AF37;
            border-right:1px solid #D4AF37;
        }}

        .kpi:last-child {{
            border-right:none;
        }}

        .kpi h2 {{
            margin:0;
            font-size:36px;
            font-weight:700;
        }}

        .kpi p {{
            margin:0;
            font-size:12px;
            letter-spacing:1px;
            opacity:0.9;
        }}

        /* CARDS */
        .card {{
            background:white;
            border-radius:14px;
            padding:18px;
            margin-bottom:14px;
            box-shadow:0 4px 10px rgba(0,0,0,0.05);
            border-left:6px solid;
        }}

        .card-title {{
            font-weight:700;
            margin-bottom:6px;
        }}

        .blue {{ border-color:#3B82F6; }}
        .cyan {{ border-color:#06B6D4; }}
        .green {{ border-color:#22C55E; }}
        .orange {{ border-color:#F97316; }}

        /* STRATEGY */
        .strategy {{
            background:#0F172A;
            color:white;
            padding:20px;
            border-radius:14px;
            margin-top:20px;
        }}

        /* FOOTER PRO */
        .footer {{
            margin-top:30px;
            font-size:12px;
            color:#6B7280;
            text-align:center;
            border-top:1px solid #E5E7EB;
            padding-top:12px;
        }}

        </style>
        </head>

        <body>

        <img src="{banner_base64}" class="banner">

        <div class="container">

        <div class="title">Executive Summary</div>
        <div class="subtitle">Market Intelligence Report</div>
        <div class="gold-line"></div>

        <div class="date">Date: {today}</div>

        <!-- KPI -->
        <div class="kpi-row">
            <div class="kpi">
                <h2>${avg_profit_val:,.0f}</h2>
                <p>AVG. PROFIT</p>
            </div>
            <div class="kpi">
                <h2>{avg_margin_val:.1f}%</h2>
                <p>MARGIN</p>
            </div>
            <div class="kpi">
                <h2>{avg_sellers_val:.0f}</h2>
                <p>SELLERS / LISTING</p>
            </div>
            <div class="kpi">
                <h2>{low_pct_val:.0%}</h2>
                <p>LOW RISK</p>
            </div>
            <div class="kpi">
                <h2>{high_pct_val:.0%}</h2>
                <p>SCALING OPPS.</p>
            </div>
        </div>

        <!-- CONTENT -->
        <div class="card blue">
            <div class="card-title">Profitability Overview</div>
            Average profit is ${avg_profit_val:,.0f} with a margin of {avg_margin_val:.1f}%.
        </div>

        <div class="card cyan">
            <div class="card-title">Competitive Landscape</div>
            Average competition: {avg_sellers_val:.0f} sellers per listing.
        </div>

        <div class="card green">
            <div class="card-title">Risk Signals</div>
            {len(low_margin)} products ({low_pct_val:.0%}) operate under low margin conditions.
        </div>

        <div class="card orange">
            <div class="card-title">Opportunities</div>
            {len(high_margin)} products ({high_pct_val:.0%}) show strong margin performance.
        </div>

        <!-- STRATEGY -->
        <div class="strategy">
            <b>Strategic Insight</b><br><br>
            {strategy_text}
        </div>

        <!-- CTA -->
        <div style="margin-top:20px; font-size:14px;">
        Want deeper insights and a custom strategy?<br>
        <b>consultora@kpistudio.net</b>
        </div>

        <!-- FOOTER MEJORADO -->
        <div class="footer">
            <b>KPI Studio</b> &copy; {today} &mdash; Confidential Report<br>
            <span style="font-size:11px; color:#9CA3AF;">
                Profit reflects real profitability after all costs.
            </span>
        </div>

        </div>
        </body>
        </html>
        """

        # -------------------------
        # PDF
        # -------------------------
        config = pdfkit.configuration(
            wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
        )

        options = {
            "enable-local-file-access": "",
            "quiet": ""
        }

        pdf_bytes = pdfkit.from_string(
            html,
            False,
            configuration=config,
            options=options
        )

        st.success("PDF report generated successfully")

        st.download_button(
            "Download PDF",
            pdf_bytes,
            file_name=f"market_report_{today}.pdf",
            mime="application/pdf"
        )


# In[ ]:





# In[ ]:





# In[ ]:





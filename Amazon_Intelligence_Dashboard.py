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
import plotly.graph_objects as go
import textwrap



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

    if uploaded_file is not None:

        # -------------------------
        # 📥 LOAD FILE
        # -------------------------
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        elif uploaded_file.name.endswith(".xlsx"):
            excel_file = pd.ExcelFile(uploaded_file)
            sheet = st.sidebar.selectbox(
                "Sheet",
                excel_file.sheet_names
            )
            df = pd.read_excel(
                uploaded_file,
                sheet_name=sheet
            )

        # -------------------------
        # 🧹 CLEANING
        # -------------------------
        df.columns = df.columns.str.strip()

        rename_map = {
            "Price  US$": "Price",
            "Price US$": "Price",
            "ASIN Revenue": "Revenue",
            "Fees  US$": "Fees",
            "Fees US$": "Fees"
        }

        df = df.rename(columns=rename_map)

        def clean_numeric(x):
            try:
                if pd.isna(x):
                    return 0.0

                x = str(x).strip()

                x = (
                    x.replace("US$", "")
                    .replace("$", "")
                    .replace("€", "")
                    .replace("£", "")
                    .replace(" ", "")
                )

                if not x:
                    return 0.0

                # Punto y coma presentes
                if "." in x and "," in x:
                    last_dot = x.rfind(".")
                    last_comma = x.rfind(",")

                    # Europeo: 88.805,96
                    if last_comma > last_dot:
                        x = (
                            x.replace(".", "")
                            .replace(",", ".")
                        )

                    # US: 88,805.96
                    else:
                        x = x.replace(",", "")

                # Solo coma
                elif "," in x:
                    decimal_places = len(
                        x.split(",")[-1]
                    )

                    # Europeo decimal: 11,25
                    if decimal_places in (1, 2):
                        x = x.replace(",", ".")

                    # US miles: 1,234
                    else:
                        x = x.replace(",", "")

                # Solo punto
                elif "." in x:
                    parts = x.split(".")

                    # Europeo miles: 1.234
                    if (
                        len(parts) > 1
                        and all(
                            len(part) == 3
                            for part in parts[1:]
                        )
                        and len(parts[0]) <= 3
                    ):
                        x = x.replace(".", "")

                return float(x)

            except (ValueError, TypeError):
                return 0.0

        # -------------------------
        # APLICAR CLEANING
        # -------------------------
        numeric_columns = [
            "Revenue",
            "Fees",
            "Price",
            "ASIN Sales",
            "Parent Level Sales"
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(
                    clean_numeric
                )

        # -------------------------
        # 🚨 VALIDACIÓN
        # -------------------------
        required_cols = [
            "Revenue",
            "Fees",
            "ASIN Sales"
        ]

        missing = [
            col
            for col in required_cols
            if col not in df.columns
        ]

        if missing:
            st.error(
                f"Missing columns: {missing}"
            )
            st.stop()

        # -------------------------
        # DEBUG TEMPORAL
        # -------------------------
        st.write(
            "Columns:",
            df.columns.tolist()
        )

        st.write(
            df[
                ["Price", "Revenue", "Fees"]
            ].head()
        )

        # -------------------------
        # SAVE STATE
        # -------------------------
        with st.spinner(
            "Processing data..."
        ):
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

    col1, col2 = st.sidebar.columns(2)

    if col1.button("Back"):
         st.session_state.step = 1

    if col2.button("Run Analysis"):
        st.session_state.cogs = cogs
        st.session_state.shipping = shipping
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

    st.session_state.shipping = shipping
# -------------------------
# FEATURES
# -------------------------
df["total_fees"] = df["Fees"] * df["ASIN Sales"]
df["estimated_profit"] = df["Revenue"] - df["total_fees"]
df["profit_margin"] = (df["estimated_profit"] / df["Revenue"]) * 100
# -------------------------
# 📣 VARIABLES FOR ADVERTISING DEPENDENCY
# -------------------------

# Preparar variables numéricas
df["Ratings"] = pd.to_numeric(
    df["Ratings"]
    .astype(str)
    .str.replace(",", ".", regex=False),
    errors="coerce"
).fillna(0)

for col in [
    "Review Count",
    "Images",
    "Review velocity",
    "Active Sellers",
    "BSR"
]:
    df[col] = pd.to_numeric(
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False),
        errors="coerce"
    ).fillna(0)


# Listing Strength necesario para el score
df["review_power"] = (
    np.sqrt(df["Review Count"].clip(lower=0))
    * df["Ratings"]
)

df["listing_score"] = (
    df["Images"]
    + df["review_power"]
)


# -------------------------
# 🛡️ COMMERCIAL TRUST SIGNALS
# -------------------------

# Helium 10 devuelve el nombre del vendedor que posee la Buy Box,
# no un valor Yes/No.
buybox_text = (
    df["Buy Box"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

invalid_buybox = {
    "",
    "nan",
    "none",
    "null",
    "-",
    "n/a"
}

# 1 = existe un vendedor identificado con Buy Box
# 0 = el campo está vacío o no contiene información válida
df["buybox_flag"] = (
    ~buybox_text.isin(invalid_buybox)
).astype(int)

# Best Seller sí se interpreta como una variable booleana
bestseller_text = (
    df["Best Seller"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

df["bestseller_flag"] = (
    bestseller_text.isin(
        ["yes", "true", "1", "si", "sí"]
    )
).astype(int)

# ¿Buy Box realmente diferencia a los productos?
buybox_is_informative = (
    df["buybox_flag"].nunique(dropna=False) > 1
)


# -------------------------
# NORMALIZACIÓN RELATIVA
# -------------------------

def normalize_relative(
    series,
    log_transform=False,
    zero_is_missing=False
):
    """
    Normaliza una variable entre 0 y 1 dentro del mercado.
    Si no existe variación, devuelve un valor neutral de 0.5.
    """

    values = pd.to_numeric(series, errors="coerce")

    if zero_is_missing:
        values = values.replace(0, np.nan)

    values = values.clip(lower=0)

    if log_transform:
        values = np.log1p(values)

    min_value = values.min()
    max_value = values.max()

    if (
        pd.isna(min_value)
        or pd.isna(max_value)
        or max_value == min_value
    ):
        return pd.Series(0.5, index=series.index)

    return (
        (values - min_value)
        / (max_value - min_value)
    ).clip(0, 1).fillna(0.5)


# -------------------------
# 📣 ADVERTISING DEPENDENCY COMPONENTS
# Cuanto más alto, mayor dependencia publicitaria estimada
# -------------------------

# BSR alto = peor posición relativa = mayor dependencia
df["ad_dep_bsr"] = normalize_relative(
    df["BSR"],
    log_transform=True,
    zero_is_missing=True
)

# Mayor Review Velocity = mayor tracción = menor dependencia
df["ad_dep_review_velocity"] = (
    1
    - normalize_relative(
        df["Review velocity"],
        log_transform=True
    )
)

# Listing más fuerte = menor dependencia
df["ad_dep_listing"] = (
    1
    - normalize_relative(df["listing_score"])
)

# Tener Buy Box reduce la dependencia
df["ad_dep_buybox"] = (
    1 - df["buybox_flag"]
)

# Tener Best Seller reduce la dependencia
df["ad_dep_bestseller"] = (
    1 - df["bestseller_flag"]
)

# Active Sellers solo tendrá peso si varía lo suficiente
df["ad_dep_sellers"] = normalize_relative(
    df["Active Sellers"],
    log_transform=True
)


# -------------------------
# ACTIVE SELLERS ADAPTATIVO
# -------------------------

seller_values = pd.to_numeric(
    df["Active Sellers"],
    errors="coerce"
).dropna()

seller_unique = seller_values.nunique()

seller_std = (
    seller_values.std()
    if len(seller_values) > 1
    else 0
)

seller_range = (
    seller_values.max() - seller_values.min()
    if not seller_values.empty
    else 0
)

sellers_informative = (
    seller_unique >= 3
    and seller_std >= 0.75
    and seller_range >= 2
)

# -------------------------------------------------------
# KPI Studio Methodology
# Advertising Dependency v2.0
#
# Variables that do not differentiate products within the
# current market automatically lose their assigned weight.
# The remaining weights are proportionally redistributed
# to preserve the full explanatory power of the score.
# -------------------------------------------------------
# -------------------------
# PESOS DEL MODELO
# -------------------------

ad_weights = {
    "ad_dep_bsr": 0.35,
    "ad_dep_review_velocity": 0.25,
    "ad_dep_listing": 0.20,
    "ad_dep_buybox": 0.05,
    "ad_dep_bestseller": 0.05,
    "ad_dep_sellers": 0.10
}

bestseller_is_informative = (
    df["bestseller_flag"].nunique(dropna=False) > 1
)

if not buybox_is_informative:
    ad_weights["ad_dep_buybox"] = 0.0

if not bestseller_is_informative:
    ad_weights["ad_dep_bestseller"] = 0.0
# Si Active Sellers no discrimina, su peso pasa a cero
if not sellers_informative:
    ad_weights["ad_dep_sellers"] = 0.0

# Redistribuir proporcionalmente para que sumen 1
# Redistribuir proporcionalmente para que sumen 1
total_ad_weight = sum(ad_weights.values())

# Validación de seguridad
if total_ad_weight > 0:

    ad_weights = {
        variable: weight / total_ad_weight
        for variable, weight in ad_weights.items()
    }

else:

    # Fallback extremadamente raro:
    # si ninguna variable aporta información,
    # utilizar únicamente las señales estructurales.
    ad_weights = {
        "ad_dep_bsr": 0.45,
        "ad_dep_review_velocity": 0.30,
        "ad_dep_listing": 0.25,
        "ad_dep_buybox": 0.00,
        "ad_dep_bestseller": 0.00,
        "ad_dep_sellers": 0.00
    }


# -------------------------
# 📊 ADVERTISING DEPENDENCY SCORE
# -------------------------

df["advertising_dependency_score"] = (
    sum(
        df[variable] * weight
        for variable, weight in ad_weights.items()
    )
    * 100
).clip(0, 100)

df["advertising_dependency_level"] = pd.cut(
    df["advertising_dependency_score"],
    bins=[-1, 20, 40, 60, 80, 100],
    labels=[
        "Very Low",
        "Low",
        "Moderate",
        "High",
        "Very High"
    ]
)


# -------------------------
# 📊 ESTIMATED TACOS BY ASIN
# -------------------------

# Referencia fija utilizada únicamente por el modelo de mercado
MODEL_BASE_TACOS = 15.0

base_tacos = MODEL_BASE_TACOS

# El escenario seleccionado sigue funcionando como referencia.
# Con un base TACOS de 15%:
# Score 0   → 8.25%
# Score 50  → 19.1%
# Score 100 → 30.0%

minimum_tacos = max(5.0, base_tacos * 0.55)
maximum_tacos = min(45.0, base_tacos * 2.00)

df["estimated_tacos"] = (
    minimum_tacos
    + (
        maximum_tacos - minimum_tacos
    )
    * (
        df["advertising_dependency_score"] / 100
    )
).clip(lower=5, upper=45)


# -------------------------
# 💰 USER COSTS → REAL PROFIT
# -------------------------

use_real_profit = (
    (cogs > 0)
    or (shipping > 0)
    or (base_tacos > 0)
)

df["cogs_cost"] = (
    cogs * df["ASIN Sales"]
)

df["shipping_cost"] = (
    shipping * df["ASIN Sales"]
)

# Cada ASIN utiliza su propio TACOS estimado
df["ads_cost"] = (
    df["Revenue"]
    * (
        df["estimated_tacos"]
        / 100
    )
)

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
# 🛡️ TRUST SCORE
# -------------------------

if buybox_is_informative:
    # Buy Box diferencia efectivamente a los ASINs
    df["trust_score"] = (
        df["buybox_flag"] * 0.60
        + df["bestseller_flag"] * 0.40
    )
else:
    # Si Buy Box es igual para todos, no aporta información comparativa
    df["trust_score"] = (
        df["bestseller_flag"].astype(float)
    )

# -------------------------
# 🏆 TRUE MARKET POWER (ADAPTIVE)
# -------------------------

# Trust aporta información solo si realmente diferencia productos.
trust_is_informative = (
    df["trust_score"].nunique(dropna=False) > 1
)

if trust_is_informative:

    df["market_power_score"] = (
        df["authority_score"] * 0.50 +
        df["momentum_score"] * 0.30 +
        df["trust_score"] * 0.20
    )

else:

    # -------------------------------------------------------
    # Adaptive Market Power Weighting
    #
    # If Trust Signals (Buy Box / Best Seller) do not provide
    # any discriminatory information within the current market,
    # their contribution is removed and the 20% weight is
    # proportionally redistributed between Authority and
    # Momentum to preserve the full explanatory power of the
    # Market Power Score.
    # -------------------------------------------------------
    
    df["market_power_score"] = (
        df["authority_score"] * 0.625 +
        df["momentum_score"] * 0.375
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
# 📈 DEMAND SCORE — MARKET LEVEL
# -------------------------

# Parámetros iniciales ajustables
SALES_TARGET = 1000
MIN_RELEVANT_SALES = 100
VELOCITY_TARGET = 100

median_sales = df["ASIN Sales"].median()
median_sales_velocity = df["sales_velocity"].median()

# 1. Nivel de ventas del mercado
median_sales_score = np.clip(
    np.log1p(median_sales) / np.log1p(SALES_TARGET) * 100,
    0,
    100
)

# 2. Amplitud de demanda:
# porcentaje de productos con al menos 100 ventas mensuales
demand_breadth_score = (
    (df["ASIN Sales"] >= MIN_RELEVANT_SALES).mean() * 100
)

# 3. Velocidad de demanda
demand_velocity_score = np.clip(
    np.log1p(median_sales_velocity) / np.log1p(VELOCITY_TARGET) * 100,
    0,
    100
)

# Score final
demand_score = (
    median_sales_score * 0.40
    + demand_breadth_score * 0.35
    + demand_velocity_score * 0.25
)

demand_score = float(np.clip(demand_score, 0, 100))

# Nivel interpretativo
if demand_score >= 80:
    demand_level = "Very Strong"
elif demand_score >= 65:
    demand_level = "Strong"
elif demand_score >= 50:
    demand_level = "Moderate"
elif demand_score >= 35:
    demand_level = "Weak"
else:
    demand_level = "Very Weak"
# -------------------------
# 💰 PROFITABILITY SCORE — MARKET LEVEL
# -------------------------

MARGIN_TARGET = 30
PROFIT_TARGET = 5000

median_real_margin = df["active_margin"].median()
median_real_profit = df["active_profit"].median()

profitable_product_share = (
    (df["active_profit"] > 0).mean() * 100
)

margin_score = np.clip(
    median_real_margin / MARGIN_TARGET * 100,
    0,
    100
)

profitable_share_score = profitable_product_share

profit_score = np.clip(
    np.log1p(max(median_real_profit, 0))
    / np.log1p(PROFIT_TARGET)
    * 100,
    0,
    100
)

profitability_score = (
    margin_score * 0.50
    + profitable_share_score * 0.30
    + profit_score * 0.20
)

profitability_score = float(
    np.clip(profitability_score, 0, 100)
)

if profitability_score >= 80:
    profitability_level = "Very Strong"
elif profitability_score >= 65:
    profitability_level = "Strong"
elif profitability_score >= 50:
    profitability_level = "Moderate"
elif profitability_score >= 35:
    profitability_level = "Weak"
else:
    profitability_level = "Very Weak"

# -------------------------
# 🏆 COMPETITION SCORE — MARKET LEVEL
# -------------------------

REVIEW_TARGET = 500

median_reviews = df["Review Count"].median()

review_barrier_score = 100 - np.clip(
    np.log1p(median_reviews) / np.log1p(REVIEW_TARGET) * 100,
    0,
    100
)

market_power_top3 = (
    df.nlargest(3, "market_power_score")["market_power_score"].sum()
)

market_power_total = df["market_power_score"].sum()

market_concentration = (
    (market_power_top3 / market_power_total) * 100
    if market_power_total > 0 else 0
)

market_concentration_score = 100 - market_concentration

listing_barrier = df["listing_score"].median()

listing_barrier_score = 100 - np.clip(
    listing_barrier,
    0,
    100
)

competition_score = (
    review_barrier_score * 0.40 +
    market_concentration_score * 0.35 +
    listing_barrier_score * 0.25
)

competition_score = float(
    np.clip(competition_score,0,100)
)

if competition_score >= 80:
    competition_level = "Very Easy"

elif competition_score >= 65:
    competition_level = "Accessible"

elif competition_score >= 50:
    competition_level = "Moderate"

elif competition_score >= 35:
    competition_level = "Difficult"

else:
    competition_level = "Highly Competitive"
# -------------------------
# ⭐ LISTING OPPORTUNITY SCORE — MARKET LEVEL
# -------------------------

# Referencias del mercado
median_sales_listing = df["ASIN Sales"].median()
median_listing_score = df["listing_score"].median()

# Productos con demanda alta y listing débil
high_demand_weak_listing = (
    (df["ASIN Sales"] >= median_sales_listing)
    & (df["listing_score"] < median_listing_score)
)

high_demand_weak_listing_share = (
    high_demand_weak_listing.mean() * 100
)

# Brecha de calidad del listing
listing_q25 = df["listing_score"].quantile(0.25)
listing_q75 = df["listing_score"].quantile(0.75)

if listing_q75 > 0:
    listing_gap_score = np.clip(
        ((listing_q75 - listing_q25) / listing_q75) * 100,
        0,
        100
    )
else:
    listing_gap_score = 0

# Penalización si todos los listings son muy fuertes
listing_strength_penalty = np.clip(
    median_listing_score / 100 * 100,
    0,
    100
)

listing_opportunity_score = (
    high_demand_weak_listing_share * 0.60
    + listing_gap_score * 0.40
)

listing_opportunity_score = float(
    np.clip(
        listing_opportunity_score
        - listing_strength_penalty * 0.10,
        0,
        100
    )
)

if listing_opportunity_score >= 80:
    listing_opportunity_level = "Very High"
elif listing_opportunity_score >= 65:
    listing_opportunity_level = "High"
elif listing_opportunity_score >= 50:
    listing_opportunity_level = "Moderate"
elif listing_opportunity_score >= 35:
    listing_opportunity_level = "Low"
else:
    listing_opportunity_level = "Very Low"

# -------------------------
# 📣 ADVERTISING SCORE — MARKET LEVEL
# -------------------------

market_avg_ad_dependency = df["advertising_dependency_score"].mean()

low_risk_ad_share = (
    df["advertising_dependency_level"]
    .astype(str)
    .isin(["Very Low", "Low", "Moderate"])
    .mean()
    * 100
)

advertising_score = (
    (100 - market_avg_ad_dependency) * 0.70
    + low_risk_ad_share * 0.30
)

advertising_score = float(
    np.clip(advertising_score, 0, 100)
)

if advertising_score >= 80:
    advertising_level = "Very Strong"
elif advertising_score >= 65:
    advertising_level = "Strong"
elif advertising_score >= 50:
    advertising_level = "Moderate"
elif advertising_score >= 35:
    advertising_level = "Weak"
else:
    advertising_level = "Very Weak"
# -------------------------
# ⭐ MARKET OPPORTUNITY SCORE — MARKET LEVEL
# -------------------------

market_opportunity_score = (
    demand_score * 0.25
    + profitability_score * 0.25
    + competition_score * 0.20
    + advertising_score * 0.15
    + listing_opportunity_score * 0.15
)

market_opportunity_score = float(
    np.clip(market_opportunity_score, 0, 100)
)

if market_opportunity_score >= 80:
    market_opportunity_level = "Excellent Opportunity"
elif market_opportunity_score >= 65:
    market_opportunity_level = "Strong Opportunity"
elif market_opportunity_score >= 50:
    market_opportunity_level = "Requires Validation"
elif market_opportunity_score >= 35:
    market_opportunity_level = "High-Risk Opportunity"
else:
    market_opportunity_level = "Low Attractiveness"

# -------------------------
# 🧠 EXECUTIVE RECOMMENDATION ENGINE
# -------------------------

strengths = []
risks = []
actions = []

# -------------------------
# DEMAND
# -------------------------
if demand_score >= 80:
    strengths.append("Very strong market demand.")
elif demand_score >= 65:
    strengths.append("Strong and broadly distributed demand.")
elif demand_score < 35:
    risks.append("Weak market demand.")
    actions.append("Validate search volume and demand consistency before entering.")

# -------------------------
# PROFITABILITY
# -------------------------
if profitability_score >= 80:
    strengths.append("Strong projected profitability after estimated costs.")
elif profitability_score >= 65:
    strengths.append("Healthy projected margins and profit potential.")
elif profitability_score < 50:
    risks.append("Projected profitability is limited or uneven.")
    actions.append("Review pricing, COGS, shipping and advertising assumptions.")

# -------------------------
# COMPETITION
# Un score alto significa competencia más manejable.
# -------------------------
if competition_score >= 80:
    strengths.append("Competitive barriers appear relatively low.")
elif competition_score >= 65:
    strengths.append("Competition appears manageable.")
elif competition_score < 50:
    risks.append("The market presents significant competitive barriers.")
    actions.append("Identify a clear differentiation strategy before launch.")

# -------------------------
# ADVERTISING
# Un score alto significa menor riesgo publicitario.
# -------------------------
if advertising_score >= 80:
    strengths.append("Low estimated dependence on advertising.")
elif advertising_score >= 65:
    strengths.append("Advertising dependency appears manageable.")
elif advertising_score < 50:
    risks.append("Advertising dependency is a relevant risk.")
    actions.append("Test profitability under a higher TACOS scenario.")

# -------------------------
# LISTING OPPORTUNITY
# -------------------------
if listing_opportunity_score >= 80:
    strengths.append("Strong opportunity to outperform existing listings.")
elif listing_opportunity_score >= 65:
    strengths.append("Visible listing differentiation opportunities.")
elif listing_opportunity_score < 40:
    risks.append("Limited listing differentiation opportunities.")
    actions.append("Strengthen product positioning beyond listing optimization.")

# -------------------------
# FINAL RECOMMENDATION
# -------------------------
if market_opportunity_score >= 80:
    executive_recommendation = (
        "The market presents strong conditions for entry. "
        "Proceed with supplier validation, product differentiation and launch planning."
    )

elif market_opportunity_score >= 65:
    executive_recommendation = (
        "The market appears attractive, although selected risks should be validated "
        "before committing inventory."
    )

elif market_opportunity_score >= 50:
    executive_recommendation = (
        "The market requires further validation. "
        "Do not proceed based on demand alone; review the identified risks and test conservative scenarios."
    )

elif market_opportunity_score >= 35:
    executive_recommendation = (
        "The market currently presents elevated risk. "
        "Entry would require a strong competitive advantage and tighter cost control."
    )

else:
    executive_recommendation = (
        "The market shows low attractiveness under the current assumptions. "
        "Consider evaluating alternative products or niches."
    )

# Evitar tarjetas vacías
if not strengths:
    strengths.append("No dominant structural strengths were identified.")

if not risks:
    risks.append("No critical risks were identified under the current assumptions.")

if not actions:
    actions.append("Continue validating suppliers, costs and market assumptions.")

# -------------------------
# 🎯 SIDEBAR (SaaS PRO)
# -------------------------
with st.sidebar.expander("Market Strategy", expanded=False):

    preset = st.radio(
        "Choose your market analysis objective",
        [
            "All Products",
            "Market Leaders",
            "High Profitability",
            "Low Competitive",
            "⚙️ Custom Filters"
        ],
        index=0
    )

# -------------------------
# 🧠 DEFAULT VALUES
# -------------------------

if preset == "All Products":
    min_profit = float("-inf")
    min_sales = 0
    min_margin = float("-inf")
    strategy = "All"
elif preset == "Market Leaders":
    min_profit = df["active_profit"].median()
    min_sales = df["ASIN Sales"].median()
    min_margin = 25
    strategy = "Balanced"

elif preset == "High Profitability":
    min_profit = df["active_profit"].quantile(0.75)
    min_sales = 0
    min_margin = 20
    strategy = "High Profit"

elif preset == "Low Competitive":
    min_profit = float("-inf")
    min_sales = 0
    min_margin = float("-inf")
    strategy = "Low Competition"

elif preset == "High Demand Products":
    min_profit = float("-inf")
    min_sales = df["ASIN Sales"].quantile(0.75)
    min_margin = float("-inf")
    strategy = "High Demand"

elif preset == "⚙️ Custom Filters":
    strategy = "All"

    st.sidebar.markdown("### Custom Market Filters")

    # acá sigue tu bloque actual de filtros avanzados

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
        min_profit = df["active_profit"].quantile(0.25)
    elif profit_preset == "Medium":
        min_profit = df["active_profit"].quantile(0.5)
    elif profit_preset == "High":
        min_profit = df["active_profit"].quantile(0.75)
    else:
        min_profit = 0    # Solo para mostrar en el widget
    
    min_profit = st.sidebar.number_input(
        "Custom value",
        value=float(min_profit),
        step=10.0
    )
    # "Any" debe permitir profits negativos
    if profit_preset == "Any":
        min_profit = float("-inf")    
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
        min_margin = 0      # Solo para mostrar en el widget
    
    min_margin = st.sidebar.number_input(
        "Custom value",
        value=int(min_margin),
        step=1
    )
    
    # Si eligió "Any", internamente no filtrar por margen
    if margin_preset == "Any":
        min_margin = float("-inf")

# -------------------------
# 💡 CONTEXTO
# -------------------------
if preset == "⚙️ Custom Filters":
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
    sales_median = df["ASIN Sales"].median()

    if strategy == "High Profit":

        df = df[
            df["active_profit"] >= profit_median
        ]

    elif strategy == "Low Competition":

        df = df[
            df["Active Sellers"] <= competition_median
        ]

    elif strategy == "High Demand":

        df = df[
            df["ASIN Sales"] >= sales_median
        ]

    elif strategy == "Balanced":

        df = df[
            (df["active_profit"] >= profit_median) &
            (df["Active Sellers"] <= competition_median)
        ]

# -------------------------
# 🚨 FALLBACK AUTOMÁTICO
# -------------------------
if df.empty and preset != "All":

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

loss_products = (
    df_original[df_original["active_profit"] < 0]
    .sort_values("active_profit")
)
top_opportunities = df.sort_values("opportunity_score", ascending=False).head(10)
top_listing = df.sort_values("listing_score", ascending=False).head(10)
top_sales = df.sort_values("ASIN Sales", ascending=False).head(10)
top_dominance = df.sort_values("market_dominance", ascending=False).head(10)


# -------------------------
# HEADER
# -------------------------
st.html("""
<div style="text-align:center; margin-bottom:10px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="180">
</div>

<div style="text-align:center; margin-bottom:22px;">

    <div style="
        font-size:40px;
        font-weight:700;
        color:#1F3B63;
        margin-bottom:8px;
    ">
        KPI Studio Intelligence Engine
    </div>

    <div style="
        font-size:18px;
        color:#475569;
        margin-bottom:8px;
    ">
        AI-Powered Market Intelligence for Amazon FBA
    </div>

    <div style="
        display:inline-block;
        padding:6px 14px;
        background:#FFF7ED;
        border:1px solid #FED7AA;
        border-radius:999px;
        font-size:13px;
        font-weight:600;
        color:#C2410C;
    ">
        Version 1.0 • Decision Intelligence Platform
    </div>

</div>
""")
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
# -------------------------
# ⭐ MARKET OPPORTUNITY SCORE — SUMMARY
# -------------------------

st.markdown(
    "<div style='height:35px;'></div>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        font-size:30px;
        font-weight:600;
        color:#1F3B63;
        margin-bottom:8px;
    ">
        Market Opportunity
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        font-size:16px;
        font-weight:600;
        color:#4B5563;
        margin-bottom:20px;
    ">
        Overall market attractiveness based on demand, profitability,
        competition, advertising dependency, and listing opportunities.
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 📊 DECISION PROFILE
# =====================================================

st.markdown("## Decision Profile")

st.caption(
    "Visual representation of the five dimensions used to calculate "
    "the KPI Studio Market Opportunity Score."
)

# -------------------------
# RADAR DATA
# -------------------------

categories = [
    "Demand",
    "Profitability",
    "Competition",
    "Advertising",
    "Listing"
]

values = [
    demand_score,
    profitability_score,
    competition_score,
    advertising_score,
    listing_opportunity_score
]

# Cerrar el radar
radar_categories = categories + [categories[0]]
radar_values = values + [values[0]]

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=radar_values,
        theta=radar_categories,
        fill="toself",
        fillcolor="rgba(31, 59, 99, 0.16)",
        line=dict(
            color="#1F3B63",
            width=3
        ),
        marker=dict(
            size=7,
            color="#1F3B63"
        ),
        hovertemplate=(
            "<b>%{theta}</b><br>"
            "Score: %{r:.1f} / 100"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    polar=dict(
        bgcolor="#FFFFFF",
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            tickvals=[0, 20, 40, 60, 80, 100],
            tickfont=dict(
                size=10,
                color="#64748B"
            ),
            gridcolor="#DCE5F0",
            linecolor="#CBD5E1"
        ),
        angularaxis=dict(
            tickfont=dict(
                size=12,
                color="#1F3B63"
            ),
            gridcolor="#CBD5E1",
            linecolor="#CBD5E1"
        )
    ),
    showlegend=False,
    height=440,
    margin=dict(
        l=30,
        r=30,
        t=25,
        b=25
    ),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF"
)

# -------------------------
# NIVEL CON INDICADOR VISUAL
# -------------------------

def level_indicator(level):
    level_text = str(level).lower()

    if "very strong" in level_text or level_text == "strong":
        return "🟢"
    elif (
        "moderate" in level_text
        or "accessible" in level_text
        or "requires validation" in level_text
    ):
        return "🟡"
    else:
        return "🔴"


# -------------------------
# LAYOUT PRINCIPAL
# -------------------------

left, right = st.columns([1.1, 1], gap="medium")

with left:

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )

with right:

    # -------------------------
    # MARKET OPPORTUNITY CARD
    # -------------------------

    st.markdown(
        f"""
<div style="
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:16px;
    padding:18px;
    text-align:center;
    margin-bottom:14px;
    box-sizing:border-box;
">

<div style="
    font-size:17px;
    color:#64748B;
    font-weight:600;
">
    Market Opportunity Score
</div>

<div style="
    font-size:46px;
    font-weight:700;
    color:#1F3B63;
    margin-top:6px;
    line-height:1.15;
">
    {market_opportunity_score:.0f}
    <span style="
        font-size:22px;
        color:#94A3B8;
        font-weight:600;
    ">
        / 100
    </span>
</div>

<div style="
    display:inline-block;
    margin-top:10px;
    padding:6px 15px;
    background:#FEF3C7;
    color:#92400E;
    border:1px solid #FDE68A;
    border-radius:999px;
    font-size:14px;
    font-weight:600;
">
    {market_opportunity_level}
</div>

</div>
""",
        unsafe_allow_html=True
    )

    # Baja levemente la tabla para equilibrarla con el radar
    st.markdown(
        "<div style='height:5px;'></div>",
        unsafe_allow_html=True
    )

    # -------------------------
    # DIMENSIONS TABLE
    # -------------------------

    decision_table = pd.DataFrame({
        "Dimension": [
            "Demand",
            "Profitability",
            "Competition",
            "Advertising",
            "Listing"
        ],
        "Score": [
            round(demand_score),
            round(profitability_score),
            round(competition_score),
            round(advertising_score),
            round(listing_opportunity_score)
        ],
        "Interpretation": [
            f"{level_indicator(demand_level)} {demand_level}",
            f"{level_indicator(profitability_level)} {profitability_level}",
            f"{level_indicator(competition_level)} {competition_level}",
            f"{level_indicator(advertising_level)} {advertising_level}",
            f"{level_indicator(listing_opportunity_level)} "
            f"{listing_opportunity_level}"
        ]
    })

    st.dataframe(
        decision_table,
        hide_index=True,
        use_container_width=True,
        height=220,
        column_config={
            "Dimension": st.column_config.TextColumn(
                "Dimension",
                width="medium"
            ),
            "Score": st.column_config.NumberColumn(
                "Score",
                format="%d",
                width="small"
            ),
            "Interpretation": st.column_config.TextColumn(
                "Interpretation",
                width="medium"
            )
        }
    )


# Espacio entre el perfil y la recomendación
st.markdown(
    "<div style='height:18px;'></div>",
    unsafe_allow_html=True
)


# =====================================================
# 🧠 EXECUTIVE RECOMMENDATION
# =====================================================

st.markdown("## Executive Recommendation")

executive_card_html = f"""
<div style="width:100%; background:#FFFFFF; border:1px solid #E2E8F0;
border-left:5px solid #F59E0B; border-radius:14px; padding:20px 24px;
margin-bottom:24px; box-sizing:border-box;">

<div style="display:flex; align-items:flex-start; gap:16px;">

<div style="min-width:42px; width:42px; height:42px; display:flex;
align-items:center; justify-content:center; background:#FFF7ED;
border:1px solid #FED7AA; border-radius:50%; font-size:20px;">
🔎
</div>

<div style="flex:1;">

<div style="font-size:20px; font-weight:700; color:#1F3B63;
margin-bottom:5px;">
{market_opportunity_level}
</div>

<div style="font-size:15px; color:#475569; line-height:1.55;">
{executive_recommendation}
</div>

</div>
</div>
</div>
"""

st.markdown(
    executive_card_html,
    unsafe_allow_html=True
)
# -------------------------
# STRENGTHS / RISKS / ACTIONS
# -------------------------

rec_col1, rec_col2, rec_col3 = st.columns(3, gap="large")

with rec_col1:

    st.markdown("### Strengths")

    for item in strengths:
        st.markdown(
            f"<div style='margin-bottom:12px;'>"
            f"<span style='color:#16A34A; font-weight:700;'>●</span> "
            f"{item}"
            f"</div>",
            unsafe_allow_html=True
        )

with rec_col2:

    st.markdown("### Risks")

    for item in risks:
        st.markdown(
            f"<div style='margin-bottom:12px;'>"
            f"<span style='color:#F59E0B; font-weight:700;'>▲</span> "
            f"{item}"
            f"</div>",
            unsafe_allow_html=True
        )

with rec_col3:

    st.markdown("### Recommended Actions")

    for item in actions:
        st.markdown(
            f"<div style='margin-bottom:12px;'>"
            f"<span style='color:#2563EB; font-weight:700;'>→</span> "
            f"{item}"
            f"</div>",
            unsafe_allow_html=True
        )

st.markdown(
    "<div style='height:20px;'></div>",
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
    "Scale": "#6DD5ED",
    "Defend": "#A5B4FC",
    "Optimize": "#FCA5A5",
    "Exit": "#F9A8D4"
}
# -------------------------
# TABS
# -------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Performance Overview",
    "Market Analysis",
    "Leadership Position",
    "Growth Opportunities",
    "Strategic Decisions",
    "Executive Report",
    "Decision Intelligence"
])


st.divider()

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
        col2.metric(
            label="Estimated Real Profit",
            value=f"${best['active_profit']:,.0f}",
            help=(
                "Estimated Real Profit is calculated using standardized FBA "
                "fulfillment fees and international shipping assumptions for "
                "products within the analyzed niche. Actual costs may vary "
                "depending on product dimensions, weight and logistics "
                "configuration, but these differences are generally limited "
                "for comparable products."
            )
        )
        
        col3.metric(
            "Estimated Real Margin",
            f"{best['active_margin']:.1f}%"
        )

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
    st.caption(
        "Projected product profitability after FBA fees, COGS, shipping, "
        "and estimated advertising costs based on KPI Studio's Advertising Dependency Model."
    )
                    
    # -------------------------
    # 📊 GRÁFICO FULL WIDTH (MEJORADO)
    # -------------------------
    profit_abs = max(
    abs(top_profit["active_profit"].min()),
    abs(top_profit["active_profit"].max())
    )
    
    fig = px.bar(
        top_profit,
        x="active_profit",
        y="label",
        orientation="h",
        text="active_profit",
        color="active_profit",
        color_continuous_scale=[
            [0.0, "#DC2626"],
            [0.5, "#F3F4F6"],
            [1.0, "#16A34A"]
        ],
        range_color=[-profit_abs, profit_abs],
        labels={
            "active_profit": "Estimated Real Profit",
            "label": "Product"
        }
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
        xaxis_title="Estimated Real Profit (After Costs)",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------------------------
    # 🏆 TOP PRODUCTS (ABAJO)
    # -------------------------

    st.markdown("## Top Market Opportunities")

    # 🔑 Agregar ASIN + nombre
    top_profit["label"] = top_profit["ASIN"] + " | " + top_profit[display_col]

    # 🔥 Renombrar columnas (EJECUTIVO)
    top_display = top_profit[[
        "label",
        "Revenue",
        "total_fees",
        "cogs_cost",
        "shipping_cost",
        "advertising_dependency_score",
        "advertising_dependency_level",
        "estimated_tacos",
        "ads_cost",
        "active_profit",
        "active_margin"
    ]].rename(columns={
        "label": "Product",
        "total_fees": "FBA Fees",
        "cogs_cost": "COGS",
        "shipping_cost": "Shipping",
        "advertising_dependency_score": "Advertising Dependency Score",
        "advertising_dependency_level": "Advertising Dependency",
        "estimated_tacos": "Estimated TACOS",
        "ads_cost": "Estimated Ad Cost",
        "active_profit": "Estimated Real Profit",
        "active_margin": "Estimated Real Margin (%)"
    })

    top_display = top_display.sort_values("Estimated Real Profit", ascending=False)

    # 🔥 Tabla final
    st.markdown(
        """
        <div style="
            font-size:16px;
            font-weight:500;
            color:#6B7280;
            margin-bottom:15px;
        ">
            Products ranked by estimated real profitability after FBA fees, COGS, shipping, and advertising costs using KPI Studio's Advertising Dependency Model.
        </div>
        """,
        unsafe_allow_html=True
    )
    
        # -------------------------
    # 🎨 ESTILO EJECUTIVO DE LA TABLA
    # -------------------------

    def style_dependency_level(value):
        styles = {
            "Very Low": "background-color:#DCFCE7; color:#166534; font-weight:600;",
            "Low": "background-color:#ECFDF5; color:#15803D; font-weight:600;",
            "Moderate": "background-color:#FEF3C7; color:#92400E; font-weight:600;",
            "High": "background-color:#FFEDD5; color:#C2410C; font-weight:600;",
            "Very High": "background-color:#FEE2E2; color:#991B1B; font-weight:600;"
        }
        return styles.get(value, "")

    # Escalas simétricas para positivos y negativos
    profit_abs = max(
        abs(top_display["Estimated Real Profit"].min()),
        abs(top_display["Estimated Real Profit"].max())
    )
    
    margin_abs = max(
        abs(top_display["Estimated Real Margin (%)"].min()),
        abs(top_display["Estimated Real Margin (%)"].max())
    )
    styled_top_display = (
        top_display
        .style
        .background_gradient(
            cmap="Blues",
            subset=["Revenue"]
        )
        .background_gradient(
            cmap="RdYlGn_r",
            subset=["Advertising Dependency Score"],
            vmin=0,
            vmax=100
        )
        .map(
            style_dependency_level,
            subset=["Advertising Dependency"]
        )
        .background_gradient(
            cmap="RdYlGn_r",
            subset=["Estimated TACOS"],
            vmin=8,
            vmax=30
        )
        .background_gradient(
            cmap="Reds",
            subset=["Estimated Ad Cost"]
        )
        .background_gradient(
            cmap="RdYlGn",
            subset=["Estimated Real Profit"],
            vmin=-profit_abs,
            vmax=profit_abs
        )
        .background_gradient(
            cmap="RdYlGn",
            subset=["Estimated Real Margin (%)"],
            vmin=-margin_abs,
            vmax=margin_abs
        )
        .format({
            "Revenue": "${:,.0f}",
            "FBA Fees": "${:,.0f}",
            "COGS": "${:,.0f}",
            "Shipping": "${:,.0f}",
            "Advertising Dependency Score": "{:.1f}",
            "Estimated TACOS": "{:.1f}%",
            "Estimated Ad Cost": "${:,.0f}",
            "Estimated Real Profit": "${:,.0f}",
            "Estimated Real Margin (%)": "{:.1f}%"
        })
    )

    st.dataframe(
        styled_top_display,
        column_config={
            "Product": st.column_config.TextColumn(
                "Product",
                width="large"
            ),
            "Revenue": st.column_config.NumberColumn(
                "Revenue",
                width="small"
            ),
            "Advertising Dependency Score": st.column_config.NumberColumn(
                "Dependency",
                width="small"
            ),
            "Advertising Dependency": st.column_config.TextColumn(
                "Level",
                width="small"
            ),
            "Estimated TACOS": st.column_config.NumberColumn(
                "Est. TACOS",
                width="small"
            ),
            "Estimated Ad Cost": st.column_config.NumberColumn(
                "Est. Ad Cost",
                width="small"
            ),
            "Estimated Real Profit": st.column_config.NumberColumn(
                "Est. Real Profit",
                width="small"
            ),
            "Estimated Real Margin (%)": st.column_config.NumberColumn(
                "Est. Margin",
                width="small"
            )
        },
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
    
# -------------------------
# 🎯 SELECT YOUR PRODUCT
# -------------------------

    st.markdown(
        """
    <div style="
        background:#EFF6FF;
        border:1px solid #BFDBFE;
        border-left:5px solid #1F3B63;
        border-radius:14px;
        padding:16px 18px;
        margin-top:8px;
        margin-bottom:12px;
    ">
    
    <div style="
        font-size:19px;
        font-weight:700;
        color:#1F3B63;
        margin-bottom:5px;
    ">
        🎯 Select Your Product
    </div>
    
    <div style="
        font-size:14px;
        color:#475569;
        line-height:1.5;
    ">
        Choose your ASIN to compare its actual TACOS, profitability and margin
        against KPI Studio's estimated market performance.
    </div>
    
    </div>
    """,
        unsafe_allow_html=True
    )
    
    selected_product = st.selectbox(
        "Your product ASIN",
        df["label"],
        index=0,
        key="selected_product_asin",
        label_visibility="collapsed"
    )
    
    st.caption(
        "The selected ASIN is used only for the product comparison below. "
        "It does not modify the Market Opportunity Score or competitor estimates."
    )
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
# ----------------------------------
# 🎯 YOUR ACTUAL TACOS
# ----------------------------------
    
    st.markdown("#### Your Product Advertising Performance")
    
    selected_actual_tacos = st.number_input(
        "Your Actual TACOS (%)",
        min_value=0.0,
        max_value=60.0,
        value=float(selected_row["estimated_tacos"]),
        step=0.5,
        key=f"actual_tacos_{selected_asin}"
    )
    
    st.caption(
        "This TACOS is applied only to the selected ASIN. "
        "Market competitors continue using KPI Studio's estimated TACOS."
    )
    
    # -------------------------
    # TACOS COMPARISON
    # -------------------------
    
    estimated_tacos = float(selected_row["estimated_tacos"])
    
    tacos_difference = (
        selected_actual_tacos
        - estimated_tacos
    )
    
    if tacos_difference <= -3:
        tacos_comment = "Excellent advertising efficiency."
        tacos_color = "#16A34A"
    
    elif tacos_difference < 0:
        tacos_comment = "Performing better than model expectations."
        tacos_color = "#22C55E"
    
    elif tacos_difference <= 3:
        tacos_comment = "In line with model expectations."
        tacos_color = "#F59E0B"
    
    else:
        tacos_comment = "Advertising costs are above the estimated level."
        tacos_color = "#DC2626"
    
    # -------------------------
    # ACTUAL PRODUCT FINANCIALS
    # -------------------------
    
    selected_actual_ads_cost = (
        selected_row["Revenue"]
        * selected_actual_tacos
        / 100
    )
    
    selected_actual_profit = (
        selected_row["Revenue"]
        - selected_row["total_fees"]
        - selected_row["cogs_cost"]
        - selected_row["shipping_cost"]
        - selected_actual_ads_cost
    )
    
    selected_actual_margin = (
        selected_actual_profit
        / selected_row["Revenue"]
        * 100
        if selected_row["Revenue"] > 0
        else 0
    )
    
    # -------------------------
    # TACOS COMPARISON CARD
    # -------------------------
    
    st.markdown(
        f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0;
    border-radius:14px; padding:18px 22px; margin-top:18px;
    margin-bottom:22px;">
    
    <div style="display:flex; justify-content:space-between;
    margin-bottom:12px;">
    
    <div>
    <div style="font-size:13px;color:#64748B;">
    Estimated TACOS (Model)
    </div>
    <div style="font-size:24px;font-weight:700;color:#1F3B63;">
    {estimated_tacos:.1f}%
    </div>
    </div>
    
    <div>
    <div style="font-size:13px;color:#64748B;">
    Your Actual TACOS
    </div>
    <div style="font-size:24px;font-weight:700;color:#1F3B63;">
    {selected_actual_tacos:.1f}%
    </div>
    </div>
    
    <div>
    <div style="font-size:13px;color:#64748B;">
    Difference
    </div>
    <div style="font-size:24px;font-weight:700;color:{tacos_color};">
    {tacos_difference:+.1f}%
    </div>
    </div>
    
    </div>
    
    <div style="font-size:14px;color:{tacos_color};font-weight:600;">
    {tacos_comment}
    </div>
    
    </div>
    """,
        unsafe_allow_html=True
    )
    
    # -------------------------
    # 📊 MARKET AVERAGE
    # -------------------------
    
    avg_profit = df["active_profit"].mean()
    avg_sales = df["ASIN Sales"].mean()
    avg_margin = df["active_margin"].mean()
    
    # -------------------------
    # 📊 COMPARISON + GAPS
    # -------------------------
    
    if not df.empty:
    
        best = df.sort_values(
            "product_score",
            ascending=False
        ).iloc[0]
    
        filtered_selected = df[
            df["ASIN"] == selected_row["ASIN"]
        ]
    
        if not filtered_selected.empty:
            selected_row = filtered_selected.iloc[0]
        else:
            st.warning(
                "Selected product no longer matches filters"
            )
            st.stop()
    
        # GAP vs LEADER
        profit_gap = (
            selected_actual_profit
            - best["active_profit"]
        )
    
        sales_gap = (
            selected_row["ASIN Sales"]
            - best["ASIN Sales"]
        )
    
        margin_gap = (
            selected_actual_margin
            - best["active_margin"]
        )
    
        # GAP vs MARKET AVERAGE
        profit_gap_avg = (
            selected_actual_profit
            - avg_profit
        )
    
        sales_gap_avg = (
            selected_row["ASIN Sales"]
            - avg_sales
        )
    
        margin_gap_avg = (
            selected_actual_margin
            - avg_margin
        )
    
        col1, col2, col3, col4, col5 = st.columns(5)
    
        # 🔎 YOUR PRODUCT
        with col1:
    
            st.markdown("#### Your Product")
    
            components.html(
                metric_card(
                    "Profit",
                    f"${selected_actual_profit:,.0f}"
                ),
                height=110
            )
    
            components.html(
                metric_card(
                    "Sales",
                    f"{int(selected_row['ASIN Sales'])}"
                ),
                height=110
            )
    
            components.html(
                metric_card(
                    "Margin",
                    f"{selected_actual_margin:.1f}%"
                ),
                height=110
            )
    
        # 🏆 MARKET LEADER
        with col2:
    
            st.markdown("#### Market Leader")
    
            components.html(
                metric_card(
                    "Profit",
                    f"${best['active_profit']:,.0f}"
                ),
                height=110
            )
    
            components.html(
                metric_card(
                    "Sales",
                    f"{int(best['ASIN Sales'])}"
                ),
                height=110
            )
    
            components.html(
                metric_card(
                    "Margin",
                    f"{best['active_margin']:.1f}%"
                ),
                height=110
            )
    
        # 📊 MARKET AVERAGE
        with col3:
    
            st.markdown("#### Market Average")
    
            components.html(
                metric_card(
                    "Profit",
                    f"${avg_profit:,.0f}"
                ),
                height=110
            )
    
            components.html(
                metric_card(
                    "Sales",
                    f"{int(avg_sales) if not pd.isna(avg_sales) else 0}"
                ),
                height=110
            )
    
            components.html(
                metric_card(
                    "Margin",
                    f"{avg_margin:.1f}%"
                ),
                height=110
            )
    
        # GAP vs LEADER
        with col4:
    
            st.markdown("#### Gap vs Leader")
    
            components.html(
                gap_signal_card(
                    "Profit Gap",
                    profit_gap
                ),
                height=110
            )
    
            components.html(
                gap_signal_card(
                    "Sales Gap",
                    sales_gap
                ),
                height=110
            )
    
            components.html(
                gap_signal_card(
                    "Margin Gap",
                    margin_gap,
                    is_pct=True
                ),
                height=110
            )
    
        # GAP vs MARKET
        with col5:
    
            st.markdown("#### Gap vs Market")
    
            components.html(
                gap_signal_card(
                    "Profit Gap",
                    profit_gap_avg
                ),
                height=110
            )
    
            components.html(
                gap_signal_card(
                    "Sales Gap",
                    sales_gap_avg
                ),
                height=110
            )
    
            components.html(
                gap_signal_card(
                    "Margin Gap",
                    margin_gap_avg,
                    is_pct=True
                ),
                height=110
            )
    
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
    
     # =====================================================
    # MARKET LEADERS
    # =====================================================
    
    st.markdown("## Market Leaders")
    
    # Se reutiliza display_col, que ya fue definido anteriormente
    # con el nombre resumido del producto.
    
    market_leaders = df[
        [
            "ASIN",
            display_col,
            "ASIN Sales",
            "listing_score"
        ]
    ].copy()
    
    # Asegurar columnas numéricas
    market_leaders["ASIN Sales"] = pd.to_numeric(
        market_leaders["ASIN Sales"],
        errors="coerce"
    )
    
    market_leaders["listing_score"] = pd.to_numeric(
        market_leaders["listing_score"],
        errors="coerce"
    )
    
    # Crear etiqueta: ASIN + nombre resumido
    market_leaders["label"] = (
        market_leaders["ASIN"].astype(str)
        + " | "
        + market_leaders[display_col].astype(str)
    )
    
    # Ordenar por ventas y luego por Listing Score
    market_leaders = (
        market_leaders
        .sort_values(
            by=["ASIN Sales", "listing_score"],
            ascending=[False, False]
        )
        .head(10)
    )
    
    # Tabla final para mostrar
    market_leaders_display = (
        market_leaders[
            [
                "label",
                "ASIN Sales",
                "listing_score"
            ]
        ]
        .rename(
            columns={
                "label": "Product",
                "ASIN Sales": "Monthly Sales",
                "listing_score": "Listing Score"
            }
        )
    )
    
    # Formato visual y degradados
    market_leaders_styled = (
        market_leaders_display.style
        .format(
            {
                "Monthly Sales": "{:,.0f}",
                "Listing Score": "{:,.1f}"
            }
        )
        .background_gradient(
            subset=["Monthly Sales"],
            cmap="Blues"
        )
        .background_gradient(
            subset=["Listing Score"],
            cmap="Purples"
        )
    )
    
    # Mostrar tabla
    st.dataframe(
        market_leaders_styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Product": st.column_config.TextColumn(
                "Product",
                width="large"
            ),
            "Monthly Sales": st.column_config.NumberColumn(
                "Monthly Sales",
                width="medium"
            ),
            "Listing Score": st.column_config.NumberColumn(
                "Listing Score",
                width="medium"
            )
        }
    )
    
    st.caption(
        "Leading products based on monthly sales and listing quality."
    )
    
    # =====================================================
    # COMPETITIVE ACTION MAP
    # =====================================================
    
    st.markdown("### Strategic Positioning Matrix")
    
    # -------------------------
    # ACTION SUMMARY
    # -------------------------
    
    scale = (df["strategy_zone"] == "Scale").sum()
    defend = (df["strategy_zone"] == "Defend").sum()
    optimize = (df["strategy_zone"] == "Optimize").sum()
    exit_ = (df["strategy_zone"] == "Exit").sum()
    total = len(df)
    
    
    # -------------------------
    # EXECUTIVE CARD FUNCTION
    # -------------------------
    
    def action_card(title, value, color):
        return f"""
        <div style='
            background:#FFFFFF;
            border-radius:18px;
            border:1px solid #E5E7EB;
            box-shadow:0px 6px 18px rgba(0,0,0,0.05);
            height:150px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            text-align:center;
            position:relative;
        '>
    
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
        components.html(
            action_card(
                "Scale",
                scale,
                strategy_colors["Scale"]
            ),
            height=150
        )
    
    with col2:
        components.html(
            action_card(
                "Defend",
                defend,
                strategy_colors["Defend"]
            ),
            height=150
        )
    
    with col3:
        components.html(
            action_card(
                "Optimize",
                optimize,
                strategy_colors["Optimize"]
            ),
            height=150
        )
    
    with col4:
        components.html(
            action_card(
                "Exit",
                exit_,
                strategy_colors["Exit"]
            ),
            height=150
        )
    
    
    st.markdown(
        "<div style='height:20px'></div>",
        unsafe_allow_html=True
    )
    
    
    # -------------------------
    # PREPARE SCATTER DATA
    # -------------------------
    
    action_map_df = df.copy()
    
    # Asegurar columnas numéricas
    action_map_df["Active Sellers"] = pd.to_numeric(
        action_map_df["Active Sellers"],
        errors="coerce"
    )
    
    action_map_df["active_profit"] = pd.to_numeric(
        action_map_df["active_profit"],
        errors="coerce"
    )
    
    action_map_df["ASIN Sales"] = pd.to_numeric(
        action_map_df["ASIN Sales"],
        errors="coerce"
    )
    
    # Eliminar únicamente registros sin datos esenciales
    action_map_df = action_map_df.dropna(
        subset=[
            "Active Sellers",
            "active_profit",
            "ASIN Sales"
        ]
    )
    
    # -----------------------------------------------------
    # VISUAL SPREAD
    # Separa productos que tienen el mismo número de sellers
    # sin modificar la clasificación real.
    # -----------------------------------------------------
    
    action_map_df["seller_group_position"] = (
        action_map_df
        .groupby("Active Sellers")
        .cumcount()
    )
    
    action_map_df["seller_group_size"] = (
        action_map_df
        .groupby("Active Sellers")["Active Sellers"]
        .transform("size")
    )
    
    action_map_df["seller_offset"] = np.where(
        action_map_df["seller_group_size"] > 1,
        (
            action_map_df["seller_group_position"]
            / (action_map_df["seller_group_size"] - 1)
            - 0.5
        ) * 0.35,
        0
    )
    
    action_map_df["seller_visual_position"] = (
        action_map_df["Active Sellers"]
        + action_map_df["seller_offset"]
    )
    
    
    # -------------------------
    # QUADRANT SCATTER
    # -------------------------
    
    fig = px.scatter(
        action_map_df,
        x="seller_visual_position",
        y="active_profit",
        size="ASIN Sales",
        color="strategy_zone",
        color_discrete_map=strategy_colors,
        hover_name=display_col,
        hover_data={
            "seller_visual_position": False,
            "Active Sellers": ":.0f",
            "active_profit": ":$,.0f",
            "ASIN Sales": ":,.0f",
            "strategy_zone": True
        },
        labels={
            "Active Sellers": "Active Sellers",
            "active_profit": "Real Profit",
            "ASIN Sales": "Monthly Sales",
            "strategy_zone": "Action"
        },
        size_max=48
    )
    
    
    # -------------------------
    # QUADRANT LINES
    # -------------------------
    
    fig.add_vline(
        x=avg_sellers,
        line_dash="dash",
        line_color="#9CA3AF",
        line_width=1.5
    )
    
    fig.add_hline(
        y=avg_profit,
        line_dash="dash",
        line_color="#9CA3AF",
        line_width=1.5
    )
    
    
    # -------------------------
    # AXIS LABELS
    # -------------------------
    
    seller_values = sorted(
        action_map_df["Active Sellers"]
        .dropna()
        .unique()
    )
    
    fig.update_xaxes(
        title="Competition — Active Sellers",
        tickmode="array",
        tickvals=seller_values,
        ticktext=[
            f"{int(value)}"
            for value in seller_values
        ],
        showgrid=True,
        gridcolor="#EEF2F7",
        zeroline=False
    )
    
    fig.update_yaxes(
        title="Real Profit",
        tickprefix="$",
        tickformat=",.0f",
        showgrid=True,
        gridcolor="#EEF2F7",
        zeroline=False
    )
    
    
    # -------------------------
    # CHART DESIGN
    # -------------------------
    
    fig.update_traces(
        marker=dict(
            opacity=0.82,
            line=dict(
                width=1,
                color="#FFFFFF"
            )
        )
    )
    
    fig.update_layout(
        height=620,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(
            color="#111827",
            family="Arial"
        ),
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        ),
        legend=dict(
            title_text="Recommended Action",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=13,
            font_color="#111827"
        )
    )
    
    st.plotly_chart(
        fig,
        use_container_width=True
    )
    
    st.caption(
        "Bubble size represents monthly sales. Dashed lines show average competition and average real profit within the current filtered market."
    )
     # -------------------------
    # 🧠 EXECUTIVE SUMMARY
    # -------------------------
    
    if optimize > total * 0.5:
    
        title = "Optimization Opportunity"
    
        insight = (
            "Most products require optimization before scaling. "
            "Improving margins, conversion rates and listing quality "
            "should be prioritized before increasing advertising investment."
        )
    
    elif scale > total * 0.4:
    
        title = "Growth Opportunity"
    
        insight = (
            "A significant portion of the portfolio is ready to scale. "
            "Current profitability and competition levels indicate favorable "
            "conditions for expanding market share."
        )
    
    else:
    
        title = "Balanced Portfolio"
    
        insight = (
            "The portfolio presents a balanced distribution between products "
            "ready for growth and products requiring optimization."
        )
    
    st.info(
        f"""
    **{title}**
    
    Current analysis is based on the selected market filters.
    
    **Recommended Actions**
    
    • Scale: {scale} products with strong growth potential.
    
    • Defend: {defend} products requiring competitive protection.
    
    • Optimize: {optimize} products needing profitability or listing improvements.
    
    • Exit: {exit_} products with limited strategic value.
    
    **Executive Insight**
    
    {insight}
    """
    )
    # -------------------------
    # 🔥 TOP SCALE PRODUCTS
    # -------------------------
    
    st.markdown("### Top Products to Scale")
    
    st.info(
        "These products combine strong profitability, demand and competitive positioning, making them the best candidates for scaling."
    )
    
    top_scale = (
        df[df["strategy_zone"] == "Scale"]
        .sort_values("estimated_profit", ascending=False)
        .head(5)
        .copy()
    )
    
    # Limpiar datos
    top_scale["ASIN Sales"] = (
        pd.to_numeric(top_scale["ASIN Sales"], errors="coerce")
        .fillna(0)
        .astype(int)
    )
    
    top_scale["active_profit"] = pd.to_numeric(
        top_scale["active_profit"],
        errors="coerce"
    )
    
    top_scale["active_margin"] = pd.to_numeric(
        top_scale["active_margin"],
        errors="coerce"
    )
    
    if len(top_scale) > 0:

        profit_abs = max(
            abs(top_scale["active_profit"].min()),
            abs(top_scale["active_profit"].max())
        )
    
        margin_abs = max(
            abs(top_scale["active_margin"].min()),
            abs(top_scale["active_margin"].max())
        )
    
        st.dataframe(
    
            top_scale[
                [
                    "strategy_zone",
                    "label",
                    "active_profit",
                    "ASIN Sales",
                    "active_margin"
                ]
            ]
            .rename(
                columns={
                    "strategy_zone": "Action",
                    "label": "Product",
                    "active_profit": "Profit",
                    "ASIN Sales": "Sales",
                    "active_margin": "Margin"
                }
            )
            .style
    
            # Color de la acción
            .map(
                lambda x:
                    "color:#16A34A; font-weight:600;" if x == "Scale"
                    else "color:#2563EB; font-weight:600;" if x == "Defend"
                    else "color:#F59E0B; font-weight:600;" if x == "Optimize"
                    else "color:#DC2626; font-weight:600;",
                subset=["Action"]          # ← ESTA ES LA LÍNEA QUE ESTABA MAL
            )
    
            # Profit
            .background_gradient(
                cmap="RdYlGn",
                subset=["Profit"],
                vmin=-profit_abs,
                vmax=profit_abs
            )
    
            # Sales
            .background_gradient(
                cmap="Blues",
                subset=["Sales"]
            )
    
            # Margin
            .background_gradient(
                cmap="RdYlGn",
                subset=["Margin"],
                vmin=-margin_abs,
                vmax=margin_abs
            )
    
            # Formatos
            .format(
                {
                    "Profit": "${:,.0f}",
                    "Sales": "{:,.0f}",
                    "Margin": "{:.1f}%"
                }
            ),
    
            use_container_width=True,
            hide_index=True
    
        )
    
    else:
    
        st.info(
            "No products currently in the Scale category based on selected filters."
        )
     
# -------------------------
# TAB 3 - LEADERSHIP
# -------------------------
with tab3:

    st.markdown("### Competitive Landscape")

    st.caption(
        "Evaluate market concentration, seller dominance and growth momentum "
        "to identify established leaders and emerging competitors."
    )

    # -------------------------
    # SELLER POWER
    # -------------------------
    seller_power = (
        df.groupby("Seller")["market_power_score"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    total_power = seller_power["market_power_score"].sum()

    if total_power > 0:
        seller_power["share"] = (
            seller_power["market_power_score"] / total_power * 100
        )
    else:
        seller_power["share"] = 0

    # KPIs
    top1 = seller_power.iloc[0]["share"] if not seller_power.empty else 0
    top3 = seller_power.head(3)["share"].sum() if not seller_power.empty else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        components.html(
            kpi_card_tab5(
                "Top Seller Share",
                f"{top1:.1f}%",
                subtitle="Power controlled by the leading seller"
            ),
            height=200
        )

    with col2:
        components.html(
            kpi_card_tab5(
                "Top 3 Share",
                f"{top3:.1f}%",
                subtitle="Combined power of the three leading sellers"
            ),
            height=200
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
    # MARKET CONCENTRATION
    # -------------------------
    st.markdown("### Market Concentration")

    st.caption(
        "Market Power Share shows how competitive authority is distributed "
        "among the leading sellers in the analyzed market."
    )

    top_sellers = seller_power.head(10).copy()

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
        texttemplate="%{text:.1f}%",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Market Power Share: %{x:.1f}%"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=380,
        margin=dict(l=20, r=50, t=20, b=20),
        xaxis_title="Market Power Share (%)",
        yaxis_title="",
        coloraxis_colorbar=dict(
            title="Share",
            ticksuffix="%"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.divider()

# -------------------------
# MARKET STRUCTURE
# -------------------------

    leaders = (
        df.sort_values("market_power_score", ascending=False)
        .head(3)
        .copy()
    )
    
    rising = (
        df.sort_values("momentum_score", ascending=False)
        .head(3)
        .copy()
    )
    
    st.markdown("### Market Structure")
    
    # Clasificación de concentración
    if top3 >= 70:
        concentration_label = "Highly Concentrated"
        concentration_color = "#DC2626"
        concentration_background = "#FFFAFA"
        concentration_border = "#FCA5A5"
    
        structure_insight = (
            "A small group of sellers controls most of the market power, "
            "creating strong competitive barriers for new entrants."
        )
    
        strategic_implication = (
            "Competing directly with established leaders may require strong differentiation, "
            "a superior value proposition and disciplined advertising investment."
        )
    
    elif top3 >= 50:
        concentration_label = "Moderately Concentrated"
        concentration_color = "#D97706"
        concentration_background = "#FFFBEB"
        concentration_border = "#FCD34D"
    
        structure_insight = (
            "Leadership is concentrated among several relevant sellers, "
            "but meaningful space remains for differentiated competitors."
        )
    
        strategic_implication = (
            "New entrants should target underserved positioning opportunities rather than "
            "competing only through price."
        )
    
    else:
        concentration_label = "Fragmented Market"
        concentration_color = "#16A34A"
        concentration_background = "#F0FDF4"
        concentration_border = "#86EFAC"
    
        structure_insight = (
            "Market power is distributed across many sellers, with no small group "
            "exercising dominant control."
        )
    
        strategic_implication = (
            "The fragmented structure creates room for new brands to gain visibility "
            "through stronger listings, positioning and execution."
        )
    
    
    # Este bloque va FUERA del if / elif / else
    market_structure_card = textwrap.dedent(
        f"""
        <div style="
            background:#FFF7F7;
            border:1px solid {concentration_border};
            border-left:4px solid {concentration_color};
            border-radius:12px;
            padding:22px 24px;
            margin-top:8px;
            margin-bottom:22px;
            box-shadow:0 4px 14px rgba(15, 23, 42, 0.05);
        ">
    
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                gap:16px;
                margin-bottom:16px;
            ">
    
                <div>
                    <div style="
                        font-size:13px;
                        color:#64748B;
                        font-weight:600;
                        text-transform:uppercase;
                        letter-spacing:0.6px;
                        margin-bottom:5px;
                    ">
                        Competitive Structure
                    </div>
    
                    <div style="
                        font-size:24px;
                        color:#0F172A;
                        font-weight:700;
                    ">
                        {concentration_label}
                    </div>
                </div>
    
                <div style="
                    background:#FFFFFF;
                    border:1px solid {concentration_border};
                    border-radius:10px;
                    padding:10px 16px;
                    text-align:center;
                    min-width:125px;
                ">
                    <div style="
                        font-size:12px;
                        color:#64748B;
                        font-weight:600;
                    ">
                        TOP 3 SHARE
                    </div>
    
                    <div style="
                        font-size:28px;
                        color:{concentration_color};
                        font-weight:700;
                    ">
                        {top3:.1f}%
                    </div>
                </div>
    
            </div>
    
            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:18px;
            ">
    
                <div style="
                    background:rgba(255,255,255,0.70);
                    border-radius:9px;
                    padding:15px;
                ">
                    <div style="
                        font-size:13px;
                        color:#475569;
                        font-weight:700;
                        margin-bottom:6px;
                    ">
                        Market Insight
                    </div>
    
                    <div style="
                        font-size:14px;
                        color:#334155;
                        line-height:1.55;
                    ">
                        {structure_insight}
                    </div>
                </div>
    
                <div style="
                    background:rgba(255,255,255,0.70);
                    border-radius:9px;
                    padding:15px;
                ">
                    <div style="
                        font-size:13px;
                        color:#475569;
                        font-weight:700;
                        margin-bottom:6px;
                    ">
                        Strategic Implication
                    </div>
    
                    <div style="
                        font-size:14px;
                        color:#334155;
                        line-height:1.55;
                    ">
                        {strategic_implication}
                    </div>
                </div>
    
            </div>
    
            <div style="
                margin-top:15px;
                padding-top:13px;
                border-top:1px solid {concentration_border};
                font-size:13px;
                color:#64748B;
            ">
                The leading seller controls <b>{top1:.1f}%</b> of market power,
                while the three leading sellers collectively control
                <b>{top3:.1f}%</b>.
            </div>
    
        </div>
        """
    ).strip()
    
    components.html(
        market_structure_card,
        height=310,
        scrolling=False
    )
    # -------------------------
    # FASTEST GROWING PRODUCTS
    # -------------------------
    
    st.markdown("### Fastest Growing Products")
    
    growth_signal_card = """
    <div style="
        box-sizing:border-box;
        width:100%;
        padding:16px 18px;
        background:#F0FDF4;
        border:1px solid #BBF7D0;
        border-left:3px solid #16A34A;
        border-radius:10px;
        box-shadow:0 4px 12px rgba(15,23,42,0.04);
        font-family:Arial, sans-serif;
    ">
        <div style="
            font-size:13px;
            color:#166534;
            font-weight:700;
            text-transform:uppercase;
            letter-spacing:0.4px;
            margin-bottom:6px;
        ">
            MOMENTUM INDICATOR
        </div>
    
        <div style="
            font-size:14px;
            color:#334155;
            line-height:1.55;
        ">

        Momentum is KPI Studio's proprietary growth indicator that combines demand acceleration, review growth and commercial activity to identify products with the highest recent momentum and the potential to become future market leaders.
        </div>
    </div>
    """
    
    components.html(
        growth_signal_card,
        height=115,
        scrolling=False
    )
    
    # Copia para evitar warnings
    rising = rising.copy()
    
    # Limpiar datos numéricos
    rising["Recent Purchases"] = (
        pd.to_numeric(
            rising["Recent Purchases"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )
    
    rising["Review velocity"] = pd.to_numeric(
        rising["Review velocity"],
        errors="coerce"
    ).fillna(0)
    
    rising["momentum_score"] = pd.to_numeric(
        rising["momentum_score"],
        errors="coerce"
    ).fillna(0)
    
    # Crear nombre del producto
    rising["label"] = (
        rising["ASIN"].astype(str)
        + " | "
        + rising[display_col].fillna("").astype(str)
    )
    
    rising_display = (
        rising[
            [
                "Seller",
                "label",
                "momentum_score",
                "Review velocity",
                "Recent Purchases"
            ]
        ]
        .rename(
            columns={
                "label": "Product",
                "momentum_score": "Momentum",
                "Review velocity": "Review Growth",
                "Recent Purchases": "Recent Demand"
            }
        )
    )
    
    rising_styled = (
        rising_display.style
    
        # Momentum
        .background_gradient(
            cmap="YlGn",
            subset=["Momentum"]
        )
    
        # Crecimiento de reseñas
        .background_gradient(
            cmap="Oranges",
            subset=["Review Growth"]
        )
    
        # Demanda reciente
        .background_gradient(
            cmap="Blues",
            subset=["Recent Demand"]
        )
    
        # Formatos
        .format(
            {
                "Momentum": "{:.1f}",
                "Review Growth": "{:.1f}",
                "Recent Demand": "{:,}"
            }
        )
    )
    
    st.dataframe(
        rising_styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Seller": st.column_config.TextColumn(
                "Seller",
                width="medium"
            ),
            "Product": st.column_config.TextColumn(
                "Product",
                width="large"
            ),
            "Momentum": st.column_config.NumberColumn(
                "Momentum",
                help="Combined indicator of recent market traction.",
                width="small"
            ),
            "Review Growth": st.column_config.NumberColumn(
                "Review Growth",
                help="Recent velocity of review accumulation.",
                width="small"
            ),
            "Recent Demand": st.column_config.NumberColumn(
                "Recent Demand",
                help="Estimated recent purchase activity.",
                width="small"
            )
        }
    )
    # -------------------------
    # TAB 4 - NEW PRODUCTS
    # -------------------------
    # -------------------------
    # GROWTH OPPORTUNITY MATRIX
    # -------------------------
with tab4: 
    
    st.markdown("### Growth Opportunity Matrix")
    
    st.caption(
        "Evaluate products according to profitability and competitive pressure "
        "to identify the most attractive areas for market entry and expansion."
    )
    
    matrix_df = df.copy()
    
    # Limpiar variables
    matrix_df["active_profit"] = pd.to_numeric(
        matrix_df["active_profit"],
        errors="coerce"
    ).fillna(0)
    
    matrix_df["Active Sellers"] = pd.to_numeric(
        matrix_df["Active Sellers"],
        errors="coerce"
    ).fillna(0)
    
    matrix_df["ASIN Sales"] = pd.to_numeric(
        matrix_df["ASIN Sales"],
        errors="coerce"
    ).fillna(0)
    
    # Crear label
    matrix_df["label"] = (
        matrix_df["ASIN"].astype(str)
        + " | "
        + matrix_df[display_col].fillna("").astype(str)
    )
    
    # Promedios para cuadrantes
    avg_profit = matrix_df["active_profit"].mean()
    avg_sellers = matrix_df["Active Sellers"].mean()
    
    fig = px.scatter(
        matrix_df,
        x="Active Sellers",
        y="active_profit",
        size="ASIN Sales",
    
        # El color ahora representa margen real
        color="active_margin",
    
        hover_name="label",
    
        hover_data={
            "label": False,
            "active_profit": ":,.0f",
            "active_margin": ":.1f",
            "ASIN Sales": ":,.0f",
            "Active Sellers": ":,.0f"
        },
    
        color_continuous_scale="YlGnBu",
    
        labels={
            "active_profit": "Estimated Profit",
            "active_margin": "Real Margin (%)",
            "ASIN Sales": "Monthly Sales",
            "Active Sellers": "Active Competitors"
        }
    )
    
    # Líneas promedio para dividir los cuadrantes
    fig.add_vline(
        x=avg_sellers,
        line_dash="dash",
        line_color="#94A3B8",
        line_width=1.5
    )
    
    fig.add_hline(
        y=avg_profit,
        line_dash="dash",
        line_color="#94A3B8",
        line_width=1.5
    )
    
    # Estilo de las burbujas y hover
    fig.update_traces(
        marker=dict(
            opacity=0.80,
            line=dict(
                width=1,
                color="#FFFFFF"
            )
        ),
    
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Estimated Profit: $%{y:,.0f}<br>"
            "Active Competitors: %{x:,.0f}<br>"
            "Monthly Sales: %{marker.size:,.0f}<br>"
            "Real Margin: %{marker.color:.1f}%"
            "<extra></extra>"
        )
    )
    
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
    
        font=dict(
            color="#111827"
        ),
    
        height=540,
    
        margin=dict(
            l=20,
            r=20,
            t=25,
            b=20
        ),
    
        xaxis_title="Active Competitors",
        yaxis_title="Estimated Profit",
    
        # Active Sellers es un conteo entero
        xaxis=dict(
            tickmode="linear",
            dtick=1,
            rangemode="tozero",
            showgrid=True,
            gridcolor="#E5E7EB",
            zeroline=False
        ),
    
        yaxis=dict(
            showgrid=True,
            gridcolor="#E5E7EB",
            zeroline=False,
            tickprefix="$",
            tickformat=",.0f"
        ),
    
        coloraxis_colorbar=dict(
            title="Real Margin",
            ticksuffix="%"
        )
    )
    
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )
    
    st.caption(
        "Bubble size represents monthly sales and color represents real margin. "
        "Dashed lines indicate market averages and divide the matrix into four strategic opportunity zones."
    )
    # -------------------------
    # OPPORTUNITY LANDSCAPE
    # -------------------------
    
    top_profit_value = matrix_df["active_profit"].max()
    avg_profit_value = matrix_df["active_profit"].mean()
    
    profit_ratio = (
        top_profit_value / avg_profit_value
        if avg_profit_value > 0
        else 0
    )
    
    high_profit_low_comp = matrix_df[
        (matrix_df["active_profit"] >= avg_profit)
        & (matrix_df["Active Sellers"] <= avg_sellers)
    ]
    
    high_profit_high_comp = matrix_df[
        (matrix_df["active_profit"] >= avg_profit)
        & (matrix_df["Active Sellers"] > avg_sellers)
    ]
    
    low_profit_low_comp = matrix_df[
        (matrix_df["active_profit"] < avg_profit)
        & (matrix_df["Active Sellers"] <= avg_sellers)
    ]
    
    low_profit_high_comp = matrix_df[
        (matrix_df["active_profit"] < avg_profit)
        & (matrix_df["Active Sellers"] > avg_sellers)
    ]
    
    if len(high_profit_low_comp) > 0:
        opportunity_label = "Attractive Expansion Potential"
        opportunity_color = "#16A34A"
        opportunity_background = "#F0FDF4"
        opportunity_border = "#86EFAC"
    
        executive_insight = (
            f"{len(high_profit_low_comp)} products combine above-average profitability "
            "with below-average competitive pressure."
        )
    
        strategic_implication = (
            "This quadrant offers the strongest conditions for market entry, "
            "product differentiation and controlled scaling."
        )
    
    elif len(high_profit_high_comp) > 0:
        opportunity_label = "Profitable but Competitive"
        opportunity_color = "#D97706"
        opportunity_background = "#FFFBEB"
        opportunity_border = "#FCD34D"
    
        executive_insight = (
            "The market contains profitable products, but most operate under "
            "above-average competitive pressure."
        )
    
        strategic_implication = (
            "Entry may still be viable, but success will depend on clear positioning, "
            "listing quality and disciplined advertising."
        )
    
    else:
        opportunity_label = "Limited Immediate Opportunity"
        opportunity_color = "#DC2626"
        opportunity_background = "#FEF2F2"
        opportunity_border = "#FCA5A5"
    
        executive_insight = (
            "Few products currently combine attractive profitability with manageable competition."
        )
    
        strategic_implication = (
            "A cautious entry strategy is recommended, prioritizing narrow niches "
            "or differentiated product propositions."
        )
    
    opportunity_landscape_card = f"""
    <div style="
        box-sizing:border-box;
        width:100%;
        background:{opportunity_background};
        border:1px solid {opportunity_border};
        border-left:4px solid {opportunity_color};
        border-radius:12px;
        padding:20px 22px;
        font-family:Arial, sans-serif;
        box-shadow:0 4px 14px rgba(15,23,42,0.05);
    ">
    
        <div style="
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
            gap:18px;
            margin-bottom:16px;
        ">
    
            <div>
                <div style="
                    font-size:13px;
                    color:#64748B;
                    font-weight:700;
                    text-transform:uppercase;
                    letter-spacing:0.5px;
                    margin-bottom:5px;
                ">
                    Opportunity Landscape
                </div>
    
                <div style="
                    font-size:23px;
                    color:#0F172A;
                    font-weight:700;
                ">
                    {opportunity_label}
                </div>
            </div>
    
            <div style="
                background:#FFFFFF;
                border:1px solid {opportunity_border};
                border-radius:10px;
                padding:10px 16px;
                text-align:center;
                min-width:145px;
            ">
                <div style="
                    font-size:12px;
                    color:#64748B;
                    font-weight:700;
                ">
                    PRIME OPPORTUNITIES
                </div>
    
                <div style="
                    font-size:27px;
                    color:{opportunity_color};
                    font-weight:700;
                ">
                    {len(high_profit_low_comp)}
                </div>
            </div>
    
        </div>
    
        <div style="
            display:grid;
            grid-template-columns:1fr 1fr;
            gap:16px;
            margin-bottom:15px;
        ">
    
            <div style="
                background:rgba(255,255,255,0.75);
                border-radius:9px;
                padding:14px;
            ">
                <div style="
                    font-size:13px;
                    color:#475569;
                    font-weight:700;
                    margin-bottom:6px;
                ">
                    Market Insight
                </div>
    
                <div style="
                    font-size:14px;
                    color:#334155;
                    line-height:1.55;
                ">
                    {executive_insight}
                </div>
            </div>
    
            <div style="
                background:rgba(255,255,255,0.75);
                border-radius:9px;
                padding:14px;
            ">
                <div style="
                    font-size:13px;
                    color:#475569;
                    font-weight:700;
                    margin-bottom:6px;
                ">
                    Strategic Implication
                </div>
    
                <div style="
                    font-size:14px;
                    color:#334155;
                    line-height:1.55;
                ">
                    {strategic_implication}
                </div>
            </div>
    
        </div>
    
        <div style="
            padding-top:12px;
            border-top:1px solid {opportunity_border};
            font-size:13px;
            color:#64748B;
            line-height:1.5;
        ">
            Quadrant distribution:
            <b>{len(high_profit_low_comp)}</b> high-profit / low-competition,
            <b>{len(high_profit_high_comp)}</b> high-profit / high-competition,
            <b>{len(low_profit_low_comp)}</b> low-profit / low-competition and
            <b>{len(low_profit_high_comp)}</b> low-profit / high-competition products.
        </div>
    
    </div>
    """
    
    components.html(
        opportunity_landscape_card,
        height=300,
        scrolling=False
    )   
    # -------------------------
    # MARKET ENTRY OPPORTUNITIES
    # -------------------------
    st.markdown("### Market Entry Opportunities")
    
    st.caption(
        "Identify products with strong demand momentum, manageable competition "
        "and healthy real margins."
    )
    
    entry_df = df.copy()
    
    # -------------------------
    # CLEAN NUMERIC VARIABLES
    # -------------------------
    
    entry_df["sales_velocity"] = pd.to_numeric(
        entry_df["sales_velocity"],
        errors="coerce"
    ).fillna(0)
    
    entry_df["Active Sellers"] = pd.to_numeric(
        entry_df["Active Sellers"],
        errors="coerce"
    ).fillna(0)
    
    entry_df["active_margin"] = pd.to_numeric(
        entry_df["active_margin"],
        errors="coerce"
    ).fillna(0)
    
    entry_df["ASIN Sales"] = pd.to_numeric(
        entry_df["ASIN Sales"],
        errors="coerce"
    ).fillna(0)
    
    # -------------------------
    # NORMALIZATION FUNCTION
    # -------------------------
    
    def min_max_score(series):
        minimum = series.min()
        maximum = series.max()
    
        if maximum == minimum:
            return pd.Series(
                50,
                index=series.index,
                dtype=float
            )
    
        return (
            (series - minimum)
            / (maximum - minimum)
            * 100
        )
    
    # -------------------------
    # ENTRY SCORE COMPONENTS
    # -------------------------
    
    entry_df["demand_score"] = min_max_score(
        entry_df["sales_velocity"]
    )
    
    entry_df["competition_score"] = (
        100
        - min_max_score(entry_df["Active Sellers"])
    )
    
    entry_df["margin_score"] = min_max_score(
        entry_df["active_margin"]
    )
    
    # Composite Entry Score
    entry_df["entry_score"] = (
        entry_df["demand_score"] * 0.40
        + entry_df["competition_score"] * 0.30
        + entry_df["margin_score"] * 0.30
    )
    
    # -------------------------
    # OPPORTUNITY CLASSIFICATION
    # -------------------------
    
    def classify_entry_opportunity(score):
        if score >= 75:
            return "High Entry Potential"
        elif score >= 60:
            return "Moderate Potential"
        elif score >= 45:
            return "Watchlist"
        else:
            return "Avoid"
    
    entry_df["entry_status"] = entry_df["entry_score"].apply(
        classify_entry_opportunity
    )
    
    # Crear label
    entry_df["label"] = (
        entry_df["ASIN"].astype(str)
        + " | "
        + entry_df[display_col].fillna("").astype(str)
    )
    
    # -------------------------
    # TOP ENTRY OPPORTUNITIES
    # -------------------------
    
    top_entry = (
        entry_df
        .sort_values("entry_score", ascending=False)
        .head(10)
        .copy()
    )
    
    st.markdown("### Recommended Entry Opportunities")
    
    entry_display = (
        top_entry[
            [
                "entry_status",
                "label",
                "entry_score",
                "sales_velocity",
                "Active Sellers",
                "active_margin"
            ]
        ]
        .rename(
            columns={
                "entry_status": "Entry Potential",
                "label": "Product",
                "entry_score": "Entry Score",
                "sales_velocity": "Demand Momentum",
                "Active Sellers": "Active Competitors",
                "active_margin": "Real Margin"
            }
        )
    )
    
    entry_margin_abs = max(
        abs(entry_display["Real Margin"].min()),
        abs(entry_display["Real Margin"].max())
    )
    entry_styled = (
        entry_display.style
    
        .map(
            lambda x:
                "color:#16A34A; font-weight:600;"
                if x == "High Entry Potential"
                else "color:#D97706; font-weight:600;"
                if x == "Moderate Potential"
                else "color:#2563EB; font-weight:600;"
                if x == "Watchlist"
                else "color:#DC2626; font-weight:600;",
            subset=["Entry Potential"]
        )
    
        .background_gradient(
            cmap="YlGn",
            subset=["Entry Score"]
        )
    
        .background_gradient(
            cmap="Greens",
            subset=["Demand Momentum"]
        )
    
        .background_gradient(
            cmap="Blues_r",
            subset=["Active Competitors"]
        )
    
        .background_gradient(
            cmap="RdYlGn",
            subset=["Real Margin"],
            vmin=-entry_margin_abs,
            vmax=entry_margin_abs
        )
    
        .format(
            {
                "Entry Score": "{:.1f}",
                "Demand Momentum": "{:.1f}",
                "Active Competitors": "{:.0f}",
                "Real Margin": "{:.1f}%"
            }
        )
    )
    
    st.dataframe(
        entry_styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Opportunity": st.column_config.TextColumn(
                "Opportunity",
                width="medium"
            ),
            "Product": st.column_config.TextColumn(
                "Product",
                width="large"
            ),
            "Opportunity Score": st.column_config.NumberColumn(
                "Opportunity Score",
                help=(
                    "Composite score (0–100) that combines demand momentum, "
                    "competitive intensity and real margin to estimate market entry attractiveness."
                ),
                width="small"
            ),
            "Demand Momentum": st.column_config.NumberColumn(
                "Demand Momentum",
                help="Relative strength and acceleration of current product demand.",
                width="small"
            ),
            "Active Competitors": st.column_config.NumberColumn(
                "Active Competitors",
                help="Number of active sellers competing for the listing.",
                width="small"
            ),
            "Real Margin": st.column_config.NumberColumn(
                "Real Margin",
                help="Estimated margin after operating and advertising costs.",
                width="small"
            )
        }
    )
    
    # -------------------------
    # MARKET ENTRY RECOMMENDATION
    # -------------------------
    
    high_potential_count = (
    entry_df["entry_status"] == "High Entry Potential"
    ).sum()
    
    moderate_potential_count = (
    entry_df["entry_status"] == "Moderate Potential"
    ).sum()
        
    best_opportunity = (
            top_entry.iloc[0]
            if not top_entry.empty
            else None
        )
        
    if high_potential_count >= 3:
        entry_signal = "Favorable Entry Environment"
        entry_color = "#16A34A"
        entry_background = "#F0FDF4"
        entry_border = "#86EFAC"
    
        entry_insight = (
            f"The market contains {high_potential_count} high-potential entry "
            "opportunities with balanced demand, competition and margin conditions."
        )
    
        entry_recommendation = (
            "Prioritize validation of the highest-ranked products and evaluate "
            "differentiated positioning before scaling investment."
        )
    
    elif high_potential_count >= 1 or moderate_potential_count >= 3:
        entry_signal = "Selective Entry Potential"
        entry_color = "#D97706"
        entry_background = "#FFFBEB"
        entry_border = "#FCD34D"
    
        entry_insight = (
            f"The market contains {high_potential_count} high-potential and "
            f"{moderate_potential_count} moderate-potential entry opportunities."
        )
    
        entry_recommendation = (
            "Entry conditions are promising for selected products, but product "
            "validation, differentiation and disciplined positioning remain essential."
        )
    
    else:
        entry_signal = "Limited Entry Potential"
        entry_color = "#DC2626"
        entry_background = "#FEF2F2"
        entry_border = "#FCA5A5"
    
        entry_insight = (
            "Few products currently combine sufficient demand, manageable "
            "competition and healthy margins."
        )
    
        entry_recommendation = (
            "Avoid broad market entry and focus on narrow differentiation, "
            "cost improvement or alternative niches."
        )
        
    if best_opportunity is not None:
            best_product_text = (
                f"The highest-ranked product has an Entry Score of "
                f"<b>{best_opportunity['entry_score']:.1f}</b>, "
                f"with <b>{best_opportunity['Active Sellers']:.0f}</b> active competitors "
                f"and a real margin of <b>{best_opportunity['active_margin']:.1f}%</b>."
            )
    else:
            best_product_text = "No product-level opportunity data is currently available."
        
    entry_recommendation_card = f"""
        <div style="
            box-sizing:border-box;
            width:100%;
            background:{entry_background};
            border:1px solid {entry_border};
            border-left:4px solid {entry_color};
            border-radius:12px;
            padding:20px 22px;
            font-family:Arial, sans-serif;
            box-shadow:0 4px 14px rgba(15,23,42,0.05);
        ">
        
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:18px;
                margin-bottom:16px;
            ">
        
                <div>
                    <div style="
                        font-size:13px;
                        color:#64748B;
                        font-weight:700;
                        text-transform:uppercase;
                        letter-spacing:0.5px;
                        margin-bottom:5px;
                    ">
                        Market Entry Recommendation
                    </div>
        
                    <div style="
                        font-size:23px;
                        color:#0F172A;
                        font-weight:700;
                    ">
                        {entry_signal}
                    </div>
                </div>
        
                <div style="
                    background:#FFFFFF;
                    border:1px solid {entry_border};
                    border-radius:10px;
                    padding:10px 16px;
                    text-align:center;
                    min-width:150px;
                ">
                    <div style="
                        font-size:12px;
                        color:#64748B;
                        font-weight:700;
                    ">
                        HIGH-POTENTIAL PRODUCTS
                    </div>
        
                    <div style="
                        font-size:27px;
                        color:{entry_color};
                        font-weight:700;
                    ">
                        {high_potential_count}
                    </div>
                </div>
        
            </div>
        
            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:16px;
                margin-bottom:15px;
            ">
        
                <div style="
                    background:rgba(255,255,255,0.75);
                    border-radius:9px;
                    padding:14px;
                ">
                    <div style="
                        font-size:13px;
                        color:#475569;
                        font-weight:700;
                        margin-bottom:6px;
                    ">
                        Market Insight
                    </div>
        
                    <div style="
                        font-size:14px;
                        color:#334155;
                        line-height:1.55;
                    ">
                        {entry_insight}
                    </div>
                </div>
        
                <div style="
                    background:rgba(255,255,255,0.75);
                    border-radius:9px;
                    padding:14px;
                ">
                    <div style="
                        font-size:13px;
                        color:#475569;
                        font-weight:700;
                        margin-bottom:6px;
                    ">
                        Recommended Action
                    </div>
        
                    <div style="
                        font-size:14px;
                        color:#334155;
                        line-height:1.55;
                    ">
                        {entry_recommendation}
                    </div>
                </div>
        
            </div>
        
            <div style="
                padding-top:12px;
                border-top:1px solid {entry_border};
                font-size:13px;
                color:#64748B;
                line-height:1.5;
            ">
                {best_product_text}
            </div>
        
        </div>
        """
        
    components.html(
            entry_recommendation_card,
            height=300,
            scrolling=False
        )

# -------------------------
# TAB 7 - STRATEGIC DECISION
# -------------------------
with tab5:

    st.markdown("## Strategic Decision")

    st.caption(
        "Executive summary and recommended decisions based on "
        "current market conditions and portfolio performance."
    )

    # =========================================================
    # 1. EXECUTIVE METRICS
    # =========================================================

    total_products = len(df)

    avg_margin = (
        df["active_margin"].mean()
        if total_products > 0
        else 0
    )

    avg_sales = (
        df["ASIN Sales"].mean()
        if total_products > 0
        else 0
    )

    avg_competitors = (
        df["Active Sellers"].mean()
        if total_products > 0
        else 0
    )

    profitable_products = (
        df[df["active_profit"] > 0]
        if total_products > 0
        else df
    )

    profitable_pct = (
        len(profitable_products) / total_products * 100
        if total_products > 0
        else 0
    )

    loss_products = (
        df[df["active_profit"] < 0]
        if total_products > 0
        else df
    )

    loss_pct = (
        len(loss_products) / total_products * 100
        if total_products > 0
        else 0
    )

    high_margin_products = (
        df[df["active_margin"] >= 30]
        if total_products > 0
        else df
    )

    high_margin_pct = (
        len(high_margin_products) / total_products * 100
        if total_products > 0
        else 0
    )

    # =========================================================
    # 2. GROWTH OPPORTUNITY SIGNAL
    # =========================================================

    high_potential_count = 0
    moderate_potential_count = 0

    try:
        if "entry_status" in entry_df.columns:

            high_potential_count = (
                entry_df["entry_status"]
                .eq("High Entry Potential")
                .sum()
            )

            moderate_potential_count = (
                entry_df["entry_status"]
                .eq("Moderate Potential")
                .sum()
            )

    except (NameError, AttributeError):
        high_potential_count = 0
        moderate_potential_count = 0

    # =========================================================
    # 3. DECISION SIGNALS
    # =========================================================

    # -------------------------
    # PROFITABILITY
    # -------------------------
    if avg_margin >= 30 and profitable_pct >= 75:

        profitability_label = "Strong"
        profitability_detail = (
            "Healthy margins and broad portfolio profitability."
        )
        profitability_color = "#16A34A"
        profitability_bg = "#F0FDF4"

    elif avg_margin >= 15 and profitable_pct >= 60:

        profitability_label = "Stable"
        profitability_detail = (
            "Positive profitability with selective optimization needs."
        )
        profitability_color = "#D97706"
        profitability_bg = "#FFFBEB"

    else:

        profitability_label = "Under Pressure"
        profitability_detail = (
            "Margins or product profitability require improvement."
        )
        profitability_color = "#DC2626"
        profitability_bg = "#FEF2F2"

    # -------------------------
    # COMPETITION
    # -------------------------
    if avg_competitors <= 8:

        competition_label = "Manageable"
        competition_detail = (
            "Competitive intensity remains favorable."
        )
        competition_color = "#16A34A"
        competition_bg = "#F0FDF4"

    elif avg_competitors <= 15:

        competition_label = "Moderate"
        competition_detail = (
            "Competition requires disciplined positioning."
        )
        competition_color = "#D97706"
        competition_bg = "#FFFBEB"

    else:

        competition_label = "High"
        competition_detail = (
            "Differentiation is required before aggressive expansion."
        )
        competition_color = "#DC2626"
        competition_bg = "#FEF2F2"

    # -------------------------
    # GROWTH OUTLOOK
    # -------------------------
    if high_potential_count >= 2:

        growth_label = "Positive"
        growth_detail = (
            f"{high_potential_count} products show high entry potential."
        )
        growth_color = "#16A34A"
        growth_bg = "#F0FDF4"

    elif high_potential_count == 1 or moderate_potential_count >= 2:

        growth_label = "Selective"
        growth_detail = (
            "Growth opportunities exist but require prioritization."
        )
        growth_color = "#D97706"
        growth_bg = "#FFFBEB"

    elif avg_sales >= 300:

        growth_label = "Conditional"
        growth_detail = (
            "Demand exists, but opportunity quality remains mixed."
        )
        growth_color = "#D97706"
        growth_bg = "#FFFBEB"

    else:

        growth_label = "Limited"
        growth_detail = (
            "Current conditions do not support broad expansion."
        )
        growth_color = "#DC2626"
        growth_bg = "#FEF2F2"

    # =========================================================
    # 4. OVERALL STRATEGIC SCORE
    # =========================================================

    strategic_score = 0

    # Profitability
    if avg_margin >= 30:
        strategic_score += 2
    elif avg_margin >= 15:
        strategic_score += 1
    else:
        strategic_score -= 2

    # Portfolio health
    if profitable_pct >= 75:
        strategic_score += 2
    elif profitable_pct >= 60:
        strategic_score += 1
    elif loss_pct > 25:
        strategic_score -= 2

    # Competition
    if avg_competitors <= 8:
        strategic_score += 2
    elif avg_competitors <= 15:
        strategic_score += 1
    else:
        strategic_score -= 1

    # Growth opportunities
    if high_potential_count >= 2:
        strategic_score += 2
    elif high_potential_count == 1:
        strategic_score += 1
    elif moderate_potential_count >= 2:
        strategic_score += 1

    # =========================================================
    # 5. EXECUTIVE RECOMMENDATION
    # =========================================================

    if strategic_score >= 7:

        recommendation = "SCALE"

        recommendation_text = (
            "Current market conditions support expansion. "
            "Profitability, competition and opportunity signals "
            "are aligned with additional investment."
        )

        recommendation_color = "#15803D"
        recommendation_bg = "#F0FDF4"
        recommendation_border = "#22C55E"

    elif strategic_score >= 4:

        recommendation = "CONTROLLED EXPANSION"

        recommendation_text = (
            "The market presents attractive conditions, but growth "
            "should remain selective and focused on the strongest opportunities."
        )

        recommendation_color = "#166534"
        recommendation_bg = "#F0FDF4"
        recommendation_border = "#4ADE80"

    elif strategic_score >= 1:

        recommendation = "OPTIMIZE BEFORE SCALING"

        recommendation_text = (
            "The market shows potential, but profitability, positioning "
            "or competitive conditions should improve before increasing investment."
        )

        recommendation_color = "#92400E"
        recommendation_bg = "#FFFBEB"
        recommendation_border = "#F59E0B"

    else:

        recommendation = "AVOID AGGRESSIVE EXPANSION"

        recommendation_text = (
            "Current conditions do not support broad expansion. "
            "Prioritize risk reduction and operational optimization."
        )

        recommendation_color = "#991B1B"
        recommendation_bg = "#FEF2F2"
        recommendation_border = "#EF4444"

    # =========================================================
    # 6. EXECUTIVE RECOMMENDATION CARD
    # =========================================================

    recommendation_card = f"""
    <div style="
        background:{recommendation_bg};
        border:1px solid {recommendation_border};
        border-left:7px solid {recommendation_border};
        border-radius:16px;
        padding:24px 26px;
        box-shadow:0px 6px 18px rgba(15,23,42,0.06);
        font-family:Arial, sans-serif;
    ">

        <div style="
            font-size:12px;
            font-weight:700;
            letter-spacing:1.3px;
            color:#64748B;
            margin-bottom:10px;
        ">
            EXECUTIVE RECOMMENDATION
        </div>

        <div style="
            font-size:27px;
            font-weight:800;
            color:{recommendation_color};
            margin-bottom:10px;
        ">
            {recommendation}
        </div>

        <div style="
            font-size:15px;
            color:#334155;
            line-height:1.6;
            max-width:900px;
        ">
            {recommendation_text}
        </div>

    </div>
    """

    components.html(
        recommendation_card,
        height=190
    )

    # =========================================================
    # 7. DECISION SIGNALS
    # =========================================================

    st.markdown("### Decision Signals")

    signal_col1, signal_col2, signal_col3 = st.columns(3)

    def decision_signal_card(
        title,
        value,
        detail,
        color,
        background
    ):
        return f"""
        <div style="
            background:{background};
            border:1px solid #E2E8F0;
            border-top:5px solid {color};
            border-radius:14px;
            padding:18px;
            min-height:145px;
            box-shadow:0px 4px 12px rgba(15,23,42,0.04);
            font-family:Arial, sans-serif;
        ">

            <div style="
                font-size:12px;
                font-weight:700;
                letter-spacing:0.8px;
                color:#64748B;
                margin-bottom:10px;
            ">
                {title.upper()}
            </div>

            <div style="
                font-size:21px;
                font-weight:800;
                color:{color};
                margin-bottom:9px;
            ">
                {value}
            </div>

            <div style="
                font-size:13.5px;
                color:#475569;
                line-height:1.45;
            ">
                {detail}
            </div>

        </div>
        """

    with signal_col1:
        components.html(
            decision_signal_card(
                "Profitability",
                profitability_label,
                profitability_detail,
                profitability_color,
                profitability_bg
            ),
            height=175
        )

    with signal_col2:
        components.html(
            decision_signal_card(
                "Competition",
                competition_label,
                competition_detail,
                competition_color,
                competition_bg
            ),
            height=175
        )

    with signal_col3:
        components.html(
            decision_signal_card(
                "Growth Outlook",
                growth_label,
                growth_detail,
                growth_color,
                growth_bg
            ),
            height=175
        )

    # =========================================================
    # 8. RECOMMENDED ACTIONS
    # =========================================================

    recommended_actions = []

    if high_potential_count > 0:

        recommended_actions.append(
            "Prioritize products classified as High Entry Potential."
        )

    elif moderate_potential_count > 0:

        recommended_actions.append(
            "Validate moderate-potential products before committing additional capital."
        )

    else:

        recommended_actions.append(
            "Maintain a selective market approach until stronger opportunities emerge."
        )

    if avg_margin < 20 or loss_pct > 15:

        recommended_actions.append(
            "Improve margins and correct unprofitable products before scaling investment."
        )

    else:

        recommended_actions.append(
            "Protect current margins while selectively increasing investment."
        )

    if avg_competitors > 15:

        recommended_actions.append(
            "Strengthen differentiation before competing more aggressively."
        )

    elif avg_competitors > 8:

        recommended_actions.append(
            "Monitor competitive pressure and maintain disciplined positioning."
        )

    else:

        recommended_actions.append(
            "Use the manageable competitive environment to consolidate market position."
        )

    actions_html = ""

    for index, action in enumerate(
        recommended_actions[:3],
        start=1
    ):
        actions_html += f"""
        <div style="
            display:flex;
            align-items:flex-start;
            gap:13px;
            padding:13px 0;
            border-bottom:1px solid #E2E8F0;
        ">

            <div style="
                min-width:28px;
                height:28px;
                border-radius:50%;
                background:#0F172A;
                color:#FFFFFF;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:13px;
                font-weight:700;
            ">
                {index}
            </div>

            <div style="
                font-size:14.5px;
                color:#334155;
                line-height:1.5;
                padding-top:3px;
            ">
                {action}
            </div>

        </div>
        """

    actions_card = f"""
    <div style="
        background:#FFFFFF;
        border:1px solid #E2E8F0;
        border-radius:15px;
        padding:20px 22px 10px 22px;
        box-shadow:0px 5px 15px rgba(15,23,42,0.05);
        font-family:Arial, sans-serif;
    ">

        <div style="
            font-size:12px;
            font-weight:700;
            letter-spacing:1px;
            color:#64748B;
            margin-bottom:5px;
        ">
            PRIORITY ACTIONS
        </div>

        {actions_html}

    </div>
    """

    st.markdown("### Recommended Actions")

    components.html(
        actions_card,
        height=245
    )

    # =========================================================
    # 9. EXECUTIVE CONCLUSION
    # =========================================================

    if recommendation == "SCALE":

        executive_conclusion = (
            "The market presents favorable conditions for expansion. "
            "Profitability is healthy, competitive pressure remains manageable "
            "and multiple products demonstrate attractive growth potential. "
            "Investment can be increased while maintaining disciplined execution."
        )

    elif recommendation == "CONTROLLED EXPANSION":

        executive_conclusion = (
            "The market supports selective expansion. The strongest opportunities "
            "combine healthy profitability, manageable competition and positive "
            "demand conditions. Investment should remain concentrated on validated "
            "products rather than broad portfolio growth."
        )

    elif recommendation == "OPTIMIZE BEFORE SCALING":

        executive_conclusion = (
            "The market contains viable opportunities, but current conditions do not "
            "justify aggressive expansion. Improving margins, listing performance and "
            "product selection should precede additional investment."
        )

    else:

        executive_conclusion = (
            "The current market structure presents elevated risk and limited expansion "
            "potential. Capital should remain protected while profitability, competitive "
            "positioning and product selection are reassessed."
        )

    conclusion_card = f"""
    <div style="
        background:#F8FAFC;
        border:1px solid #CBD5E1;
        border-left:6px solid #475569;
        border-radius:15px;
        padding:21px 23px;
        box-shadow:0px 4px 12px rgba(15,23,42,0.04);
        font-family:Arial, sans-serif;
    ">

        <div style="
            font-size:12px;
            font-weight:700;
            letter-spacing:1px;
            color:#64748B;
            margin-bottom:9px;
        ">
            EXECUTIVE CONCLUSION
        </div>

        <div style="
            font-size:15px;
            color:#334155;
            line-height:1.65;
        ">
            {executive_conclusion}
        </div>

    </div>
    """

    st.markdown("### Executive Conclusion")

    components.html(
        conclusion_card,
        height=175
    )

    # =========================================================
    # 10. CONSULTING CTA
    # =========================================================

    st.markdown("---")

    cta_col1, cta_col2 = st.columns(
        [3, 1],
        vertical_alignment="center"
    )

    with cta_col1:

        st.markdown("#### Need help executing this strategy?")

        st.caption(
            "Turn market intelligence into a focused and measurable action plan."
        )

    with cta_col2:

        st.link_button(
            "Book a Strategy Call",
            "mailto:consultora@kpistudio.net",
            use_container_width=True
        )



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
        # DATA
        # -------------------------
                
        avg_profit_val = df["active_profit"].mean()
        avg_margin_val = df["active_margin"].mean()
        avg_sellers_val = df["Active Sellers"].mean()
        
        low_margin = df[df["active_margin"] < 15]
        high_margin = df[df["active_margin"] >= 30]
        
        low_pct_val = (
            len(low_margin) / len(df)
            if len(df) > 0
            else 0
        )
        
        high_pct_val = (
            len(high_margin) / len(df)
            if len(df) > 0
            else 0
        )

        # -------------------------
        # 🧠 SMART INSIGHT
        # -------------------------
        strategy_text = executive_conclusion

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
            margin: 0;
            background: #F5F7FA;
        }}

        .banner {{
            display: block;
            width: 100%;
            margin: 0;
            padding: 0;
        }}

        .container {{
            padding: 20px 28px 8px 28px;
        }}

        .title {{
            font-size: 28px;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 4px;
        }}

        .subtitle {{
            font-size: 14px;
            color: #64748B;
            margin-bottom: 10px;
        }}

        .gold-line {{
            width: 100%;
            height: 4px;
            background: #D4AF37;
            margin-bottom: 16px;
        }}

        .date {{
            font-size: 13px;
            color: #6B7280;
            margin-bottom: 12px;
        }}

        /* KPI ROW */

        .kpi-row {{
            display: table;
            width: 100%;
            table-layout: fixed;
            background: #0B1A2B;
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 18px;
        }}

        .kpi {{
            display: table-cell;
            text-align: center;
            vertical-align: middle;
            padding: 20px 8px;
            color: #D4AF37;
            border-right: 1px solid #D4AF37;
        }}

        .kpi:last-child {{
            border-right: none;
        }}

        .kpi h2 {{
            margin: 0;
            font-size: 34px;
            font-weight: 700;
        }}

        .kpi p {{
            margin: 3px 0 0 0;
            font-size: 11px;
            letter-spacing: 0.8px;
            opacity: 0.9;
        }}

        /* CARDS */

        .card {{
            background: white;
            border-radius: 14px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.05);
            border-left: 6px solid;
            page-break-inside: avoid;
        }}

        .card-title {{
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .blue {{
            border-color: #3B82F6;
        }}

        .cyan {{
            border-color: #06B6D4;
        }}

        .green {{
            border-color: #22C55E;
        }}

        .orange {{
            border-color: #F97316;
        }}

        /* STRATEGY */

        .strategy {{
            background: #0F172A;
            color: white;
            padding: 16px;
            border-radius: 14px;
            margin-top: 14px;
            page-break-inside: avoid;
        }}

        /* FOOTER */

        .footer {{
            margin-top: 10px;
            padding-top: 8px;
            padding-bottom: 0;
            font-size: 11px;
            color: #6B7280;
            text-align: center;
            border-top: 1px solid #E5E7EB;
            page-break-inside: avoid;
        }}

        </style>

        </head>

        <body>

        <img src="{banner_base64}" class="banner">

        <div class="container">

            <div class="title">
                Executive Market Assessment
            </div>

            <div class="subtitle">
                Amazon FBA Market Intelligence Report
            </div>

            <div class="gold-line"></div>

            <div class="date">
                Date: {today}
            </div>

            <!-- KPI ROW -->

            <div class="kpi-row">

                <div class="kpi">
                    <h2>${avg_profit_val:,.0f}</h2>
                    <p>AVG. PROFIT</p>
                </div>

                <div class="kpi">
                    <h2>{avg_margin_val:.1f}%</h2>
                    <p>REAL MARGIN</p>
                </div>

                <div class="kpi">
                    <h2>{avg_sellers_val:.0f}</h2>
                    <p>AVG. SELLERS PER LISTING</p>
                </div>

                <div class="kpi">
                    <h2>{high_potential_count}</h2>
                    <p>HIGH-POTENTIAL PRODUCTS</p>
                </div>

                <div class="kpi">
                    <h2>{recommendation}</h2>
                    <p>EXECUTIVE DECISION</p>
                </div>

            </div>

            <!-- PROFITABILITY -->

            <div class="card blue">

                <div class="card-title">
                    Profitability
                </div>

                Average real margin is
                <b>{avg_margin_val:.1f}%</b>
                with
                <b>{profitable_pct:.0f}%</b>
                of products generating positive profit.

            </div>

            <!-- COMPETITION -->

            <div class="card cyan">

                <div class="card-title">
                    Competition
                </div>

                The market averages
                <b>{avg_sellers_val:.0f}</b>
                active competitors per listing, indicating
                <b>{competition_label}</b>
                competitive conditions.

            </div>

            <!-- GROWTH OUTLOOK -->

            <div class="card green">

                <div class="card-title">
                    Growth Outlook
                </div>

                The portfolio currently contains
                <b>{high_potential_count}</b>
                High Entry Potential products and
                <b>{moderate_potential_count}</b>
                Moderate Potential opportunities.

            </div>

            <!-- EXECUTIVE RECOMMENDATION -->

            <div class="card orange">

                <div class="card-title">
                    Executive Recommendation
                </div>

                <b>{recommendation}</b>

            </div>

            <!-- STRATEGY -->

            <div class="strategy">
                <b>Strategic Insight</b><br><br>
                {strategy_text}
            </div>

            <!-- FOOTER -->

            <div class="footer">

                <div style="
                    font-size: 11px;
                    color: #334155;
                    margin-bottom: 4px;
                ">
                    <b>Strategy Call:</b> consultora@kpistudio.net
                </div>

                <b>KPI Studio</b>
                &copy; {today}
                &mdash; Confidential Report
                <br>

                <span style="
                    font-size: 9px;
                    color: #9CA3AF;
                ">
                    Automatically generated using KPI Studio proprietary market
                    intelligence models.
                </span>

            </div>

        </div>

        </body>
        </html>
        """

        # -------------------------
        # 📄 PDF
        # -------------------------
        config = pdfkit.configuration(
            wkhtmltopdf=(
                r"C:\Program Files\wkhtmltopdf"
                r"\bin\wkhtmltopdf.exe"
            )
        )

        options = {
            "enable-local-file-access": "",
            "quiet": "",
            "page-size": "A4",
            "margin-top": "0mm",
            "margin-right": "0mm",
            "margin-bottom": "0mm",
            "margin-left": "0mm",
            "disable-smart-shrinking": "",
            "encoding": "UTF-8"
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


with tab7:

    st.markdown("## Model Validation")

    st.caption(
        "Evaluate the internal consistency of the market intelligence model. Correlation analysis helps verify that key indicators behave in line with expected market dynamics."
        "Correlations indicate association, not causal validation."
    )

    # -------------------------
    # DATASET DE VALIDACIÓN
    # -------------------------

    validation_df = df.copy()

    validation_columns = [
        "ASIN Sales",
        "Revenue",
        "Review Count",
        "listing_score",
        "advertising_dependency_score",
        "active_profit",
        "active_margin",
        "BSR"
    ]

    available_validation_columns = [
        col for col in validation_columns
        if col in validation_df.columns
    ]

    for col in available_validation_columns:
        validation_df[col] = pd.to_numeric(
            validation_df[col],
            errors="coerce"
        )

    validation_df = validation_df[
        available_validation_columns
    ].replace([np.inf, -np.inf], np.nan)

    # -------------------------
    # CORRELACIONES SPEARMAN
    # -------------------------

    correlation_matrix = validation_df.corr(
        method="spearman"
    )

    target_correlations = {
        "Sales": correlation_matrix.loc[
            "ASIN Sales",
            "active_profit"
        ] if {
            "ASIN Sales",
            "active_profit"
        }.issubset(correlation_matrix.columns) else np.nan,

        "Revenue": correlation_matrix.loc[
            "Revenue",
            "active_profit"
        ] if {
            "Revenue",
            "active_profit"
        }.issubset(correlation_matrix.columns) else np.nan,

        "Listing Strength": correlation_matrix.loc[
            "listing_score",
            "active_profit"
        ] if {
            "listing_score",
            "active_profit"
        }.issubset(correlation_matrix.columns) else np.nan,

        "Advertising Dependency": correlation_matrix.loc[
            "advertising_dependency_score",
            "active_profit"
        ] if {
            "advertising_dependency_score",
            "active_profit"
        }.issubset(correlation_matrix.columns) else np.nan
    }

    # -------------------------
    # KPI CARDS
    # -------------------------

    val_col1, val_col2, val_col3, val_col4 = st.columns(4)

    def format_corr(value):
        return "N/A" if pd.isna(value) else f"{value:.2f}"

    val_col1.metric(
        "Profit vs Sales",
        format_corr(target_correlations["Sales"])
    )

    val_col2.metric(
        "Profit vs Revenue",
        format_corr(target_correlations["Revenue"])
    )

    val_col3.metric(
        "Profit vs Listing",
        format_corr(target_correlations["Listing Strength"])
    )

    val_col4.metric(
        "Profit vs Ad Dependency",
        format_corr(target_correlations["Advertising Dependency"])
    )

    st.divider()

    # -------------------------
    # MATRIZ DE CORRELACIÓN
    # -------------------------

    st.markdown("### Market Intelligence Correlation Matrix")

    st.caption(
        "Spearman correlation is used because Amazon market variables "
        "are often non-linear and contain outliers."
    )

    readable_names = {
        "ASIN Sales": "Sales",
        "Revenue": "Revenue",
        "Review Count": "Reviews",
        "listing_score": "Listing Strength",
        "advertising_dependency_score": "Ad Dependency",
        "active_profit": "Estimated Real Profit",
        "active_margin": "Estimated Real Margin",
        "BSR": "BSR"
    }

    display_corr = correlation_matrix.rename(
        index=readable_names,
        columns=readable_names
    )

# -------------------------
# CORRELATION MATRIX TABLE
# -------------------------

# -------------------------
# MARKET INTELLIGENCE CORRELATION MATRIX
# -------------------------
    
    fig_validation = px.imshow(
        display_corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1
    )
    
    fig_validation.update_layout(
        height=600,
        coloraxis_colorbar_title="Correlation",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            size=13,
            color="#334155"
        )
    )
    
    fig_validation.update_traces(
        textfont=dict(size=14)
    )
    
    st.plotly_chart(
        fig_validation,
        use_container_width=True
    )
# -------------------------
# MODEL ASSESSMENT
# -------------------------
    profit_sales_corr = target_correlations["Sales"]
    profit_revenue_corr = target_correlations["Revenue"]
    profit_listing_corr = target_correlations["Listing Strength"]
    profit_ad_corr = target_correlations["Advertising Dependency"]    
    
    st.markdown("### Model Assessment")
    
    if all(
        not pd.isna(v)
        for v in target_correlations.values()
    ):
    
        assessment = (
            "The validation results indicate that the model behaves consistently "
            "with expected market dynamics. Estimated profitability shows a strong "
            "positive association with both sales and revenue, while advertising "
            "dependency exhibits a pronounced negative relationship. These findings "
            "support the internal coherence of the scoring methodology, although "
            "they should not be interpreted as causal evidence."
        )
    
    elif (
        not pd.isna(target_correlations["Sales"])
        and not pd.isna(target_correlations["Revenue"])
    ):
    
        assessment = (
            "The model demonstrates moderate internal consistency. Core financial "
            "variables exhibit meaningful relationships, although some indicators "
            "show weaker associations and should be interpreted with caution."
        )
    
    else:
    
        assessment = (
            "The current dataset does not contain sufficient statistical evidence "
            "to evaluate the internal consistency of the market intelligence model."
        )
    
    
    assessment_card = f"""
    <div style="
        background:#F8FAFC;
        border:1px solid #CBD5E1;
        border-left:6px solid #2563EB;
        border-radius:15px;
        padding:22px;
        box-shadow:0px 5px 14px rgba(15,23,42,0.05);
        font-family:Arial,sans-serif;
    ">
    
    <div style="
        font-size:12px;
        font-weight:700;
        letter-spacing:1px;
        color:#64748B;
        margin-bottom:10px;
    ">
    MODEL ASSESSMENT
    </div>
    
    <div style="
        font-size:15px;
        line-height:1.65;
        color:#334155;
    ">
    {assessment}
    </div>
    
    </div>
    """
    
    components.html(
        assessment_card,
        height=185
    )
    st.markdown("### Methodological Note")
    
    st.info(
        "This analysis evaluates the internal consistency of KPI Studio's "
        "market intelligence model using Spearman correlation. The results "
        "support the reliability of the scoring framework, but they should "
        "not be interpreted as proof of causal relationships or actual "
        "competitor financial performance."
    )

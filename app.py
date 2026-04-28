import streamlit as st
import pandas as pd
import numpy as np

import streamlit as st
import pandas as pd
import os
import plotly.express as px


import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Análisis Comercial", layout="wide")

st.markdown("## 📈 Análisis Comercial de Operaciones")

# ---------------- LOAD ----------------
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    mov = pd.read_excel(os.path.join(base_path, "2024mov.xlsx"))
    rec = pd.read_excel(os.path.join(base_path, "recep2024.xlsx"))

    mov.columns = mov.columns.str.strip()
    rec.columns = rec.columns.str.strip()

    # Ajustá nombres si difieren
    mov["Fecha"] = pd.to_datetime(mov["Fecha"], errors="coerce")

    return mov, rec

mov, rec = load_data()

# ---------------- NORMALIZACIÓN ----------------
col_producto = mov.columns[0]
col_tipo = mov.columns[1]

mov["Año"] = mov["Fecha"].dt.year

# ---------------- FILTROS ----------------
st.sidebar.header("🔎 Filtros")

años = mov["Año"].dropna().unique()
año_sel = st.sidebar.selectbox("Año", sorted(años))

productos = mov[col_producto].dropna().unique()
prod_sel = st.sidebar.selectbox("Producto (opcional)", ["Todos"] + list(productos))

df = mov[mov["Año"] == año_sel]

if prod_sel != "Todos":
    df = df[df[col_producto] == prod_sel]

# ---------------- KPIs ----------------
st.markdown("### 📊 Indicadores Clave")

col1, col2, col3, col4, col5 = st.columns(5)

ventas = df[df[col_tipo].astype(str).str.contains("VENTA", case=False, na=False)]
traslados = df[df[col_tipo].str.contains("TRAS", case=False, na=False)]
devol = df[df[col_tipo].str.contains("DEV", case=False, na=False)]

col1.metric("Operaciones Totales", len(df))
col2.metric("Ventas", len(ventas))
col3.metric("Traslados", len(traslados))
col4.metric("Devoluciones", len(devol))
col5.metric("Productos Únicos", df[col_producto].nunique())

# ---------------- TOP PRODUCTOS ----------------
st.markdown("### 🏆 Productos con mayor movimiento")

top = (
    ventas[col_producto]
    .value_counts()
    .head(20)
)

fig_top = px.bar(
    x=top.values,
    y=top.index,
    orientation="h",
    title="Top productos (ventas)",
)

fig_top.update_layout(height=500)

st.plotly_chart(fig_top, use_container_width=True)

# ---------------- TOP POR AÑO ----------------
st.markdown("### 📅 Evolución de ventas por año")

ventas_anuales = (
    mov[mov[col_tipo].str.contains("VENTA", case=False, na=False)]
    .groupby("Año")
    .size()
)

fig_year = px.line(
    x=ventas_anuales.index,
    y=ventas_anuales.values,
    markers=True,
    title="Ventas por año"
)

st.plotly_chart(fig_year, use_container_width=True)

# ---------------- FLUJO (SANKEY) ----------------
st.markdown("### 🔁 Flujo de operaciones")

flow = df.groupby(col_tipo).size().reset_index()
flow.columns = ["tipo", "cantidad"]

labels = list(flow["tipo"])
values = list(flow["cantidad"])

source = [0]*len(values)
target = list(range(len(values)))

fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(label=["Operaciones"] + labels),
    link=dict(
        source=[0]*len(labels),
        target=list(range(1, len(labels)+1)),
        value=values
    )
)])

fig_sankey.update_layout(height=400)

st.plotly_chart(fig_sankey, use_container_width=True)

# ---------------- DETALLE ----------------
st.markdown("### 📋 Detalle de datos")

st.dataframe(df, use_container_width=True)

# ---------------- ORIGEN ----------------
st.markdown("### ℹ️ Fuente de información")

st.markdown("""
- Movimientos: **2024mov.xlsx**
- Recepciones: **recep2024.xlsx**
- Tipos: ventas, traslados, devoluciones
""")

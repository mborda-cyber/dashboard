import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Análisis Comercial", layout="wide")

st.markdown("## 📈 Análisis Comercial de Operaciones")

# ---------------- LOAD ----------------
@st.cache_data
def load_data():
    mov = pd.read_excel("2024mov.xlsx")
    rec = pd.read_excel("recep2024.xlsx")

    mov.columns = mov.columns.str.strip()
    rec.columns = rec.columns.str.strip()

    if "Fecha" not in mov.columns:
        st.error("❌ No se encontró la columna 'Fecha'")
        st.stop()

    mov["Fecha"] = pd.to_datetime(mov["Fecha"], errors="coerce")
    mov["Año"] = mov["Fecha"].dt.year

    return mov, rec

mov, rec = load_data()

# ---------------- COLUMNAS ----------------
col_producto = mov.columns[0]
col_tipo = mov.columns[1]

# ---------------- FILTROS ----------------
st.sidebar.header("🔎 Filtros")

años = mov["Año"].dropna().unique()
año_sel = st.sidebar.selectbox("Año", sorted(años))

productos = mov[col_producto].dropna().unique()
prod_sel = st.sidebar.selectbox("Producto (opcional)", ["Todos"] + list(productos))

df = mov[mov["Año"] == año_sel].copy()
df[col_tipo] = df[col_tipo].astype(str)

if prod_sel != "Todos":
    df = df[df[col_producto] == prod_sel]

# ---------------- FUNCION SEGURA ----------------
def contains_safe(series, text):
    return series.astype(str).str.contains(text, case=False, na=False)

# ---------------- KPIs ----------------
st.markdown("### 📊 Indicadores Clave")

col1, col2, col3, col4, col5 = st.columns(5)

ventas = df[contains_safe(df[col_tipo], "VENTA")]
traslados = df[contains_safe(df[col_tipo], "TRAS")]
devol = df[contains_safe(df[col_tipo], "DEV")]

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

if len(top) > 0:
    top_df = top.reset_index()
    top_df.columns = ["producto", "cantidad"]

    fig_top = px.bar(
        top_df,
        x="cantidad",
        y="producto",
        orientation="h",
        title="Top productos (ventas)",
    )

    fig_top.update_layout(height=500)
    st.plotly_chart(fig_top, use_container_width=True)
else:
    st.warning("No hay datos de ventas para mostrar")

# ---------------- TOP POR AÑO ----------------
st.markdown("### 📅 Evolución de ventas por año")

mov[col_tipo] = mov[col_tipo].astype(str)

ventas_anuales = (
    mov[contains_safe(mov[col_tipo], "VENTA")]
    .groupby("Año")
    .size()
)

if len(ventas_anuales) > 0:
    fig_year = px.line(
        x=ventas_anuales.index,
        y=ventas_anuales.values,
        markers=True,
        title="Ventas por año"
    )

    st.plotly_chart(fig_year, use_container_width=True)
else:
    st.warning("No hay datos históricos de ventas")

# ---------------- FLUJO (SANKEY) ----------------
st.markdown("### 🔁 Flujo de operaciones")

flow = df.groupby(col_tipo).size().reset_index()
flow.columns = ["tipo", "cantidad"]

if len(flow) > 0:
    labels = ["Operaciones"] + list(flow["tipo"])
    values = list(flow["cantidad"])

    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(label=labels),
        link=dict(
            source=[0] * len(values),
            target=list(range(1, len(values) + 1)),
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

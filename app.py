import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.title("📊 Dashboard Comercial - Agroinsumos")

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def load_data():
    mov = pd.read_excel("2024mov.xlsx")
    rec = pd.read_excel("recep2024.xlsx")

    mov.columns = mov.columns.str.strip()
    rec.columns = rec.columns.str.strip()

    mov["Fecha"] = pd.to_datetime(mov["Fecha"])
    rec["Fecha"] = pd.to_datetime(rec["Fecha"])

    return mov, rec

mov, rec = load_data()

# =========================
# FILTROS
# =========================
st.sidebar.header("Filtros")

fecha_min = mov["Fecha"].min()
fecha_max = mov["Fecha"].max()

rango = st.sidebar.date_input("Rango de fechas", [fecha_min, fecha_max])

mov = mov[(mov["Fecha"] >= pd.to_datetime(rango[0])) &
          (mov["Fecha"] <= pd.to_datetime(rango[1]))]

# =========================
# DATOS BASE
# =========================
sales = mov[mov["Documento"] == "Remito de Venta"].copy()
sales.rename(columns={"Cantidad ": "Cantidad"}, inplace=True)

compras = rec.copy()
compras.rename(columns={"Cantidad primaria": "Cantidad"}, inplace=True)

ventas_prod = sales.groupby("Producto")["Cantidad"].sum()
compras_prod = compras.groupby("Producto")["Cantidad"].sum()

# STOCK ESTIMADO
stock = compras_prod.subtract(ventas_prod, fill_value=0)

# =========================
# KPIs
# =========================
st.subheader("📌 Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Ventas totales", f"{ventas_prod.sum():,.0f}")
col2.metric("Compras totales", f"{compras_prod.sum():,.0f}")
col3.metric("Stock estimado", f"{stock.sum():,.0f}")

# =========================
# TOP PRODUCTOS
# =========================
st.subheader("🏆 Top productos")

top = ventas_prod.sort_values(ascending=False).head(10)
st.bar_chart(top)

# =========================
# PARETO
# =========================
st.subheader("📊 Pareto")

top20 = ventas_prod.sort_values(ascending=False).head(20)
cum = top20.cumsum() / top20.sum()

pareto_df = pd.DataFrame({
    "Ventas": top20,
    "% acumulado": cum
})

st.line_chart(pareto_df)

# =========================
# STOCK INTELIGENTE
# =========================
st.subheader("📦 Stock inteligente")

df_stock = pd.DataFrame({
    "Stock": stock,
    "Ventas": ventas_prod
}).fillna(0)

df_stock["Venta diaria"] = df_stock["Ventas"] / 30
df_stock["Cobertura (días)"] = df_stock["Stock"] / df_stock["Venta diaria"]
df_stock.replace([np.inf, -np.inf], 0, inplace=True)

st.dataframe(df_stock.sort_values("Stock", ascending=False))

# =========================
# ALERTAS
# =========================
st.subheader("🚨 Alertas")

criticos = df_stock[df_stock["Cobertura (días)"] < 15]
sobrestock = df_stock[df_stock["Cobertura (días)"] > 120]

col1, col2 = st.columns(2)

with col1:
    st.write("🔴 Stock crítico")
    st.dataframe(criticos.head(10))

with col2:
    st.write("🟡 Sobrestock")
    st.dataframe(sobrestock.head(10))

# =========================
# COMPRAS VS VENTAS
# =========================
st.subheader("📈 Compras vs Ventas")

sales["Mes"] = sales["Fecha"].dt.to_period("M")
compras["Mes"] = compras["Fecha"].dt.to_period("M")

ventas_mes = sales.groupby("Mes")["Cantidad"].sum()
compras_mes = compras.groupby("Mes")["Cantidad"].sum()

df_mes = pd.DataFrame({
    "Ventas": ventas_mes,
    "Compras": compras_mes
}).fillna(0)

st.line_chart(df_mes)

# =========================
# ROTACIÓN
# =========================
st.subheader("🔄 Rotación")

df_stock["Rotación"] = df_stock["Ventas"] / df_stock["Stock"]
df_stock.replace([np.inf, -np.inf], 0, inplace=True)

st.dataframe(df_stock.sort_values("Rotación", ascending=False).head(20))

# =========================
# RECOMENDADOR
# =========================
st.subheader("🤖 Recomendaciones")

recomendaciones = df_stock.copy()

recomendaciones["Sugerido comprar"] = np.where(
    recomendaciones["Cobertura (días)"] < 20,
    recomendaciones["Ventas"] * 0.5,
    0
)

st.dataframe(
    recomendaciones[recomendaciones["Sugerido comprar"] > 0]
    .sort_values("Sugerido comprar", ascending=False)
    .head(10)
)
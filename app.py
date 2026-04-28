import streamlit as st
import pandas as pd
import numpy as np

import streamlit as st
import pandas as pd
import os
import plotly.express as px

# CONFIGURACIÓN GENERAL
st.set_page_config(page_title="Dashboard Comercial", layout="wide")

st.title("📊 Dashboard Comercial - Agroinsumos")

# CARGA DE DATOS
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    
    mov = pd.read_excel(os.path.join(base_path, "2024mov.xlsx"))
    rec = pd.read_excel(os.path.join(base_path, "recep2024.xlsx"))

    mov.columns = mov.columns.str.strip()
    rec.columns = rec.columns.str.strip()

    return mov, rec

mov, rec = load_data()

# LIMPIEZA BÁSICA
# (ajustá nombres si en tu excel son distintos)
col_producto = mov.columns[0]
col_tipo = mov.columns[1]

# FILTRO POR TIPO DE MOVIMIENTO
st.subheader("🔎 Filtro de movimientos")

tipos = mov[col_tipo].dropna().unique()
tipo_seleccionado = st.selectbox("Seleccionar tipo de movimiento", tipos)

mov_filtrado = mov[mov[col_tipo] == tipo_seleccionado]

# TOP PRODUCTOS
st.subheader("🏆 Top 50 Productos")

top_productos = (
    mov_filtrado[col_producto]
    .value_counts()
    .head(50)
)

fig = px.bar(
    x=top_productos.index,
    y=top_productos.values,
    labels={'x': 'Producto', 'y': 'Cantidad'},
    title=f"Top 50 Productos - {tipo_seleccionado}"
)

fig.update_layout(
    width=900,
    height=500
)

st.plotly_chart(fig, use_container_width=False)

# TABLA DETALLE
st.subheader("📋 Detalle de movimientos")

st.dataframe(mov_filtrado, use_container_width=True)

# INFORMACIÓN DE ORIGEN
st.subheader("ℹ️ Origen de los datos")

st.markdown("""
- Archivo de movimientos: **2024mov.xlsx**
- Archivo de recepciones: **recep2024.xlsx**
- Tipos incluidos: ventas, traslados, devoluciones
""")

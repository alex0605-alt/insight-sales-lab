from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics import calculate_kpis, monthly_performance
from src.paths import CLEAN_SALES_PATH

st.set_page_config(page_title="Insight Sales Lab", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #f5f6f2; }
    [data-testid="stMetric"] { background: white; border: 1px solid #e3e6df; padding: 18px; border-radius: 14px; }
    h1, h2, h3 { letter-spacing: -0.03em; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(CLEAN_SALES_PATH, parse_dates=["order_date"])


data = load_data()
st.sidebar.title("Filtros")
date_min, date_max = data["order_date"].min().date(), data["order_date"].max().date()
date_range = st.sidebar.date_input("Periodo", (date_min, date_max), min_value=date_min, max_value=date_max)
regions = st.sidebar.multiselect("Región", sorted(data["region"].unique()), default=sorted(data["region"].unique()))
channels = st.sidebar.multiselect("Canal", sorted(data["channel"].unique()), default=sorted(data["channel"].unique()))
categories = st.sidebar.multiselect("Categoría", sorted(data["category"].unique()), default=sorted(data["category"].unique()))

start_date, end_date = date_range if len(date_range) == 2 else (date_min, date_max)
filtered = data[
    data["order_date"].dt.date.between(start_date, end_date)
    & data["region"].isin(regions)
    & data["channel"].isin(channels)
    & data["category"].isin(categories)
]

st.caption("INSIGHT SALES LAB · RETAIL ANALYTICS")
st.title("Panel ejecutivo de ventas")
st.write("Visión integrada de ingresos, rentabilidad, clientes y calidad comercial.")

if filtered.empty:
    st.warning("No hay datos con la combinación de filtros seleccionada.")
    st.stop()

kpis = calculate_kpis(filtered)
columns = st.columns(5)
columns[0].metric("Ingresos netos", f"${kpis['net_revenue']:,.0f}")
columns[1].metric("Utilidad bruta", f"${kpis['gross_profit']:,.0f}")
columns[2].metric("Margen bruto", f"{kpis['gross_margin_pct']:.1f}%")
columns[3].metric("Pedidos", f"{kpis['orders']:,}")
columns[4].metric("Devoluciones", f"{kpis['return_rate_pct']:.1f}%")

monthly = monthly_performance(filtered)
revenue_chart = px.area(monthly, x="month", y="net_revenue", markers=True, color_discrete_sequence=["#176b52"])
revenue_chart.update_layout(title="Evolución mensual de ingresos", xaxis_title="Mes", yaxis_title="Ingresos netos", plot_bgcolor="white")

category = filtered.groupby("category", as_index=False).agg(net_revenue=("net_sales", "sum"), gross_profit=("gross_profit", "sum"))
category_chart = px.bar(category.sort_values("net_revenue"), x="net_revenue", y="category", orientation="h", color="gross_profit", color_continuous_scale=["#dfeae4", "#176b52"])
category_chart.update_layout(title="Ingresos y utilidad por categoría", xaxis_title="Ingresos netos", yaxis_title="", plot_bgcolor="white")

left, right = st.columns([1.4, 1])
left.plotly_chart(revenue_chart, use_container_width=True)
right.plotly_chart(category_chart, use_container_width=True)

region_channel = filtered.groupby(["region", "channel"], as_index=False)["net_sales"].sum()
mix_chart = px.bar(region_channel, x="region", y="net_sales", color="channel", barmode="group", color_discrete_map={"Tienda": "#176b52", "Online": "#e49f50"})
mix_chart.update_layout(title="Mezcla regional por canal", yaxis_title="Ingresos netos", xaxis_title="", plot_bgcolor="white")

product = filtered.groupby(["product", "category"], as_index=False).agg(net_revenue=("net_sales", "sum"), gross_profit=("gross_profit", "sum"), return_rate=("returned", "mean"))
product["margin_pct"] = product["gross_profit"] / product["net_revenue"] * 100
scatter = px.scatter(product, x="net_revenue", y="margin_pct", size="gross_profit", color="category", hover_name="product")
scatter.update_layout(title="Mapa de productos: ingresos vs. margen", xaxis_title="Ingresos netos", yaxis_title="Margen %", plot_bgcolor="white")

left, right = st.columns(2)
left.plotly_chart(mix_chart, use_container_width=True)
right.plotly_chart(scatter, use_container_width=True)

st.subheader("Productos que requieren atención")
attention = product.sort_values(["margin_pct", "return_rate"], ascending=[True, False]).head(8).copy()
attention["return_rate"] = (attention["return_rate"] * 100).round(1)
attention["margin_pct"] = attention["margin_pct"].round(1)
st.dataframe(attention, use_container_width=True, hide_index=True)

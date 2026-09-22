from __future__ import annotations

from typing import Any

import pandas as pd


def calculate_kpis(data: pd.DataFrame) -> dict[str, Any]:
    if data.empty:
        return {
            "net_revenue": 0.0,
            "gross_profit": 0.0,
            "gross_margin_pct": 0.0,
            "orders": 0,
            "units": 0,
            "average_ticket": 0.0,
            "return_rate_pct": 0.0,
            "discount_intensity_pct": 0.0,
        }

    revenue = float(data["net_sales"].sum())
    profit = float(data["gross_profit"].sum())
    gross_sales = float(data["gross_sales"].sum())
    orders = int(data["order_id"].nunique())
    returned_orders = int(data.loc[data["returned"], "order_id"].nunique())

    return {
        "net_revenue": round(revenue, 2),
        "gross_profit": round(profit, 2),
        "gross_margin_pct": round((profit / revenue * 100) if revenue else 0, 2),
        "orders": orders,
        "units": int(data["units"].sum()),
        "average_ticket": round((revenue / orders) if orders else 0, 2),
        "return_rate_pct": round((returned_orders / orders * 100) if orders else 0, 2),
        "discount_intensity_pct": round(((gross_sales - revenue) / gross_sales * 100) if gross_sales else 0, 2),
    }


def monthly_performance(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    frame["month"] = pd.to_datetime(frame["order_date"]).dt.to_period("M").astype(str)
    return (
        frame.groupby("month", as_index=False)
        .agg(net_revenue=("net_sales", "sum"), gross_profit=("gross_profit", "sum"), orders=("order_id", "nunique"))
        .sort_values("month")
    )

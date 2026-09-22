from __future__ import annotations

import json

import pandas as pd

from src.metrics import calculate_kpis, monthly_performance
from src.paths import CLEAN_SALES_PATH, EDA_REPORT_PATH, REPORTS_DIR


def build_analysis(data: pd.DataFrame) -> dict[str, object]:
    kpis = calculate_kpis(data)
    by_category = (
        data.groupby("category", as_index=False)
        .agg(net_revenue=("net_sales", "sum"), gross_profit=("gross_profit", "sum"), orders=("order_id", "nunique"))
        .sort_values("net_revenue", ascending=False)
    )
    by_region = (
        data.groupby("region", as_index=False)
        .agg(net_revenue=("net_sales", "sum"), gross_profit=("gross_profit", "sum"), return_rate=("returned", "mean"))
        .sort_values("net_revenue", ascending=False)
    )
    low_margin_products = (
        data.groupby(["category", "product"], as_index=False)
        .agg(net_revenue=("net_sales", "sum"), gross_profit=("gross_profit", "sum"))
    )
    low_margin_products["margin_pct"] = (low_margin_products["gross_profit"] / low_margin_products["net_revenue"] * 100).round(2)
    low_margin_products = low_margin_products.sort_values("margin_pct").head(5)

    return {
        "kpis": kpis,
        "top_category": by_category.iloc[0].to_dict(),
        "top_region": by_region.iloc[0].to_dict(),
        "lowest_margin_products": low_margin_products.to_dict(orient="records"),
        "insights": [
            f"{by_category.iloc[0]['category']} lidera los ingresos netos.",
            f"{by_region.iloc[0]['region']} es la región con mayor facturación.",
            f"El margen bruto global es {kpis['gross_margin_pct']:.2f}%.",
            f"La tasa de devolución es {kpis['return_rate_pct']:.2f}%.",
        ],
    }


def main() -> None:
    data = pd.read_csv(CLEAN_SALES_PATH, parse_dates=["order_date"])
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    monthly_performance(data).to_csv(REPORTS_DIR / "monthly_performance.csv", index=False)
    result = build_analysis(data)
    EDA_REPORT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result["kpis"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

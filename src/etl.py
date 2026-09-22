from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import pandas as pd

from src.paths import CLEAN_SALES_PATH, DATABASE_PATH, QUALITY_REPORT_PATH, RAW_SALES_PATH


def clean_sales(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    data = raw.copy()
    rows_before = len(data)
    duplicate_rows = int(data.duplicated(subset=["order_id"]).sum())
    missing_before = {column: int(value) for column, value in data.isna().sum().items() if value}

    data.columns = [column.strip().lower() for column in data.columns]
    data = data.drop_duplicates(subset=["order_id"], keep="first")
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")

    numeric_columns = ["units", "unit_price", "discount_pct", "unit_cost", "satisfaction"]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    store_regions = data.dropna(subset=["region"]).groupby("store_id")["region"].agg(lambda values: values.mode().iloc[0])
    data["region"] = data["region"].fillna(data["store_id"].map(store_regions)).fillna("Sin región")
    data["satisfaction"] = data["satisfaction"].fillna(data["satisfaction"].median()).round().clip(1, 5).astype(int)

    invalid_mask = (
        data["order_date"].isna()
        | data["units"].isna()
        | (data["units"] <= 0)
        | data["unit_price"].isna()
        | (data["unit_price"] <= 0)
        | data["unit_cost"].isna()
        | (data["unit_cost"] <= 0)
    )
    invalid_rows = int(invalid_mask.sum())
    data = data.loc[~invalid_mask].copy()
    extreme_discounts = int(((data["discount_pct"] < 0) | (data["discount_pct"] > 0.50)).sum())
    data["discount_pct"] = data["discount_pct"].clip(0, 0.50)
    data["units"] = data["units"].astype(int)
    data["returned"] = data["returned"].astype(str).str.lower().map({"true": True, "false": False}).fillna(False)

    data["gross_sales"] = (data["units"] * data["unit_price"]).round(2)
    data["discount_amount"] = (data["gross_sales"] * data["discount_pct"]).round(2)
    data["net_sales"] = (data["gross_sales"] - data["discount_amount"]).round(2)
    data["total_cost"] = (data["units"] * data["unit_cost"]).round(2)
    data["gross_profit"] = (data["net_sales"] - data["total_cost"]).round(2)
    data["margin_pct"] = (data["gross_profit"] / data["net_sales"] * 100).round(2)

    q1, q3 = data["net_sales"].quantile([0.25, 0.75])
    upper_bound = q3 + 1.5 * (q3 - q1)
    data["is_high_value_order"] = data["net_sales"] > upper_bound
    data = data.sort_values(["order_date", "order_id"]).reset_index(drop=True)

    report = {
        "rows_before": rows_before,
        "rows_after": len(data),
        "duplicates_removed": duplicate_rows,
        "invalid_rows_removed": invalid_rows,
        "extreme_discounts_corrected": extreme_discounts,
        "missing_values_before": missing_before,
        "missing_values_after": int(data.isna().sum().sum()),
        "high_value_orders_flagged": int(data["is_high_value_order"].sum()),
    }
    return data, report


def build_star_schema(data: pd.DataFrame, database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    products = data[["category", "product"]].drop_duplicates().sort_values(["category", "product"]).reset_index(drop=True)
    products.insert(0, "product_key", range(1, len(products) + 1))
    stores = data[["store_id", "region"]].drop_duplicates().sort_values("store_id").reset_index(drop=True)
    stores.insert(0, "store_key", range(1, len(stores) + 1))
    dates = pd.DataFrame({"order_date": sorted(data["order_date"].dt.date.unique())})
    dates.insert(0, "date_key", pd.to_datetime(dates["order_date"]).dt.strftime("%Y%m%d").astype(int))
    dates["year"] = pd.to_datetime(dates["order_date"]).dt.year
    dates["month"] = pd.to_datetime(dates["order_date"]).dt.month
    dates["month_name"] = pd.to_datetime(dates["order_date"]).dt.strftime("%b")
    dates["quarter"] = "Q" + pd.to_datetime(dates["order_date"]).dt.quarter.astype(str)

    fact = data.merge(products, on=["category", "product"]).merge(stores, on=["store_id", "region"])
    fact["date_key"] = fact["order_date"].dt.strftime("%Y%m%d").astype(int)
    fact = fact[
        ["order_id", "date_key", "store_key", "product_key", "channel", "customer_segment", "payment_method",
         "units", "unit_price", "discount_pct", "unit_cost", "gross_sales", "discount_amount", "net_sales",
         "total_cost", "gross_profit", "margin_pct", "returned", "satisfaction", "is_high_value_order"]
    ]

    with sqlite3.connect(database_path) as connection:
        products.to_sql("dim_product", connection, if_exists="replace", index=False)
        stores.to_sql("dim_store", connection, if_exists="replace", index=False)
        dates.to_sql("dim_date", connection, if_exists="replace", index=False)
        fact.to_sql("fact_sales", connection, if_exists="replace", index=False)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON fact_sales(date_key)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON fact_sales(product_key)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_fact_sales_store ON fact_sales(store_key)")


def run_pipeline(raw_path: Path = RAW_SALES_PATH, clean_path: Path = CLEAN_SALES_PATH, database_path: Path = DATABASE_PATH) -> dict[str, object]:
    raw = pd.read_csv(raw_path)
    clean, report = clean_sales(raw)
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(clean_path, index=False, date_format="%Y-%m-%d")
    build_star_schema(clean, database_path)
    QUALITY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUALITY_REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Limpia ventas y construye el modelo analítico.")
    parser.add_argument("--input", type=Path, default=RAW_SALES_PATH)
    parser.add_argument("--output", type=Path, default=CLEAN_SALES_PATH)
    parser.add_argument("--database", type=Path, default=DATABASE_PATH)
    args = parser.parse_args()
    report = run_pipeline(args.input, args.output, args.database)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

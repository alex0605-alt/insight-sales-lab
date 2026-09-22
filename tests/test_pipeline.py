import sqlite3

import pandas as pd

from src.etl import build_star_schema, clean_sales
from src.metrics import calculate_kpis


def sample_raw() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"order_id": "A", "order_date": "2025-01-01", "store_id": "GDL-01", "region": "Occidente", "channel": "Tienda", "category": "Oficina", "product": "Silla", "units": 2, "unit_price": 100, "discount_pct": 0.10, "unit_cost": 50, "customer_segment": "Nuevo", "payment_method": "Tarjeta", "returned": False, "satisfaction": 5},
            {"order_id": "A", "order_date": "2025-01-01", "store_id": "GDL-01", "region": "Occidente", "channel": "Tienda", "category": "Oficina", "product": "Silla", "units": 2, "unit_price": 100, "discount_pct": 0.10, "unit_cost": 50, "customer_segment": "Nuevo", "payment_method": "Tarjeta", "returned": False, "satisfaction": 5},
            {"order_id": "B", "order_date": "2025-01-02", "store_id": "GDL-01", "region": None, "channel": "Online", "category": "Hogar", "product": "Cafetera", "units": 1, "unit_price": 300, "discount_pct": 1.20, "unit_cost": 180, "customer_segment": "Recurrente", "payment_method": "Tarjeta", "returned": True, "satisfaction": None},
            {"order_id": "C", "order_date": "2025-01-03", "store_id": "GDL-01", "region": "Occidente", "channel": "Tienda", "category": "Hogar", "product": "Licuadora", "units": -1, "unit_price": 200, "discount_pct": 0, "unit_cost": 100, "customer_segment": "Nuevo", "payment_method": "Efectivo", "returned": False, "satisfaction": 4},
        ]
    )


def test_clean_sales_applies_quality_rules():
    clean, report = clean_sales(sample_raw())
    assert len(clean) == 2
    assert report["duplicates_removed"] == 1
    assert report["invalid_rows_removed"] == 1
    assert report["extreme_discounts_corrected"] == 1
    assert clean["region"].isna().sum() == 0
    assert clean["discount_pct"].max() == 0.50


def test_kpis_are_calculated_from_clean_values():
    clean, _ = clean_sales(sample_raw())
    kpis = calculate_kpis(clean)
    assert kpis["orders"] == 2
    assert kpis["units"] == 3
    assert kpis["net_revenue"] == 330.0
    assert kpis["gross_profit"] == 50.0
    assert kpis["return_rate_pct"] == 50.0


def test_star_schema_creates_fact_and_dimensions(tmp_path):
    clean, _ = clean_sales(sample_raw())
    database = tmp_path / "analytics.db"
    build_star_schema(clean, database)
    with sqlite3.connect(database) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        fact_rows = connection.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    assert {"fact_sales", "dim_product", "dim_store", "dim_date"}.issubset(tables)
    assert fact_rows == len(clean)

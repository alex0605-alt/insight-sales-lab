from __future__ import annotations

import argparse
import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.paths import RAW_SALES_PATH

SEED = 20260922

PRODUCTS = [
    ("Electrónica", "Audífonos Bluetooth", 699.0, 385.0),
    ("Electrónica", "Teclado mecánico", 1199.0, 720.0),
    ("Electrónica", "Monitor 24 pulgadas", 3299.0, 2350.0),
    ("Hogar", "Cafetera programable", 1499.0, 870.0),
    ("Hogar", "Licuadora", 999.0, 560.0),
    ("Hogar", "Juego de sábanas", 649.0, 310.0),
    ("Deportes", "Mancuernas 10 kg", 899.0, 520.0),
    ("Deportes", "Tapete de yoga", 399.0, 160.0),
    ("Deportes", "Mochila deportiva", 749.0, 340.0),
    ("Oficina", "Silla ergonómica", 2899.0, 1820.0),
    ("Oficina", "Lámpara LED", 549.0, 240.0),
    ("Oficina", "Organizador de escritorio", 289.0, 105.0),
]

STORES = [
    ("GDL-01", "Occidente"), ("GDL-02", "Occidente"), ("ZAP-01", "Occidente"),
    ("MTY-01", "Norte"), ("MTY-02", "Norte"), ("CHH-01", "Norte"),
    ("CDMX-01", "Centro"), ("CDMX-02", "Centro"), ("PUE-01", "Centro"),
    ("VER-01", "Golfo"), ("MER-01", "Sureste"), ("CAN-01", "Sureste"),
]


def generate_sales(rows: int = 3600, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    random.seed(seed)
    start = date(2025, 1, 1)
    records: list[dict[str, object]] = []

    for index in range(rows):
        category, product, base_price, base_cost = random.choice(PRODUCTS)
        store_id, region = random.choice(STORES)
        order_date = start + timedelta(days=int(rng.integers(0, 365)))
        channel = rng.choice(["Tienda", "Online"], p=[0.68, 0.32])
        units = int(rng.choice([1, 2, 3, 4, 5, 6], p=[0.39, 0.27, 0.16, 0.09, 0.06, 0.03]))
        seasonal = 1.10 if order_date.month in (11, 12) else 1.0
        unit_price = round(base_price * seasonal * float(rng.normal(1.0, 0.025)), 2)
        discount = float(rng.choice([0, 0.05, 0.10, 0.15, 0.20, 0.30], p=[0.30, 0.18, 0.24, 0.14, 0.10, 0.04]))
        returned_probability = 0.11 if channel == "Online" else 0.055
        returned = bool(rng.random() < returned_probability)
        satisfaction = int(rng.choice([1, 2, 3, 4, 5], p=[0.04, 0.07, 0.18, 0.38, 0.33]))

        records.append(
            {
                "order_id": f"ORD-{index + 1:06d}",
                "order_date": order_date.isoformat(),
                "store_id": store_id,
                "region": region,
                "channel": channel,
                "category": category,
                "product": product,
                "units": units,
                "unit_price": unit_price,
                "discount_pct": discount,
                "unit_cost": round(base_cost * float(rng.normal(1.0, 0.015)), 2),
                "customer_segment": rng.choice(["Nuevo", "Recurrente", "Empresa"], p=[0.38, 0.52, 0.10]),
                "payment_method": rng.choice(["Tarjeta", "Efectivo", "Transferencia"], p=[0.61, 0.27, 0.12]),
                "returned": returned,
                "satisfaction": satisfaction,
            }
        )

    frame = pd.DataFrame(records)
    # Problemas intencionales para demostrar limpieza.
    frame.loc[rng.choice(frame.index, 28, replace=False), "region"] = None
    frame.loc[rng.choice(frame.index, 18, replace=False), "satisfaction"] = np.nan
    frame.loc[rng.choice(frame.index, 8, replace=False), "units"] = -1
    frame.loc[rng.choice(frame.index, 7, replace=False), "discount_pct"] = 1.25
    duplicates = frame.sample(32, random_state=seed)
    return pd.concat([frame, duplicates], ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)


def write_dataset(output: Path = RAW_SALES_PATH, rows: int = 3600) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    generate_sales(rows=rows).to_csv(output, index=False)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera ventas minoristas sintéticas y reproducibles.")
    parser.add_argument("--rows", type=int, default=3600)
    parser.add_argument("--output", type=Path, default=RAW_SALES_PATH)
    args = parser.parse_args()
    path = write_dataset(args.output, args.rows)
    print(f"Dataset generado: {path}")


if __name__ == "__main__":
    main()

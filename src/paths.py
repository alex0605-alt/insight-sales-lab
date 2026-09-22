from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
RAW_SALES_PATH = RAW_DIR / "retail_sales_dirty.csv"
CLEAN_SALES_PATH = PROCESSED_DIR / "retail_sales_clean.csv"
DATABASE_PATH = PROCESSED_DIR / "sales_analytics.db"
QUALITY_REPORT_PATH = REPORTS_DIR / "data_quality_report.json"
EDA_REPORT_PATH = REPORTS_DIR / "eda_summary.json"

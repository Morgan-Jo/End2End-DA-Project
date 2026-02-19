import os
import datetime as dt
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

from fx_database import init_db, get_connection, DB_PATH

load_dotenv()

APP_ID = os.getenv("OPENEXCHANGERATES_APP_ID")
BASE_CURRENCY = os.getenv("BASE_CURRENCY", "USD")

DATA_DIR = Path("data")
FULL_CSV = DATA_DIR / "fx_rates_full.csv"
FULL_XLSX = DATA_DIR / "fx_rates_full.xlsx"

API_URL = "https://openexchangerates.org/api/latest.json"

def fetch_latest_rates():
    if not APP_ID:
        raise ValueError("OPENEXCHANGERATES_APP_ID is not set in environment or .env")

    params = {"app_id": APP_ID}
    # Note: Free plans use USD as base; we respect that.
    resp = requests.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data


def store_rates(data: dict):
    timestamp = dt.datetime.utcfromtimestamp(data["timestamp"]).isoformat()
    base = data.get("base", "USD")
    rates = data["rates"]

    conn = get_connection()
    cur = conn.cursor()

    rows = []
    for currency, rate in rates.items():
        rows.append((timestamp, base, currency, rate))

    cur.executemany(
        "INSERT INTO fx_rates (timestamp_utc, base, currency, rate) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()


def export_full_history():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM fx_rates", conn)
    conn.close()

    df.to_csv(FULL_CSV, index=False)
    df.to_excel(FULL_XLSX, index=False)
    print(f"Exported full history to {FULL_CSV} and {FULL_XLSX}")


def main():
    DATA_DIR.mkdir(exist_ok=True)
    init_db()

    print("Fetching latest FX rates...")
    data = fetch_latest_rates()
    store_rates(data)
    print("Stored latest FX rates into database.")

    print("Exporting full history to CSV and XLSX...")
    export_full_history()

if __name__ == "__main__":
    main()

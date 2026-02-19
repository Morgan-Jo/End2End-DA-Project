# eda_fx.py
import pandas as pd
from pathlib import Path
from fx_database import get_connection, DATA_DIR

DAILY_CSV = DATA_DIR / "fx_rates_daily.csv"
DAILY_XLSX = DATA_DIR / "fx_rates_daily.xlsx"

def run_eda():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM fx_rates", conn)
    conn.close()

    if df.empty:
        print("No data found in fx_rates table.")
        return

    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])
    df["date"] = df["timestamp_utc"].dt.date

    # Quick sanity check
    print("Min date:", df["timestamp_utc"].min(), "Max date:", df["timestamp_utc"].max())
    print("Unique dates:", df["date"].nunique())

    daily = (
        df.groupby(["currency", "date"], as_index=False)["rate"]
        .mean()
        .sort_values(["currency", "date"])
    )

    # Daily percent change per currency
    daily["pct_change"] = (
        daily.groupby("currency")["rate"].pct_change() * 100
    )

    # Rolling volatility with min_periods=1 so you see values earlier
    daily["rolling_vol_7d"] = (
        daily.groupby("currency")["pct_change"]
        .apply(lambda s: s.rolling(window=7, min_periods=1).std())
        .values
    )

    # Optional: keep NaNs, or fill some if you prefer
    # daily["pct_change"] = daily["pct_change"].fillna(0)

    daily.to_csv(DAILY_CSV, index=False)
    daily.to_excel(DAILY_XLSX, index=False)
    print(f"Saved daily dataset to {DAILY_CSV} and {DAILY_XLSX}")

if __name__ == "__main__":
    run_eda()
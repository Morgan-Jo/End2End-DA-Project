"""
Stock Market Price Explorer
Fetches stock data with yfinance, calculates indicators,
stores results in SQLite, runs basic EDA, and exports CSV/Excel for Tableau or Excel.
"""

import os
from pathlib import Path
from typing import List, Optional

import pandas as pd
import yfinance as yf
import sqlalchemy as sa

from config import (
    TICKERS,
    START_DATE,
    END_DATE,
    DB_PATH,
    TABLE_NAME,
    VOL_WINDOW,
    SMA_WINDOWS,
    RSI_PERIOD,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
)

# -----------------------------
# Data fetch & indicator helpers
# -----------------------------

def fetch_data_for_ticker(ticker: str, start: str, end: Optional[str]) -> pd.DataFrame:
    """Fetch OHLCV data for a single ticker using yfinance."""
    df = yf.download(ticker, start=start, end=end, progress=False)

    if df.empty:
        print(f"[WARN] No data returned for {ticker}")
        return df

    df = df.reset_index()  # move Date index to a column
    df.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        },
        inplace=True,
    )
    df["ticker"] = ticker
    return df

def calculate_sma(df: pd.DataFrame, windows: List[int]) -> pd.DataFrame:
    """Add simple moving averages for given windows."""
    for w in windows:
        df[f"sma_{w}"] = df["close"].rolling(window=w, min_periods=1).mean()
    return df

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Calculate RSI (Relative Strength Index) using Wilder's smoothing."""
    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's moving average: exponential with alpha = 1/period
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    # Avoid division by zero
    avg_loss = avg_loss.replace(0, pd.NA)

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df[f"rsi_{period}"] = rsi
    return df

def calculate_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    """Calculate MACD, signal, and histogram."""
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()

    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    hist = macd - signal

    df["macd"] = macd
    df["macd_signal"] = signal
    df["macd_hist"] = hist
    return df

def add_returns_and_volatility(df: pd.DataFrame, vol_window: int = 20) -> pd.DataFrame:
    """Add daily returns and rolling volatility."""
    df["daily_return"] = df["close"].pct_change()
    df[f"rolling_vol_{vol_window}"] = (
        df["daily_return"].rolling(window=vol_window, min_periods=1).std()
    )
    return df

def enrich_with_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all indicator functions to a ticker-level DataFrame."""
    df = df.sort_values("date")
    df = add_returns_and_volatility(df, VOL_WINDOW)
    df = calculate_sma(df, SMA_WINDOWS)
    df = calculate_rsi(df, RSI_PERIOD)
    df = calculate_macd(df, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    return df

# -----------------------------
# IO helpers
# -----------------------------

def ensure_data_folder() -> Path:
    """Make sure data folder exists for exports."""
    data_path = Path("data")
    data_path.mkdir(exist_ok=True)
    return data_path

def create_db_engine(db_path: str) -> sa.Engine:
    """Create a SQLAlchemy engine for SQLite."""
    conn_str = f"sqlite:///{db_path}"
    engine = sa.create_engine(conn_str)
    return engine

def store_in_db(df: pd.DataFrame, engine: sa.Engine, table_name: str) -> None:
    """Write DataFrame to SQLite (replace existing table)."""
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)
    print(f"[INFO] Written {len(df):,} rows to table '{table_name}' in {DB_PATH}")

# -----------------------------
# EDA
# -----------------------------

def run_basic_eda(df: pd.DataFrame) -> None:
    """Print a few EDA summaries to the console."""
    # Make a copy and flatten any index levels
    df = df.copy()
    df = df.reset_index()  # bring any index levels into columns

    print("\n========== BASIC EDA ==========\n")

    # Ensure date is datetime
    df["date"] = pd.to_datetime(df["date"])

    # Overall shape
    print(f"Rows: {len(df):,}, Columns: {len(df.columns)}\n")

    # Date range by ticker
    print("Date range by ticker:")
    date_ranges = (
        df.groupby("ticker")["date"]
        .agg(["min", "max", "count"])
        .rename(columns={"min": "start_date", "max": "end_date", "count": "rows"})
    )
    print(date_ranges)
    print()

    # Summary stats for daily_return
    if "daily_return" in df.columns:
        print("Summary of daily returns by ticker:")
        daily_return_summary = (
            df.groupby("ticker")["daily_return"]
            .describe()[["mean", "std", "min", "max"]]
        )
        print(daily_return_summary)
        print()
    else:
        print("Column 'daily_return' not found, skipping daily return summary.\n")

    # Top 5 most volatile tickers over last 60 days
    print("Top 5 most volatile tickers (last 60 days, by std of daily_return):")

    # Compute last_date per ticker without merges
    df["last_date"] = df.groupby("ticker")["date"].transform("max")
    df["days_from_last"] = (df["last_date"] - df["date"]).dt.days

    recent = df[(df["days_from_last"] <= 60) & df["daily_return"].notna()].copy()

    if not recent.empty:
        vol_rank = (
            recent.groupby("ticker")["daily_return"]
            .std()
            .sort_values(ascending=False)
            .head(5)
        )
        print(vol_rank)
    else:
        print("No data found in the last 60 days window.")
    print()

    # Missing data check
    print("Missing values per column:")
    print(df.isna().sum())
    print("\n========== END EDA ==========\n")

# -----------------------------
# Main pipeline
# -----------------------------

def main() -> None:
    print("[INFO] Starting Stock Market Price Explorer pipeline")

    all_data_frames: List[pd.DataFrame] = []

    for ticker in TICKERS:
        print(f"[INFO] Fetching data for {ticker}")
        df_ticker = fetch_data_for_ticker(ticker, START_DATE, END_DATE)
        if df_ticker.empty:
            continue

        df_ticker = enrich_with_indicators(df_ticker)
        all_data_frames.append(df_ticker)

    if not all_data_frames:
        print("[ERROR] No data fetched for any ticker. Check configuration or network.")
        return

    full_df = pd.concat(all_data_frames, ignore_index=True)

    # Ensure date is datetime
    full_df["date"] = pd.to_datetime(full_df["date"])

    # Store in SQLite
    engine = create_db_engine(DB_PATH)
    store_in_db(full_df, engine, TABLE_NAME)

    # EDA
    run_basic_eda(full_df)

    # Flatten MultiIndex columns if necessary
    if isinstance(full_df.columns, pd.MultiIndex):
        full_df.columns = [
            "_".join([str(c) for c in col if c != ""]) 
            for col in full_df.columns
        ]

    # Export CSV and Excel for Tableau / Excel analysis
    data_folder = ensure_data_folder()

    csv_path = data_folder / "price_data_for_tableau.csv"
    excel_path = data_folder / "price_data_for_tableau.xlsx"
    
    # Export files
    full_df.to_csv(csv_path, index=False)
    full_df.to_excel(excel_path, index=False)

    print(f"[INFO] Exported CSV to: {csv_path.resolve()}")
    print(f"[INFO] Exported Excel to: {excel_path.resolve()}")

if __name__ == "__main__":
    main()

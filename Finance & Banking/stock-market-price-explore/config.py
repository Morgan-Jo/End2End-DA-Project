# List of tickers to analyse
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN"]

# Date range for historical data
START_DATE = "2020-01-01"
END_DATE = None  # None = up to latest available

# SQLite database settings
DB_PATH = "market_data.db"
TABLE_NAME = "price_data"

# Rolling window parameters
VOL_WINDOW = 20       # for rolling volatility
SMA_WINDOWS = [20, 50, 200]
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
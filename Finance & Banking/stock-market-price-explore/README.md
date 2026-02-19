# Stock Market Price Explorer: Python, SQL & Tableau

## Overview

Stock Market Price Explorer is a small analytics project that pulls historical stock data with Python, stores it in a SQL database, calculates technical indicators, and prepares a clean dataset for visualisation in Tableau.

You can use it to explore:

- Price history
- Volume trends
- Volatility
- Moving averages (20, 50, 200)
- RSI (14)
- MACD (12–26–9)

The final dataset can feed a Tableau dashboard that shows price and volume trends and compares performance across tickers or sectors.

---

## Tech stack

- **Python**: data ingestion, cleaning, indicators, EDA
- **yfinance**: fetch historical price data
- **Pandas**: data wrangling and indicator calculations
- **SQLite**: local database storage
- **Tableau**: visualisation (price history, volume trends, comparisons)

---

## Project structure

```text
stock-market-price-explorer/
│
├─ app.py                  # Main script: fetch, store, analyse, export
├─ config.py               # Configuration for tickers, dates, DB path
├─ README.mdS
│
├─ data/
│   └─ price_data_for_tableau.csv   # Exported dataset for Tableau
│   └─ price_data_for_tableau.xlsx   # Exported dataset for Tableau
│
└─ market_data.db          # SQLite database (auto-created)

--- 

## Requirements
- Python 3.9+ 

---

## Author

Morgan J. Tonner

--- 

## Diclaimer

This project is for portfolio and learning only
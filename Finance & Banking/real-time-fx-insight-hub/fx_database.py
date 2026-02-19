import sqlite3
from pathlib import Path

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "fx_rates.db"

DATA_DIR.mkdir(exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS fx_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_utc TEXT NOT NULL,
            base TEXT NOT NULL,
            currency TEXT NOT NULL,
            rate REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
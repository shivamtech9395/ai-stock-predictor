# ============================================
# DATABASE CONNECTION
# SQLite use kar rahe hain abhi (free, no install)
# Spiral 3 mein PostgreSQL pe shift karenge
# ============================================

import sqlite3
import os

# Database file ka path
# os.path.dirname = current file ki directory
# abspath = poora path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "stock_data.db")

def get_connection():
    """
    Database connection return karta hai.
    Jab bhi database se baat karni ho — ye function call karo.
    """
    conn = sqlite3.connect(DB_PATH)
    # row_factory = results ko dictionary format mein deta hai
    # Matlab result['symbol'] likhenge, result[0] nahi
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """
    Pehli baar chalane pe tables banata hai.
    Agar table already hai toh kuch nahi karta.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── TABLE 1: STOCKS ───────────────────────
    # Master list of all stocks we track
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol      TEXT UNIQUE NOT NULL,
            company     TEXT NOT NULL,
            sector      TEXT NOT NULL,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── TABLE 2: PRICE DATA ───────────────────
    # Daily OHLCV data for every stock
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_data (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol      TEXT NOT NULL,
            date        TEXT NOT NULL,
            open        REAL,
            high        REAL,
            low         REAL,
            close       REAL,
            volume      INTEGER,
            UNIQUE(symbol, date)
        )
    """)

    # ── TABLE 3: PREDICTIONS ─────────────────
    # AI predictions for every stock every day
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol          TEXT NOT NULL,
            prediction_date TEXT NOT NULL,
            prob_up         REAL,
            prob_down       REAL,
            signal          TEXT,
            accuracy        REAL,
            actual_outcome  TEXT DEFAULT NULL,
            was_correct     INTEGER DEFAULT NULL,
            created_at      TEXT DEFAULT (datetime('now')),
            UNIQUE(symbol, prediction_date)
        )
    """)

    conn.commit()
    conn.close()
    print("   Database initialized successfully!")
    print(f"   Location: {DB_PATH}")

# Test karo — seedha is file ko run karo
if __name__ == "__main__":
    print("Setting up database...")
    init_database()
    print("Done!")
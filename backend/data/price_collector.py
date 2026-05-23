# ============================================
# PRICE COLLECTOR
# Downloads stock data and saves to database
# ============================================

import yfinance as yf
import pandas as pd
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Apni database connection import karo
# sys.path = Python ko batao ki files kahan dhundhe
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database.connection import get_connection, init_database

# ── STOCKS LIST ───────────────────────────────
# Yahan se start karenge — baad mein 500 karenge
STOCKS = [
    ("RELIANCE.NS",   "Reliance Industries",  "Energy"),
    ("TCS.NS",        "Tata Consultancy",      "IT"),
    ("HDFCBANK.NS",   "HDFC Bank",             "Banking"),
    ("INFY.NS",       "Infosys",               "IT"),
    ("ICICIBANK.NS",  "ICICI Bank",            "Banking"),
    ("HINDUNILVR.NS", "Hindustan Unilever",    "FMCG"),
    ("SBIN.NS",       "State Bank of India",   "Banking"),
    ("BHARTIARTL.NS", "Bharti Airtel",         "Telecom"),
    ("KOTAKBANK.NS",  "Kotak Mahindra Bank",   "Banking"),  # Try new symbol
    ("LT.NS",         "Larsen & Toubro",       "Infrastructure"),
]

def save_stocks_master():
    """
    Stocks ki master list database mein save karo.
    Ye sirf ek baar chalega — already hai toh skip karega.
    """
    conn = get_connection()
    cursor = conn.cursor()

    for symbol, company, sector in STOCKS:
        # INSERT OR IGNORE = agar already hai toh skip karo
        cursor.execute("""
            INSERT OR IGNORE INTO stocks (symbol, company, sector)
            VALUES (?, ?, ?)
        """, (symbol.replace(".NS", ""), company, sector))

    conn.commit()
    conn.close()
    print(f"   Stocks master list saved — {len(STOCKS)} stocks")

def download_and_save(symbol, company):
    """
    Ek stock ka data download karo aur database mein save karo.
    """
    try:
        # Download 2 saal ka data
        df = yf.download(symbol, period="2y", interval="1d", progress=False)
        df.columns = df.columns.get_level_values(0)

        if len(df) < 50:
            print(f"      Not enough data for {symbol}")
            return 0

        conn = get_connection()
        cursor = conn.cursor()

        saved_count = 0
        sym_clean = symbol.replace(".NS", "")

        # Har row database mein save karo
        for date, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO price_data
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sym_clean,
                    str(date.date()),
                    round(float(row['Open']), 2),
                    round(float(row['High']), 2),
                    round(float(row['Low']), 2),
                    round(float(row['Close']), 2),
                    int(row['Volume']),
                ))
                saved_count += 1
            except:
                continue

        conn.commit()
        conn.close()
        return saved_count

    except Exception as e:
        print(f"      Error downloading {symbol}: {e}")
        return 0

def collect_all_stocks():
    """
    Sab stocks ka data collect karo — ye main function hai.
    """
    print("=" * 55)
    print("   PRICE COLLECTOR - Starting...")
    print("=" * 55)

    # Pehle database aur master list setup karo
    init_database()
    save_stocks_master()

    total_saved = 0

    for i, (symbol, company, sector) in enumerate(STOCKS):
        print(f"\n   [{i+1}/{len(STOCKS)}] Downloading {company}...")
        count = download_and_save(symbol, company)
        total_saved += count
        print(f"          Saved {count} days of data")

    print("\n" + "=" * 55)
    print(f"   COLLECTION COMPLETE!")
    print(f"   Total records saved: {total_saved}")
    print("=" * 55)

def get_latest_prices():
    """
    Database se latest prices dikhao — check karne ke liye.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.symbol, s.company, s.sector,
               p.close, p.volume, p.date
        FROM price_data p
        JOIN stocks s ON p.symbol = s.symbol
        WHERE p.date = (
            SELECT MAX(date) FROM price_data p2
            WHERE p2.symbol = p.symbol
        )
        ORDER BY p.close DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

# ── RUN KARO ──────────────────────────────────
if __name__ == "__main__":
    # Step 1: Sab data download aur save karo
    collect_all_stocks()

    # Step 2: Verify — database mein kya hai check karo
    print("\n   LATEST PRICES IN DATABASE:")
    print("-" * 55)
    print(f"   {'SYMBOL':<12} {'COMPANY':<22} {'CLOSE':>8} {'DATE'}")
    print("-" * 55)

    prices = get_latest_prices()
    for row in prices:
        print(f"   {row['symbol']:<12} {row['company']:<22} "
              f"Rs.{row['close']:>7.2f} {row['date']}")

    print("-" * 55)
    print(f"   Total stocks in DB: {len(prices)}")
    print()
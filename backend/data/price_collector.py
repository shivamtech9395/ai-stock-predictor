# ============================================
# PRICE COLLECTOR V4 - AUTO .NS ADD
# ============================================

import yfinance as yf
import sys, os, warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database.connection import get_connection, init_database
from backend.data.stocks_list import NIFTY_500_STOCKS

def save_stocks_master():
    conn = get_connection()
    cursor = conn.cursor()
    for symbol, company, sector in NIFTY_500_STOCKS:
        cursor.execute("""
            INSERT OR IGNORE INTO stocks (symbol, company, sector)
            VALUES (?, ?, ?)
        """, (symbol, company, sector))
    conn.commit()
    conn.close()
    print(f"   Stocks master list saved — {len(NIFTY_500_STOCKS)} stocks")

def download_and_save(symbol, company):
    """
    symbol = clean symbol WITHOUT .NS (e.g. TATASTEEL)
    We add .NS automatically for yfinance
    """
    try:
        # Add .NS for yfinance
        yf_symbol = symbol + ".NS"

        df = yf.download(yf_symbol, period="2y", interval="1d", progress=False)

        if df is None or df.empty or len(df) < 10:
            return 0

        # Multi-level columns fix
        if hasattr(df.columns, 'levels'):
            df.columns = df.columns.get_level_values(0)

        conn = get_connection()
        cursor = conn.cursor()
        saved = 0

        for date, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO price_data
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    str(date.date()),
                    round(float(row['Open']), 2),
                    round(float(row['High']), 2),
                    round(float(row['Low']), 2),
                    round(float(row['Close']), 2),
                    int(row['Volume']),
                ))
                saved += 1
            except:
                continue

        conn.commit()
        conn.close()
        return saved

    except Exception as e:
        return 0

def collect_all_stocks():
    print("=" * 60)
    print("   PRICE COLLECTOR V4 - Starting...")
    print(f"   Total stocks: {len(NIFTY_500_STOCKS)}")
    print("=" * 60)

    init_database()
    save_stocks_master()

    total_saved = 0
    success = 0
    failed = []

    for i, (symbol, company, sector) in enumerate(NIFTY_500_STOCKS):
        print(f"   [{i+1}/{len(NIFTY_500_STOCKS)}] {company}...", end=" ", flush=True)
        count = download_and_save(symbol, company)
        if count > 0:
            total_saved += count
            success += 1
            print(f"✅ {count} days")
        else:
            failed.append(symbol)
            print(f"❌ skipped")

    print("\n" + "=" * 60)
    print(f"   COMPLETE!")
    print(f"   ✅ Successful : {success} stocks")
    print(f"   ❌ Failed     : {len(failed)} stocks")
    print(f"   📊 Total records: {total_saved}")
    if failed:
        print(f"   Failed list: {', '.join(failed[:10])}")
    print("=" * 60)
    return total_saved

def get_latest_prices():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.symbol, s.company, s.sector, p.close, p.date
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

if __name__ == "__main__":
    collect_all_stocks()
    print("\n   STOCKS IN DATABASE:")
    print("-" * 55)
    prices = get_latest_prices()
    print(f"   Total: {len(prices)} stocks")
    for row in prices[:15]:
        print(f"   {row['symbol']:<14} {row['company']:<28} ₹{row['close']}")
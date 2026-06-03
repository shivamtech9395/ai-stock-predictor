# ============================================
# MARKET CLOSE REPORT V2 - FIXED
# ============================================

import yfinance as yf
import sys, os, warnings, struct, json
from datetime import datetime, date
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database.connection import get_connection

def safe_float(val):
    if val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    if isinstance(val, bytes):
        try: return struct.unpack('f', val)[0]
        except:
            try: return struct.unpack('d', val)[0]
            except: return 0.0
    try: return float(val)
    except: return 0.0

def get_index_data():
    indices = {
        "NIFTY50":   "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "SENSEX":    "^BSESN",
        "FINNIFTY":  "^CNXFIN",
        "VIX":       "^INDIAVIX",
    }
    result = {}
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d", interval="1d")
            if not hist.empty and len(hist) >= 2:
                today_close = float(hist['Close'].iloc[-1])
                prev_close  = float(hist['Close'].iloc[-2])
                change      = today_close - prev_close
                change_pct  = (change / prev_close) * 100
                result[name] = {
                    "close":      round(today_close, 2),
                    "prev_close": round(prev_close, 2),
                    "change":     round(change, 2),
                    "change_pct": round(change_pct, 2),
                }
        except:
            continue
    return result

def get_top_movers():
    conn = get_connection()
    cursor = conn.cursor()
    today = str(date.today())
    cursor.execute("""
        SELECT p.symbol, s.company, s.sector,
               p.prob_up, p.signal,
               pd.close as price
        FROM predictions p
        JOIN stocks s ON p.symbol = s.symbol
        LEFT JOIN price_data pd ON (
            pd.symbol = p.symbol AND
            pd.date = (SELECT MAX(date) FROM price_data WHERE symbol = p.symbol)
        )
        WHERE p.prediction_date = ?
        ORDER BY p.prob_up DESC
    """, (today,))
    rows = cursor.fetchall()
    conn.close()

    bullish = []
    bearish = []

    for row in rows:
        signal = str(row['signal'] or "")
        prob_up = safe_float(row['prob_up'])
        price   = safe_float(row['price'])
        item = {
            "symbol":  str(row['symbol']),
            "company": str(row['company']),
            "sector":  str(row['sector']),
            "prob_up": round(prob_up, 1),
            "signal":  signal.replace("🚀","").replace("📈","").replace("🔴","").replace("📉","").replace("⚖️","").strip(),
            "price":   round(price, 2),
        }
        if "BUY" in signal.upper():
            bullish.append(item)
        elif "SELL" in signal.upper():
            bearish.append(item)

    return bullish[:10], bearish[:10]

def get_sector_summary():
    conn = get_connection()
    cursor = conn.cursor()
    today = str(date.today())
    cursor.execute("""
        SELECT s.sector,
               COUNT(*) as total,
               AVG(p.prob_up) as avg_up,
               SUM(CASE WHEN p.prob_up >= 55 THEN 1 ELSE 0 END) as bullish_count,
               SUM(CASE WHEN p.prob_down >= 55 THEN 1 ELSE 0 END) as bearish_count
        FROM predictions p
        JOIN stocks s ON p.symbol = s.symbol
        WHERE p.prediction_date = ?
        GROUP BY s.sector
        ORDER BY avg_up DESC
    """, (today,))
    rows = cursor.fetchall()
    conn.close()

    sectors = []
    for row in rows:
        avg_up = safe_float(row['avg_up'])
        mood = "BULLISH 📈" if avg_up > 55 else "BEARISH 📉" if avg_up < 45 else "NEUTRAL ➖"
        sectors.append({
            "sector":        str(row['sector']),
            "total":         int(row['total'] or 0),
            "avg_up":        round(avg_up, 1),
            "bullish_count": int(row['bullish_count'] or 0),
            "bearish_count": int(row['bearish_count'] or 0),
            "mood":          mood,
        })
    return sectors

def generate_market_analysis(indices, bullish, bearish, sectors):
    nifty = indices.get("NIFTY50", {})
    vix   = indices.get("VIX", {})
    analysis = []

    if nifty:
        chg = nifty.get('change', 0)
        pct = nifty.get('change_pct', 0)
        if chg > 0:
            analysis.append(f"Nifty 50 aaj {abs(pct):.2f}% upar close hua ({nifty['close']:,.0f} pe). Broad market bullish raha.")
        else:
            analysis.append(f"Nifty 50 aaj {abs(pct):.2f}% neeche close hua ({nifty['close']:,.0f} pe). Selling pressure dikh raha tha.")

    if vix:
        vix_val = vix.get('close', 0)
        if vix_val > 20:
            analysis.append(f"VIX {vix_val:.1f} pe hai — HIGH fear. Market mein uncertainty hai.")
        elif vix_val > 15:
            analysis.append(f"VIX {vix_val:.1f} pe hai — Medium fear. Normal market conditions.")
        else:
            analysis.append(f"VIX {vix_val:.1f} pe hai — LOW fear. Market calm hai.")

    if sectors:
        top    = sectors[0]
        worst  = sectors[-1]
        analysis.append(f"Best sector: {top['sector']} ({top['bullish_count']}/{top['total']} stocks bullish)")
        analysis.append(f"Weakest sector: {worst['sector']} ({worst['bearish_count']}/{worst['total']} stocks bearish)")

    if bullish:
        top3 = ", ".join([f"{s['symbol']} ({s['prob_up']:.0f}%)" for s in bullish[:3]])
        analysis.append(f"AI top picks: {top3}")

    if bearish:
        avoid3 = ", ".join([s['symbol'] for s in bearish[:3]])
        analysis.append(f"Avoid: {avoid3}")

    return analysis

def save_report_to_db(report_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT UNIQUE,
            report_json TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    cursor.execute("""
        INSERT OR REPLACE INTO market_reports (report_date, report_json)
        VALUES (?, ?)
    """, (str(date.today()), json.dumps(report_data)))
    conn.commit()
    conn.close()

def generate_close_report():
    print("=" * 60)
    print("   📊 MARKET CLOSE REPORT")
    print(f"   Date: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
    print("=" * 60)

    print("\n   Fetching index data...")
    indices = get_index_data()

    print("   Getting top movers...")
    bullish, bearish = get_top_movers()

    print("   Analyzing sectors...")
    sectors = get_sector_summary()

    # Index performance
    print("\n   📈 INDEX PERFORMANCE TODAY")
    print("   " + "-" * 50)
    for name, data in indices.items():
        chg = data.get('change', 0)
        pct = data.get('change_pct', 0)
        arrow = "▲" if chg >= 0 else "▼"
        direction = "UP" if chg >= 0 else "DN"
        print(f"   {name:<12} {data['close']:>10,.2f}  "
              f"{arrow} {abs(chg):>8.2f} ({direction} {abs(pct):.2f}%)")

    # Sector summary
    print("\n   🏢 SECTOR PERFORMANCE")
    print("   " + "-" * 50)
    print(f"   {'SECTOR':<20} {'STOCKS':>6} {'AVG UP%':>8} {'MOOD'}")
    print("   " + "-" * 50)
    for s in sectors[:10]:
        print(f"   {s['sector']:<20} {s['total']:>6} "
              f"{s['avg_up']:>7.1f}% {s['mood']}")

    # Top bullish
    print("\n   🚀 TOP BULLISH STOCKS")
    print("   " + "-" * 50)
    for i, s in enumerate(bullish[:8], 1):
        print(f"   {i}. {s['symbol']:<12} {s['company']:<25} UP: {s['prob_up']:.0f}%")

    # Top bearish
    print("\n   🔴 STOCKS TO AVOID")
    print("   " + "-" * 50)
    for i, s in enumerate(bearish[:5], 1):
        print(f"   {i}. {s['symbol']:<12} {s['company']:<25} UP: {s['prob_up']:.0f}%")

    # AI Analysis
    print("\n   🤖 AI MARKET ANALYSIS")
    print("   " + "-" * 50)
    analysis = generate_market_analysis(indices, bullish, bearish, sectors)
    for point in analysis:
        print(f"   • {point}")

    # Save
    report_data = {
        "date":     str(date.today()),
        "indices":  indices,
        "bullish":  bullish,
        "bearish":  bearish,
        "sectors":  sectors,
        "analysis": analysis,
    }
    save_report_to_db(report_data)

    print("\n" + "=" * 60)
    print("   ✅ Report saved to database!")
    print("   ⚠️  Disclaimer: AI analysis only, not financial advice")
    print("=" * 60)

    return report_data

if __name__ == "__main__":
    generate_close_report()
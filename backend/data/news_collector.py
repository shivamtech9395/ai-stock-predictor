# ============================================
# NEWS COLLECTOR - NewsAPI Version
# Free: 100 requests/day
# ============================================

import requests
import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# .env file se API key load karo
load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database.connection import get_connection

# ── STOCK KEYWORDS ────────────────────────────
STOCK_KEYWORDS = {
    "RELIANCE":   "Reliance Industries OR RIL OR Jio",
    "TCS":        "TCS OR Tata Consultancy",
    "HDFCBANK":   "HDFC Bank",
    "INFY":       "Infosys",
    "ICICIBANK":  "ICICI Bank",
    "HINDUNILVR": "Hindustan Unilever OR HUL",
    "SBIN":       "SBI OR State Bank of India",
    "BHARTIARTL": "Airtel OR Bharti Airtel",
    "LT":         "Larsen Toubro OR L&T",
}

def create_news_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol          TEXT,
            headline        TEXT NOT NULL,
            source          TEXT,
            published_at    TEXT,
            sentiment       REAL DEFAULT 0,
            sentiment_label TEXT DEFAULT 'neutral',
            fetched_at      TEXT DEFAULT (datetime('now')),
            UNIQUE(headline, symbol)
        )
    """)
    conn.commit()
    conn.close()

def fetch_news_for_stock(symbol, query):
    """
    NewsAPI se ek stock ki news fetch karo.
    """
    if not NEWS_API_KEY:
        print("   ERROR: NEWS_API_KEY not found in .env file!")
        return []

    try:
        # NewsAPI ka URL
        url = "https://newsapi.org/v2/everything"

        # Parameters — NewsAPI ko batao kya chahiye
        params = {
            "q":        query,           # Search query
            "language": "en",            # English news
            "sortBy":   "publishedAt",   # Latest pehle
            "pageSize": 10,              # 10 articles per stock
            "apiKey":   NEWS_API_KEY,    # API key
            # Last 2 days ki news
            "from": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            print(f"   API Error: {data.get('message', 'Unknown error')}")
            return []

        articles = data.get("articles", [])
        news_list = []

        for article in articles:
            if article.get("title") and article["title"] != "[Removed]":
                news_list.append({
                    "headline":     article["title"],
                    "source":       article.get("source", {}).get("name", "NewsAPI"),
                    "published_at": article.get("publishedAt", str(datetime.now())),
                })

        return news_list

    except Exception as e:
        print(f"   Error fetching news: {e}")
        return []

def save_news_to_db(symbol, headline, source, published_at):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO news
            (symbol, headline, source, published_at)
            VALUES (?, ?, ?, ?)
        """, (symbol, headline, source, published_at))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def collect_all_news():
    """
    Sab stocks ki news collect karo.
    """
    print("=" * 55)
    print("   NEWS COLLECTOR - NewsAPI")
    print("=" * 55)

    create_news_table()

    if not NEWS_API_KEY:
        print("\n   ERROR: Add NEWS_API_KEY in .env file!")
        return 0

    print(f"\n   API Key found: {NEWS_API_KEY[:8]}...")
    total_saved = 0

    # Pehle market news fetch karo
    print("\n   [MARKET] Fetching general market news...")
    market_news = fetch_news_for_stock(
        "MARKET",
        "Nifty OR Sensex OR NSE OR BSE OR Indian stock market"
    )
    for news in market_news:
        save_news_to_db("MARKET", news['headline'],
                       news['source'], news['published_at'])
    print(f"          Got {len(market_news)} market headlines")
    total_saved += len(market_news)

    # Har stock ki news fetch karo
    for i, (symbol, query) in enumerate(STOCK_KEYWORDS.items()):
        print(f"\n   [{i+1}/{len(STOCK_KEYWORDS)}] {symbol}...")
        news_list = fetch_news_for_stock(symbol, query)

        saved = 0
        for news in news_list:
            if save_news_to_db(symbol, news['headline'],
                              news['source'], news['published_at']):
                saved += 1

        total_saved += saved
        print(f"          Got {len(news_list)} | Saved {saved} headlines")

    print("\n" + "=" * 55)
    print(f"   TOTAL NEWS SAVED: {total_saved}")
    print("=" * 55)
    return total_saved

def get_recent_news(symbol, hours=48):
    """
    Ek stock ki recent news database se nikalo.
    """
    conn = get_connection()
    cursor = conn.cursor()
    since = datetime.now() - timedelta(hours=hours)
    cursor.execute("""
        SELECT headline, source, published_at,
               sentiment, sentiment_label
        FROM news
        WHERE symbol = ?
        AND fetched_at >= ?
        ORDER BY fetched_at DESC
        LIMIT 10
    """, (symbol, str(since)))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_news_for_sentiment():
    """
    Wo news nikalo jo abhi analyze nahi hui.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, symbol, headline
        FROM news
        WHERE sentiment = 0
        ORDER BY fetched_at DESC
        LIMIT 100
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ── MAIN ──────────────────────────────────────
if __name__ == "__main__":
    total = collect_all_news()

    if total > 0:
        print("\n   SAMPLE NEWS COLLECTED:")
        print("-" * 55)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT symbol, headline, source
            FROM news
            ORDER BY fetched_at DESC
            LIMIT 15
        """)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            headline = row['headline'][:50] + "..." \
                      if len(row['headline']) > 50 else row['headline']
            print(f"   [{row['symbol']:<10}] {headline}")

        print("-" * 55)
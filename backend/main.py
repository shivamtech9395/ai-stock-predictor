# ============================================
# FASTAPI BACKEND - FULLY FIXED VERSION
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import struct
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_connection, init_database
from datetime import date

app = FastAPI(title="AI Stock Predictor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_database()
    print("Database ready!")

def safe_float(val):
    """
    Koi bhi value ko safely float mein convert karo.
    Binary, string, int — sab handle karta hai.
    """
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, bytes):
        try:
            return struct.unpack('f', val)[0]
        except:
            try:
                return struct.unpack('d', val)[0]
            except:
                return 0.0
    try:
        return float(val)
    except:
        return 0.0

@app.get("/")
def root():
    return {"message": "AI Stock Predictor API Running!"}

@app.get("/api/predictions/today")
def get_today_predictions():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        today = str(date.today())

        cursor.execute("""
            SELECT 
                p.symbol,
                s.company,
                s.sector,
                p.prob_up,
                p.prob_down,
                p.signal,
                p.accuracy,
                p.prediction_date,
                pd.close as price
            FROM predictions p
            JOIN stocks s ON p.symbol = s.symbol
            LEFT JOIN price_data pd ON (
                pd.symbol = p.symbol AND
                pd.date = (
                    SELECT MAX(date) FROM price_data 
                    WHERE symbol = p.symbol
                )
            )
            WHERE p.prediction_date = ?
            ORDER BY p.prob_up DESC
        """, (today,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {"status": "no_data", "data": [], "date": today}

        results = []
        for row in rows:
            price = safe_float(row['price'])
            prob_up = safe_float(row['prob_up'])
            prob_down = safe_float(row['prob_down'])
            accuracy = safe_float(row['accuracy'])

            if price <= 500:
                price_range = "100-500"
            elif price <= 1000:
                price_range = "500-1000"
            elif price <= 3000:
                price_range = "1000-3000"
            else:
                price_range = "3000+"

            signal = str(row['signal'] or "")
            for emoji in ["🚀","📈","🔴","📉","⚖️"]:
                signal = signal.replace(emoji, "").strip()

            results.append({
                "symbol":          str(row['symbol']),
                "company":         str(row['company']),
                "sector":          str(row['sector']),
                "price":           round(price, 2),
                "price_range":     price_range,
                "prob_up":         round(prob_up, 1),
                "prob_down":       round(prob_down, 1),
                "signal":          signal,
                "accuracy":        round(accuracy, 1),
                "prediction_date": str(row['prediction_date']),
            })

        return {"status": "ok", "data": results, "date": today}

    except Exception as e:
        return {"status": "error", "message": str(e), "data": []}


@app.get("/api/market/summary")
def get_market_summary():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        today = str(date.today())

        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN prob_up >= 65 THEN 1 ELSE 0 END) as strong_buy,
                SUM(CASE WHEN prob_up >= 55 AND prob_up < 65 THEN 1 ELSE 0 END) as buy,
                SUM(CASE WHEN prob_down >= 65 THEN 1 ELSE 0 END) as strong_sell,
                SUM(CASE WHEN prob_down >= 55 AND prob_down < 65 THEN 1 ELSE 0 END) as sell,
                AVG(prob_up) as avg_bullish,
                AVG(accuracy) as avg_accuracy
            FROM predictions
            WHERE prediction_date = ?
        """, (today,))

        row = cursor.fetchone()
        conn.close()

        if not row or not row['total']:
            return {"status": "no_data"}

        avg = safe_float(row['avg_bullish'])
        mood = "BULLISH" if avg > 55 else "BEARISH" if avg < 45 else "NEUTRAL"

        return {
            "status":       "ok",
            "date":         today,
            "total":        int(row['total'] or 0),
            "strong_buy":   int(row['strong_buy'] or 0),
            "buy":          int(row['buy'] or 0),
            "strong_sell":  int(row['strong_sell'] or 0),
            "sell":         int(row['sell'] or 0),
            "avg_bullish":  round(avg, 1),
            "avg_accuracy": round(safe_float(row['avg_accuracy']), 1),
            "market_mood":  mood
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/stock/{symbol}")
def get_stock_detail(symbol: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM stocks WHERE symbol = ?",
                      (symbol.upper(),))
        stock = cursor.fetchone()

        if not stock:
            return {"error": "Stock not found"}

        cursor.execute("""
            SELECT date, open, high, low, close, volume
            FROM price_data WHERE symbol = ?
            ORDER BY date DESC LIMIT 30
        """, (symbol.upper(),))
        prices = cursor.fetchall()

        cursor.execute("""
            SELECT * FROM predictions WHERE symbol = ?
            ORDER BY prediction_date DESC LIMIT 1
        """, (symbol.upper(),))
        prediction = cursor.fetchone()

        cursor.execute("""
            SELECT headline, source, published_at,
                   sentiment, sentiment_label
            FROM news WHERE symbol = ?
            ORDER BY fetched_at DESC LIMIT 10
        """, (symbol.upper(),))
        news = cursor.fetchall()

        conn.close()

        # Price data clean karo
        clean_prices = []
        for p in prices:
            clean_prices.append({
                "date":   str(p['date']),
                "open":   round(safe_float(p['open']), 2),
                "high":   round(safe_float(p['high']), 2),
                "low":    round(safe_float(p['low']), 2),
                "close":  round(safe_float(p['close']), 2),
                "volume": int(safe_float(p['volume'])),
            })

        return {
            "stock":      dict(stock),
            "prices":     clean_prices,
            "prediction": dict(prediction) if prediction else None,
            "news":       [dict(n) for n in news],
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/news/market")
def get_market_news():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT headline, source, published_at,
                   sentiment, sentiment_label
            FROM news WHERE symbol = 'MARKET'
            ORDER BY fetched_at DESC LIMIT 20
        """)
        rows = cursor.fetchall()
        conn.close()
        return {"news": [dict(r) for r in rows]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/news/{symbol}")
def get_stock_news(symbol: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT headline, source, published_at,
                   sentiment, sentiment_label, fetched_at
            FROM news WHERE symbol = ?
            ORDER BY fetched_at DESC LIMIT 20
        """, (symbol.upper(),))
        rows = cursor.fetchall()
        conn.close()
        return {"symbol": symbol, "news": [dict(r) for r in rows]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/predictions/history")
def get_prediction_history():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT symbol, prediction_date, prob_up,
                   signal, accuracy, was_correct
            FROM predictions
            ORDER BY prediction_date DESC LIMIT 50
        """)
        rows = cursor.fetchall()
        conn.close()
        return {"history": [dict(r) for r in rows]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
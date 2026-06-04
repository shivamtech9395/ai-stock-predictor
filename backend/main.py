from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys, os, struct, yfinance as yf
from datetime import date, datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.connection import get_connection, init_database

app = FastAPI(title="AI Stock Predictor API", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "https://stockai-frontend-osx3.onrender.com"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    init_database()
    print("Database ready!")

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

def clean_row(row):
    """Convert any row to clean dict — no binary values"""
    result = {}
    for key in row.keys():
        val = row[key]
        if isinstance(val, bytes):
            try: result[key] = round(safe_float(val), 4)
            except: result[key] = 0.0
        else:
            result[key] = val
    return result

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
            SELECT p.symbol, s.company, s.sector,
                p.prob_up, p.prob_down, p.signal, p.accuracy,
                p.prediction_date, pd.close as price
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
        if not rows:
            return {"status": "no_data", "data": [], "date": today}
        results = []
        for row in rows:
            price = safe_float(row['price'])
            prob_up = safe_float(row['prob_up'])
            prob_down = safe_float(row['prob_down'])
            accuracy = safe_float(row['accuracy'])
            if price <= 500: price_range = "100-500"
            elif price <= 1000: price_range = "500-1000"
            elif price <= 3000: price_range = "1000-3000"
            else: price_range = "3000+"
            signal = str(row['signal'] or "")
            for e in ["🚀","📈","🔴","📉","⚖️"]: signal = signal.replace(e,"").strip()
            results.append({
                "symbol": str(row['symbol']),
                "company": str(row['company']),
                "sector": str(row['sector']),
                "price": round(price, 2),
                "price_range": price_range,
                "prob_up": round(prob_up, 1),
                "prob_down": round(prob_down, 1),
                "signal": signal,
                "accuracy": round(accuracy, 1),
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
            SELECT COUNT(*) as total,
                SUM(CASE WHEN prob_up >= 65 THEN 1 ELSE 0 END) as strong_buy,
                SUM(CASE WHEN prob_up >= 55 AND prob_up < 65 THEN 1 ELSE 0 END) as buy,
                SUM(CASE WHEN prob_down >= 65 THEN 1 ELSE 0 END) as strong_sell,
                SUM(CASE WHEN prob_down >= 55 AND prob_down < 65 THEN 1 ELSE 0 END) as sell,
                AVG(prob_up) as avg_bullish, AVG(accuracy) as avg_accuracy
            FROM predictions WHERE prediction_date = ?
        """, (today,))
        row = cursor.fetchone()
        conn.close()
        if not row or not row['total']: return {"status": "no_data"}
        avg = safe_float(row['avg_bullish'])
        mood = "BULLISH" if avg > 55 else "BEARISH" if avg < 45 else "NEUTRAL"
        return {"status": "ok", "date": today, "total": int(row['total'] or 0),
            "strong_buy": int(row['strong_buy'] or 0), "buy": int(row['buy'] or 0),
            "strong_sell": int(row['strong_sell'] or 0), "sell": int(row['sell'] or 0),
            "avg_bullish": round(avg, 1),
            "avg_accuracy": round(safe_float(row['avg_accuracy']), 1), "market_mood": mood}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/stock/{symbol}")
def get_stock_detail(symbol: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stocks WHERE symbol = ?", (symbol.upper(),))
        stock = cursor.fetchone()
        if not stock: return {"error": "Stock not found"}
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
            SELECT headline, source, published_at, sentiment, sentiment_label
            FROM news WHERE symbol = ?
            ORDER BY fetched_at DESC LIMIT 10
        """, (symbol.upper(),))
        news = cursor.fetchall()
        conn.close()
        clean_prices = [{
            "date": str(p['date']),
            "open": round(safe_float(p['open']), 2),
            "high": round(safe_float(p['high']), 2),
            "low": round(safe_float(p['low']), 2),
            "close": round(safe_float(p['close']), 2),
            "volume": int(safe_float(p['volume'])),
        } for p in prices]
        return {
            "stock": clean_row(stock),
            "prices": clean_prices,
            "prediction": clean_row(prediction) if prediction else None,
            "news": [clean_row(n) for n in news],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/news/market")
def get_market_news():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT headline, source, published_at, sentiment, sentiment_label
            FROM news WHERE symbol = 'MARKET' ORDER BY fetched_at DESC LIMIT 20""")
        rows = cursor.fetchall()
        conn.close()
        return {"news": [clean_row(r) for r in rows]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/news/{symbol}")
def get_stock_news(symbol: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT headline, source, published_at,
            sentiment, sentiment_label, fetched_at
            FROM news WHERE symbol = ? ORDER BY fetched_at DESC LIMIT 20""",
            (symbol.upper(),))
        rows = cursor.fetchall()
        conn.close()
        return {"symbol": symbol, "news": [clean_row(r) for r in rows]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/predictions/history")
def get_prediction_history():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT symbol, prediction_date, prob_up,
            signal, accuracy, was_correct
            FROM predictions ORDER BY prediction_date DESC LIMIT 50""")
        rows = cursor.fetchall()
        conn.close()
        return {"history": [clean_row(r) for r in rows]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/live/prices")
def get_live_prices():
    try:
        STOCK_SYMBOLS = {
            "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS",
            "HDFCBANK": "HDFCBANK.NS", "INFY": "INFY.NS",
            "ICICIBANK": "ICICIBANK.NS", "HINDUNILVR": "HINDUNILVR.NS",
            "SBIN": "SBIN.NS", "BHARTIARTL": "BHARTIARTL.NS", "LT": "LT.NS",
        }
        INDEX_SYMBOLS = {
            "NIFTY50": "^NSEI", "BANKNIFTY": "^NSEBANK",
            "SENSEX": "^BSESN", "FINNIFTY": "^CNXFIN",
        }
        prices = {}
        indices = {}
        for sym, yf_sym in STOCK_SYMBOLS.items():
            try:
                ticker = yf.Ticker(yf_sym)
                hist = ticker.history(period="2d", interval="1m")
                if not hist.empty and len(hist) >= 2:
                    curr = float(hist['Close'].iloc[-1])
                    prev = float(hist['Close'].iloc[-2])
                    chg = curr - prev
                    pct = (chg / prev) * 100
                    prices[sym] = {"price": round(curr,2), "change": round(chg,2), "change_pct": round(pct,2)}
            except: continue
        for name, yf_sym in INDEX_SYMBOLS.items():
            try:
                ticker = yf.Ticker(yf_sym)
                hist = ticker.history(period="2d", interval="1m")
                if not hist.empty and len(hist) >= 2:
                    curr = float(hist['Close'].iloc[-1])
                    prev = float(hist['Close'].iloc[-2])
                    chg = curr - prev
                    pct = (chg / prev) * 100
                    indices[name] = {"price": round(curr,2), "change": round(chg,2), "change_pct": round(pct,2)}
            except: continue
        return {"status": "ok", "prices": prices, "indices": indices,
                "updated_at": datetime.now().strftime("%H:%M:%S")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/earnings/upcoming")
def get_upcoming_earnings():
    return {"earnings": [
        {"symbol": "INFY", "company": "Infosys", "date": "2026-07-17", "quarter": "Q1 FY27"},
        {"symbol": "TCS", "company": "Tata Consultancy", "date": "2026-07-10", "quarter": "Q1 FY27"},
        {"symbol": "HDFCBANK", "company": "HDFC Bank", "date": "2026-07-19", "quarter": "Q1 FY27"},
        {"symbol": "RELIANCE", "company": "Reliance Industries", "date": "2026-07-25", "quarter": "Q1 FY27"},
        {"symbol": "ICICIBANK", "company": "ICICI Bank", "date": "2026-07-26", "quarter": "Q1 FY27"},
    ]}
@app.get("/api/market/close-report")
def get_market_close_report():
    try:
        import json
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT UNIQUE,
                report_json TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cursor.execute("""
            SELECT report_json, report_date, created_at
            FROM market_reports
            ORDER BY report_date DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        if not row:
            return {"status": "no_data", "message": "Run market_close_report.py first"}
        return {
            "status": "ok",
            "report_date": row['report_date'],
            "created_at": row['created_at'],
            "data": json.loads(row['report_json'])
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
from fastapi.responses import StreamingResponse
from backend.pdf_generator import generate_stock_pdf, generate_news_pdf

@app.get("/api/pdf/stock/{symbol}")
def download_stock_pdf(symbol: str):
    try:
        buffer = generate_stock_pdf(symbol.upper())
        if not buffer:
            return {"error": "Stock not found"}
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={symbol}_report.pdf"}
        )
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/pdf/news")
def download_news_pdf():
    try:
        buffer = generate_news_pdf()
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=daily_news_report.pdf"}
        )
    except Exception as e:
        return {"error": str(e)}    
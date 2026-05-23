# ============================================
# AI STOCK PREDICTOR - MULTI STOCK VERSION
# Predicts TOP 10 Nifty stocks at once
# ============================================

import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

# ── TOP 10 NIFTY STOCKS ───────────────────────
# Format: ("SYMBOL.NS", "Company Name", "Sector")
STOCKS = [
    ("RELIANCE.NS",   "Reliance Industries",  "Energy"),
    ("TCS.NS",        "Tata Consultancy",      "IT"),
    ("HDFCBANK.NS",   "HDFC Bank",             "Banking"),
    ("INFY.NS",       "Infosys",               "IT"),
    ("ICICIBANK.NS",  "ICICI Bank",            "Banking"),
    ("HINDUNILVR.NS", "Hindustan Unilever",    "FMCG"),
    ("SBIN.NS",       "State Bank of India",   "Banking"),
    ("BHARTIARTL.NS", "Bharti Airtel",         "Telecom"),
    ("KOTAKBANK.NS",  "Kotak Mahindra Bank",   "Banking"),
    ("LT.NS",         "Larsen & Toubro",       "Infrastructure"),
]

# ── FUNCTION: Calculate Indicators ────────────
# "def" matlab hum ek reusable block bana rahe hain
# Jab bhi kisi stock ke indicators chahiye — ye function call karenge
def calculate_indicators(df):
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    macd = ta.macd(df['Close'])
    df['MACD'] = macd.iloc[:, 0]
    df['MACD_Signal'] = macd.iloc[:, 1]
    
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['SMA_50'] = ta.sma(df['Close'], length=50)
    
    bbands = ta.bbands(df['Close'], length=20)
    df['BB_Upper'] = bbands.iloc[:, 0]
    df['BB_Lower'] = bbands.iloc[:, 2]
    
    df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
    df['Daily_Return'] = df['Close'].pct_change() * 100
    df['Price_Position'] = (
        (df['Close'] - df['Low'].rolling(52).min()) /
        (df['High'].rolling(52).max() - df['Low'].rolling(52).min())
    )
    return df

# ── FUNCTION: Train and Predict ───────────────
def predict_stock(symbol, company, sector):
    try:
        # Download data
        df = yf.download(symbol, period="2y", interval="1d", progress=False)
        df.columns = df.columns.get_level_values(0)
        
        if len(df) < 100:
            return None
        
        # Calculate indicators
        df = calculate_indicators(df)
        
        # Create target
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        features = ['RSI', 'MACD', 'MACD_Signal', 'SMA_20', 'SMA_50',
                    'BB_Upper', 'BB_Lower', 'Volume_Ratio',
                    'Daily_Return', 'Price_Position']
        
        df_clean = df[features + ['Target']].dropna()
        
        X = df_clean[features]
        y = df_clean['Target']
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        model = XGBClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            random_state=42,
            eval_metric='logloss'
        )
        model.fit(X_train, y_train)
        
        # Accuracy
        preds = model.predict(X_test)
        accuracy = accuracy_score(y_test, preds) * 100
        
        # Predict tomorrow
        latest = X.iloc[-1:].values
        prob = model.predict_proba(latest)[0]
        prob_up = prob[1] * 100
        prob_down = prob[0] * 100
        
        # Current price and RSI
        current_price = float(df['Close'].iloc[-1])
        current_rsi = float(df['RSI'].iloc[-1])
        
        # Signal
        if prob_up >= 65:
            signal = "STRONG BUY  🚀"
        elif prob_up >= 55:
            signal = "BUY         📈"
        elif prob_down >= 65:
            signal = "STRONG SELL 🔴"
        elif prob_down >= 55:
            signal = "SELL        📉"
        else:
            signal = "NEUTRAL     ⚖️ "

        # Return result as dictionary
        # Dictionary = ek container jisme key:value pairs hote hain
        return {
            "symbol":   symbol.replace(".NS", ""),
            "company":  company,
            "sector":   sector,
            "price":    current_price,
            "rsi":      current_rsi,
            "prob_up":  prob_up,
            "prob_down":prob_down,
            "accuracy": accuracy,
            "signal":   signal,
        }
    
    except Exception as e:
        # Agar koi stock fail ho — skip karo, baaki chalta rahe
        print(f"      Skipping {symbol} - {e}")
        return None

# ── MAIN PROGRAM ──────────────────────────────
print("=" * 65)
print("   AI STOCK PREDICTOR - NIFTY TOP 10 ANALYSIS")
print(f"   Analyzing {len(STOCKS)} stocks...")
print("=" * 65)

results = []  # Empty list — isme sab results store honge

for i, (symbol, company, sector) in enumerate(STOCKS):
    print(f"\n   [{i+1}/{len(STOCKS)}] Analyzing {company}...")
    result = predict_stock(symbol, company, sector)
    if result:
        results.append(result)
        print(f"          Price: Rs.{result['price']:.2f} | "
              f"UP: {result['prob_up']:.1f}% | "
              f"Signal: {result['signal']}")

# ── SORT BY HIGHEST UP PROBABILITY ────────────
# sorted() = list ko arrange karta hai
# key=lambda x: x['prob_up'] = prob_up ke basis pe sort karo
# reverse=True = highest pehle
results = sorted(results, key=lambda x: x['prob_up'], reverse=True)

# ── FINAL REPORT ──────────────────────────────
print("\n\n" + "=" * 65)
print("   FINAL REPORT - STOCKS RANKED BY AI CONFIDENCE")
print("=" * 65)
print(f"   {'RANK':<5} {'STOCK':<12} {'COMPANY':<22} {'PRICE':>8} "
      f"{'UP%':>6} {'RSI':>6} {'SIGNAL'}")
print("-" * 65)

for rank, r in enumerate(results, 1):
    print(f"   {rank:<5} {r['symbol']:<12} {r['company']:<22} "
          f"Rs.{r['price']:>7.0f} {r['prob_up']:>5.1f}% "
          f"{r['rsi']:>5.1f} {r['signal']}")

print("=" * 65)

# ── TOP 3 PICKS ───────────────────────────────
print("\n   TODAY'S TOP 3 AI PICKS:")
print("-" * 65)
for i, r in enumerate(results[:3], 1):
    print(f"\n   #{i} {r['company']} ({r['symbol']})")
    print(f"      Sector    : {r['sector']}")
    print(f"      Price     : Rs.{r['price']:.2f}")
    print(f"      UP Prob   : {r['prob_up']:.1f}%")
    print(f"      RSI       : {r['rsi']:.1f}")
    print(f"      Accuracy  : {r['accuracy']:.1f}%")
    print(f"      Signal    : {r['signal']}")

print("\n" + "=" * 65)
print("   DISCLAIMER: AI prediction only, not financial advice.")
print("   Always do your own research before investing!")
print("=" * 65 + "\n")
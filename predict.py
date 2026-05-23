# ============================================
# AI STOCK PREDICTOR - SPIRAL 1
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

print("=" * 50)
print("   AI STOCK PREDICTOR - Starting...")
print("=" * 50)

# ── STEP 1: Download Data ──────────────────────
print("\n[1/4] Downloading RELIANCE data from NSE...")
df = yf.download("RELIANCE.NS", period="2y", interval="1d")
df.columns = df.columns.get_level_values(0)
print(f"      Got {len(df)} days of data!")
print(f"      From: {df.index[0].date()} To: {df.index[-1].date()}")

# ── STEP 2: Calculate Technical Indicators ────
print("\n[2/4] Calculating technical indicators...")

df['RSI'] = ta.rsi(df['Close'], length=14)

macd = ta.macd(df['Close'])
df['MACD'] = macd.iloc[:, 0]
df['MACD_Signal'] = macd.iloc[:, 1]

df['SMA_20'] = ta.sma(df['Close'], length=20)
df['SMA_50'] = ta.sma(df['Close'], length=50)

# Bollinger Bands - FIXED for new pandas_ta version
bbands = ta.bbands(df['Close'], length=20)
df['BB_Upper'] = bbands.iloc[:, 0]
df['BB_Lower'] = bbands.iloc[:, 2]

df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
df['Daily_Return'] = df['Close'].pct_change() * 100
df['Price_Position'] = (df['Close'] - df['Low'].rolling(52).min()) / \
                       (df['High'].rolling(52).max() - df['Low'].rolling(52).min())

print("      RSI, MACD, Bollinger Bands, Moving Averages - Done!")

# ── STEP 3: Train AI Model ────────────────────
print("\n[3/4] Training XGBoost AI Model...")

df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

features = ['RSI', 'MACD', 'MACD_Signal', 'SMA_20', 'SMA_50',
            'BB_Upper', 'BB_Lower', 'Volume_Ratio',
            'Daily_Return', 'Price_Position']

df_clean = df[features + ['Target']].dropna()

X = df_clean[features]
y = df_clean['Target']

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

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions) * 100
print(f"      Model trained on {len(X_train)} days of data")
print(f"      Model accuracy: {accuracy:.1f}%")

# ── STEP 4: Predict Tomorrow ──────────────────
print("\n[4/4] Predicting tomorrow's movement...")

latest_data = X.iloc[-1:].values
prob = model.predict_proba(latest_data)[0]
prob_down = prob[0] * 100
prob_up = prob[1] * 100

latest_close = float(df['Close'].iloc[-1])
latest_rsi = float(df['RSI'].iloc[-1])
latest_volume_ratio = float(df['Volume_Ratio'].iloc[-1])

# ── FINAL RESULT ──────────────────────────────
print("\n" + "=" * 50)
print("   PREDICTION RESULT - RELIANCE.NS")
print("=" * 50)
print(f"   Today's Close Price : Rs.{latest_close:.2f}")
print(f"   RSI (14)            : {latest_rsi:.1f}")
print(f"   Volume vs Average   : {latest_volume_ratio:.2f}x")
print("-" * 50)
print(f"   Model Accuracy      : {accuracy:.1f}%")
print(f"   UP Probability      : {prob_up:.1f}%")
print(f"   DOWN Probability    : {prob_down:.1f}%")
print("-" * 50)

if prob_up >= 60:
    signal = "STRONG BUY >> "
elif prob_up >= 55:
    signal = "BUY >> "
elif prob_down >= 60:
    signal = "STRONG SELL <<"
elif prob_down >= 55:
    signal = "SELL <<"
else:
    signal = "NEUTRAL - Wait & Watch"

print(f"   SIGNAL              :  {signal}")
print("=" * 50)
print("\n  DISCLAIMER: AI prediction only, not financial advice.")
print("  Always do your own research before investing!\n")
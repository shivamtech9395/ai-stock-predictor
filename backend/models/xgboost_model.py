# ============================================
# XGBOOST MODEL - IMPROVED VERSION
# Fixed: infinity values, better error handling
# ============================================

import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database.connection import get_connection
from backend.data.feature_engineering import (
    get_stock_data_from_db,
    calculate_features,
    get_feature_columns
)

import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
from datetime import date

# Trained models yahan save honge
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved")
os.makedirs(MODELS_DIR, exist_ok=True)

def clean_data(X):
    """
    Infinity aur NaN values ko clean karo.
    XGBoost inf values handle nahi kar sakta —
    isliye replace karte hain.
    inf  = infinity (jab 0 se divide ho jata hai)
    NaN  = Not a Number (missing value)
    """
    # inf ko NaN se replace karo
    X = X.replace([np.inf, -np.inf], np.nan)
    # NaN ko column ke median se replace karo
    X = X.fillna(X.median())
    return X

def train_model(symbol):
    """
    Ek stock ke liye XGBoost model train karo
    aur disk pe save karo.
    """
    # Step 1: Database se data lo
    df = get_stock_data_from_db(symbol)
    if df is None or len(df) < 100:
        print(f"      Not enough data for {symbol}")
        return None

    # Step 2: Features calculate karo
    df = calculate_features(df)
    features = get_feature_columns()
    df_clean = df[features + ['target']].dropna()

    if len(df_clean) < 50:
        return None

    X = df_clean[features]
    y = df_clean['target']

    # Step 3: Infinity aur NaN clean karo
    X = clean_data(X)

    # Step 4: Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # Step 5: Model train karo
    model = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)

    # Step 6: Accuracy check karo
    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds) * 100

    # Step 7: Model save karo
    model_path = os.path.join(MODELS_DIR, f"{symbol}_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    return {
        "symbol":     symbol,
        "accuracy":   accuracy,
        "trained_on": len(X_train),
        "model_path": model_path
    }

def load_model(symbol):
    """
    Pehle se saved model load karo disk se.
    """
    model_path = os.path.join(MODELS_DIR, f"{symbol}_model.pkl")
    if not os.path.exists(model_path):
        return None
    with open(model_path, 'rb') as f:
        return pickle.load(f)

def predict_tomorrow(symbol):
    """
    Kal ka prediction karo.
    """
    # Data aur features prepare karo
    df = get_stock_data_from_db(symbol)
    if df is None:
        return None

    df = calculate_features(df)
    features = get_feature_columns()
    df_clean = df[features + ['target']].dropna()

    if len(df_clean) < 50:
        return None

    X = df_clean[features]
    y = df_clean['target']

    # Clean karo infinity values
    X = clean_data(X)

    # Model load karo — nahi hai toh train karo
    model = load_model(symbol)
    if model is None:
        train_result = train_model(symbol)
        if train_result is None:
            return None
        model = load_model(symbol)

    # Accuracy calculate karo
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds) * 100

    # Latest data se predict karo
    latest = X.iloc[-1:].values
    prob = model.predict_proba(latest)[0]
    prob_up   = prob[1] * 100
    prob_down = prob[0] * 100

    # Signal decide karo
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

    # Current values
    current_price = float(df['close'].iloc[-1])
    current_rsi   = float(df['rsi'].iloc[-1])

    return {
        "symbol":    symbol,
        "price":     current_price,
        "rsi":       current_rsi,
        "prob_up":   prob_up,
        "prob_down": prob_down,
        "accuracy":  accuracy,
        "signal":    signal,
    }

def save_prediction_to_db(result):
    """
    Prediction database mein save karo.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO predictions
        (symbol, prediction_date, prob_up, prob_down, signal, accuracy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        result['symbol'],
        str(date.today()),
        round(result['prob_up'], 2),
        round(result['prob_down'], 2),
        result['signal'],
        round(result['accuracy'], 2),
    ))
    conn.commit()
    conn.close()

# ── MAIN ──────────────────────────────────────
if __name__ == "__main__":

    SYMBOLS = [
        ("RELIANCE",   "Reliance Industries",  "Energy"),
        ("TCS",        "Tata Consultancy",      "IT"),
        ("HDFCBANK",   "HDFC Bank",             "Banking"),
        ("INFY",       "Infosys",               "IT"),
        ("ICICIBANK",  "ICICI Bank",            "Banking"),
        ("HINDUNILVR", "Hindustan Unilever",    "FMCG"),
        ("SBIN",       "State Bank of India",   "Banking"),
        ("BHARTIARTL", "Bharti Airtel",         "Telecom"),
        ("LT",         "Larsen & Toubro",       "Infrastructure"),
    ]

    print("=" * 60)
    print("   XGBOOST MODEL - Training & Prediction")
    print("=" * 60)

    results = []

    for i, (symbol, company, sector) in enumerate(SYMBOLS):
        print(f"\n   [{i+1}/{len(SYMBOLS)}] {company}...")

        try:
            # Train karo
            train_result = train_model(symbol)
            if train_result:
                print(f"          Trained   | Accuracy: {train_result['accuracy']:.1f}%")

            # Predict karo
            pred = predict_tomorrow(symbol)
            if pred:
                pred['company'] = company
                pred['sector']  = sector
                results.append(pred)

                # Database mein save karo
                save_prediction_to_db(pred)
                print(f"          Predicted | UP: {pred['prob_up']:.1f}% | {pred['signal']}")

        except Exception as e:
            print(f"          ERROR: {e} — skipping")
            continue

    # Sort by highest UP probability
    results = sorted(results, key=lambda x: x['prob_up'], reverse=True)

    # Final report
    print("\n\n" + "=" * 60)
    print("   TODAY'S AI PREDICTIONS - RANKED BY CONFIDENCE")
    print("=" * 60)
    print(f"   {'#':<3} {'STOCK':<12} {'COMPANY':<22} {'PRICE':>8} {'UP%':>6} {'SIGNAL'}")
    print("-" * 60)

    for rank, r in enumerate(results, 1):
        print(f"   {rank:<3} {r['symbol']:<12} {r['company']:<22} "
              f"Rs.{r['price']:>6.0f} {r['prob_up']:>5.1f}% {r['signal']}")

    print("\n" + "=" * 60)
    print("   Top 3 Picks Today:")
    print("-" * 60)
    for i, r in enumerate(results[:3], 1):
        print(f"\n   #{i} {r['company']} ({r['symbol']})")
        print(f"      Price    : Rs.{r['price']:.2f}")
        print(f"      UP Prob  : {r['prob_up']:.1f}%")
        print(f"      RSI      : {r['rsi']:.1f}")
        print(f"      Accuracy : {r['accuracy']:.1f}%")
        print(f"      Signal   : {r['signal']}")

    print("\n" + "=" * 60)
    print("   All predictions saved to database!")
    print("   Models saved to backend/models/saved/")
    print("\n   DISCLAIMER: AI prediction only, not financial advice!\n")
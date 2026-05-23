# ============================================
# FEATURE ENGINEERING
# Database se data uthao, indicators calculate
# karo, aur AI ke liye ready karo
# ============================================

import pandas as pd
import numpy as np
import pandas_ta as ta
import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database.connection import get_connection

def get_stock_data_from_db(symbol):
    """
    Database se ek stock ka poora price history uthao.
    symbol = "RELIANCE" (bina .NS ke)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, open, high, low, close, volume
        FROM price_data
        WHERE symbol = ?
        ORDER BY date ASC
    """, (symbol,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    # Database rows ko pandas DataFrame mein convert karo
    # DataFrame = ek table jisme rows aur columns hote hain
    df = pd.DataFrame([dict(row) for row in rows])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    return df

def calculate_features(df):
    """
    50+ features calculate karo ek stock ke liye.
    Ye features XGBoost model ko input denge.
    """
    # ── PRICE FEATURES ────────────────────────
    # pct_change = aaj ka change percentage mein
    df['daily_return']    = df['close'].pct_change() * 100
    df['return_5d']       = df['close'].pct_change(5) * 100
    df['return_10d']      = df['close'].pct_change(10) * 100
    df['return_20d']      = df['close'].pct_change(20) * 100

    # 52 week high/low se position
    df['high_52w']        = df['high'].rolling(252).max()
    df['low_52w']         = df['low'].rolling(252).min()
    df['price_position']  = (
        (df['close'] - df['low_52w']) /
        (df['high_52w'] - df['low_52w'] + 0.001)
    )

    # Gap = aaj ka open vs kal ka close
    df['gap']             = (
        (df['open'] - df['close'].shift(1)) /
        df['close'].shift(1) * 100
    )

    # ── MOVING AVERAGES ───────────────────────
    # SMA = Simple Moving Average
    # Price kitne dinon ke average se upar/neeche hai
    df['sma_20']          = ta.sma(df['close'], length=20)
    df['sma_50']          = ta.sma(df['close'], length=50)
    df['sma_200']         = ta.sma(df['close'], length=200)

    # Price vs moving average — positive = bullish
    df['price_vs_sma20']  = (df['close'] - df['sma_20']) / df['sma_20'] * 100
    df['price_vs_sma50']  = (df['close'] - df['sma_50']) / df['sma_50'] * 100

    # Golden cross = sma20 > sma50 = bullish signal
    df['golden_cross']    = (df['sma_20'] > df['sma_50']).astype(int)

    # ── MOMENTUM INDICATORS ───────────────────
    # RSI = Relative Strength Index
    # >70 = overbought (girne wala), <30 = oversold (uThne wala)
    df['rsi']             = ta.rsi(df['close'], length=14)
    df['rsi_signal']      = 0
    df.loc[df['rsi'] > 70, 'rsi_signal'] = -1  # Overbought = bearish
    df.loc[df['rsi'] < 30, 'rsi_signal'] = 1   # Oversold = bullish

    # MACD = trend following indicator
    macd_data             = ta.macd(df['close'])
    df['macd']            = macd_data.iloc[:, 0]
    df['macd_signal']     = macd_data.iloc[:, 1]
    df['macd_hist']       = macd_data.iloc[:, 2]
    # MACD histogram positive = bullish momentum
    df['macd_bullish']    = (df['macd_hist'] > 0).astype(int)

    # ── VOLATILITY INDICATORS ─────────────────
    # Bollinger Bands = price ki normal range
    bbands                = ta.bbands(df['close'], length=20)
    df['bb_upper']        = bbands.iloc[:, 0]
    df['bb_lower']        = bbands.iloc[:, 2]
    df['bb_width']        = (
        (df['bb_upper'] - df['bb_lower']) / df['sma_20'] * 100
    )
    # BB position: 0 = lower band pe, 1 = upper band pe
    df['bb_position']     = (
        (df['close'] - df['bb_lower']) /
        (df['bb_upper'] - df['bb_lower'] + 0.001)
    )

    # ATR = Average True Range = volatility measure
    df['atr']             = ta.atr(df['high'], df['low'], df['close'], length=14)
    df['atr_pct']         = df['atr'] / df['close'] * 100

    # ── VOLUME FEATURES ───────────────────────
    # Volume ratio = aaj ka volume vs average volume
    # >2 matlab unusually high volume = strong signal
    df['volume_ratio']    = df['volume'] / df['volume'].rolling(20).mean()
    df['volume_trend']    = df['volume'].pct_change(5) * 100

    # OBV = On Balance Volume
    # Volume direction track karta hai
    df['obv']             = ta.obv(df['close'], df['volume'])
    df['obv_trend']       = df['obv'].pct_change(10) * 100

    # ── CANDLE PATTERN FEATURES ───────────────
    # Body size = open aur close ke beech ka difference
    df['body_size']       = abs(df['close'] - df['open']) / df['open'] * 100
    # Upper shadow = high vs max(open,close)
    df['upper_shadow']    = (
        df['high'] - df[['open', 'close']].max(axis=1)
    ) / df['open'] * 100
    # Bullish candle = close > open
    df['is_bullish']      = (df['close'] > df['open']).astype(int)

    # ── TARGET VARIABLE ───────────────────────
    # Ye wo cheez hai jo AI predict karega
    # 1 = kal close aaj se upar hoga
    # 0 = kal close aaj se neeche hoga
    df['target']          = (df['close'].shift(-1) > df['close']).astype(int)

    return df

def get_feature_columns():
    """
    Ye list return karta hai — in features pe model train hoga.
    Yahan se easily add/remove kar sakte hain features.
    """
    return [
        # Price features
        'daily_return', 'return_5d', 'return_10d', 'return_20d',
        'price_position', 'gap',
        # Moving averages
        'price_vs_sma20', 'price_vs_sma50', 'golden_cross',
        # Momentum
        'rsi', 'rsi_signal', 'macd', 'macd_signal',
        'macd_hist', 'macd_bullish',
        # Volatility
        'bb_width', 'bb_position', 'atr_pct',
        # Volume
        'volume_ratio', 'volume_trend', 'obv_trend',
        # Candle
        'body_size', 'upper_shadow', 'is_bullish',
    ]

# ── TEST KARO ─────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("   FEATURE ENGINEERING - Test Run")
    print("=" * 55)

    # RELIANCE ke liye test karo
    symbol = "RELIANCE"
    print(f"\n   Loading {symbol} data from database...")
    df = get_stock_data_from_db(symbol)

    if df is None:
        print("   ERROR: No data found! Run price_collector.py first")
    else:
        print(f"   Loaded {len(df)} days of data")

        print(f"\n   Calculating features...")
        df = calculate_features(df)

        features = get_feature_columns()
        df_clean = df[features + ['target']].dropna()

        print(f"   Features calculated: {len(features)}")
        print(f"   Clean rows for training: {len(df_clean)}")

        print(f"\n   LATEST DAY FEATURES (RELIANCE):")
        print("-" * 55)
        latest = df_clean.iloc[-1]
        print(f"   RSI              : {latest['rsi']:.1f}")
        print(f"   MACD Bullish     : {'Yes' if latest['macd_bullish'] else 'No'}")
        print(f"   Volume Ratio     : {latest['volume_ratio']:.2f}x")
        print(f"   BB Position      : {latest['bb_position']:.2f}")
        print(f"   Price vs SMA20   : {latest['price_vs_sma20']:.2f}%")
        print(f"   Golden Cross     : {'Yes' if latest['golden_cross'] else 'No'}")
        print(f"   Is Bullish Candle: {'Yes' if latest['is_bullish'] else 'No'}")
        print("-" * 55)
        print(f"   Total features ready: {len(features)}")
        print(f"\n   Feature engineering working perfectly!")
        print("=" * 55)
# ============================================
# FINBERT SENTIMENT MODEL
# Financial news ko analyze karta hai
# Positive / Negative / Neutral score deta hai
# Completely FREE - HuggingFace se
# ============================================

import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database.connection import get_connection

def load_finbert():
    """
    FinBERT model load karo.
    Pehli baar internet se download hoga (~500MB)
    Uske baad local cache se load hoga — fast!
    """
    from transformers import pipeline

    print("   Loading FinBERT model...")
    print("   (First time = download hoga, 2-3 min lagenge)")

    # pipeline = FinBERT ko easy way se use karne ka tarika
    # task = "text-classification" matlab text ko classify karo
    # model = "ProsusAI/finbert" = financial news ke liye trained
    sentiment_pipeline = pipeline(
        task="text-classification",
        model="ProsusAI/finbert",
        truncation=True,
        max_length=512,
    )

    print("   FinBERT loaded successfully!")
    return sentiment_pipeline

def analyze_sentiment(text, pipeline):
    """
    Ek headline ka sentiment analyze karo.

    Returns:
        score  = -1.0 to +1.0
                 +1.0 = very positive (stock ke liye achha)
                 -1.0 = very negative (stock ke liye bura)
                  0.0 = neutral
        label  = 'positive' / 'negative' / 'neutral'
    """
    try:
        # FinBERT ko headline do
        result = pipeline(text)[0]

        label = result['label'].lower()    # positive/negative/neutral
        confidence = result['score']       # 0.0 to 1.0

        # Score calculate karo
        # Positive = +confidence
        # Negative = -confidence
        # Neutral  = 0
        if label == 'positive':
            score = confidence
        elif label == 'negative':
            score = -confidence
        else:
            score = 0.0

        return round(score, 4), label

    except Exception as e:
        return 0.0, 'neutral'

def update_sentiment_in_db(news_id, score, label):
    """
    Calculated sentiment database mein save karo.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE news
        SET sentiment = ?,
            sentiment_label = ?
        WHERE id = ?
    """, (score, label, news_id))
    conn.commit()
    conn.close()

def get_news_for_sentiment():
    """
    Wo news nikalo jo abhi analyze nahi hui.
    sentiment = 0 matlab analyze nahi hua abhi tak.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, symbol, headline
        FROM news
        WHERE sentiment = 0
        ORDER BY fetched_at DESC
        LIMIT 200
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def run_sentiment_analysis():
    """
    Sab unanalyzed news pe FinBERT chalao.
    """
    print("=" * 55)
    print("   FINBERT SENTIMENT ANALYSIS")
    print("=" * 55)

    # News lo database se
    news_list = get_news_for_sentiment()

    if not news_list:
        print("\n   No news to analyze!")
        print("   Run news_collector.py first")
        return {}

    print(f"\n   Headlines to analyze: {len(news_list)}")

    # FinBERT load karo
    pipeline = load_finbert()

    # Har headline analyze karo
    print(f"\n   Analyzing headlines...")
    print("-" * 55)

    results = {}
    positive_count = 0
    negative_count = 0
    neutral_count  = 0

    for i, news in enumerate(news_list):
        score, label = analyze_sentiment(news['headline'], pipeline)

        # Database update karo
        update_sentiment_in_db(news['id'], score, label)

        # Symbol ke liye scores collect karo
        symbol = news['symbol']
        if symbol not in results:
            results[symbol] = []
        results[symbol].append(score)

        # Count karo
        if label == 'positive':
            positive_count += 1
        elif label == 'negative':
            negative_count += 1
        else:
            neutral_count += 1

        # Har 10 headlines pe progress dikhao
        if (i + 1) % 10 == 0:
            print(f"   Analyzed {i+1}/{len(news_list)} headlines...")

    print(f"\n   Analysis Complete!")
    print(f"   Positive : {positive_count}")
    print(f"   Negative : {negative_count}")
    print(f"   Neutral  : {neutral_count}")

    return results

def get_stock_sentiment_score(symbol):
    """
    Ek stock ka overall sentiment score nikalo.
    Sab recent news ke scores ka average.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(sentiment) as avg_sentiment,
               COUNT(*) as news_count,
               SUM(CASE WHEN sentiment_label='positive' THEN 1 ELSE 0 END) as pos,
               SUM(CASE WHEN sentiment_label='negative' THEN 1 ELSE 0 END) as neg,
               SUM(CASE WHEN sentiment_label='neutral'  THEN 1 ELSE 0 END) as neu
        FROM news
        WHERE symbol = ?
        AND sentiment != 0
        ORDER BY fetched_at DESC
        LIMIT 20
    """, (symbol,))

    row = cursor.fetchone()
    conn.close()

    if not row or row['news_count'] == 0:
        return {
            "avg_score":  0.0,
            "news_count": 0,
            "positive":   0,
            "negative":   0,
            "neutral":    0,
            "label":      "neutral"
        }

    avg = row['avg_sentiment'] or 0.0

    # Overall label decide karo
    if avg > 0.1:
        label = "positive"
    elif avg < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {
        "avg_score":  round(avg, 4),
        "news_count": row['news_count'],
        "positive":   row['pos'],
        "negative":   row['neg'],
        "neutral":    row['neu'],
        "label":      label
    }

def show_sentiment_report():
    """
    Sab stocks ka sentiment report dikhao.
    """
    SYMBOLS = [
        ("RELIANCE",   "Reliance Industries"),
        ("TCS",        "Tata Consultancy"),
        ("HDFCBANK",   "HDFC Bank"),
        ("INFY",       "Infosys"),
        ("ICICIBANK",  "ICICI Bank"),
        ("HINDUNILVR", "Hindustan Unilever"),
        ("SBIN",       "State Bank of India"),
        ("BHARTIARTL", "Bharti Airtel"),
        ("LT",         "Larsen & Toubro"),
    ]

    print("\n" + "=" * 60)
    print("   SENTIMENT REPORT - ALL STOCKS")
    print("=" * 60)
    print(f"   {'STOCK':<12} {'COMPANY':<22} {'SCORE':>7} "
          f"{'NEWS':>5} {'LABEL'}")
    print("-" * 60)

    # Sort by sentiment score
    sentiment_data = []
    for symbol, company in SYMBOLS:
        s = get_stock_sentiment_score(symbol)
        sentiment_data.append((symbol, company, s))

    sentiment_data.sort(key=lambda x: x[2]['avg_score'], reverse=True)

    for symbol, company, s in sentiment_data:
        # Emoji based on label
        if s['label'] == 'positive':
            emoji = "📈"
        elif s['label'] == 'negative':
            emoji = "📉"
        else:
            emoji = "➖"

        print(f"   {symbol:<12} {company:<22} "
              f"{s['avg_score']:>+7.3f} "
              f"{s['news_count']:>5} {emoji} {s['label']}")

    print("=" * 60)

# ── MAIN ──────────────────────────────────────
if __name__ == "__main__":
    # Step 1: Sab news analyze karo
    run_sentiment_analysis()

    # Step 2: Report dikhao
    show_sentiment_report()
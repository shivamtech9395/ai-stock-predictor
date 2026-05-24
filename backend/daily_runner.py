# ============================================
# DAILY RUNNER
# Ek command se poora pipeline chalao:
# 1. News collect karo
# 2. Sentiment analyze karo  
# 3. Price data update karo
# 4. AI predictions run karo
# 5. Final report dikhao
# ============================================

import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

# Sab modules import karo
from backend.data.price_collector import collect_all_stocks
from backend.data.news_collector import collect_all_news
from backend.data.feature_engineering import (
    get_stock_data_from_db,
    calculate_features,
    get_feature_columns
)
from backend.models.xgboost_model import (
    train_model,
    predict_tomorrow,
    save_prediction_to_db
)
from backend.models.sentiment_model import (
    load_finbert,
    run_sentiment_analysis,
    get_stock_sentiment_score
)
from backend.database.connection import get_connection

# ── STOCKS LIST ───────────────────────────────
STOCKS = [
    ("RELIANCE",   "Reliance Industries",  "Energy",          1354),
    ("TCS",        "Tata Consultancy",      "IT",              2317),
    ("HDFCBANK",   "HDFC Bank",             "Banking",          767),
    ("INFY",       "Infosys",               "IT",              1174),
    ("ICICIBANK",  "ICICI Bank",            "Banking",         1264),
    ("HINDUNILVR", "Hindustan Unilever",    "FMCG",            2204),
    ("SBIN",       "State Bank of India",   "Banking",          949),
    ("BHARTIARTL", "Bharti Airtel",         "Telecom",         1871),
    ("LT",         "Larsen & Toubro",       "Infrastructure",  3927),
]

def get_price_range(price):
    """
    Price ke hisaab se range category batao.
    """
    if price <= 500:
        return "₹100-500"
    elif price <= 1000:
        return "₹500-1000"
    elif price <= 3000:
        return "₹1000-3000"
    else:
        return "₹3000+"

def run_daily_pipeline():
    """
    Poora daily pipeline ek function mein.
    """
    start_time = datetime.now()

    print("\n" + "🚀 " * 25)
    print("   AI STOCK PREDICTOR — DAILY PIPELINE")
    print(f"   Date: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
    print("🚀 " * 25 + "\n")

    # ══════════════════════════════════════════
    # STEP 1: PRICE DATA UPDATE
    # ══════════════════════════════════════════
    print("━" * 55)
    print("   STEP 1/4 — Updating Price Data")
    print("━" * 55)
    collect_all_stocks()

    # ══════════════════════════════════════════
    # STEP 2: NEWS COLLECTION
    # ══════════════════════════════════════════
    print("\n" + "━" * 55)
    print("   STEP 2/4 — Collecting Latest News")
    print("━" * 55)
    collect_all_news()

    # ══════════════════════════════════════════
    # STEP 3: SENTIMENT ANALYSIS
    # ══════════════════════════════════════════
    print("\n" + "━" * 55)
    print("   STEP 3/4 — Running FinBERT Sentiment")
    print("━" * 55)
    run_sentiment_analysis()

    # ══════════════════════════════════════════
    # STEP 4: AI PREDICTIONS
    # ══════════════════════════════════════════
    print("\n" + "━" * 55)
    print("   STEP 4/4 — Running AI Predictions")
    print("━" * 55)

    results = []

    for symbol, company, sector, approx_price in STOCKS:
        print(f"\n   Predicting {company}...")

        try:
            # Train + Predict
            train_model(symbol)
            pred = predict_tomorrow(symbol)

            if pred:
                # Sentiment score add karo
                sentiment = get_stock_sentiment_score(symbol)
                pred['company']   = company
                pred['sector']    = sector
                pred['sentiment'] = sentiment['avg_score']
                pred['sent_label']= sentiment['label']
                pred['news_count']= sentiment['news_count']
                pred['price_range']= get_price_range(pred['price'])

                # Combined score — AI + Sentiment
                # 70% AI prediction + 30% sentiment
                combined = (pred['prob_up'] * 0.70) + \
                           (sentiment['avg_score'] * 100 * 0.30)
                pred['combined_score'] = round(combined, 2)

                results.append(pred)
                save_prediction_to_db(pred)

                print(f"   ✅ UP: {pred['prob_up']:.1f}% | "
                      f"Sentiment: {sentiment['label']} | "
                      f"Combined: {pred['combined_score']:.1f}")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue

    # ══════════════════════════════════════════
    # FINAL REPORT
    # ══════════════════════════════════════════
    results_sorted = sorted(
        results,
        key=lambda x: x['combined_score'],
        reverse=True
    )

    end_time = datetime.now()
    duration = (end_time - start_time).seconds

    print("\n\n" + "═" * 60)
    print("   📊 TODAY'S AI REPORT")
    print(f"   Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
    print("═" * 60)

    # ── Price range wise breakdown ─────────────
    ranges = ["₹100-500", "₹500-1000", "₹1000-3000", "₹3000+"]
    for price_range in ranges:
        range_stocks = [r for r in results_sorted
                       if r['price_range'] == price_range]
        if range_stocks:
            print(f"\n   💰 PRICE RANGE: {price_range}")
            print(f"   {'STOCK':<12} {'COMPANY':<20} {'PRICE':>8} "
                  f"{'AI%':>6} {'SENT':>8} {'SIGNAL'}")
            print("   " + "-" * 58)
            for r in range_stocks:
                sent_emoji = "📈" if r['sent_label'] == 'positive' \
                           else "📉" if r['sent_label'] == 'negative' \
                           else "➖"
                print(f"   {r['symbol']:<12} {r['company']:<20} "
                      f"₹{r['price']:>6.0f} "
                      f"{r['prob_up']:>5.1f}% "
                      f"{sent_emoji}{r['sentiment']:>+6.2f} "
                      f"{r['signal']}")

    # ── Top 5 overall picks ────────────────────
    print("\n\n   🏆 TOP 5 PICKS TODAY (AI + Sentiment Combined)")
    print("   " + "═" * 55)

    for i, r in enumerate(results_sorted[:5], 1):
        sent_emoji = "📈" if r['sent_label'] == 'positive' \
                   else "📉" if r['sent_label'] == 'negative' \
                   else "➖"

        print(f"""
   #{i} {r['company']} ({r['symbol']})
   ┌─────────────────────────────────────────
   │ Sector       : {r['sector']}
   │ Price Range  : {r['price_range']}
   │ Current Price: ₹{r['price']:.2f}
   │ RSI          : {r['rsi']:.1f}
   │ AI Score     : {r['prob_up']:.1f}% UP probability
   │ News Sentiment: {sent_emoji} {r['sent_label'].upper()} ({r['sentiment']:+.3f})
   │ News Count   : {r['news_count']} articles analyzed
   │ Combined Score: {r['combined_score']:.1f}/100
   │ SIGNAL       : {r['signal']}
   └─────────────────────────────────────────""")

    # ── Stocks to AVOID ───────────────────────
    avoid = [r for r in results_sorted
             if 'SELL' in r['signal'] and r['sent_label'] == 'negative']
    if avoid:
        print("\n   ⚠️  STOCKS TO AVOID TODAY:")
        print("   " + "-" * 40)
        for r in avoid:
            print(f"   ❌ {r['company']} ({r['symbol']}) — "
                  f"AI: {r['prob_up']:.1f}% UP | "
                  f"Sentiment: {r['sent_label']}")

    print(f"\n   ⏱️  Pipeline completed in {duration} seconds")
    print("   💾 All predictions saved to database")
    print("\n   ⚠️  DISCLAIMER: AI prediction only!")
    print("   Always research before investing!")
    print("═" * 60 + "\n")

    return results_sorted

# ── MAIN ──────────────────────────────────────
if __name__ == "__main__":
    run_daily_pipeline()
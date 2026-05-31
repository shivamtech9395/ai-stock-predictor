# ============================================
# DAILY RUNNER
# Ek command se poora pipeline chalao:
# 1. News collect karo
# 2. Sentiment analyze karo  
# 3. Price data update karo
# 4. AI predictions run karo
# 5. Final report dikhao
# ============================================
# ============================================
# DAILY RUNNER V2 - 142 STOCKS
# ============================================

import sys, os, warnings
warnings.filterwarnings('ignore')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from backend.data.price_collector import collect_all_stocks
from backend.data.news_collector import collect_all_news
from backend.data.feature_engineering import (
    get_stock_data_from_db, calculate_features, get_feature_columns
)
from backend.models.xgboost_model import train_model, predict_tomorrow, save_prediction_to_db
from backend.models.sentiment_model import run_sentiment_analysis, get_stock_sentiment_score
from backend.database.connection import get_connection
from backend.data.stocks_list import NIFTY_500_STOCKS

def get_price_range(price):
    if price <= 500:   return "100-500"
    elif price <= 1000: return "500-1000"
    elif price <= 3000: return "1000-3000"
    else:               return "3000+"

def run_daily_pipeline():
    start_time = datetime.now()

    print("\n" + "🚀 " * 20)
    print("   AI STOCK PREDICTOR — DAILY PIPELINE V2")
    print(f"   Date: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
    print(f"   Stocks: {len(NIFTY_500_STOCKS)}")
    print("🚀 " * 20 + "\n")

    # STEP 1: Price data
    print("━" * 55)
    print("   STEP 1/4 — Updating Price Data")
    print("━" * 55)
    collect_all_stocks()

    # STEP 2: News
    print("\n" + "━" * 55)
    print("   STEP 2/4 — Collecting News")
    print("━" * 55)
    collect_all_news()

    # STEP 3: Sentiment
    print("\n" + "━" * 55)
    print("   STEP 3/4 — FinBERT Sentiment")
    print("━" * 55)
    run_sentiment_analysis()

    # STEP 4: Predictions
    print("\n" + "━" * 55)
    print("   STEP 4/4 — AI Predictions")
    print(f"   Training models for {len(NIFTY_500_STOCKS)} stocks...")
    print("   (This will take 20-30 minutes)")
    print("━" * 55)

    results = []
    success = 0
    failed = 0

    for i, (symbol, company, sector) in enumerate(NIFTY_500_STOCKS):
        print(f"\n   [{i+1}/{len(NIFTY_500_STOCKS)}] {company}...", end=" ", flush=True)
        try:
            train_result = train_model(symbol)
            if not train_result:
                print("❌ no data")
                failed += 1
                continue

            pred = predict_tomorrow(symbol)
            if not pred:
                print("❌ predict failed")
                failed += 1
                continue

            sentiment = get_stock_sentiment_score(symbol)
            pred['company']     = company
            pred['sector']      = sector
            pred['sentiment']   = sentiment['avg_score']
            pred['sent_label']  = sentiment['label']
            pred['news_count']  = sentiment['news_count']
            pred['price_range'] = get_price_range(pred['price'])

            combined = (pred['prob_up'] * 0.70) + (sentiment['avg_score'] * 100 * 0.30)
            pred['combined_score'] = round(combined, 2)

            results.append(pred)
            save_prediction_to_db(pred)
            success += 1

            signal = pred['signal'].replace("🚀","").replace("📈","").replace("🔴","").replace("📉","").replace("⚖️","").strip()
            print(f"✅ UP:{pred['prob_up']:.0f}% | {signal}")

        except Exception as e:
            print(f"❌ {str(e)[:30]}")
            failed += 1
            continue

    # Sort by combined score
    results = sorted(results, key=lambda x: x['combined_score'], reverse=True)

    duration = (datetime.now() - start_time).seconds
    mins = duration // 60
    secs = duration % 60

    # Final report
    print("\n\n" + "═" * 60)
    print("   📊 TODAY'S AI REPORT")
    print(f"   Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
    print("═" * 60)

    # Price range breakdown
    ranges = ["100-500", "500-1000", "1000-3000", "3000+"]
    range_labels = {"100-500": "₹100-500", "500-1000": "₹500-1000",
                    "1000-3000": "₹1000-3000", "3000+": "₹3000+"}

    for pr in ranges:
        range_stocks = [r for r in results if r.get('price_range') == pr]
        if range_stocks:
            print(f"\n   💰 {range_labels[pr]} — {len(range_stocks)} stocks")
            print(f"   {'STOCK':<12} {'COMPANY':<22} {'PRICE':>8} {'UP%':>6} {'SIGNAL'}")
            print("   " + "-" * 55)
            for r in range_stocks[:5]:  # Top 5 per range
                sig = r['signal'].replace("🚀","").replace("📈","").replace("🔴","").replace("📉","").replace("⚖️","").strip()
                print(f"   {r['symbol']:<12} {r['company']:<22} ₹{r['price']:>6.0f} {r['prob_up']:>5.1f}% {sig}")

    # Top 10 overall
    print("\n\n   🏆 TOP 10 PICKS TODAY")
    print("   " + "═" * 55)
    for i, r in enumerate(results[:10], 1):
        sig = r['signal'].replace("🚀","").replace("📈","").replace("🔴","").replace("📉","").replace("⚖️","").strip()
        sent_emoji = "📈" if r['sent_label'] == 'positive' else "📉" if r['sent_label'] == 'negative' else "➖"
        print(f"   #{i:<2} {r['symbol']:<12} {r['company']:<22} UP:{r['prob_up']:.0f}% {sent_emoji} {sig}")

    print(f"\n   ✅ Successful : {success}/{len(NIFTY_500_STOCKS)} stocks")
    print(f"   ⏱️  Time taken  : {mins}m {secs}s")
    print(f"   💾 All predictions saved to database")
    print("\n   ⚠️  DISCLAIMER: AI prediction only, not financial advice!")
    print("═" * 60 + "\n")

    return results

if __name__ == "__main__":
    run_daily_pipeline()
# ============================================
# PDF GENERATOR
# Stock detail + News PDF download
# ============================================

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import struct, sys, os, json
from datetime import date, datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database.connection import get_connection

# Colors
DARK_BG    = HexColor('#0a0e1a')
BLUE       = HexColor('#1d4ed8')
LIGHT_BLUE = HexColor('#3b82f6')
GREEN      = HexColor('#10b981')
RED        = HexColor('#ef4444')
YELLOW     = HexColor('#f59e0b')
GRAY       = HexColor('#6b7280')
LIGHT_GRAY = HexColor('#f3f4f6')
WHITE      = white

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

def get_styles():
    styles = getSampleStyleSheet()
    custom = {
        'title': ParagraphStyle('title', fontSize=22, textColor=BLUE,
                                spaceAfter=6, fontName='Helvetica-Bold', alignment=TA_CENTER),
        'subtitle': ParagraphStyle('subtitle', fontSize=13, textColor=GRAY,
                                   spaceAfter=4, fontName='Helvetica', alignment=TA_CENTER),
        'h1': ParagraphStyle('h1', fontSize=14, textColor=BLUE,
                             spaceAfter=4, spaceBefore=12, fontName='Helvetica-Bold'),
        'h2': ParagraphStyle('h2', fontSize=12, textColor=LIGHT_BLUE,
                             spaceAfter=3, spaceBefore=8, fontName='Helvetica-Bold'),
        'body': ParagraphStyle('body', fontSize=10, textColor=black,
                               spaceAfter=3, fontName='Helvetica', leading=14),
        'small': ParagraphStyle('small', fontSize=9, textColor=GRAY,
                                spaceAfter=2, fontName='Helvetica'),
        'disclaimer': ParagraphStyle('disclaimer', fontSize=8, textColor=GRAY,
                                     spaceAfter=2, fontName='Helvetica-Oblique',
                                     alignment=TA_CENTER),
    }
    return custom

def generate_stock_pdf(symbol):
    """
    Ek stock ka complete PDF generate karo
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Stock info
    cursor.execute("SELECT * FROM stocks WHERE symbol = ?", (symbol.upper(),))
    stock = cursor.fetchone()

    # Price data
    cursor.execute("""
        SELECT date, open, high, low, close, volume
        FROM price_data WHERE symbol = ?
        ORDER BY date DESC LIMIT 30
    """, (symbol.upper(),))
    prices = cursor.fetchall()

    # Prediction
    cursor.execute("""
        SELECT * FROM predictions WHERE symbol = ?
        ORDER BY prediction_date DESC LIMIT 1
    """, (symbol.upper(),))
    pred = cursor.fetchone()

    # News
    cursor.execute("""
        SELECT headline, source, published_at, sentiment_label
        FROM news WHERE symbol = ?
        ORDER BY fetched_at DESC LIMIT 15
    """, (symbol.upper(),))
    news = cursor.fetchall()

    conn.close()

    if not stock:
        return None

    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = get_styles()
    story = []

    # ── HEADER ──────────────────────────────────
    story.append(Paragraph("StockAI — NSE Intelligence Platform", styles['subtitle']))
    story.append(Paragraph(f"{symbol} — {stock['company']}", styles['title']))
    story.append(Paragraph(f"Report generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
                           styles['small']))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=12))

    # ── STOCK INFO ───────────────────────────────
    story.append(Paragraph("Company Overview", styles['h1']))

    info_data = [
        ["Symbol", symbol.upper(), "Sector", stock['sector']],
        ["Company", stock['company'], "Exchange", "NSE"],
        ["Report Date", str(date.today()), "Status", "Active"],
    ]
    info_table = Table(info_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), LIGHT_BLUE),
        ('BACKGROUND', (2,0), (2,-1), LIGHT_BLUE),
        ('TEXTCOLOR', (0,0), (0,-1), WHITE),
        ('TEXTCOLOR', (2,0), (2,-1), WHITE),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, GRAY),
        ('ROWBACKGROUNDS', (1,0), (1,-1), [LIGHT_GRAY, WHITE]),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # ── AI PREDICTION ────────────────────────────
    if pred:
        story.append(Paragraph("AI Prediction", styles['h1']))

        prob_up   = safe_float(pred['prob_up'])
        prob_down = safe_float(pred['prob_down'])
        accuracy  = safe_float(pred['accuracy'])
        signal    = str(pred['signal'] or "").replace("🚀","").replace("📈","").replace("🔴","").replace("📉","").replace("⚖️","").strip()

        signal_color = GREEN if "BUY" in signal.upper() else RED if "SELL" in signal.upper() else YELLOW

        pred_data = [
            ["Signal", signal, "Prediction Date", str(pred['prediction_date'])],
            ["UP Probability", f"{prob_up:.1f}%", "DOWN Probability", f"{prob_down:.1f}%"],
            ["Model Accuracy", f"{accuracy:.1f}%", "Model", "XGBoost + Features"],
        ]
        pred_table = Table(pred_data, colWidths=[4*cm, 5*cm, 4*cm, 4*cm])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), BLUE),
            ('BACKGROUND', (2,0), (2,-1), BLUE),
            ('TEXTCOLOR', (0,0), (0,-1), WHITE),
            ('TEXTCOLOR', (2,0), (2,-1), WHITE),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('PADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, GRAY),
            ('ROWBACKGROUNDS', (1,0), (1,-1), [LIGHT_GRAY, WHITE]),
            ('TEXTCOLOR', (1,0), (1,0), signal_color),
            ('FONTNAME', (1,0), (1,0), 'Helvetica-Bold'),
        ]))
        story.append(pred_table)

        # AI explanation
        story.append(Spacer(1, 8))
        if prob_up >= 65:
            explanation = f"BULLISH SIGNAL: AI model predicts {prob_up:.1f}% probability of upward price movement. This is based on XGBoost model trained on 2 years of daily price data with 24 technical features including RSI, MACD, Bollinger Bands, Volume Ratio, and news sentiment. Consider this stock for potential gains. Always use stop-loss."
        elif prob_up <= 35:
            explanation = f"BEARISH SIGNAL: AI model predicts only {prob_up:.1f}% chance of going up (DOWN probability: {prob_down:.1f}%). Strong downward pattern detected. Avoid buying today. If holding, consider booking profits or setting tight stop-loss."
        else:
            explanation = f"NEUTRAL SIGNAL: Mixed signals with {prob_up:.1f}% up probability. No clear directional bias today. Wait for a clearer signal before entering a position. Patience is key in uncertain markets."

        story.append(Paragraph(f"<b>AI Analysis:</b> {explanation}", styles['body']))
        story.append(Spacer(1, 12))

    # ── PRICE HISTORY ────────────────────────────
    if prices:
        story.append(Paragraph("Price History (Last 30 Trading Days)", styles['h1']))

        price_header = ["Date", "Open", "High", "Low", "Close", "Volume"]
        price_rows   = [price_header]
        for p in prices[:20]:
            price_rows.append([
                str(p['date']),
                f"₹{safe_float(p['open']):,.2f}",
                f"₹{safe_float(p['high']):,.2f}",
                f"₹{safe_float(p['low']):,.2f}",
                f"₹{safe_float(p['close']):,.2f}",
                f"{int(safe_float(p['volume'])):,}",
            ])

        price_table = Table(price_rows, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3.5*cm])
        price_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), BLUE),
            ('TEXTCOLOR', (0,0), (-1,0), WHITE),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('PADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.3, GRAY),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ]))
        story.append(price_table)
        story.append(Spacer(1, 12))

    # ── NEWS ─────────────────────────────────────
    if news:
        story.append(Paragraph("Latest News & Sentiment Analysis", styles['h1']))

        for n in news:
            sentiment = str(n['sentiment_label'] or 'neutral')
            color = GREEN if sentiment == 'positive' else RED if sentiment == 'negative' else GRAY
            emoji = "▲" if sentiment == 'positive' else "▼" if sentiment == 'negative' else "—"

            news_data = [
                [f"{emoji} {str(n['headline'][:80])}..."],
                [f"Source: {n['source']} | Date: {str(n['published_at'])[:10]} | Sentiment: {sentiment.upper()}"],
            ]
            news_table = Table(news_data, colWidths=[17*cm])
            news_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
                ('FONTNAME', (0,1), (0,1), 'Helvetica'),
                ('FONTSIZE', (0,0), (0,0), 9),
                ('FONTSIZE', (0,1), (0,1), 8),
                ('TEXTCOLOR', (0,1), (0,1), GRAY),
                ('PADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('BACKGROUND', (0,0), (0,0), LIGHT_GRAY),
                ('LINEBELOW', (0,-1), (-1,-1), 0.3, GRAY),
            ]))
            story.append(news_table)
            story.append(Spacer(1, 3))

    # ── DISCLAIMER ───────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=GRAY))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "DISCLAIMER: This report is generated by AI for educational purposes only. "
        "It is NOT financial advice. Stock market investments are subject to market risks. "
        "Always do your own research and consult a SEBI-registered financial advisor before investing. "
        "Past performance does not guarantee future results.",
        styles['disclaimer']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_news_pdf():
    """
    Daily market news PDF generate karo
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Market news
    cursor.execute("""
        SELECT symbol, headline, source, published_at, sentiment_label
        FROM news
        ORDER BY fetched_at DESC
        LIMIT 50
    """)
    all_news = cursor.fetchall()
    conn.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = get_styles()
    story = []

    # Header
    story.append(Paragraph("StockAI — Daily News Report", styles['subtitle']))
    story.append(Paragraph(f"Market News & Sentiment Analysis", styles['title']))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')} | Total articles: {len(all_news)}",
        styles['small']
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=12))

    # Sentiment summary
    pos = sum(1 for n in all_news if str(n['sentiment_label']) == 'positive')
    neg = sum(1 for n in all_news if str(n['sentiment_label']) == 'negative')
    neu = len(all_news) - pos - neg

    summary_data = [
        ["Total Articles", str(len(all_news)), "Positive", str(pos), "Negative", str(neg), "Neutral", str(neu)],
    ]
    summary_table = Table(summary_data, colWidths=[3*cm, 2*cm, 2.5*cm, 1.5*cm, 2.5*cm, 1.5*cm, 2.5*cm, 1.5*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), BLUE),
        ('BACKGROUND', (2,0), (3,0), GREEN),
        ('BACKGROUND', (4,0), (5,0), RED),
        ('BACKGROUND', (6,0), (7,0), GRAY),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Group by symbol
    from collections import defaultdict
    news_by_symbol = defaultdict(list)
    for n in all_news:
        news_by_symbol[str(n['symbol'] or 'MARKET')].append(n)

    for symbol, articles in sorted(news_by_symbol.items()):
        story.append(Paragraph(f"{symbol}", styles['h2']))
        for n in articles[:5]:
            sentiment = str(n['sentiment_label'] or 'neutral')
            emoji = "▲" if sentiment == 'positive' else "▼" if sentiment == 'negative' else "—"
            headline = str(n['headline'])
            if len(headline) > 100:
                headline = headline[:100] + "..."

            story.append(Paragraph(
                f"<b>{emoji}</b> {headline}",
                styles['body']
            ))
            story.append(Paragraph(
                f"Source: {n['source']} | {str(n['published_at'])[:10]} | {sentiment.upper()}",
                styles['small']
            ))
            story.append(Spacer(1, 3))
        story.append(HRFlowable(width="100%", thickness=0.3, color=LIGHT_GRAY))
        story.append(Spacer(1, 6))

    # Disclaimer
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=GRAY))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "DISCLAIMER: This report is for educational purposes only. Not financial advice. "
        "Always consult a SEBI-registered advisor before investing.",
        styles['disclaimer']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    print("Testing PDF generation...")
    buf = generate_stock_pdf("RELIANCE")
    if buf:
        with open("test_stock.pdf", "wb") as f:
            f.write(buf.read())
        print("Stock PDF saved: test_stock.pdf")

    buf2 = generate_news_pdf()
    if buf2:
        with open("test_news.pdf", "wb") as f:
            f.write(buf2.read())
        print("News PDF saved: test_news.pdf")
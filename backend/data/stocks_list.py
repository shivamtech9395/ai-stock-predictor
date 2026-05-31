# ============================================
# NIFTY 500 STOCKS LIST
# Ye file sare NSE stocks ki master list hai
# Price range wise categorized
# ============================================

# Nifty 500 stocks — symbol aur company name
# Yfinance format mein (.NS suffix)
NIFTY_500_STOCKS = [
    # ── BANKING ──────────────────────────────
    ("HDFCBANK", "HDFC Bank", "Banking"),
    ("ICICIBANK", "ICICI Bank", "Banking"),
    ("SBIN", "State Bank of India", "Banking"),
    ("KOTAKBANK", "Kotak Mahindra Bank", "Banking"),
    ("AXISBANK", "Axis Bank", "Banking"),
    ("INDUSINDBK", "IndusInd Bank", "Banking"),
    ("BANDHANBNK", "Bandhan Bank", "Banking"),
    ("FEDERALBNK", "Federal Bank", "Banking"),
    ("IDFCFIRSTB", "IDFC First Bank", "Banking"),
    ("PNB", "Punjab National Bank", "Banking"),
    ("BANKBARODA", "Bank of Baroda", "Banking"),
    ("CANBK", "Canara Bank", "Banking"),
    ("UNIONBANK", "Union Bank of India", "Banking"),
    ("RBLBANK", "RBL Bank", "Banking"),
    ("YESBANK", "Yes Bank", "Banking"),

    # ── IT ───────────────────────────────────
    ("TCS", "Tata Consultancy Services", "IT"),
    ("INFY", "Infosys", "IT"),
    ("HCLTECH", "HCL Technologies", "IT"),
    ("WIPRO", "Wipro", "IT"),
    ("TECHM", "Tech Mahindra", "IT"),
    ("LTIM", "LTIMindtree", "IT"),
    ("MPHASIS", "Mphasis", "IT"),
    ("PERSISTENT", "Persistent Systems", "IT"),
    ("COFORGE", "Coforge", "IT"),
    ("KPITTECH", "KPIT Technologies", "IT"),
    ("OFSS", "Oracle Financial Services", "IT"),
    ("HEXAWARE", "Hexaware Technologies", "IT"),

    # ── ENERGY & OIL ─────────────────────────
    ("RELIANCE", "Reliance Industries", "Energy"),
    ("ONGC", "Oil & Natural Gas Corp", "Energy"),
    ("POWERGRID", "Power Grid Corp", "Energy"),
    ("NTPC", "NTPC Limited", "Energy"),
    ("ADANIGREEN", "Adani Green Energy", "Energy"),
    ("ADANIPOWER", "Adani Power", "Energy"),
    ("TATAPOWER", "Tata Power", "Energy"),
    ("TORNTPOWER", "Torrent Power", "Energy"),
    ("IOC", "Indian Oil Corporation", "Energy"),
    ("BPCL", "Bharat Petroleum", "Energy"),
    ("HINDPETRO", "Hindustan Petroleum", "Energy"),
    ("GAIL", "GAIL India", "Energy"),
    ("PETRONET", "Petronet LNG", "Energy"),

    # ── FMCG ─────────────────────────────────
    ("HINDUNILVR", "Hindustan Unilever", "FMCG"),
    ("ITC", "ITC Limited", "FMCG"),
    ("NESTLEIND", "Nestle India", "FMCG"),
    ("BRITANNIA", "Britannia Industries", "FMCG"),
    ("DABUR", "Dabur India", "FMCG"),
    ("MARICO", "Marico", "FMCG"),
    ("COLPAL", "Colgate Palmolive", "FMCG"),
    ("GODREJCP", "Godrej Consumer Products", "FMCG"),
    ("EMAMILTD", "Emami", "FMCG"),
    ("TATACONSUM", "Tata Consumer Products", "FMCG"),
    ("VBL", "Varun Beverages", "FMCG"),
    ("RADICO", "Radico Khaitan", "FMCG"),

    # ── PHARMA ───────────────────────────────
    ("SUNPHARMA", "Sun Pharmaceutical", "Pharma"),
    ("DRREDDY", "Dr Reddys Laboratories", "Pharma"),
    ("CIPLA", "Cipla", "Pharma"),
    ("DIVISLAB", "Divi's Laboratories", "Pharma"),
    ("AUROPHARMA", "Aurobindo Pharma", "Pharma"),
    ("BIOCON", "Biocon", "Pharma"),
    ("LUPIN", "Lupin", "Pharma"),
    ("TORNTPHARM", "Torrent Pharmaceuticals", "Pharma"),
    ("ALKEM", "Alkem Laboratories", "Pharma"),
    ("IPCALAB", "IPCA Laboratories", "Pharma"),
    ("GLAND", "Gland Pharma", "Pharma"),
    ("ABBOTINDIA", "Abbott India", "Pharma"),

    # ── AUTO ─────────────────────────────────
    ("MARUTI", "Maruti Suzuki", "Auto"),
    ("TATAMOTORS", "Tata Motors", "Auto"),
    ("M&M", "Mahindra & Mahindra", "Auto"),
    ("BAJAJ-AUTO", "Bajaj Auto", "Auto"),
    ("HEROMOTOCO", "Hero MotoCorp", "Auto"),
    ("EICHERMOT", "Eicher Motors", "Auto"),
    ("ASHOKLEY", "Ashok Leyland", "Auto"),
    ("TVSMOTOR", "TVS Motor Company", "Auto"),
    ("BALKRISIND", "Balkrishna Industries", "Auto"),
    ("MOTHERSON", "Samvardhana Motherson", "Auto"),
    ("BOSCHLTD", "Bosch", "Auto"),
    ("MRF", "MRF", "Auto"),

    # ── FINANCE / NBFC ───────────────────────
    ("BAJFINANCE", "Bajaj Finance", "Finance"),
    ("BAJAJFINSV", "Bajaj Finserv", "Finance"),
    ("HDFCLIFE", "HDFC Life Insurance", "Finance"),
    ("SBILIFE", "SBI Life Insurance", "Finance"),
    ("ICICIGI", "ICICI Lombard", "Finance"),
    ("MUTHOOTFIN", "Muthoot Finance", "Finance"),
    ("CHOLAFIN", "Cholamandalam Finance", "Finance"),
    ("RECLTD", "REC Limited", "Finance"),
    ("PFC", "Power Finance Corp", "Finance"),
    ("M&MFIN", "Mahindra Finance", "Finance"),
    ("LTFH", "L&T Finance", "Finance"),
    ("MANAPPURAM", "Manappuram Finance", "Finance"),

    # ── INFRASTRUCTURE ───────────────────────
    ("LT", "Larsen & Toubro", "Infrastructure"),
    ("ADANIPORTS", "Adani Ports", "Infrastructure"),
    ("ULTRACEMCO", "UltraTech Cement", "Infrastructure"),
    ("GRASIM", "Grasim Industries", "Infrastructure"),
    ("AMBUJACEM", "Ambuja Cements", "Infrastructure"),
    ("ACC", "ACC Limited", "Infrastructure"),
    ("JKCEMENT", "JK Cement", "Infrastructure"),
    ("SHREECEM", "Shree Cement", "Infrastructure"),
    ("DLF", "DLF Limited", "Infrastructure"),
    ("GODREJPROP", "Godrej Properties", "Infrastructure"),
    ("OBEROIRLTY", "Oberoi Realty", "Infrastructure"),
    ("PRESTIGE", "Prestige Estates", "Infrastructure"),

    # ── TELECOM ──────────────────────────────
    ("BHARTIARTL", "Bharti Airtel", "Telecom"),
    ("INDUSTOWER", "Indus Towers", "Telecom"),
    ("TATACOMM", "Tata Communications", "Telecom"),

    # ── METALS ───────────────────────────────
    ("TATASTEEL", "Tata Steel", "Metals"),
    ("JSWSTEEL", "JSW Steel", "Metals"),
    ("HINDALCO", "Hindalco Industries", "Metals"),
    ("VEDL", "Vedanta", "Metals"),
    ("SAIL", "Steel Authority of India", "Metals"),
    ("NATIONALUM", "National Aluminium", "Metals"),
    ("COALINDIA", "Coal India", "Metals"),
    ("NMDC", "NMDC", "Metals"),
    ("HINDCOPPER", "Hindustan Copper", "Metals"),

    # ── CONSUMER DURABLES ────────────────────
    ("TITAN", "Titan Company", "Consumer"),
    ("VOLTAS", "Voltas", "Consumer"),
    ("HAVELLS", "Havells India", "Consumer"),
    ("CROMPTON", "Crompton Greaves", "Consumer"),
    ("WHIRLPOOL", "Whirlpool India", "Consumer"),
    ("VGUARD", "V-Guard Industries", "Consumer"),
    ("ORIENTELEC", "Orient Electric", "Consumer"),
    ("SYMSYS", "Symphony", "Consumer"),

    # ── HEALTHCARE ───────────────────────────
    ("APOLLOHOSP", "Apollo Hospitals", "Healthcare"),
    ("FORTIS", "Fortis Healthcare", "Healthcare"),
    ("MAXHEALTH", "Max Healthcare", "Healthcare"),
    ("METROPOLIS", "Metropolis Healthcare", "Healthcare"),
    ("LALPATHLAB", "Dr Lal PathLabs", "Healthcare"),
    ("THYROCARE", "Thyrocare Technologies", "Healthcare"),

    # ── CHEMICALS ────────────────────────────
    ("PIDILITIND", "Pidilite Industries", "Chemicals"),
    ("SRF", "SRF Limited", "Chemicals"),
    ("DEEPAKNTR", "Deepak Nitrite", "Chemicals"),
    ("NAVINFLUOR", "Navin Fluorine", "Chemicals"),
    ("AARTIIND", "Aarti Industries", "Chemicals"),
    ("VINATIORGA", "Vinati Organics", "Chemicals"),
    ("FINPIPE", "Finolex Industries", "Chemicals"),

    # ── AVIATION & LOGISTICS ─────────────────
    ("INDIGO", "IndiGo (InterGlobe)", "Aviation"),
    ("BLUEDART", "Blue Dart Express", "Logistics"),
    ("DELHIVERY", "Delhivery", "Logistics"),
    ("CONCOR", "Container Corp of India", "Logistics"),
    ("MAHLOG", "Mahindra Logistics", "Logistics"),

    # ── RETAIL & E-COMMERCE ──────────────────
    ("TRENT", "Trent (Zara India)", "Retail"),
    ("DMART", "Avenue Supermarts (DMart)", "Retail"),
    ("NYKAA", "FSN E-Commerce (Nykaa)", "Retail"),
    ("ZOMATO", "Zomato", "Retail"),
    ("PAYTM", "One97 Communications", "Retail"),

    # ── DEFENSE ──────────────────────────────
    ("HAL", "Hindustan Aeronautics", "Defense"),
    ("BEL", "Bharat Electronics", "Defense"),
    ("BHEL", "Bharat Heavy Electricals", "Defense"),
    ("COCHINSHIP", "Cochin Shipyard", "Defense"),
    ("MIDHANI", "MIDHANI", "Defense"),
]

def get_all_stocks():
    """Poori stock list return karo"""
    return NIFTY_500_STOCKS

def get_stocks_by_sector(sector):
    """Sector ke hisaab se stocks filter karo"""
    return [(s, c, sec) for s, c, sec in NIFTY_500_STOCKS if sec == sector]

def get_all_sectors():
    """Unique sectors ki list"""
    return list(set(sec for _, _, sec in NIFTY_500_STOCKS))

def get_stock_count():
    return len(NIFTY_500_STOCKS)

if __name__ == "__main__":
    print(f"Total stocks: {get_stock_count()}")
    sectors = get_all_sectors()
    print(f"Total sectors: {len(sectors)}")
    print(f"Sectors: {', '.join(sorted(sectors))}")
    print("\nSample stocks:")
    for sym, company, sector in NIFTY_500_STOCKS[:5]:
        print(f"  {sym} — {company} ({sector})")
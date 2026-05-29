import { useState, useEffect } from "react"
import { ArrowLeft, TrendingUp, TrendingDown, Minus,
         RefreshCw, Clock, Zap, Newspaper, BarChart2,
         Building2, Globe, Users, DollarSign } from "lucide-react"
import axios from "axios"

const API = "http://localhost:8000"

function safe(val, fallback = 0) {
  const n = parseFloat(val)
  return isNaN(n) ? fallback : n
}

function LiveClock() {
  const [time, setTime] = useState(new Date())
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return (
    <span className="text-xs text-gray-400 flex items-center gap-1">
      <Clock size={11}/>
      {time.toLocaleTimeString('en-IN')}
    </span>
  )
}

function SignalBadge({ signal }) {
  const s = (signal || "").toUpperCase()
  if (s.includes("STRONG BUY"))
    return <span className="px-3 py-1 rounded-full text-sm font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">🚀 STRONG BUY</span>
  if (s.includes("BUY"))
    return <span className="px-3 py-1 rounded-full text-sm font-bold bg-green-500/20 text-green-400 border border-green-500/30">📈 BUY</span>
  if (s.includes("STRONG SELL"))
    return <span className="px-3 py-1 rounded-full text-sm font-bold bg-red-500/20 text-red-400 border border-red-500/30">🔴 STRONG SELL</span>
  if (s.includes("SELL"))
    return <span className="px-3 py-1 rounded-full text-sm font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">📉 SELL</span>
  return <span className="px-3 py-1 rounded-full text-sm font-bold bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">⚖️ NEUTRAL</span>
}

// Company info database
const COMPANY_INFO = {
  RELIANCE: {
    fullName: "Reliance Industries Limited",
    description: "Reliance Industries is India's largest private sector company. It operates across energy, petrochemicals, natural gas, retail, telecommunications, and entertainment. Founded by Dhirubhai Ambani in 1966, now led by Mukesh Ambani. It runs Jio — India's largest telecom network with 450M+ subscribers, and JioMart — a major e-commerce platform.",
    founded: "1966",
    headquarters: "Mumbai, Maharashtra",
    employees: "2,36,000+",
    marketCap: "₹18.3 Lakh Cr",
    sector: "Energy / Telecom / Retail",
    exchange: "NSE & BSE",
    website: "ril.com",
    keyProducts: ["Jio Telecom", "JioMart", "Reliance Retail", "Petrochemicals", "Oil Refining"],
    recentNews: "Expanding 5G network, growing retail footprint, exploring green energy"
  },
  TCS: {
    fullName: "Tata Consultancy Services Limited",
    description: "TCS is India's largest IT services company and second largest employer. It provides IT services, consulting and business solutions to clients worldwide. Part of the Tata Group, TCS serves Fortune 500 companies across banking, retail, manufacturing, and healthcare sectors. Present in 55 countries.",
    founded: "1968",
    headquarters: "Mumbai, Maharashtra",
    employees: "6,00,000+",
    marketCap: "₹8.3 Lakh Cr",
    sector: "Information Technology",
    exchange: "NSE & BSE",
    website: "tcs.com",
    keyProducts: ["IT Consulting", "Software Development", "Cloud Services", "AI/ML Solutions"],
    recentNews: "Strong deal wins in AI transformation projects, focus on GenAI services"
  },
  HDFCBANK: {
    fullName: "HDFC Bank Limited",
    description: "HDFC Bank is India's largest private sector bank by assets. It offers a wide range of banking services including retail banking, wholesale banking, treasury operations. Known for best-in-class asset quality and consistent profitability. Recently merged with HDFC Ltd (parent housing finance company) in 2023.",
    founded: "1994",
    headquarters: "Mumbai, Maharashtra",
    employees: "1,77,000+",
    marketCap: "₹12.1 Lakh Cr",
    sector: "Banking & Financial Services",
    exchange: "NSE & BSE",
    website: "hdfcbank.com",
    keyProducts: ["Retail Banking", "Home Loans", "Credit Cards", "Corporate Banking"],
    recentNews: "Post-merger integration with HDFC Ltd, focus on deposit growth"
  },
  INFY: {
    fullName: "Infosys Limited",
    description: "Infosys is a global leader in next-generation digital services and consulting. It helps clients in over 50 countries navigate digital transformation. Founded by Narayana Murthy and 6 co-founders with just $250 capital in 1981. Now a $90B+ company, it is a pioneer of the Indian IT industry.",
    founded: "1981",
    headquarters: "Bengaluru, Karnataka",
    employees: "3,17,000+",
    marketCap: "₹4.8 Lakh Cr",
    sector: "Information Technology",
    exchange: "NSE & BSE",
    website: "infosys.com",
    keyProducts: ["Digital Transformation", "Cloud Migration", "AI Services", "Consulting"],
    recentNews: "Large deal wins in Europe, focus on cost optimization for clients"
  },
  ICICIBANK: {
    fullName: "ICICI Bank Limited",
    description: "ICICI Bank is India's second largest private sector bank. It offers retail, corporate, and international banking services. Known for its technology-first approach and strong digital banking platform — iMobile Pay. Consistently gaining market share across loans, credit cards, and insurance.",
    founded: "1994",
    headquarters: "Mumbai, Maharashtra",
    employees: "1,35,000+",
    marketCap: "₹9.1 Lakh Cr",
    sector: "Banking & Financial Services",
    exchange: "NSE & BSE",
    website: "icicibank.com",
    keyProducts: ["Retail Banking", "iMobile Pay", "Credit Cards", "Corporate Banking", "ICICI Prudential"],
    recentNews: "Strong loan growth, rising NIM, expanding credit card market share"
  },
  HINDUNILVR: {
    fullName: "Hindustan Unilever Limited",
    description: "HUL is India's largest FMCG (Fast Moving Consumer Goods) company. It owns iconic brands used by millions of Indian households every day. Part of Unilever global group. Products range from soaps and shampoos to tea and ice cream. Present in every Indian home through its 35+ brands.",
    founded: "1933",
    headquarters: "Mumbai, Maharashtra",
    employees: "21,000+",
    marketCap: "₹5.2 Lakh Cr",
    sector: "FMCG",
    exchange: "NSE & BSE",
    website: "hul.co.in",
    keyProducts: ["Surf Excel", "Dove", "Lux", "Lipton Tea", "Kwality Walls", "Clinic Plus"],
    recentNews: "Volume growth recovery, rural demand improving, premiumization strategy"
  },
  SBIN: {
    fullName: "State Bank of India",
    description: "SBI is India's largest public sector bank and largest bank overall. It has the biggest branch and ATM network in India. Backed by Government of India, it serves over 500 million customers. Plays a critical role in India's financial system — every major government scheme runs through SBI.",
    founded: "1955",
    headquarters: "Mumbai, Maharashtra",
    employees: "2,32,000+",
    marketCap: "₹8.7 Lakh Cr",
    sector: "Banking (Public Sector)",
    exchange: "NSE & BSE",
    website: "sbi.co.in",
    keyProducts: ["Savings Accounts", "Home Loans", "YONO App", "Corporate Banking", "Government Schemes"],
    recentNews: "Strong NPA improvement, YONO digital platform growth, government infra lending"
  },
  BHARTIARTL: {
    fullName: "Bharti Airtel Limited",
    description: "Airtel is India's second largest telecom operator and one of Asia's biggest. It operates mobile, broadband, DTH, and enterprise services. Present in 18 countries across South Asia and Africa. Rapidly expanding its 5G network and fiber broadband. Also owns a stake in OneWeb satellite internet.",
    founded: "1995",
    headquarters: "New Delhi",
    employees: "18,000+",
    marketCap: "₹11.1 Lakh Cr",
    sector: "Telecommunications",
    exchange: "NSE & BSE",
    website: "airtel.in",
    keyProducts: ["Mobile Services", "Airtel Xstream Fiber", "Airtel DTH", "Airtel Business", "Africa Operations"],
    recentNews: "5G rollout, ARPU improvement, Africa growth, stake in BT Group"
  },
  LT: {
    fullName: "Larsen & Toubro Limited",
    description: "L&T is India's largest engineering and construction conglomerate. It builds everything — bridges, metros, nuclear reactors, defense equipment, IT systems, and financial services. L&T has built iconic projects like Mumbai Metro, Delhi Airport, and various defense platforms for India.",
    founded: "1938",
    headquarters: "Mumbai, Maharashtra",
    employees: "50,000+",
    marketCap: "₹5.7 Lakh Cr",
    sector: "Infrastructure & Engineering",
    exchange: "NSE & BSE",
    website: "larsentoubro.com",
    keyProducts: ["Construction", "Defense Equipment", "Metros & Airports", "IT Services (LTIMindtree)", "Financial Services"],
    recentNews: "Large order wins in Middle East, defense exports growing, data center projects"
  },
}

function CompanyCard({ symbol }) {
  const info = COMPANY_INFO[symbol]
  if (!info) return null

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 mb-4">
      <div className="flex items-start gap-3 mb-4">
        <div className="w-12 h-12 bg-blue-600/20 border border-blue-600/30 rounded-xl flex items-center justify-center flex-shrink-0">
          <Building2 size={22} className="text-blue-400"/>
        </div>
        <div>
          <h2 className="font-bold text-base text-white">{info.fullName}</h2>
          <p className="text-gray-400 text-xs">{info.sector} · {info.exchange}</p>
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-300 text-sm leading-relaxed mb-4">{info.description}</p>

      {/* Key stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-4">
        {[
          { icon: <DollarSign size={13}/>, label: "Market Cap", val: info.marketCap },
          { icon: <Users size={13}/>, label: "Employees", val: info.employees },
          { icon: <Clock size={13}/>, label: "Founded", val: info.founded },
          { icon: <Globe size={13}/>, label: "Headquarters", val: info.headquarters },
          { icon: <Globe size={13}/>, label: "Website", val: info.website },
          { icon: <Building2 size={13}/>, label: "Exchange", val: info.exchange },
        ].map((item, i) => (
          <div key={i} className="bg-gray-800/50 rounded-lg p-2">
            <div className="flex items-center gap-1 text-gray-500 text-xs mb-1">
              {item.icon} {item.label}
            </div>
            <div className="text-white text-xs font-medium">{item.val}</div>
          </div>
        ))}
      </div>

      {/* Key products */}
      <div className="mb-3">
        <p className="text-xs text-gray-500 mb-2">Key Products / Services</p>
        <div className="flex flex-wrap gap-1.5">
          {info.keyProducts.map((p, i) => (
            <span key={i} className="text-xs bg-blue-600/10 text-blue-400 border border-blue-600/20 px-2 py-0.5 rounded-full">
              {p}
            </span>
          ))}
        </div>
      </div>

      {/* Recent news context */}
      <div className="bg-yellow-900/20 border border-yellow-700/20 rounded-lg p-2">
        <p className="text-xs text-yellow-400 font-medium mb-0.5">📌 Current Context</p>
        <p className="text-xs text-gray-300">{info.recentNews}</p>
      </div>
    </div>
  )
}

function PriceChart({ prices }) {
  if (!prices || prices.length === 0) return null

  const sorted = [...prices].sort((a,b) => a.date > b.date ? 1 : -1)
  const closes = sorted.map(p => safe(p.close))
  const maxP = Math.max(...closes)
  const minP = Math.min(...closes)
  const range = maxP - minP || 1

  const W = 600
  const H = 160
  const pad = { top: 10, bottom: 30, left: 50, right: 10 }
  const chartW = W - pad.left - pad.right
  const chartH = H - pad.top - pad.bottom

  const pts = closes.map((c, i) => {
    const x = pad.left + (i / (closes.length - 1)) * chartW
    const y = pad.top + (1 - (c - minP) / range) * chartH
    return `${x},${y}`
  })
  const polyline = pts.join(" ")

  const firstClose = closes[0]
  const lastClose  = closes[closes.length - 1]
  const isUp = lastClose >= firstClose
  const color = isUp ? "#10b981" : "#ef4444"

  const yLabels = [maxP, (maxP + minP) / 2, minP]

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 mb-4">
      <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
        <BarChart2 size={15} className="text-blue-400"/>
        Price History (Last 30 Days)
      </h3>
      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto", minWidth: "280px" }}>
          {/* Grid lines */}
          {yLabels.map((val, i) => {
            const y = pad.top + (i / (yLabels.length - 1)) * chartH
            return (
              <g key={i}>
                <line x1={pad.left} y1={y} x2={W - pad.right} y2={y}
                  stroke="#374151" strokeWidth="0.5" strokeDasharray="4,4"/>
                <text x={pad.left - 4} y={y + 4} textAnchor="end"
                  fontSize="10" fill="#9ca3af">
                  {val.toFixed(0)}
                </text>
              </g>
            )
          })}

          {/* Area fill */}
          <polygon
            points={`${pad.left},${pad.top + chartH} ${polyline} ${W - pad.right},${pad.top + chartH}`}
            fill={isUp ? "rgba(16,185,129,0.1)" : "rgba(239,68,68,0.1)"}/>

          {/* Line */}
          <polyline points={polyline} fill="none" stroke={color} strokeWidth="1.5"/>

          {/* Date labels */}
          {[0, Math.floor(sorted.length / 2), sorted.length - 1].map((idx) => {
            const x = pad.left + (idx / (closes.length - 1)) * chartW
            const date = sorted[idx]?.date?.slice(5) || ""
            return (
              <text key={idx} x={x} y={H - 5} textAnchor="middle"
                fontSize="9" fill="#6b7280">{date}</text>
            )
          })}
        </svg>
      </div>
      <div className="flex justify-between text-xs mt-2">
        <span className="text-gray-500">30-day low: <span className="text-red-400">₹{minP.toFixed(2)}</span></span>
        <span className={isUp ? "text-emerald-400" : "text-red-400"}>
          {isUp ? "▲" : "▼"} {Math.abs(((lastClose - firstClose) / firstClose) * 100).toFixed(2)}% in 30 days
        </span>
        <span className="text-gray-500">30-day high: <span className="text-emerald-400">₹{maxP.toFixed(2)}</span></span>
      </div>
    </div>
  )
}

function AIAnalysis({ prediction }) {
  if (!prediction) return null

  const up   = safe(prediction.prob_up)
  const down = safe(prediction.prob_down)
  const acc  = safe(prediction.accuracy)
  const signal = (prediction.signal || "").replace(/[🚀📈🔴📉⚖️]/g, "").trim()

  const reasons = []

  if (up >= 65)
    reasons.push({ icon: "🤖", title: "AI Prediction", text: `Model predicts ${up.toFixed(1)}% probability of price going UP tomorrow. This is based on XGBoost model trained on 2 years of daily price data with 24 technical features.` })
  else if (up <= 35)
    reasons.push({ icon: "🤖", title: "AI Prediction", text: `Model predicts only ${up.toFixed(1)}% chance of going up. Strong BEARISH pattern detected. DOWN probability is ${down.toFixed(1)}%.` })
  else
    reasons.push({ icon: "🤖", title: "AI Prediction", text: `Mixed signals — UP: ${up.toFixed(1)}% vs DOWN: ${down.toFixed(1)}%. No clear directional bias today.` })

  reasons.push({ icon: "🎯", title: "Model Accuracy", text: `This model has been ${acc.toFixed(1)}% accurate on test data. Note: Even the best models are right ~60% of the time in stock markets — always use with caution.` })

  if (signal.includes("BUY"))
    reasons.push({ icon: "✅", title: "Trading Conclusion", text: `BULLISH signal. If you plan to trade, consider entering with a stop-loss. Never invest more than you can afford to lose. This is AI prediction, not guaranteed profit.` })
  else if (signal.includes("SELL"))
    reasons.push({ icon: "❌", title: "Trading Conclusion", text: `BEARISH signal. Avoid fresh buying today. If holding, consider setting a stop-loss to protect capital. Market can always surprise — AI is not 100% correct.` })
  else
    reasons.push({ icon: "⏳", title: "Trading Conclusion", text: `No clear signal today. Best strategy: wait for tomorrow's fresh signal. Forced trades in uncertain market often lead to losses.` })

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 mb-4">
      <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
        <Zap size={15} className="text-yellow-400"/>
        AI Analysis & Prediction
      </h3>

      <div className="flex items-center justify-between mb-4">
        <SignalBadge signal={signal}/>
        <div className="text-right">
          <p className="text-xs text-gray-500">Prediction date</p>
          <p className="text-xs text-gray-300">{prediction.prediction_date}</p>
        </div>
      </div>

      {/* UP/DOWN bar */}
      <div className="mb-4">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-emerald-400 font-medium">UP {up.toFixed(1)}%</span>
          <span className="text-gray-500">AI Confidence</span>
          <span className="text-red-400 font-medium">DOWN {down.toFixed(1)}%</span>
        </div>
        <div className="h-3 bg-red-900/50 rounded-full overflow-hidden">
          <div className="h-full bg-emerald-500 rounded-full"
               style={{ width: `${up}%` }}/>
        </div>
      </div>

      {/* Reasons */}
      <div className="space-y-2">
        {reasons.map((r, i) => (
          <div key={i} className="flex gap-2 bg-gray-800/60 rounded-lg p-2.5">
            <span className="text-base flex-shrink-0">{r.icon}</span>
            <div>
              <p className="text-xs text-gray-400 font-semibold mb-0.5">{r.title}</p>
              <p className="text-xs text-gray-300 leading-relaxed">{r.text}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function NewsSection({ news }) {
  if (!news || news.length === 0)
    return (
      <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 mb-4">
        <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
          <Newspaper size={15} className="text-blue-400"/> Latest News
        </h3>
        <p className="text-gray-500 text-xs">No recent news found for this stock</p>
      </div>
    )

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 mb-4">
      <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
        <Newspaper size={15} className="text-blue-400"/>
        Latest News & Market Impact
      </h3>
      <div className="space-y-2">
        {news.map((n, i) => (
          <div key={i} className="flex gap-2 bg-gray-800/40 rounded-lg p-2.5">
            <span className="text-base flex-shrink-0">
              {n.sentiment_label === "positive" ? "📈" : n.sentiment_label === "negative" ? "📉" : "📰"}
            </span>
            <div>
              <p className="text-xs text-gray-200 leading-relaxed">{n.headline}</p>
              <div className="flex items-center gap-2 mt-1 flex-wrap">
                <span className={`text-xs font-medium ${
                  n.sentiment_label === "positive" ? "text-emerald-400" :
                  n.sentiment_label === "negative" ? "text-red-400" : "text-gray-500"
                }`}>{n.sentiment_label || "neutral"}</span>
                <span className="text-gray-600 text-xs">· {n.source}</span>
                <span className="text-gray-600 text-xs">· {(n.published_at||"").slice(0,10)}</span>
              </div>
              {n.sentiment_label === "positive" && (
                <p className="text-xs text-emerald-400/70 mt-1">↑ Positive news — may attract buyers</p>
              )}
              {n.sentiment_label === "negative" && (
                <p className="text-xs text-red-400/70 mt-1">↓ Negative news — may create selling pressure</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function StockDetail() {
  const symbol = window.location.pathname.split("/stock/")[1]?.toUpperCase()
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    if (!symbol) return
    axios.get(`${API}/api/stock/${symbol}`)
      .then(r => {
        if (r.data.error) setError(r.data.error)
        else setData(r.data)
        setLoading(false)
      })
      .catch(() => { setError("Failed to load data"); setLoading(false) })
  }, [symbol])

  if (!symbol) return (
    <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center">
      <p className="text-gray-400">No stock symbol provided</p>
    </div>
  )

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-white">

      {/* Header */}
      <div className="sticky top-0 z-50 bg-[#0d1221]/98 backdrop-blur border-b border-gray-800">
        <div className="px-3 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <a href="/" className="text-gray-500 hover:text-white transition-colors p-1">
              <ArrowLeft size={18}/>
            </a>
            <div>
              <h1 className="font-bold text-sm">{symbol}</h1>
              <p className="text-gray-500 text-xs">
                {COMPANY_INFO[symbol]?.fullName || "Stock Detail"}
              </p>
            </div>
          </div>
          <LiveClock/>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-3 py-4">

        {loading ? (
          <div className="text-center py-16 text-gray-500">
            <RefreshCw className="animate-spin mx-auto mb-3" size={28}/>
            <p className="text-sm">Loading {symbol} data...</p>
          </div>
        ) : error ? (
          <div className="text-center py-16 text-gray-500">
            <p className="text-sm text-red-400">{error}</p>
            <a href="/" className="text-blue-400 text-xs mt-2 block">← Back to Dashboard</a>
          </div>
        ) : (
          <>
            {/* Live price banner */}
            {data?.prices?.[0] && (
              <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 mb-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-500 text-xs mb-1">{symbol} · NSE</p>
                    <p className="text-3xl font-bold font-mono">
                      ₹{safe(data.prices[0].close).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </p>
                    <p className="text-gray-500 text-xs mt-1">Last close · {data.prices[0].date}</p>
                  </div>
                  {data.prediction && <SignalBadge signal={data.prediction.signal}/>}
                </div>
              </div>
            )}

            {/* Company info */}
            <CompanyCard symbol={symbol}/>

            {/* Price chart */}
            <PriceChart prices={data?.prices}/>

            {/* AI Analysis */}
            <AIAnalysis prediction={data?.prediction}/>

            {/* News */}
            <NewsSection news={data?.news}/>

            {/* Disclaimer */}
            <div className="bg-yellow-900/20 border border-yellow-700/30 rounded-xl p-3 mt-4">
              <p className="text-yellow-200/60 text-xs leading-relaxed">
                <strong className="text-yellow-400">Disclaimer:</strong> All information is for educational purposes only. Not financial advice. Always consult a SEBI-registered advisor before investing.
              </p>
            </div>
            <div className="text-center text-gray-700 text-xs py-4">
              <a href="/" className="text-blue-400/50 hover:text-blue-400">← Back to Dashboard</a>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
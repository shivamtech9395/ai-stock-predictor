import { useState, useEffect } from "react"
import { TrendingUp, TrendingDown, Minus, RefreshCw,
         Activity, Newspaper, Target, AlertCircle,
         ChevronDown, ChevronUp, Clock, BarChart2 } from "lucide-react"
import axios from "axios"

const API = "http://localhost:8000"

// ── HELPERS ───────────────────────────────────
function safe(val, fallback = 0) {
  const n = parseFloat(val)
  return isNaN(n) ? fallback : n
}

function SignalBadge({ signal }) {
  const s = (signal || "").toUpperCase()
  if (s.includes("STRONG BUY"))
    return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">🚀 STRONG BUY</span>
  if (s.includes("BUY"))
    return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-green-500/20 text-green-400 border border-green-500/30">📈 BUY</span>
  if (s.includes("STRONG SELL"))
    return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30">🔴 STRONG SELL</span>
  if (s.includes("SELL"))
    return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">📉 SELL</span>
  return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">⚖️ NEUTRAL</span>
}

function SentBadge({ label }) {
  if (label === "positive") return <span className="text-emerald-400 text-xs flex items-center gap-1"><TrendingUp size={11}/>Positive</span>
  if (label === "negative") return <span className="text-red-400 text-xs flex items-center gap-1"><TrendingDown size={11}/>Negative</span>
  return <span className="text-gray-400 text-xs flex items-center gap-1"><Minus size={11}/>Neutral</span>
}

function LiveClock() {
  const [time, setTime] = useState(new Date())
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return (
    <span className="text-xs text-gray-400 flex items-center gap-1">
      <Clock size={12}/>
      {time.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
    </span>
  )
}

function AIReason({ stock }) {
  const reasons = []
  const up = safe(stock.prob_up)
  const rsi = safe(stock.rsi, 50)
  const sent = stock.sent_label || "neutral"

  if (up >= 65) reasons.push({ icon: "🤖", text: `AI model predicts ${up}% probability of upward movement tomorrow based on historical price patterns` })
  else if (up <= 35) reasons.push({ icon: "🤖", text: `AI model predicts only ${up}% chance of going up — strong downward pattern detected` })
  else reasons.push({ icon: "🤖", text: `AI model shows mixed signals with ${up}% up probability — wait for clearer trend` })

  if (rsi < 30) reasons.push({ icon: "📊", text: `RSI at ${rsi} — Stock is OVERSOLD. This means it has fallen too much and a bounce/recovery is likely` })
  else if (rsi > 70) reasons.push({ icon: "📊", text: `RSI at ${rsi} — Stock is OVERBOUGHT. Too many buyers pushed it up — correction possible` })
  else reasons.push({ icon: "📊", text: `RSI at ${rsi} — Normal range. No extreme buying or selling pressure detected` })

  if (sent === "positive") reasons.push({ icon: "📰", text: `Recent news about this company is POSITIVE — good developments reported in media which can push stock up` })
  else if (sent === "negative") reasons.push({ icon: "📰", text: `Recent news is NEGATIVE — bad news in media can create selling pressure` })
  else reasons.push({ icon: "📰", text: `News sentiment is NEUTRAL — no major positive or negative news recently` })

  const signal = (stock.signal || "").toUpperCase()
  if (signal.includes("BUY")) {
    reasons.push({ icon: "✅", text: `CONCLUSION: Multiple indicators align bullishly. Consider this stock for potential gains. Always use stop-loss.` })
  } else if (signal.includes("SELL")) {
    reasons.push({ icon: "❌", text: `CONCLUSION: Multiple indicators show weakness. Avoid buying today. If you hold, consider booking profits.` })
  } else {
    reasons.push({ icon: "⏳", text: `CONCLUSION: Wait for a clearer signal. Don't rush to buy or sell today.` })
  }

  return (
    <div className="mt-3 space-y-2">
      <p className="text-xs text-blue-400 font-semibold uppercase tracking-wide">Why AI says this:</p>
      {reasons.map((r, i) => (
        <div key={i} className="flex gap-2 bg-gray-800/50 rounded-lg p-2">
          <span className="text-base flex-shrink-0">{r.icon}</span>
          <p className="text-xs text-gray-300 leading-relaxed">{r.text}</p>
        </div>
      ))}
    </div>
  )
}

function StockNews({ symbol }) {
  const [news, setNews] = useState([])
  useEffect(() => {
    axios.get(`${API}/api/news/${symbol}`)
      .then(r => setNews(r.data.news || []))
      .catch(() => {})
  }, [symbol])

  if (!news.length) return <p className="text-gray-500 text-xs mt-2">No news found for this stock</p>

  return (
    <div className="mt-3 space-y-2">
      <p className="text-xs text-blue-400 font-semibold uppercase tracking-wide">Latest News</p>
      {news.slice(0, 5).map((n, i) => (
        <div key={i} className="bg-gray-800/50 rounded-lg p-2 flex gap-2">
          <span className="text-base flex-shrink-0">
            {n.sentiment_label === "positive" ? "📈" : n.sentiment_label === "negative" ? "📉" : "📰"}
          </span>
          <div>
            <p className="text-xs text-gray-200 leading-relaxed">{n.headline}</p>
            <p className="text-gray-500 text-xs mt-0.5">{n.source} · {n.published_at?.slice(0,10)}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

// ── MAIN DASHBOARD ────────────────────────────
export default function Dashboard() {
  const [stocks, setStocks]     = useState([])
  const [summary, setSummary]   = useState(null)
  const [loading, setLoading]   = useState(true)
  const [selected, setSelected] = useState(null)
  const [filter, setFilter]     = useState("ALL")
  const [lastUpdated, setLastUpdated] = useState(new Date())

  const sectors = ["ALL", "Banking", "IT", "Energy", "Telecom", "FMCG", "Infrastructure"]

  const fetchData = async () => {
    setLoading(true)
    try {
      const [predRes, sumRes] = await Promise.all([
        axios.get(`${API}/api/predictions/today`),
        axios.get(`${API}/api/market/summary`),
      ])
      if (predRes.data.status === "ok") setStocks(predRes.data.data || [])
      if (sumRes.data.status === "ok") setSummary(sumRes.data)
      setLastUpdated(new Date())
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [])

  const filtered = filter === "ALL" ? stocks : stocks.filter(s => s.sector === filter)
  const sorted   = [...filtered].sort((a, b) => safe(b.prob_up) - safe(a.prob_up))

  const buyStocks  = stocks.filter(s => (s.signal||"").includes("BUY"))
  const sellStocks = stocks.filter(s => (s.signal||"").includes("SELL"))

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-white">

      {/* ── HEADER ── */}
      <div className="sticky top-0 z-50 bg-[#0d1221]/95 backdrop-blur border-b border-gray-800">
        {/* Index bar */}
        <div className="border-b border-gray-800/50 px-4 py-1.5 flex items-center gap-6 overflow-x-auto">
          {[
            { name: "NIFTY 50", val: "23,719", chg: "+64.60", pct: "+0.27%" },
            { name: "BANKNIFTY", val: "54,055", chg: "+615.95", pct: "+1.15%" },
            { name: "SENSEX", val: "75,415", chg: "+231.99", pct: "+0.31%" },
            { name: "FINNIFTY", val: "25,531", chg: "+294.30", pct: "+1.17%" },
          ].map(idx => (
            <div key={idx.name} className="flex items-center gap-2 flex-shrink-0">
              <span className="text-gray-400 text-xs">{idx.name}</span>
              <span className="text-white text-xs font-mono font-semibold">{idx.val}</span>
              <span className="text-emerald-400 text-xs">{idx.chg} ({idx.pct})</span>
            </div>
          ))}
          <div className="ml-auto flex-shrink-0">
            <LiveClock/>
          </div>
        </div>

        {/* Main header */}
        <div className="px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center">
              <Activity size={15} className="text-white"/>
            </div>
            <div>
              <h1 className="font-bold text-sm leading-none">StockAI</h1>
              <p className="text-gray-500 text-xs">NSE Intelligence</p>
            </div>
          </div>
          <button onClick={fetchData}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/20 
                       hover:bg-blue-600/40 border border-blue-600/30 
                       rounded-lg text-xs text-blue-400 transition-all">
            <RefreshCw size={12} className={loading ? "animate-spin" : ""}/>
            Refresh
          </button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-3 py-4">

        {/* ── STATS ── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {[
            { label: "Stocks Analyzed", val: stocks.length, color: "text-white", icon: "📊" },
            { label: "Buy Signals", val: buyStocks.length, color: "text-emerald-400", icon: "🚀" },
            { label: "Sell Signals", val: sellStocks.length, color: "text-red-400", icon: "🔴" },
            { label: "Market Mood", val: summary?.market_mood || "...", color: summary?.market_mood === "BULLISH" ? "text-emerald-400" : "text-red-400", icon: "🎯" },
          ].map(s => (
            <div key={s.label} className="bg-gray-900/60 border border-gray-800 rounded-xl p-3">
              <div className="flex justify-between items-center mb-1">
                <span className="text-gray-500 text-xs">{s.label}</span>
                <span>{s.icon}</span>
              </div>
              <div className={`text-xl font-bold ${s.color}`}>{s.val}</div>
            </div>
          ))}
        </div>

        {/* ── MORNING REPORT ── */}
        <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 
                        border border-blue-700/30 rounded-xl p-4 mb-4">
          <div className="flex gap-2">
            <Target className="text-blue-400 flex-shrink-0 mt-0.5" size={18}/>
            <div>
              <h2 className="font-semibold text-blue-400 text-sm mb-1">
                🌅 Today's AI Morning Report — {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
              </h2>
              <p className="text-gray-300 text-xs leading-relaxed">
                AI analyzed <strong>{stocks.length} NSE stocks</strong> today.
                {buyStocks.length > 0 && <> Top picks: <strong className="text-emerald-400">{buyStocks.slice(0,3).map(s=>s.symbol).join(", ")}</strong> showing bullish signals.</>}
                {sellStocks.length > 0 && <> Avoid: <strong className="text-red-400">{sellStocks.slice(0,2).map(s=>s.symbol).join(", ")}</strong>.</>}
                {" "}Market mood: <strong className={summary?.market_mood === "BULLISH" ? "text-emerald-400" : "text-red-400"}>{summary?.market_mood || "Analyzing..."}</strong>
              </p>
            </div>
          </div>
        </div>

        {/* ── SECTOR FILTER ── */}
        <div className="flex gap-2 mb-3 overflow-x-auto pb-1">
          {sectors.map(s => (
            <button key={s} onClick={() => setFilter(s)}
              className={`px-3 py-1 rounded-full text-xs font-medium 
                         border flex-shrink-0 transition-all ${
                filter === s
                  ? "bg-blue-600 border-blue-600 text-white"
                  : "bg-gray-900 border-gray-700 text-gray-400 hover:border-gray-500"
              }`}>
              {s}
            </button>
          ))}
        </div>

        {/* ── STOCKS LIST ── */}
        {loading ? (
          <div className="text-center py-12 text-gray-500">
            <RefreshCw className="animate-spin mx-auto mb-2" size={24}/>
            <p className="text-sm">Loading AI predictions...</p>
          </div>
        ) : sorted.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <BarChart2 className="mx-auto mb-2 opacity-50" size={24}/>
            <p className="text-sm">No predictions yet. Run daily_runner.py first.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {sorted.map((stock, idx) => {
              const isOpen = selected?.symbol === stock.symbol
              const up     = safe(stock.prob_up)
              const down   = safe(stock.prob_down)

              return (
                <div key={stock.symbol}
                  className={`bg-gray-900/60 border rounded-xl overflow-hidden 
                             transition-all ${
                    isOpen ? "border-blue-600/50" : "border-gray-800 hover:border-gray-700"
                  }`}>

                  {/* Stock row */}
                  <div className="p-3 cursor-pointer"
                    onClick={() => setSelected(isOpen ? null : stock)}>
                    <div className="flex items-center justify-between">

                      {/* Left: rank + name */}
                      <div className="flex items-center gap-3">
                        <span className="text-gray-600 text-xs w-4">{idx+1}</span>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm">{stock.symbol}</span>
                            <span className="text-gray-500 text-xs hidden sm:block">{stock.company}</span>
                          </div>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-gray-600 text-xs">{stock.sector}</span>
                            <span className="text-gray-600 text-xs">·</span>
                            <span className="text-gray-600 text-xs">₹{stock.price_range}</span>
                          </div>
                        </div>
                      </div>

                      {/* Right: price + signal + chevron */}
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <div className="font-mono font-semibold text-sm">
                            ₹{safe(stock.price).toLocaleString('en-IN')}
                          </div>
                          <div className="text-gray-500 text-xs">{stock.prediction_date}</div>
                        </div>
                        <SignalBadge signal={stock.signal}/>
                        {isOpen ? <ChevronUp size={14} className="text-gray-500"/> : <ChevronDown size={14} className="text-gray-500"/>}
                      </div>
                    </div>

                    {/* AI Score bar */}
                    <div className="mt-2">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-emerald-400">UP {up.toFixed(1)}%</span>
                        <span className="text-gray-500 text-xs">AI Confidence</span>
                        <span className="text-red-400">DOWN {down.toFixed(1)}%</span>
                      </div>
                      <div className="h-1.5 bg-red-900/50 rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-500 rounded-full transition-all"
                             style={{ width: `${up}%` }}/>
                      </div>
                    </div>
                  </div>

                  {/* Expanded detail */}
                  {isOpen && (
                    <div className="border-t border-gray-800 p-3 bg-gray-900/80">

                      {/* Stats grid */}
                      <div className="grid grid-cols-3 gap-2 mb-3">
                        {[
                          { label: "Price", val: `₹${safe(stock.price).toLocaleString('en-IN')}`, color: "text-white" },
                          { label: "RSI (14)", val: safe(stock.rsi, 50).toFixed(1), color: safe(stock.rsi,50) < 30 ? "text-emerald-400" : safe(stock.rsi,50) > 70 ? "text-red-400" : "text-yellow-400" },
                          { label: "Accuracy", val: `${safe(stock.accuracy).toFixed(1)}%`, color: "text-blue-400" },
                          { label: "Sector", val: stock.sector, color: "text-gray-300" },
                          { label: "Range", val: `₹${stock.price_range}`, color: "text-gray-300" },
                          { label: "Sentiment", val: stock.sent_label || "neutral", color: stock.sent_label === "positive" ? "text-emerald-400" : stock.sent_label === "negative" ? "text-red-400" : "text-gray-400" },
                        ].map(item => (
                          <div key={item.label} className="bg-gray-800/50 rounded-lg p-2">
                            <div className="text-gray-500 text-xs">{item.label}</div>
                            <div className={`font-semibold text-xs mt-0.5 ${item.color}`}>{item.val}</div>
                          </div>
                        ))}
                      </div>

                      {/* AI Reasons */}
                      <AIReason stock={stock}/>

                      {/* News */}
                      <StockNews symbol={stock.symbol}/>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* ── DISCLAIMER ── */}
        <div className="mt-4 flex gap-2 bg-yellow-900/20 border border-yellow-700/30 rounded-lg p-3">
          <AlertCircle size={14} className="text-yellow-500 flex-shrink-0 mt-0.5"/>
          <p className="text-yellow-200/60 text-xs">
            <strong>Disclaimer:</strong> AI predictions are for educational purposes only. 
            Not financial advice. Always do your own research before investing.
          </p>
        </div>

      </div>
    </div>
  )
}
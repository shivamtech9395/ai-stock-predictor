import { useState, useEffect, useCallback } from "react"
import { TrendingUp, TrendingDown, Minus, RefreshCw, Download,
         Activity, Newspaper, Target, AlertCircle,
         ChevronDown, ChevronUp, Clock, BarChart2,
         Zap, Calendar } from "lucide-react"
import axios from "axios"

const API = "https://ai-stock-predictor-bytw.onrender.com"

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
      {time.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
    </span>
  )
}

function SignalBadge({ signal }) {
  const s = (signal || "").toUpperCase()
  if (s.includes("STRONG BUY"))
    return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 whitespace-nowrap">🚀 STRONG BUY</span>
  if (s.includes("BUY"))
    return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-green-500/20 text-green-400 border border-green-500/30 whitespace-nowrap">📈 BUY</span>
  if (s.includes("STRONG SELL"))
    return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30 whitespace-nowrap">🔴 STRONG SELL</span>
  if (s.includes("SELL"))
    return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30 whitespace-nowrap">📉 SELL</span>
  return <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 whitespace-nowrap">⚖️ NEUTRAL</span>
}

function PriceChange({ change, pct }) {
  const c = safe(change)
  const p = safe(pct)
  const color = c >= 0 ? "text-emerald-400" : "text-red-400"
  const arrow = c >= 0 ? "▲" : "▼"
  return (
    <span className={`text-xs ${color}`}>
      {arrow} {Math.abs(c).toFixed(2)} ({Math.abs(p).toFixed(2)}%)
    </span>
  )
}

function AIReason({ stock, livePrice }) {
  const up    = safe(stock.prob_up)
  const rsi   = safe(stock.rsi, 50)
  const sent  = stock.sent_label || "neutral"
  const change = livePrice ? safe(livePrice.change) : 0
  const reasons = []

  if (up >= 65)
    reasons.push({ icon: "🤖", title: "AI Model Signal", text: `AI model predicts ${up}% probability of upward movement based on 24 technical features and 2 years of price history.` })
  else if (up <= 35)
    reasons.push({ icon: "🤖", title: "AI Model Signal", text: `AI model predicts only ${up}% chance of going up. Strong downward pattern detected in price history.` })
  else
    reasons.push({ icon: "🤖", title: "AI Model Signal", text: `AI model shows mixed signals with ${up}% up probability. Market is undecided — better to wait.` })

  if (rsi < 30)
    reasons.push({ icon: "📊", title: "RSI Oversold", text: `RSI is at ${rsi.toFixed(1)} — below 30 means OVERSOLD. Stock has fallen too much too fast. A price bounce/recovery is likely soon.` })
  else if (rsi > 70)
    reasons.push({ icon: "📊", title: "RSI Overbought", text: `RSI is at ${rsi.toFixed(1)} — above 70 means OVERBOUGHT. Too many buyers pushed price up. A correction is possible.` })
  else
    reasons.push({ icon: "📊", title: "RSI Normal", text: `RSI is at ${rsi.toFixed(1)} — in normal range (30-70). No extreme buying or selling pressure.` })

  if (change > 0)
    reasons.push({ icon: "📈", title: "Today's Movement", text: `Stock is UP ₹${change.toFixed(2)} today in live market. Positive momentum supporting the AI prediction.` })
  else if (change < 0)
    reasons.push({ icon: "📉", title: "Today's Movement", text: `Stock is DOWN ₹${Math.abs(change).toFixed(2)} today. Selling pressure visible in live market.` })

  if (sent === "positive")
    reasons.push({ icon: "📰", title: "News Sentiment", text: `Recent news about this company is POSITIVE. Good developments reported — positive news usually attracts buyers.` })
  else if (sent === "negative")
    reasons.push({ icon: "📰", title: "News Sentiment", text: `Recent news is NEGATIVE. Bad news in media is creating selling pressure. Investors are cautious.` })
  else
    reasons.push({ icon: "📰", title: "News Sentiment", text: `News sentiment is NEUTRAL. No major positive or negative news recently.` })

  const sig = (stock.signal || "").toUpperCase()
  if (sig.includes("BUY"))
    reasons.push({ icon: "✅", title: "Final Conclusion", text: `BULLISH — Multiple indicators aligned positively. Consider this for trading but ALWAYS use a stop-loss.` })
  else if (sig.includes("SELL"))
    reasons.push({ icon: "❌", title: "Final Conclusion", text: `BEARISH — Multiple indicators show weakness. Avoid buying today. Consider booking profits if holding.` })
  else
    reasons.push({ icon: "⏳", title: "Final Conclusion", text: `WAIT & WATCH — Mixed signals. No clear direction today. Better opportunities may come tomorrow.` })

  return (
    <div className="space-y-2 mt-3">
      <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider flex items-center gap-1">
        <Zap size={11}/> Why AI says this
      </p>
      {reasons.map((r, i) => (
        <div key={i} className="flex gap-2 bg-gray-800/60 rounded-lg p-2.5 border border-gray-700/30">
          <span className="text-base flex-shrink-0">{r.icon}</span>
          <div>
            <p className="text-xs text-gray-400 font-semibold mb-0.5">{r.title}</p>
            <p className="text-xs text-gray-300 leading-relaxed">{r.text}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

function StockNews({ symbol }) {
  const [news, setNews]       = useState([])
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    axios.get(`${API}/api/news/${symbol}`)
      .then(r => { setNews(r.data.news || []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [symbol])

  return (
    <div className="mt-3">
      <p className="text-xs text-blue-400 font-semibold uppercase tracking-wider flex items-center gap-1 mb-2">
        <Newspaper size={11}/> Latest News
      </p>
      {loading ? <p className="text-gray-500 text-xs">Loading...</p>
      : news.length === 0 ? <p className="text-gray-500 text-xs">No news found</p>
      : (
        <div className="space-y-2">
          {news.slice(0, 5).map((n, i) => (
            <div key={i} className="flex gap-2 bg-gray-800/40 rounded-lg p-2 border border-gray-700/20">
              <span className="text-base flex-shrink-0">
                {n.sentiment_label === "positive" ? "📈" : n.sentiment_label === "negative" ? "📉" : "📰"}
              </span>
              <div className="min-w-0">
                <p className="text-xs text-gray-200 leading-relaxed">{n.headline}</p>
                <div className="flex items-center gap-2 mt-1 flex-wrap">
                  <span className="text-gray-500 text-xs">{n.source}</span>
                  <span className="text-gray-600 text-xs">·</span>
                  <span className={`text-xs font-medium ${
                    n.sentiment_label === "positive" ? "text-emerald-400" :
                    n.sentiment_label === "negative" ? "text-red-400" : "text-gray-500"
                  }`}>{n.sentiment_label || "neutral"}</span>
                  <span className="text-gray-600 text-xs">·</span>
                  <span className="text-gray-600 text-xs">{(n.published_at||"").slice(0,10)}</span>
                </div>
              </div>
            </div>
          ))}
          <a href="/news" className="block text-center text-xs text-blue-400 hover:text-blue-300 py-2 border border-blue-800/30 rounded-lg hover:bg-blue-900/20 transition-all">
            View all news →
            </a>
            <a href={`http://localhost:8000/api/pdf/stock/${stock.symbol}`}
               target="_blank"
               onClick={e => e.stopPropagation()}
               className="mt-2 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600/20 hover:bg-blue-600/40 border border-blue-600/30 rounded-lg text-xs text-blue-400 transition-all w-full">
              <Download size={12}/> Download {stock.symbol} PDF Report
          </a>
        </div>
      )}
    </div>
  )
}

function EarningsPanel() {
  const [earnings, setEarnings] = useState([])
  useEffect(() => {
    axios.get(`${API}/api/earnings/upcoming`)
      .then(r => setEarnings(r.data.earnings || []))
      .catch(() => {})
  }, [])
  if (!earnings.length) return null
  return (
    <div className="bg-gray-900/60 border border-yellow-700/30 rounded-xl p-4 mb-4">
      <h3 className="text-yellow-400 text-sm font-semibold flex items-center gap-2 mb-3">
        <Calendar size={14}/> Upcoming Earnings Results
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
        {earnings.map((e, i) => (
          <div key={i} className="bg-gray-800/50 rounded-lg p-2 border border-gray-700/30">
            <div className="flex justify-between items-start">
              <div>
                <p className="font-bold text-xs text-white">{e.symbol}</p>
                <p className="text-gray-400 text-xs">{e.company}</p>
              </div>
              <div className="text-right">
                <p className="text-yellow-400 text-xs font-semibold">{e.quarter}</p>
                <p className="text-gray-500 text-xs">{e.date}</p>
              </div>
            </div>
            <p className="text-gray-500 text-xs mt-1">📅 Watch for big movement</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function MarketCloseReport() {
  const [report, setReport]   = useState(null)
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    axios.get(`${API}/api/market/close-report`)
      .then(r => { if (r.data.status === "ok") setReport(r.data) })
      .catch(() => {})
  }, [])

  if (!report) return null

  const data     = report.data
  const bullish  = data.bullish  || []
  const bearish  = data.bearish  || []
  const sectors  = data.sectors  || []
  const analysis = data.analysis || []
  const indices  = data.indices  || {}

  return (
    <div className="bg-gray-900/60 border border-purple-700/30 rounded-xl mb-4 overflow-hidden">
      <div className="flex items-center justify-between p-4 cursor-pointer"
           onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center gap-2">
          <BarChart2 size={16} className="text-purple-400"/>
          <div>
            <h3 className="text-sm font-semibold text-purple-400">
              📊 Market Close Report — {report.report_date}
            </h3>
            <p className="text-xs text-gray-500">AI analysis of today's market</p>
          </div>
        </div>
        {expanded ? <ChevronUp size={16} className="text-gray-500"/> : <ChevronDown size={16} className="text-gray-500"/>}
      </div>

      {expanded && (
        <div className="border-t border-gray-800 p-4">

          {Object.keys(indices).length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 font-semibold uppercase mb-2">Index Performance</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {Object.entries(indices).map(([name, d]) => (
                  <div key={name} className="bg-gray-800/50 rounded-lg p-2">
                    <p className="text-xs text-gray-500">{name}</p>
                    <p className="text-sm font-bold font-mono">{d.close?.toLocaleString('en-IN')}</p>
                    <p className={`text-xs ${d.change >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                      {d.change >= 0 ? "▲" : "▼"} {Math.abs(d.change_pct).toFixed(2)}%
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {analysis.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 font-semibold uppercase mb-2">AI Analysis</p>
              <div className="space-y-1">
                {analysis.map((point, i) => (
                  <p key={i} className="text-xs text-gray-300 flex gap-2">
                    <span className="text-purple-400 flex-shrink-0">•</span>{point}
                  </p>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            <div>
              <p className="text-xs text-emerald-400 font-semibold uppercase mb-2">🚀 Top Bullish</p>
              <div className="space-y-1">
                {bullish.slice(0, 6).map((s, i) => (
                  <div key={i} className="flex justify-between items-center bg-gray-800/40 rounded px-2 py-1">
                    <div>
                      <span className="text-xs font-bold text-white">{s.symbol}</span>
                      <span className="text-gray-500 text-xs ml-1">{s.sector}</span>
                    </div>
                    <span className="text-emerald-400 text-xs font-bold">UP {s.prob_up?.toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs text-red-400 font-semibold uppercase mb-2">🔴 Avoid Today</p>
              <div className="space-y-1">
                {bearish.slice(0, 6).map((s, i) => (
                  <div key={i} className="flex justify-between items-center bg-gray-800/40 rounded px-2 py-1">
                    <div>
                      <span className="text-xs font-bold text-white">{s.symbol}</span>
                      <span className="text-gray-500 text-xs ml-1">{s.sector}</span>
                    </div>
                    <span className="text-red-400 text-xs font-bold">UP {s.prob_up?.toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div>
            <p className="text-xs text-gray-500 font-semibold uppercase mb-2">Sector Summary</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {sectors.slice(0, 9).map((s, i) => (
                <div key={i} className="bg-gray-800/40 rounded-lg p-2">
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-300 font-medium">{s.sector}</span>
                    <span className="text-xs text-gray-500">{s.total}</span>
                  </div>
                  <div className="flex justify-between mt-1">
                    <span className={`text-xs font-bold ${s.avg_up > 55 ? "text-emerald-400" : s.avg_up < 45 ? "text-red-400" : "text-yellow-400"}`}>
                      {s.avg_up?.toFixed(1)}%
                    </span>
                    <span className="text-xs">{s.mood?.split(' ')[1]}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [stocks, setStocks]           = useState([])
  const [summary, setSummary]         = useState(null)
  const [livePrices, setLivePrices]   = useState({})
  const [liveIndices, setLiveIndices] = useState({})
  const [loading, setLoading]         = useState(true)
  const [liveLoading, setLiveLoading] = useState(false)
  const [selected, setSelected]       = useState(null)
  const [filter, setFilter]           = useState("ALL")
  const [liveTime, setLiveTime]       = useState("")

  const sectors = ["ALL","Banking","IT","Energy","Telecom","FMCG","Infrastructure",
                   "Auto","Pharma","Metals","Finance","Consumer","Chemicals",
                   "Defense","Healthcare","Retail","Logistics","Aviation"]

  const fetchPredictions = async () => {
    setLoading(true)
    try {
      const [predRes, sumRes] = await Promise.all([
        axios.get(`${API}/api/predictions/today`),
        axios.get(`${API}/api/market/summary`),
      ])
      if (predRes.data.status === "ok") setStocks(predRes.data.data || [])
      if (sumRes.data.status === "ok") setSummary(sumRes.data)
    } catch(e) { console.error(e) }
    setLoading(false)
  }

  const fetchLivePrices = useCallback(async () => {
    setLiveLoading(true)
    try {
      const res = await axios.get(`${API}/api/live/prices`)
      if (res.data.status === "ok") {
        setLivePrices(res.data.prices || {})
        setLiveIndices(res.data.indices || {})
        setLiveTime(res.data.updated_at || "")
      }
    } catch(e) { console.error(e) }
    setLiveLoading(false)
  }, [])

  useEffect(() => {
    fetchPredictions()
    fetchLivePrices()
    const interval = setInterval(fetchLivePrices, 60000)
    return () => clearInterval(interval)
  }, [fetchLivePrices])

  const filtered = filter === "ALL" ? stocks : stocks.filter(s => s.sector === filter)
  const sorted   = [...filtered].sort((a,b) => safe(b.prob_up) - safe(a.prob_up))
  const buyCount  = stocks.filter(s => (s.signal||"").includes("BUY")).length
  const sellCount = stocks.filter(s => (s.signal||"").includes("SELL")).length

  const indexList = [
    { key: "NIFTY50",   label: "NIFTY 50" },
    { key: "BANKNIFTY", label: "BANKNIFTY" },
    { key: "SENSEX",    label: "SENSEX" },
    { key: "FINNIFTY",  label: "FINNIFTY" },
  ]

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-white">
      <div className="sticky top-0 z-50 bg-[#0d1221]/98 backdrop-blur border-b border-gray-800">
        <div className="border-b border-gray-800/50 px-3 py-1.5 flex items-center gap-4 overflow-x-auto">
          {indexList.map(idx => {
            const live = liveIndices[idx.key]
            const price = live ? live.price : null
            const chg   = live ? live.change : 0
            const pct   = live ? live.change_pct : 0
            const isUp  = chg >= 0
            return (
              <div key={idx.key} className="flex items-center gap-1.5 flex-shrink-0">
                <span className="text-gray-500 text-xs">{idx.label}</span>
                <span className="text-white text-xs font-mono font-semibold">
                  {price ? price.toLocaleString('en-IN') : "..."}
                </span>
                {live && (
                  <span className={`text-xs ${isUp ? "text-emerald-400" : "text-red-400"}`}>
                    {isUp ? "▲" : "▼"}{Math.abs(chg).toFixed(2)} ({Math.abs(pct).toFixed(2)}%)
                  </span>
                )}
              </div>
            )
          })}
          <div className="ml-auto flex items-center gap-2 flex-shrink-0">
            {liveLoading && <span className="text-xs text-yellow-400 animate-pulse">Updating...</span>}
            {liveTime && <span className="text-xs text-gray-600">Live: {liveTime}</span>}
            <LiveClock/>
          </div>
        </div>
        <div className="px-3 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center">
              <Activity size={15} className="text-white"/>
            </div>
            <div>
              <h1 className="font-bold text-sm">StockAI</h1>
              <p className="text-gray-500 text-xs">NSE Intelligence Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"/>
            <a href="/news"
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-xs text-gray-300 transition-all">
              <Newspaper size={12}/> News
            </a>
            <button onClick={() => { fetchPredictions(); fetchLivePrices() }}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/20 hover:bg-blue-600/40 border border-blue-600/30 rounded-lg text-xs text-blue-400 transition-all">
              <RefreshCw size={12} className={loading ? "animate-spin" : ""}/>
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-3 py-4">

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {[
            { label: "Stocks Analyzed", val: stocks.length, color: "text-white", icon: "📊" },
            { label: "Buy Signals", val: buyCount, color: "text-emerald-400", icon: "🚀" },
            { label: "Sell Signals", val: sellCount, color: "text-red-400", icon: "🔴" },
            { label: "Market Mood", val: summary?.market_mood || "...",
              color: summary?.market_mood === "BULLISH" ? "text-emerald-400" :
                     summary?.market_mood === "BEARISH" ? "text-red-400" : "text-yellow-400",
              icon: "🎯" },
          ].map(s => (
            <div key={s.label} className="bg-gray-900/60 border border-gray-800 rounded-xl p-3">
              <div className="flex justify-between items-center mb-1">
                <span className="text-gray-500 text-xs">{s.label}</span>
                <span className="text-base">{s.icon}</span>
              </div>
              <div className={`text-xl font-bold ${s.color}`}>{s.val}</div>
            </div>
          ))}
        </div>

        <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-700/30 rounded-xl p-4 mb-4">
          <div className="flex gap-2">
            <Target className="text-blue-400 flex-shrink-0 mt-0.5" size={16}/>
            <div>
              <h2 className="font-semibold text-blue-400 text-sm mb-1">
                🌅 Today's AI Morning Report — {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
              </h2>
              <p className="text-gray-300 text-xs leading-relaxed">
                AI analyzed <strong>{stocks.length} NSE stocks</strong> today.
                {buyCount > 0 && <> Top bullish: <strong className="text-emerald-400">{stocks.filter(s=>(s.signal||"").includes("BUY")).slice(0,3).map(s=>s.symbol).join(", ")}</strong>.</>}
                {sellCount > 0 && <> Avoid: <strong className="text-red-400">{stocks.filter(s=>(s.signal||"").includes("SELL")).slice(0,2).map(s=>s.symbol).join(", ")}</strong>.</>}
                {" "}Market mood: <strong className={summary?.market_mood === "BULLISH" ? "text-emerald-400" : summary?.market_mood === "BEARISH" ? "text-red-400" : "text-yellow-400"}>{summary?.market_mood || "Analyzing..."}</strong>.
              </p>
            </div>
          </div>
        </div>

        <EarningsPanel/>
        <MarketCloseReport/>

        <div className="flex gap-2 mb-3 overflow-x-auto pb-1">
          {sectors.map(s => (
            <button key={s} onClick={() => setFilter(s)}
              className={`px-3 py-1 rounded-full text-xs font-medium border flex-shrink-0 transition-all ${
                filter === s ? "bg-blue-600 border-blue-600 text-white" : "bg-gray-900 border-gray-700 text-gray-400 hover:border-gray-500"
              }`}>{s}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-16 text-gray-500">
            <RefreshCw className="animate-spin mx-auto mb-3" size={28}/>
            <p className="text-sm">Loading AI predictions...</p>
          </div>
        ) : sorted.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <BarChart2 className="mx-auto mb-3 opacity-40" size={28}/>
            <p className="text-sm">No predictions yet</p>
            <p className="text-xs mt-1">Run: python backend/daily_runner.py</p>
          </div>
        ) : (
          <div className="space-y-2">
            {sorted.map((stock, idx) => {
              const isOpen = selected?.symbol === stock.symbol
              const live   = livePrices[stock.symbol]
              const price  = live ? safe(live.price) : safe(stock.price)
              const up     = safe(stock.prob_up)
              const down   = safe(stock.prob_down)
              return (
                <div key={stock.symbol}
                  className={`bg-gray-900/60 border rounded-xl overflow-hidden transition-all ${
                    isOpen ? "border-blue-600/50 shadow-lg shadow-blue-900/20" : "border-gray-800 hover:border-gray-700"
                  }`}>
                  <div className="p-3 cursor-pointer" onClick={() => setSelected(isOpen ? null : stock)}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-2 min-w-0">
                        <span className="text-gray-600 text-xs mt-1 w-4 flex-shrink-0">{idx+1}</span>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <a href={`/stock/${stock.symbol}`}
                               onClick={e => e.stopPropagation()}
                               className="font-bold text-sm hover:text-blue-400 transition-colors">
                              {stock.symbol}
                            </a>
                            <span className="text-gray-400 text-xs truncate">{stock.company}</span>
                          </div>
                          <div className="flex items-center gap-1.5 mt-0.5 flex-wrap">
                            <span className="text-gray-600 text-xs">{stock.sector}</span>
                            <span className="text-gray-700 text-xs">·</span>
                            <span className="text-gray-600 text-xs">₹{stock.price_range}</span>
                            {live && (<><span className="text-gray-700 text-xs">·</span><PriceChange change={live.change} pct={live.change_pct}/></>)}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <div className="text-right">
                          <div className="font-mono font-semibold text-sm">
                            ₹{price.toLocaleString('en-IN', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
                          </div>
                          {live && <div className="text-xs text-emerald-600">● Live</div>}
                        </div>
                        <SignalBadge signal={stock.signal}/>
                        {isOpen ? <ChevronUp size={14} className="text-gray-500 flex-shrink-0"/> : <ChevronDown size={14} className="text-gray-500 flex-shrink-0"/>}
                      </div>
                    </div>
                    <div className="mt-2.5">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-emerald-400 font-medium">UP {up.toFixed(1)}%</span>
                        <span className="text-gray-600 text-xs">AI Confidence</span>
                        <span className="text-red-400 font-medium">DOWN {down.toFixed(1)}%</span>
                      </div>
                      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full transition-all ${
                          up >= 65 ? "bg-emerald-500" : up >= 55 ? "bg-green-500" :
                          down >= 65 ? "bg-red-500" : "bg-yellow-500"
                        }`} style={{ width: `${up}%` }}/>
                      </div>
                    </div>
                  </div>

                  {isOpen && (
                    <div className="border-t border-gray-800 p-3 bg-[#0d1221]/80">
                      {live && (
                        <div className="bg-emerald-900/20 border border-emerald-700/30 rounded-lg p-3 mb-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-xs text-emerald-400 font-semibold">● Live Market Price</p>
                              <p className="text-xl font-bold font-mono mt-0.5">
                                ₹{safe(live.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                              </p>
                            </div>
                            <div className="text-right">
                              <PriceChange change={live.change} pct={live.change_pct}/>
                              <p className="text-gray-500 text-xs mt-1">Updated: {liveTime}</p>
                            </div>
                          </div>
                        </div>
                      )}
                      <div className="grid grid-cols-3 gap-2 mb-3">
                        {[
                          { label: "AI UP Score", val: `${up.toFixed(1)}%`, color: up >= 55 ? "text-emerald-400" : "text-red-400" },
                          { label: "RSI (14)", val: safe(stock.rsi, 50).toFixed(1), color: safe(stock.rsi,50) < 30 ? "text-emerald-400" : safe(stock.rsi,50) > 70 ? "text-red-400" : "text-yellow-400" },
                          { label: "Accuracy", val: `${safe(stock.accuracy).toFixed(1)}%`, color: "text-blue-400" },
                          { label: "Sector", val: stock.sector, color: "text-gray-300" },
                          { label: "Price Range", val: `₹${stock.price_range}`, color: "text-gray-300" },
                          { label: "Sentiment", val: stock.sent_label || "neutral", color: stock.sent_label === "positive" ? "text-emerald-400" : stock.sent_label === "negative" ? "text-red-400" : "text-gray-400" },
                        ].map(item => (
                          <div key={item.label} className="bg-gray-800/50 rounded-lg p-2">
                            <div className="text-gray-500 text-xs">{item.label}</div>
                            <div className={`font-semibold text-xs mt-0.5 capitalize ${item.color}`}>{item.val}</div>
                          </div>
                        ))}
                      </div>
                      <AIReason stock={stock} livePrice={live}/>
                      <StockNews symbol={stock.symbol}/>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

        <div className="mt-4 flex gap-2 bg-yellow-900/20 border border-yellow-700/30 rounded-xl p-3">
          <AlertCircle size={14} className="text-yellow-500 flex-shrink-0 mt-0.5"/>
          <p className="text-yellow-200/60 text-xs leading-relaxed">
            <strong className="text-yellow-400">Disclaimer:</strong> AI predictions are for educational purposes only. Not financial advice. Always do your own research before investing.
          </p>
        </div>
        <div className="mt-3 text-center text-gray-700 text-xs pb-6">
          StockAI — Powered by XGBoost + FinBERT · Live prices update every 60 seconds
        </div>
      </div>
    </div>
  )
}
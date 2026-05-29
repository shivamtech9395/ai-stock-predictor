import { useState, useEffect } from "react"
import { Newspaper, TrendingUp, TrendingDown, Minus,
         RefreshCw, Clock, Filter, ArrowLeft } from "lucide-react"
import axios from "axios"

const API = "http://localhost:8000"

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

function SentBadge({ label, score }) {
  if (label === "positive")
    return <span className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20"><TrendingUp size={10}/>Positive</span>
  if (label === "negative")
    return <span className="flex items-center gap-1 text-xs text-red-400 bg-red-500/10 px-2 py-0.5 rounded-full border border-red-500/20"><TrendingDown size={10}/>Negative</span>
  return <span className="flex items-center gap-1 text-xs text-gray-400 bg-gray-500/10 px-2 py-0.5 rounded-full border border-gray-500/20"><Minus size={10}/>Neutral</span>
}

const STOCK_SYMBOLS = [
  "MARKET","RELIANCE","TCS","HDFCBANK","INFY",
  "ICICIBANK","HINDUNILVR","SBIN","BHARTIARTL","LT"
]

export default function News() {
  const [news, setNews]         = useState([])
  const [loading, setLoading]   = useState(true)
  const [selected, setSelected] = useState("MARKET")
  const [filter, setFilter]     = useState("ALL")
  const [lastUpdated, setLastUpdated] = useState(new Date())

  const fetchNews = async (symbol) => {
    setLoading(true)
    try {
      const url = symbol === "MARKET"
        ? `${API}/api/news/market`
        : `${API}/api/news/${symbol}`
      const res = await axios.get(url)
      setNews(res.data.news || [])
      setLastUpdated(new Date())
    } catch(e) { console.error(e) }
    setLoading(false)
  }

  useEffect(() => { fetchNews(selected) }, [selected])

  // Auto refresh har 5 minutes
  useEffect(() => {
    const t = setInterval(() => fetchNews(selected), 300000)
    return () => clearInterval(t)
  }, [selected])

  const filtered = filter === "ALL" ? news
    : news.filter(n => n.sentiment_label === filter.toLowerCase())

  const posCount = news.filter(n => n.sentiment_label === "positive").length
  const negCount = news.filter(n => n.sentiment_label === "negative").length
  const neuCount = news.filter(n => n.sentiment_label === "neutral").length

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-white">

      {/* Header */}
      <div className="sticky top-0 z-50 bg-[#0d1221]/98 backdrop-blur border-b border-gray-800">
        <div className="px-3 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <a href="/" className="text-gray-500 hover:text-white transition-colors">
              <ArrowLeft size={18}/>
            </a>
            <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center">
              <Newspaper size={15} className="text-white"/>
            </div>
            <div>
              <h1 className="font-bold text-sm">News Feed</h1>
              <p className="text-gray-500 text-xs">Live market news + history</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <LiveClock/>
            <button onClick={() => fetchNews(selected)}
              className="p-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg transition-all">
              <RefreshCw size={13} className={loading ? "animate-spin text-blue-400" : "text-gray-400"}/>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-3 py-4">

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-3">
            <div className="text-gray-500 text-xs mb-1">Total News</div>
            <div className="text-xl font-bold text-white">{news.length}</div>
          </div>
          <div className="bg-gray-900/60 border border-emerald-800/30 rounded-xl p-3">
            <div className="text-gray-500 text-xs mb-1">Positive</div>
            <div className="text-xl font-bold text-emerald-400">{posCount}</div>
          </div>
          <div className="bg-gray-900/60 border border-red-800/30 rounded-xl p-3">
            <div className="text-gray-500 text-xs mb-1">Negative</div>
            <div className="text-xl font-bold text-red-400">{negCount}</div>
          </div>
        </div>

        {/* Stock selector */}
        <div className="mb-3">
          <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
            <Filter size={11}/> Select Stock / Market
          </p>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {STOCK_SYMBOLS.map(sym => (
              <button key={sym} onClick={() => setSelected(sym)}
                className={`px-3 py-1 rounded-full text-xs font-medium
                           border flex-shrink-0 transition-all ${
                  selected === sym
                    ? "bg-blue-600 border-blue-600 text-white"
                    : "bg-gray-900 border-gray-700 text-gray-400 hover:border-gray-500"
                }`}>{sym}
              </button>
            ))}
          </div>
        </div>

        {/* Sentiment filter */}
        <div className="flex gap-2 mb-4">
          {["ALL","POSITIVE","NEGATIVE","NEUTRAL"].map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-full text-xs font-medium
                         border transition-all ${
                filter === f
                  ? f === "POSITIVE" ? "bg-emerald-600 border-emerald-600 text-white"
                  : f === "NEGATIVE" ? "bg-red-600 border-red-600 text-white"
                  : "bg-blue-600 border-blue-600 text-white"
                  : "bg-gray-900 border-gray-700 text-gray-400"
              }`}>{f}
            </button>
          ))}
        </div>

        {/* News list */}
        {loading ? (
          <div className="text-center py-12 text-gray-500">
            <RefreshCw className="animate-spin mx-auto mb-2" size={24}/>
            <p className="text-sm">Loading news...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Newspaper className="mx-auto mb-2 opacity-40" size={24}/>
            <p className="text-sm">No news found</p>
            <p className="text-xs mt-1">Run daily_runner.py to collect news</p>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((n, i) => (
              <div key={i}
                className="bg-gray-900/60 border border-gray-800 
                           hover:border-gray-700 rounded-xl p-3 
                           transition-all">
                <div className="flex gap-3">
                  <span className="text-xl flex-shrink-0 mt-0.5">
                    {n.sentiment_label === "positive" ? "📈"
                    : n.sentiment_label === "negative" ? "📉" : "📰"}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-gray-100 leading-relaxed mb-2">
                      {n.headline}
                    </p>
                    <div className="flex items-center gap-2 flex-wrap">
                      <SentBadge label={n.sentiment_label} score={n.sentiment}/>
                      <span className="text-gray-600 text-xs">
                        {n.source}
                      </span>
                      <span className="text-gray-700 text-xs">·</span>
                      <span className="text-gray-600 text-xs">
                        {(n.published_at||"").slice(0,10)}
                      </span>
                      {n.fetched_at && (
                        <>
                          <span className="text-gray-700 text-xs">·</span>
                          <span className="text-gray-600 text-xs">
                            Saved: {(n.fetched_at||"").slice(0,16).replace("T"," ")}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-4 text-center text-gray-700 text-xs pb-6">
          News auto-refreshes every 5 minutes · Last updated: {lastUpdated.toLocaleTimeString('en-IN')}
        </div>
      </div>
    </div>
  )
}
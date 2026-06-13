import { useState, useEffect } from "react"
import { ArrowLeft, Star, StarOff, RefreshCw, 
         Clock, TrendingUp, TrendingDown, 
         ChevronDown, ChevronUp, Trash2 } from "lucide-react"
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
      {time.toLocaleTimeString('en-IN')}
    </span>
  )
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

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState([])
  const [allStocks, setAllStocks] = useState([])
  const [predictions, setPredictions] = useState({})
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [showSearch, setShowSearch] = useState(false)

  // Load watchlist from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('stockai_watchlist')
    if (saved) setWatchlist(JSON.parse(saved))
  }, [])

  // Save watchlist to localStorage
  const saveWatchlist = (list) => {
    setWatchlist(list)
    localStorage.setItem('stockai_watchlist', JSON.stringify(list))
  }

  // Fetch all stocks + predictions
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [stocksRes, predsRes] = await Promise.all([
          axios.get(`${API}/api/stocks`),
          axios.get(`${API}/api/predictions/today`),
        ])
        
        if (stocksRes.data.stocks) {
          setAllStocks(stocksRes.data.stocks)
        }
        
        if (predsRes.data.status === "ok") {
          const predMap = {}
          predsRes.data.data.forEach(p => {
            predMap[p.symbol] = p
          })
          setPredictions(predMap)
        }
      } catch(e) { console.error(e) }
      setLoading(false)
    }
    fetchData()
  }, [])

  const addToWatchlist = (symbol) => {
    if (!watchlist.includes(symbol)) {
      saveWatchlist([...watchlist, symbol])
    }
    setSearch("")
    setShowSearch(false)
  }

  const removeFromWatchlist = (symbol) => {
    saveWatchlist(watchlist.filter(s => s !== symbol))
  }

  const filteredStocks = allStocks.filter(s =>
    s.symbol.includes(search.toUpperCase()) ||
    s.company.toLowerCase().includes(search.toLowerCase())
  ).slice(0, 10)

  const watchlistData = watchlist.map(symbol => ({
    symbol,
    ...predictions[symbol],
    stock: allStocks.find(s => s.symbol === symbol),
  }))

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-white">
      {/* Header */}
      <div className="sticky top-0 z-50 bg-[#0d1221]/98 backdrop-blur border-b border-gray-800">
        <div className="px-3 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <a href="/" className="text-gray-500 hover:text-white transition-colors">
              <ArrowLeft size={18}/>
            </a>
            <div className="w-7 h-7 bg-yellow-600 rounded-lg flex items-center justify-center">
              <Star size={15} className="text-white"/>
            </div>
            <div>
              <h1 className="font-bold text-sm">My Watchlist</h1>
              <p className="text-gray-500 text-xs">{watchlist.length} stocks tracked</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <LiveClock/>
            <button onClick={() => setShowSearch(!showSearch)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-600/20 hover:bg-yellow-600/40 border border-yellow-600/30 rounded-lg text-xs text-yellow-400 transition-all">
              + Add Stock
            </button>
          </div>
        </div>

        {/* Search bar */}
        {showSearch && (
          <div className="px-3 pb-3">
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search stock name or symbol..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-yellow-600"
              autoFocus
            />
            {search && (
              <div className="mt-1 bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
                {filteredStocks.map(s => (
                  <div key={s.symbol}
                    onClick={() => addToWatchlist(s.symbol)}
                    className="flex items-center justify-between px-3 py-2 hover:bg-gray-700 cursor-pointer border-b border-gray-700/50 last:border-0">
                    <div>
                      <span className="font-bold text-sm text-white">{s.symbol}</span>
                      <span className="text-gray-400 text-xs ml-2">{s.company}</span>
                    </div>
                    <span className="text-gray-500 text-xs">{s.sector}</span>
                  </div>
                ))}
                {filteredStocks.length === 0 && (
                  <p className="text-gray-500 text-xs p-3">No stocks found</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="max-w-3xl mx-auto px-3 py-4">

        {watchlist.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <Star className="mx-auto mb-3 opacity-40" size={40}/>
            <p className="text-sm font-semibold">Watchlist empty hai!</p>
            <p className="text-xs mt-2">
              "Add Stock" button dabao aur apne favourite stocks add karo
            </p>
            <p className="text-xs mt-1 text-gray-600">
              Ye stocks hamesha top pe dikhenge
            </p>
          </div>
        ) : loading ? (
          <div className="text-center py-16 text-gray-500">
            <RefreshCw className="animate-spin mx-auto mb-3" size={28}/>
            <p className="text-sm">Loading watchlist data...</p>
          </div>
        ) : (
          <div className="space-y-2">
            {watchlistData.map((item, idx) => {
              const pred = predictions[item.symbol]
              const up   = safe(pred?.prob_up)
              const down = safe(pred?.prob_down)

              return (
                <div key={item.symbol}
                  className="bg-gray-900/60 border border-yellow-700/20 rounded-xl overflow-hidden hover:border-yellow-700/40 transition-all">
                  <div className="p-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-2 min-w-0">
                        <Star size={14} className="text-yellow-500 mt-1 flex-shrink-0"/>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <a href={`/stock/${item.symbol}`}
                               className="font-bold text-sm hover:text-blue-400 transition-colors">
                              {item.symbol}
                            </a>
                            <span className="text-gray-400 text-xs">
                              {item.stock?.company || item.company || ""}
                            </span>
                          </div>
                          <div className="flex items-center gap-1.5 mt-0.5">
                            <span className="text-gray-600 text-xs">
                              {item.stock?.sector || item.sector || ""}
                            </span>
                            {pred && (
                              <>
                                <span className="text-gray-700 text-xs">·</span>
                                <span className="text-gray-600 text-xs">
                                  ₹{safe(pred.price).toLocaleString('en-IN')}
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        {pred && <SignalBadge signal={pred.signal}/>}
                        <button onClick={() => removeFromWatchlist(item.symbol)}
                          className="p-1 text-gray-600 hover:text-red-400 transition-colors">
                          <Trash2 size={14}/>
                        </button>
                      </div>
                    </div>

                    {pred && (
                      <div className="mt-2.5">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-emerald-400 font-medium">UP {up.toFixed(1)}%</span>
                          <span className="text-gray-600 text-xs">AI Confidence</span>
                          <span className="text-red-400 font-medium">DOWN {down.toFixed(1)}%</span>
                        </div>
                        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${
                            up >= 65 ? "bg-emerald-500" : up >= 55 ? "bg-green-500" :
                            down >= 65 ? "bg-red-500" : "bg-yellow-500"
                          }`} style={{ width: `${up}%` }}/>
                        </div>
                      </div>
                    )}

                    {!pred && (
                      <p className="text-gray-600 text-xs mt-2">
                        No prediction today — run daily_runner.py
                      </p>
                    )}
                  </div>
                </div>
              )
            })}

            {/* Clear all */}
            <button onClick={() => saveWatchlist([])}
              className="w-full py-2 text-xs text-gray-600 hover:text-red-400 transition-colors">
              Clear all watchlist
            </button>
          </div>
        )}

        <div className="text-center text-gray-700 text-xs py-4">
          <a href="/" className="text-blue-400/50 hover:text-blue-400">← Back to Dashboard</a>
        </div>
      </div>
    </div>
  )
}
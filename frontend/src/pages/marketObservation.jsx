import { useState, useEffect } from "react"
import { ArrowLeft, TrendingUp, TrendingDown, Minus,
         RefreshCw, Clock, BarChart2, Zap, 
         ChevronDown, ChevronUp, Activity } from "lucide-react"
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

function IndexCard({ name, data }) {
  if (!data) return null
  const isUp = data.change >= 0
  return (
    <div className={`bg-gray-900/60 border rounded-xl p-4 ${
      isUp ? "border-emerald-700/30" : "border-red-700/30"
    }`}>
      <p className="text-gray-500 text-xs mb-1">{name}</p>
      <p className="text-xl font-bold font-mono">
        {data.close?.toLocaleString('en-IN')}
      </p>
      <p className={`text-sm font-semibold ${isUp ? "text-emerald-400" : "text-red-400"}`}>
        {isUp ? "▲" : "▼"} {Math.abs(data.change).toFixed(2)} ({Math.abs(data.change_pct).toFixed(2)}%)
      </p>
      <p className="text-gray-600 text-xs mt-1">
        Prev: {data.prev_close?.toLocaleString('en-IN')}
      </p>
    </div>
  )
}

function WhyMarketMoved({ indices, sectors, analysis }) {
  const nifty = indices?.NIFTY50
  const vix   = indices?.VIX
  const [expanded, setExpanded] = useState(true)

  if (!nifty) return null

  const isUp = nifty.change >= 0

  return (
    <div className={`border rounded-xl overflow-hidden mb-4 ${
      isUp ? "border-emerald-700/30 bg-emerald-900/10" : "border-red-700/30 bg-red-900/10"
    }`}>
      <div className="p-4 cursor-pointer flex justify-between items-center"
           onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            isUp ? "bg-emerald-500/20" : "bg-red-500/20"
          }`}>
            {isUp ? <TrendingUp size={20} className="text-emerald-400"/> 
                  : <TrendingDown size={20} className="text-red-400"/>}
          </div>
          <div>
            <h2 className={`font-bold text-lg ${isUp ? "text-emerald-400" : "text-red-400"}`}>
              Market Aaj {isUp ? "UPAR" : "NEECHE"} Kyun Gayi?
            </h2>
            <p className="text-gray-400 text-xs">
              Nifty {isUp ? "+" : ""}{nifty.change?.toFixed(2)} pts ({isUp ? "+" : ""}{nifty.change_pct?.toFixed(2)}%)
            </p>
          </div>
        </div>
        {expanded ? <ChevronUp size={16} className="text-gray-500"/> 
                  : <ChevronDown size={16} className="text-gray-500"/>}
      </div>

      {expanded && (
        <div className="border-t border-gray-800 p-4">
          {/* Main reasons */}
          <div className="space-y-3 mb-4">
            {analysis?.map((point, i) => (
              <div key={i} className="flex gap-3 bg-gray-800/40 rounded-lg p-3">
                <span className="text-xl flex-shrink-0">
                  {i === 0 ? "📊" : i === 1 ? "😰" : i === 2 ? "🏆" : i === 3 ? "📉" : "🎯"}
                </span>
                <div>
                  <p className="text-sm text-gray-200 leading-relaxed">{point}</p>
                </div>
              </div>
            ))}
          </div>

          {/* VIX */}
          {vix && (
            <div className="bg-gray-800/40 rounded-lg p-3 mb-3">
              <p className="text-xs text-gray-500 mb-1">Fear Index (VIX)</p>
              <div className="flex items-center gap-3">
                <p className="text-2xl font-bold font-mono">{vix.close?.toFixed(2)}</p>
                <div>
                  <p className={`text-xs font-semibold ${
                    vix.close > 20 ? "text-red-400" : 
                    vix.close > 15 ? "text-yellow-400" : "text-emerald-400"
                  }`}>
                    {vix.close > 20 ? "⚠️ HIGH FEAR — Market uncertain" :
                     vix.close > 15 ? "😐 MEDIUM FEAR — Normal" :
                     "😌 LOW FEAR — Market calm"}
                  </p>
                  <p className="text-gray-500 text-xs">
                    {vix.close > 20 
                      ? "Traders scared — avoid risky trades today"
                      : vix.close > 15 
                      ? "Normal market conditions"
                      : "Good conditions — confident market"}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Sector breakdown */}
          {sectors && sectors.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 font-semibold uppercase mb-2">
                Which Sectors Moved?
              </p>
              <div className="space-y-2">
                {sectors.slice(0, 8).map((s, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-xs text-gray-400 w-20 flex-shrink-0">{s.sector}</span>
                    <div className="flex-1 bg-gray-800 rounded-full h-2 overflow-hidden">
                      <div className={`h-full rounded-full ${
                        s.avg_up > 55 ? "bg-emerald-500" : 
                        s.avg_up < 45 ? "bg-red-500" : "bg-yellow-500"
                      }`} style={{ width: `${s.avg_up}%` }}/>
                    </div>
                    <span className={`text-xs font-bold w-12 text-right ${
                      s.avg_up > 55 ? "text-emerald-400" : 
                      s.avg_up < 45 ? "text-red-400" : "text-yellow-400"
                    }`}>{s.avg_up?.toFixed(0)}%</span>
                    <span className="text-xs">{s.mood?.split(' ')[1]}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function TopMovers({ bullish, bearish }) {
  const [tab, setTab] = useState("bullish")

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl overflow-hidden mb-4">
      <div className="flex border-b border-gray-800">
        <button onClick={() => setTab("bullish")}
          className={`flex-1 py-3 text-sm font-semibold transition-all ${
            tab === "bullish" 
              ? "bg-emerald-900/30 text-emerald-400 border-b-2 border-emerald-500"
              : "text-gray-500 hover:text-gray-300"
          }`}>
          🚀 Top Gainers ({bullish?.length || 0})
        </button>
        <button onClick={() => setTab("bearish")}
          className={`flex-1 py-3 text-sm font-semibold transition-all ${
            tab === "bearish"
              ? "bg-red-900/30 text-red-400 border-b-2 border-red-500"
              : "text-gray-500 hover:text-gray-300"
          }`}>
          🔴 Top Losers ({bearish?.length || 0})
        </button>
      </div>

      <div className="p-3">
        {tab === "bullish" ? (
          <div className="space-y-2">
            {bullish?.slice(0, 10).map((s, i) => (
              <div key={i} className="flex items-center justify-between bg-gray-800/40 rounded-lg p-3">
                <div className="flex items-center gap-3">
                  <span className="text-emerald-400 font-bold text-sm w-6">{i+1}</span>
                  <div>
                    <p className="font-bold text-sm text-white">{s.symbol}</p>
                    <p className="text-gray-500 text-xs">{s.company}</p>
                    <p className="text-gray-600 text-xs">{s.sector}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-emerald-400 font-bold text-sm">
                    UP {s.prob_up?.toFixed(0)}%
                  </p>
                  <p className="text-gray-500 text-xs">₹{s.price?.toLocaleString('en-IN')}</p>
                  <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full">
                    {s.signal}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {bearish?.slice(0, 10).map((s, i) => (
              <div key={i} className="flex items-center justify-between bg-gray-800/40 rounded-lg p-3">
                <div className="flex items-center gap-3">
                  <span className="text-red-400 font-bold text-sm w-6">{i+1}</span>
                  <div>
                    <p className="font-bold text-sm text-white">{s.symbol}</p>
                    <p className="text-gray-500 text-xs">{s.company}</p>
                    <p className="text-gray-600 text-xs">{s.sector}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-red-400 font-bold text-sm">
                    DOWN {(100 - s.prob_up)?.toFixed(0)}%
                  </p>
                  <p className="text-gray-500 text-xs">₹{s.price?.toLocaleString('en-IN')}</p>
                  <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full">
                    {s.signal}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function MarketObservation() {
  const [report, setReport]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  const fetchReport = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`${API}/api/market/close-report`)
      if (res.data.status === "ok") {
        setReport(res.data)
      } else {
        setError("No report available today")
      }
    } catch(e) {
      setError("Failed to load report")
    }
    setLoading(false)
  }

  useEffect(() => { fetchReport() }, [])

  const data    = report?.data || {}
  const indices = data.indices || {}
  const nifty   = indices.NIFTY50

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-white">
      {/* Header */}
      <div className="sticky top-0 z-50 bg-[#0d1221]/98 backdrop-blur border-b border-gray-800">
        <div className="px-3 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <a href="/" className="text-gray-500 hover:text-white transition-colors">
              <ArrowLeft size={18}/>
            </a>
            <div className="w-7 h-7 bg-purple-600 rounded-lg flex items-center justify-center">
              <Activity size={15} className="text-white"/>
            </div>
            <div>
              <h1 className="font-bold text-sm">Market Observation</h1>
              <p className="text-gray-500 text-xs">Daily market analysis</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <LiveClock/>
            <button onClick={fetchReport}
              className="p-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg">
              <RefreshCw size={13} className={loading ? "animate-spin text-blue-400" : "text-gray-400"}/>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-3 py-4">
        {loading ? (
          <div className="text-center py-16 text-gray-500">
            <RefreshCw className="animate-spin mx-auto mb-3" size={28}/>
            <p className="text-sm">Loading market observation...</p>
          </div>
        ) : error ? (
          <div className="text-center py-16">
            <BarChart2 className="mx-auto mb-3 opacity-40 text-gray-500" size={28}/>
            <p className="text-gray-400 text-sm">{error}</p>
            <p className="text-gray-600 text-xs mt-2">
              Market close hone ke baad report aayegi
            </p>
            <a href="/" className="text-blue-400 text-xs mt-4 block">← Back to Dashboard</a>
          </div>
        ) : (
          <>
            {/* Date header */}
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">
                  📊 {report?.report_date} — Daily Report
                </h2>
                <p className="text-gray-500 text-xs">
                  AI-powered market observation
                </p>
              </div>
              {nifty && (
                <div className={`px-3 py-1.5 rounded-full text-sm font-bold ${
                  nifty.change >= 0 
                    ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    : "bg-red-500/20 text-red-400 border border-red-500/30"
                }`}>
                  {nifty.change >= 0 ? "📈 BULLISH" : "📉 BEARISH"}
                </div>
              )}
            </div>

            {/* Index cards */}
            {Object.keys(indices).length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                {Object.entries(indices).map(([name, d]) => (
                  <IndexCard key={name} name={name} data={d}/>
                ))}
              </div>
            )}

            {/* Why market moved */}
            <WhyMarketMoved
              indices={indices}
              sectors={data.sectors}
              analysis={data.analysis}
            />

            {/* Top movers */}
            <TopMovers bullish={data.bullish} bearish={data.bearish}/>

            {/* Disclaimer */}
            <div className="bg-yellow-900/20 border border-yellow-700/30 rounded-xl p-3 mt-4">
              <p className="text-yellow-200/60 text-xs leading-relaxed">
                <strong className="text-yellow-400">Disclaimer:</strong> AI analysis for educational purposes only. Not financial advice.
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
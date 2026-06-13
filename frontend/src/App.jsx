import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import News from './pages/News'
import StockDetail from './pages/StockDetail'
import MarketObservation from './pages/MarketObservation'
import Watchlist from './pages/Watchlist'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/news" element={<News />} />
        <Route path="/stock/:symbol" element={<StockDetail />} />
        <Route path="/market" element={<MarketObservation />} />
        <Route path="/watchlist" element={<Watchlist />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
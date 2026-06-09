import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import News from './pages/News'
import StockDetail from './pages/StockDetail'
import MarketObservation from './pages/MarketObservation'
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/news" element={<News />} />
        <Route path="/stock/:sy++++++++++++mbol" element={<StockDetail />} />
        <Route path="/market" element={<MarketObservation />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
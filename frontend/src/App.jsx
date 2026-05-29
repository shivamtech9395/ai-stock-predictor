import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import News from './pages/News'
import StockDetail from './pages/StockDetail'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/news" element={<News />} />
        <Route path="/stock/:symbol" element={<StockDetail />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
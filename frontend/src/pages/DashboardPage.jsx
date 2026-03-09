import { useEffect, useState } from 'react'
import MarketSnapshotTable from '../components/MarketSnapshotTable'
import RankedEtfTable from '../components/RankedEtfTable'
import TopMoversPanel from '../components/TopMoversPanel'
import BreadthPanel from '../components/BreadthPanel'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

export default function DashboardPage() {
  const [summary, setSummary] = useState(null)
  const [metrics, setMetrics] = useState([])

  useEffect(() => {
    fetch(`${API_BASE}/api/dashboard/latest`).then((r) => r.json()).then(setSummary)
    fetch(`${API_BASE}/api/metrics/latest`).then((r) => r.json()).then(setMetrics)
  }, [])

  return (
    <main>
      <h1>ETF Relative Strength Dashboard</h1>
      <div className="grid-two">
        <MarketSnapshotTable summary={summary} />
        <BreadthPanel summary={summary} />
      </div>
      <TopMoversPanel movers={summary?.top_5_movers || []} />
      <RankedEtfTable rows={metrics} />
    </main>
  )
}

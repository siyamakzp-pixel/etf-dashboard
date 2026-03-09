import { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

export default function SparklineCell({ symbol }) {
  const [points, setPoints] = useState([])

  useEffect(() => {
    fetch(`${API_BASE}/api/prices/sparkline/${symbol}`)
      .then((r) => r.json())
      .then(setPoints)
      .catch(() => setPoints([]))
  }, [symbol])

  if (!points.length) return <span>-</span>

  const closes = points.map((p) => p.close)
  const min = Math.min(...closes)
  const max = Math.max(...closes)
  const normalized = closes.map((c, idx) => {
    const x = (idx / Math.max(closes.length - 1, 1)) * 100
    const y = 20 - ((c - min) / Math.max(max - min, 0.0001)) * 20
    return `${x},${y}`
  }).join(' ')

  return (
    <svg width="120" height="24" viewBox="0 0 100 22">
      <polyline fill="none" stroke="#2563eb" strokeWidth="1.5" points={normalized} />
    </svg>
  )
}

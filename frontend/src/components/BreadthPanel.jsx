export default function BreadthPanel({ summary }) {
  if (!summary) return null

  return (
    <div className="card">
      <h3>Market Breadth</h3>
      <p>Above 10DMA: {summary.pct_above_10dma?.toFixed(1)}%</p>
      <p>Above 20DMA: {summary.pct_above_20dma?.toFixed(1)}%</p>
      <p>Above 50DMA: {summary.pct_above_50dma?.toFixed(1)}%</p>
      <p>Health: <strong>{summary.market_health_label}</strong></p>
    </div>
  )
}

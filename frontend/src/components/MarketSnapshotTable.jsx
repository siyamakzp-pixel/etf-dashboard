export default function MarketSnapshotTable({ summary }) {
  if (!summary) return null

  return (
    <div className="card">
      <h3>Market Snapshot ({summary.date})</h3>
      <table>
        <tbody>
          <tr><td>Average Trend Score</td><td>{summary.average_trend_score?.toFixed(2)}</td></tr>
          <tr><td>Top Entries</td><td>{summary.top_entries?.length ?? 0}</td></tr>
          <tr><td>Pullback Entries</td><td>{summary.pullback_entries?.length ?? 0}</td></tr>
        </tbody>
      </table>
    </div>
  )
}

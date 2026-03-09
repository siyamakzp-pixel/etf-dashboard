import SparklineCell from './SparklineCell'

export default function RankedEtfTable({ rows = [] }) {
  return (
    <div className="card">
      <h3>Ranked ETFs</h3>
      <table>
        <thead>
          <tr>
            <th>Rank</th><th>Symbol</th><th>RS</th><th>Signal</th><th>Momentum</th><th>Sparkline</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.symbol}>
              <td>{r.rank_today}</td>
              <td>{r.symbol}</td>
              <td>{r.rs_score?.toFixed(4)}</td>
              <td>{r.signal_label}</td>
              <td>{r.momentum_label}</td>
              <td><SparklineCell symbol={r.symbol} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

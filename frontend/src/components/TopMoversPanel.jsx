export default function TopMoversPanel({ movers = [] }) {
  return (
    <div className="card">
      <h3>Top 5 Rank Movers</h3>
      <ul>
        {movers.map((m) => (
          <li key={m.symbol}>{m.symbol}: {m.rank_change_5d ?? '-'} </li>
        ))}
      </ul>
    </div>
  )
}

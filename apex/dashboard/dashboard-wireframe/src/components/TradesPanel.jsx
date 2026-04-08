import React from 'react';
import './TradesPanel.css';

export default function TradesPanel({ rows = [] }) {
  return (
    <section className="trades-panel">
      <div className="paper-banner">⚠️ PAPER TRADING — No real funds at risk</div>

      <table className="trades-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Symbol</th>
            <th>Side</th>
            <th>Qty</th>
            <th>Price</th>
            <th>PNL</th>
            <th>On‑Chain</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id}>
              <td>{r.time}</td>
              <td>{r.symbol}</td>
              <td><span className={`pill pill-${r.side.toLowerCase()}`}>{r.side}</span></td>
              <td>{r.qty}</td>
              <td>${r.price}</td>
              <td className={r.pnl>0?'pnl-pos' : r.pnl<0 ? 'pnl-neg' : ''}>{r.pnl>0?`+${r.pnl}`:r.pnl}</td>
              <td>{r.onChainTx ? <button className="link">Verify</button> : '-'}</td>
              <td><span className={`status status-${r.status}`}>{r.status}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

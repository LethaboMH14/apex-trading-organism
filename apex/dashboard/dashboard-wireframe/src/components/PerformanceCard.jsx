import React, { useState, useMemo } from 'react';
import {
  ComposedChart, Area, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';

// Generate realistic mock PnL curve
function generateMockData(timeframe) {
  const points = timeframe === '1H' ? 12 : timeframe === '4H' ? 24 : timeframe === '24H' ? 48 : 90;
  const data = [];
  let pnl = 0;
  let sharpe = 1.2;
  for (let i = 0; i < points; i++) {
    pnl += (Math.random() - 0.38) * 45;
    sharpe += (Math.random() - 0.5) * 0.12;
    sharpe = Math.max(0.3, Math.min(2.8, sharpe));
    const hour = Math.floor((i / points) * 24);
    const min = Math.floor((i % (points / 24)) * (60 / (points / 24)));
    data.push({
      time: `${String(hour).padStart(2,'0')}:${String(min).padStart(2,'0')}`,
      pnl: Math.round(pnl * 100) / 100,
      sharpe: Math.round(sharpe * 1000) / 1000,
    });
  }
  return data;
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'rgba(10,16,28,0.95)',
      border: '1px solid rgba(34,211,238,0.2)',
      borderRadius: 8,
      padding: '8px 12px',
      fontSize: 11,
      fontFamily: "'JetBrains Mono', monospace",
    }}>
      <div style={{ color: 'rgba(255,255,255,0.4)', marginBottom: 4 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, fontWeight: 600 }}>
          {p.name === 'pnl' ? `PnL: $${p.value.toFixed(2)}` : `Sharpe: ${p.value.toFixed(3)}`}
        </div>
      ))}
    </div>
  );
};

export default function PerformanceCard({ metrics = {}, timeframe: initialTf = '24H' }) {
  const [tf, setTf] = useState(initialTf);
  const data = useMemo(() => generateMockData(tf), [tf]);
  const maxPnl = Math.max(...data.map(d => d.pnl));
  const minPnl = Math.min(...data.map(d => d.pnl));

  return (
    <div style={{
      background: 'rgba(10,18,32,0.85)',
      backdropFilter: 'blur(16px)',
      border: '1px solid rgba(255,255,255,0.07)',
      borderTop: '1px solid rgba(255,255,255,0.12)',
      borderRadius: 16,
      marginBottom: 16,
      overflow: 'hidden',
      boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
    }}>
      {/* Metrics Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr 1fr',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}>
        {[
          { label: "TODAY'S PNL", value: `$${(metrics.todayPnl || 1247.89).toLocaleString('en-US', {minimumFractionDigits:2})}`, color: '#f59e0b', big: true },
          { label: 'SHARPE RATIO', value: (metrics.currentSharpe || 1.84).toString(), color: '#22d3ee' },
          { label: 'MAX DRAWDOWN', value: metrics.maxDrawdown || '-2.3%', color: '#f43f5e' },
        ].map((m, i) => (
          <div key={i} style={{
            padding: '14px 18px',
            borderRight: i < 2 ? '1px solid rgba(255,255,255,0.06)' : 'none',
          }}>
            <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.28)', marginBottom: 5 }}>
              {m.label}
            </div>
            <div style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: m.big ? 22 : 18,
              fontWeight: 700,
              color: m.color,
              lineHeight: 1,
              letterSpacing: '-0.02em',
              ...(m.big ? {
                background: 'linear-gradient(135deg, #f59e0b, #fbbf24)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              } : {}),
            }}>
              {m.value}
            </div>
          </div>
        ))}
      </div>

      {/* Timeframe buttons */}
      <div style={{ display: 'flex', gap: 4, padding: '8px 14px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        {['1H','4H','24H','ALL'].map(t => (
          <button key={t} onClick={() => setTf(t)} style={{
            padding: '4px 10px',
            borderRadius: 999,
            border: tf === t ? '1px solid rgba(34,211,238,0.4)' : '1px solid transparent',
            background: tf === t ? 'rgba(34,211,238,0.1)' : 'transparent',
            color: tf === t ? '#22d3ee' : 'rgba(255,255,255,0.3)',
            fontSize: 11, fontWeight: 600, fontFamily: 'inherit',
            cursor: 'pointer', letterSpacing: '0.04em', transition: 'all 0.15s',
          }}>{t}</button>
        ))}
      </div>

      {/* Chart */}
      <div style={{ padding: '12px 8px 16px', height: 220 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 8, right: 40, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="pnlGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fill: 'rgba(255,255,255,0.2)', fontSize: 9, fontFamily: "'JetBrains Mono', monospace" }}
              axisLine={false} tickLine={false}
              interval={Math.floor(data.length / 6)}
            />
            <YAxis
              yAxisId="pnl"
              tick={{ fill: 'rgba(255,255,255,0.2)', fontSize: 9, fontFamily: "'JetBrains Mono', monospace" }}
              axisLine={false} tickLine={false}
              tickFormatter={v => `$${v.toFixed(0)}`}
              width={48}
            />
            <YAxis
              yAxisId="sharpe"
              orientation="right"
              tick={{ fill: 'rgba(34,211,238,0.4)', fontSize: 9, fontFamily: "'JetBrains Mono', monospace" }}
              axisLine={false} tickLine={false}
              tickFormatter={v => v.toFixed(1)}
              width={32}
            />
            <ReferenceLine yAxisId="pnl" y={0} stroke="rgba(255,255,255,0.15)" strokeDasharray="4 4" />
            <Tooltip content={<CustomTooltip />} />
            <Area
              yAxisId="pnl"
              type="monotone"
              dataKey="pnl"
              stroke="#f59e0b"
              strokeWidth={2}
              fill="url(#pnlGradient)"
            />
            <Line
              yAxisId="sharpe"
              type="monotone"
              dataKey="sharpe"
              stroke="#22d3ee"
              strokeWidth={1.5}
              strokeDasharray="4 2"
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

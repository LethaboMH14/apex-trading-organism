import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis,
  ResponsiveContainer, Tooltip, Area, AreaChart
} from 'recharts';

const historyData = [
  { day: 'Mar 28', score: 72 },
  { day: 'Mar 29', score: 75 },
  { day: 'Mar 30', score: 73 },
  { day: 'Mar 31', score: 78 },
  { day: 'Apr 1',  score: 80 },
  { day: 'Apr 2',  score: 83 },
  { day: 'Apr 3',  score: 85 },
];

export default function ReputationCard({ score = 85, validations = 140, tradesOnChain = 93 }) {
  return (
    <div style={{
      background: 'rgba(10,18,32,0.85)',
      backdropFilter: 'blur(16px)',
      border: '1px solid rgba(255,255,255,0.07)',
      borderTop: '1px solid rgba(255,255,255,0.12)',
      borderRadius: 16,
      marginBottom: 12,
      overflow: 'hidden',
      boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
    }}>
      {/* Score */}
      <div style={{ textAlign: 'center', padding: '22px 20px 10px' }}>
        <div style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 60,
          fontWeight: 700,
          lineHeight: 1,
          letterSpacing: '-0.04em',
          background: 'linear-gradient(135deg, #00DC82, #34d399)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          filter: 'drop-shadow(0 0 20px rgba(0,220,130,0.3))',
        }}>{score}</div>
        <div style={{
          fontSize: 9, fontWeight: 700, letterSpacing: '0.14em',
          textTransform: 'uppercase', color: 'rgba(255,255,255,0.28)', marginTop: 6,
        }}>ERC-8004 Reputation Score</div>
      </div>

      {/* 7-Day Chart */}
      <div style={{ padding: '4px 12px 8px' }}>
        <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.25)', marginBottom: 6 }}>
          7-Day Score History
        </div>
        <div style={{ height: 70 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={historyData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="repGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <XAxis dataKey="day" tick={{ fill: 'rgba(255,255,255,0.2)', fontSize: 8 }} axisLine={false} tickLine={false} />
              <YAxis domain={[60, 100]} hide />
              <Tooltip
                contentStyle={{ background: 'rgba(10,16,28,0.95)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 6, fontSize: 10, fontFamily: "'JetBrains Mono', monospace" }}
                labelStyle={{ color: 'rgba(255,255,255,0.4)' }}
                itemStyle={{ color: '#f59e0b' }}
              />
              <Area type="monotone" dataKey="score" stroke="#f59e0b" strokeWidth={2} fill="url(#repGrad)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stats */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr',
        gap: 8, padding: '8px 14px 12px',
        borderTop: '1px solid rgba(255,255,255,0.06)',
      }}>
        {[
          { val: validations, label: 'Validations Published' },
          { val: tradesOnChain, label: 'Trades On-Chain' },
        ].map((s, i) => (
          <div key={i} style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.07)',
            borderRadius: 10, padding: '10px 12px', textAlign: 'center',
          }}>
            <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 20, fontWeight: 700, color: '#22d3ee', lineHeight: 1 }}>{s.val}</div>
            <div style={{ fontSize: 9, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 3, fontWeight: 600 }}>{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

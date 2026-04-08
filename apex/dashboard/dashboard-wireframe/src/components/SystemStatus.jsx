import React, { useState, useEffect } from 'react';

export default function SystemStatus({ lastUpdate = null, mode = 'PAPER', activeSymbols = 5, sessionDuration = null }) {
  const [duration, setDuration] = useState('0h 0m');

  useEffect(() => {
    const start = Date.now();
    const tick = () => {
      const elapsed = Date.now() - start;
      const h = Math.floor(elapsed / 3600000);
      const m = Math.floor((elapsed % 3600000) / 60000);
      setDuration(`${h}h ${m}m`);
    };
    const id = setInterval(tick, 30000);
    tick();
    return () => clearInterval(id);
  }, []);

  const rows = [
    { key: 'Last Update', val: lastUpdate || 'Synchronizing...', mono: true },
    { key: 'Mode', val: null, chip: mode },
    { key: 'Active Symbols', val: `${activeSymbols} Pairs`, mono: true },
    { key: 'Session Duration', val: sessionDuration || duration, mono: true },
  ];

  return (
    <div style={{
      background: 'rgba(10,18,32,0.85)',
      backdropFilter: 'blur(16px)',
      border: '1px solid rgba(255,255,255,0.07)',
      borderTop: '1px solid rgba(255,255,255,0.12)',
      borderRadius: 16, overflow: 'hidden',
      boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
    }}>
      <div style={{ padding: '12px 16px 4px' }}>
        <div style={{
          fontSize: 9, fontWeight: 700, letterSpacing: '0.12em',
          textTransform: 'uppercase', color: '#22d3ee', marginBottom: 8,
        }}>⚡ System Status</div>

        {rows.map((r, i) => (
          <div key={i} style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '6px 0',
            borderBottom: i < rows.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none',
          }}>
            <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', fontWeight: 500 }}>{r.key}</span>
            {r.chip ? (
              <span style={{
                padding: '2px 8px', borderRadius: 4, fontSize: 9, fontWeight: 800,
                letterSpacing: '0.07em', textTransform: 'uppercase',
                background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.25)',
                color: '#f59e0b',
              }}>{r.chip}</span>
            ) : (
              <span style={{
                fontSize: 11, color: 'rgba(255,255,255,0.85)',
                fontFamily: r.mono ? "'JetBrains Mono', monospace" : 'inherit',
              }}>{r.val}</span>
            )}
          </div>
        ))}

        {/* Progress bar decoration */}
        <div style={{ margin: '10px 0 12px', height: 2, background: 'rgba(255,255,255,0.05)', borderRadius: 99, overflow: 'hidden' }}>
          <div style={{
            height: '100%', width: '68%',
            background: 'linear-gradient(90deg, #3b82f6, #22d3ee)',
            borderRadius: 99,
          }} />
        </div>
      </div>
    </div>
  );
}

import React, { useState } from 'react';

const STATUS_CONFIG = {
  executing:  { label: 'EXECUTING',  bg: 'rgba(34,211,238,0.1)',  border: 'rgba(34,211,238,0.3)',  color: '#22d3ee',  glow: 'rgba(34,211,238,0.08)',  accent: '#22d3ee'  },
  validated:  { label: 'VALIDATED',  bg: 'rgba(0,220,130,0.1)',   border: 'rgba(0,220,130,0.3)',   color: '#00DC82',  glow: 'rgba(0,220,130,0.08)',   accent: '#00DC82'  },
  learning:   { label: 'LEARNING',   bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.3)',  color: '#f59e0b',  glow: 'rgba(245,158,11,0.08)',  accent: '#f59e0b'  },
  analyzing:  { label: 'ANALYZING',  bg: 'rgba(168,85,247,0.1)',  border: 'rgba(168,85,247,0.3)',  color: '#a855f7',  glow: 'rgba(168,85,247,0.08)',  accent: '#a855f7'  },
  decided:    { label: 'DECIDED',    bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.3)',  color: '#f59e0b',  glow: 'rgba(245,158,11,0.08)',  accent: '#f59e0b'  },
  idle:       { label: 'IDLE',       bg: 'rgba(255,255,255,0.04)', border: 'rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.3)', glow: 'transparent', accent: 'rgba(255,255,255,0.2)' },
};

function AgentCard({ agent }) {
  const [expanded, setExpanded] = useState(false);
  const cfg = STATUS_CONFIG[agent.status] || STATUS_CONFIG.idle;
  const confColor = agent.confidence >= 80 ? '#22d3ee' : agent.confidence >= 60 ? '#f59e0b' : '#f43f5e';

  // Reasoning data based on agent status
  const reasoningData = {
    executing: {
      signal: '+0.42',
      sentiment: 71,
      riskCheck: 'PASSED',
      reasoning: 'Volume spike detected at resistance level. Sentiment trending bullish across 12 news sources. Sharpe above threshold (1.18). Position size: 0.5 BTC. Executing.',
      hash: '0x8f3a2b1c9d7e5f4a6b8c0d2e9f1a3b5c7d9e0f2a4b6c8d0e2f4a6b8c0d2e9f1'
    },
    validated: {
      signal: '+0.67',
      sentiment: 84,
      riskCheck: 'PASSED',
      reasoning: 'Breakout pattern confirmed above $45,200 resistance. RSI showing momentum divergence. 8/10 technical indicators bullish. Risk/reward ratio: 2.3:1. Validated.',
      hash: '0x7e2c9d4a1f8b3e6c0a5d8b2f9e1a7c3d5b9e0f2a4c6d8e0b2f4a6c8d0e2f4a6b8'
    },
    learning: {
      signal: '-0.12',
      sentiment: 48,
      riskCheck: 'FAILED',
      reasoning: 'Market consolidation detected. Volume below 20-day average. Sentiment mixed with bearish bias. Sharpe below threshold (0.84). Skipping trade. Learning from false signals.',
      hash: '0x3d8b5e2a9f1c7d4e0b6a8c2d9e3f5a7b1c9e0f2a4b6c8d0e2f4a6b8c0d2e9f1a3'
    },
    analyzing: {
      signal: '+0.08',
      sentiment: 62,
      riskCheck: 'PASSED',
      reasoning: 'Accumulation phase identified. Large holder wallets increasing positions. On-chain volume rising gradually. Risk metrics within acceptable range. Analyzing entry points.',
      hash: '0x9c4a7d2e5f1b8c3e6a0d9b2f7e1a5c3d9e0f2a4b6c8d0e2f4a6b8c0d2e9f1a3b5'
    },
    decided: {
      signal: '+0.31',
      sentiment: 77,
      riskCheck: 'PASSED',
      reasoning: 'Trend confirmation across multiple timeframes. Moving averages showing bullish alignment. Social sentiment positive. Position sizing optimized for current volatility. Decision confirmed.',
      hash: '0x5f2c8d1a7e3b9c4f0a6d8b2e9f1a5c3d7e0f2a4b6c8d0e2f4a6b8c0d2e9f1a3b5c7'
    }
  };

  const currentReasoning = reasoningData[agent.status] || reasoningData.analyzing;
  const truncatedHash = `${currentReasoning.hash.slice(0, 6)}...${currentReasoning.hash.slice(-4)}`;

  return (
    <div style={{
      background: 'rgba(13,21,38,0.7)',
      border: `1px solid ${cfg.glow === 'transparent' ? 'rgba(255,255,255,0.06)' : cfg.border.replace('0.3','0.15')}`,
      borderRadius: expanded ? '12px 12px 10px 10px' : 12,
      padding: '13px 14px 10px',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      position: 'relative',
      overflow: 'hidden',
      boxShadow: cfg.glow !== 'transparent' ? `0 0 0 1px ${cfg.glow}, 0 2px 12px ${cfg.glow}` : 'none',
    }}
    onClick={() => setExpanded(!expanded)}
    >
      {/* Left accent bar */}
      <div style={{
        position: 'absolute', left: 0, top: 10, bottom: 10, width: 2,
        borderRadius: '0 2px 2px 0', background: cfg.accent, opacity: 0.8,
      }} />

      {/* Top row: name + status */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 6, paddingLeft: 10 }}>
        <div>
          <div style={{
            fontSize: 11, fontWeight: 700, color: 'rgba(255,255,255,0.92)',
            letterSpacing: '0.04em', textTransform: 'uppercase',
            fontFamily: "'Space Grotesk', sans-serif",
          }}>{agent.name}</div>
          <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.28)', marginTop: 2 }}>{agent.role}</div>
        </div>
        <div style={{
          padding: '2px 7px', borderRadius: 999,
          background: cfg.bg, border: `1px solid ${cfg.border}`,
          color: cfg.color, fontSize: 9, fontWeight: 700, letterSpacing: '0.07em',
          textTransform: 'uppercase', whiteSpace: 'nowrap', flexShrink: 0,
        }}>{cfg.label}</div>
      </div>

      {/* Address + time */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingLeft: 10, marginBottom: 8 }}>
        <span style={{
          fontFamily: "'JetBrains Mono', monospace", fontSize: 9,
          color: '#22d3ee', background: 'rgba(34,211,238,0.06)',
          border: '1px solid rgba(34,211,238,0.15)', borderRadius: 5,
          padding: '2px 6px',
        }}>🔗 {agent.addressShort}</span>
        <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.25)' }}>2m ago</span>
      </div>

      {/* Confidence bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingLeft: 10, marginBottom: 8 }}>
        <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.28)', width: 64, flexShrink: 0 }}>Confidence</span>
        <div style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 99, overflow: 'hidden' }}>
          <div style={{
            height: '100%', width: `${agent.confidence}%`, borderRadius: 99,
            background: `linear-gradient(90deg, ${confColor}99, ${confColor})`,
            transition: 'width 0.6s cubic-bezier(0.4,0,0.2,1)',
          }} />
        </div>
        <span style={{
          fontFamily: "'JetBrains Mono', monospace", fontSize: 11,
          fontWeight: 600, color: 'rgba(255,255,255,0.92)', width: 30, textAlign: 'right',
        }}>{agent.confidence}%</span>
      </div>

      {/* Show reasoning toggle */}
      <div style={{ paddingLeft: 10 }}>
        <button style={{
          background: 'none', border: 'none',
          color: '#3b82f6', fontSize: 10, fontWeight: 500,
          fontFamily: 'inherit', cursor: 'pointer', padding: '2px 0', opacity: 0.8,
        }} onClick={e => { e.stopPropagation(); setExpanded(!expanded); }}>
          {expanded ? '▼ Hide Reasoning' : '▶ Show Reasoning'}
        </button>
      </div>

      {/* Expanded reasoning section */}
      {expanded && (
        <div style={{
          marginTop: 10, paddingLeft: 10,
          borderTop: '1px solid rgba(255,255,255,0.06)',
          paddingTop: 12, paddingBottom: 14,
          background: 'rgba(0,0,0,0.3)',
          borderRadius: '0 0 10px 10px',
          margin: '10px -14px -10px -10px',
          padding: '12px 14px 14px 14px',
          animation: 'slideDown 0.3s ease-out',
        }}>
          {/* Signal row with 3 mini stats */}
          <div style={{
            display: 'flex', gap: 12, marginBottom: 10,
            justifyContent: 'space-between',
          }}>
            <div style={{ textAlign: 'center', flex: 1 }}>
              <div style={{ fontSize: 9, color: 'rgba(255,255,255,0.28)', marginBottom: 2 }}>Signal</div>
              <div style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 14, fontWeight: 700, color: '#22d3ee',
              }}>{currentReasoning.signal}</div>
            </div>
            <div style={{ textAlign: 'center', flex: 1 }}>
              <div style={{ fontSize: 9, color: 'rgba(255,255,255,0.28)', marginBottom: 2 }}>Sentiment</div>
              <div style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 14, fontWeight: 700, color: '#f59e0b',
              }}>{currentReasoning.sentiment}/100</div>
            </div>
            <div style={{ textAlign: 'center', flex: 1 }}>
              <div style={{ fontSize: 9, color: 'rgba(255,255,255,0.28)', marginBottom: 2 }}>Risk Check</div>
              <div style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 14, fontWeight: 700,
                color: currentReasoning.riskCheck === 'PASSED' ? '#10b981' : '#ef4444',
              }}>{currentReasoning.riskCheck}</div>
            </div>
          </div>

          {/* Reasoning text block */}
          <div style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 11, color: 'rgba(255,255,255,0.5)',
            lineHeight: 1.6, marginBottom: 10,
            padding: '8px 10px',
            background: 'rgba(255,255,255,0.02)',
            border: '1px solid rgba(255,255,255,0.04)',
            borderRadius: 6,
          }}>
            {currentReasoning.reasoning}
          </div>

          {/* On-chain proof row */}
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            marginBottom: 8,
          }}>
            <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.28)' }}>On-Chain Proof</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 10, color: '#22d3ee',
                background: 'rgba(34,211,238,0.06)',
                border: '1px solid rgba(34,211,238,0.15)',
                borderRadius: 4, padding: '2px 6px',
              }}>{truncatedHash}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  window.open('https://sepolia.basescan.org', '_blank');
                }}
                style={{
                  background: 'none', border: 'none',
                  color: '#3b82f6', fontSize: 9, fontWeight: 500,
                  cursor: 'pointer', padding: '2px 6px',
                  borderRadius: 4, transition: 'background 0.2s',
                }}
                onMouseEnter={(e) => e.target.style.background = 'rgba(59,130,246,0.1)'}
                onMouseLeave={(e) => e.target.style.background = 'none'}
              >
                ↗ Verify
              </button>
            </div>
          </div>

          {/* Timestamp */}
          <div style={{
            fontSize: 9, color: 'rgba(255,255,255,0.25)',
            textAlign: 'center', fontStyle: 'italic',
          }}>
            Decision logged: 2 minutes ago
          </div>
        </div>
      )}
    </div>
  );
}

export default function AgentList({ agents = [] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: '75vh', overflowY: 'auto', paddingRight: 2 }}>
      {agents.map(a => <AgentCard key={a.id} agent={a} />)}
    </div>
  );
}

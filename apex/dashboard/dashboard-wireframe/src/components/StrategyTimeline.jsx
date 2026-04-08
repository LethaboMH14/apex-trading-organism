import React from 'react';

/**
 * StrategyTimeline Component
 * Shows APEX's self-improvement history with strategy evolution over time
 * @returns {JSX.Element} Vertical timeline of strategy versions
 */
export default function StrategyTimeline() {
  // Mock strategy evolution data
  const timelineData = [
    {
      id: 1,
      date: 'Apr 3, 09:00',
      version: 'Strategy v1',
      sharpe: 0.84,
      sharpeChange: null,
      trigger: 'Initial deployment — baseline weights',
      weights: { momentum: 0.40, sentiment: 0.40, volume: 0.20 },
      status: 'superseded'
    },
    {
      id: 2,
      date: 'Apr 3, 17:30',
      version: 'Strategy v2',
      sharpe: 1.12,
      sharpeChange: 33.3,
      trigger: 'Sharpe below threshold — sentiment weight increased',
      weights: { momentum: 0.35, sentiment: 0.50, volume: 0.15 },
      status: 'superseded'
    },
    {
      id: 3,
      date: 'Apr 4, 02:15',
      version: 'Strategy v3',
      sharpe: 1.18,
      sharpeChange: 5.4,
      trigger: 'Volume signal underperforming — momentum boosted',
      weights: { momentum: 0.45, sentiment: 0.45, volume: 0.10 },
      status: 'superseded'
    },
    {
      id: 4,
      date: 'Apr 4, 14:00',
      version: 'Strategy v4',
      sharpe: 1.31,
      sharpeChange: 11.0,
      trigger: 'Overnight learning cycle — full rebalance',
      weights: { momentum: 0.50, sentiment: 0.40, volume: 0.10 },
      status: 'superseded'
    },
    {
      id: 5,
      date: 'Apr 5, 08:00',
      version: 'Strategy v5 (CURRENT)',
      sharpe: 1.47,
      sharpeChange: 12.2,
      trigger: 'DR. AMARA autonomous rewrite — sentiment confirmed alpha',
      weights: { momentum: 0.48, sentiment: 0.42, volume: 0.10 },
      status: 'ACTIVE'
    }
  ];

  /**
   * Weight bar component for visualizing strategy weights
   * @param {Object} weights - Strategy weights object
   * @returns {JSX.Element} Horizontal weight bars
   */
  const WeightBars = ({ weights }) => (
    <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
      {Object.entries(weights).map(([key, value]) => (
        <div key={key} style={{ flex: 1 }}>
          <div style={{
            fontSize: '9px',
            color: 'rgba(255,255,255,0.35)',
            marginBottom: '3px',
            textTransform: 'capitalize',
            fontFamily: "'JetBrains Mono', monospace"
          }}>
            {key}
          </div>
          <div style={{
            height: '6px',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '3px',
            overflow: 'hidden',
            position: 'relative'
          }}>
            <div style={{
              height: '100%',
              width: `${value * 100}%`,
              borderRadius: '3px',
              background: key === 'momentum' ? '#22d3ee' : 
                         key === 'sentiment' ? '#f59e0b' : '#a855f7',
              transition: 'width 0.3s ease'
            }} />
          </div>
          <div style={{
            fontSize: '8px',
            color: 'rgba(255,255,255,0.5)',
            marginTop: '2px',
            fontFamily: "'JetBrains Mono', monospace"
          }}>
            {(value * 100).toFixed(0)}%
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div style={{
      background: 'rgba(10,18,32,0.7)',
      border: '1px solid rgba(255,255,255,0.07)',
      borderRadius: '12px',
      padding: '16px',
      marginTop: '16px'
    }}>
      {/* Header */}
      <div style={{
        fontSize: '12px',
        fontWeight: '700',
        color: '#22d3ee',
        marginBottom: '16px',
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        fontFamily: "'Space Grotesk', sans-serif"
      }}>
        🧠 DR. AMARA Strategy Evolution
      </div>

      {/* Timeline */}
      <div style={{ position: 'relative', paddingLeft: '20px' }}>
        {/* Vertical line */}
        <div style={{
          position: 'absolute',
          left: '8px',
          top: '12px',
          bottom: '12px',
          width: '2px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '1px'
        }} />

        {/* Timeline entries */}
        {timelineData.map((entry, index) => (
          <div key={entry.id} style={{ 
            position: 'relative', 
            marginBottom: index < timelineData.length - 1 ? '20px' : '0' 
          }}>
            {/* Timeline dot */}
            <div style={{
              position: 'absolute',
              left: '-12px',
              top: '16px',
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: entry.status === 'ACTIVE' ? '#10b981' : 'rgba(255,255,255,0.2)',
              border: entry.status === 'ACTIVE' ? '2px solid #10b981' : '2px solid rgba(255,255,255,0.1)',
              boxShadow: entry.status === 'ACTIVE' ? '0 0 12px rgba(16,185,129,0.4)' : 'none',
              zIndex: 2
            }} />

            {/* Entry card */}
            <div style={{
              background: entry.status === 'ACTIVE' ? 'rgba(16,185,129,0.05)' : 'rgba(10,18,32,0.7)',
              border: entry.status === 'ACTIVE' ? '1px solid rgba(16,185,129,0.3)' : '1px solid rgba(255,255,255,0.07)',
              borderRadius: '12px',
              padding: '12px 14px',
              marginLeft: '16px',
              position: 'relative',
              boxShadow: entry.status === 'ACTIVE' ? '0 4px 20px rgba(16,185,129,0.15)' : 'none'
            }}>
              {/* Status badge */}
              {entry.status === 'ACTIVE' && (
                <div style={{
                  position: 'absolute',
                  top: '-8px',
                  right: '12px',
                  background: '#10b981',
                  color: '#fff',
                  fontSize: '9px',
                  fontWeight: '700',
                  padding: '2px 8px',
                  borderRadius: '999px',
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  fontFamily: "'JetBrains Mono', monospace",
                  boxShadow: '0 2px 8px rgba(16,185,129,0.3)'
                }}>
                  LIVE
                </div>
              )}

              {/* Version and date */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '8px'
              }}>
                <div>
                  <div style={{
                    fontSize: '13px',
                    fontWeight: '700',
                    color: entry.status === 'ACTIVE' ? '#10b981' : 'rgba(255,255,255,0.9)',
                    fontFamily: "'Space Grotesk', sans-serif"
                  }}>
                    {entry.version}
                  </div>
                  <div style={{
                    fontSize: '10px',
                    color: 'rgba(255,255,255,0.3)',
                    marginTop: '2px',
                    fontFamily: "'JetBrains Mono', monospace"
                  }}>
                    {entry.date}
                  </div>
                </div>
                
                {/* Sharpe with improvement badge */}
                <div style={{
                  textAlign: 'right',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-end'
                }}>
                  <div style={{
                    fontSize: '16px',
                    fontWeight: '700',
                    color: entry.status === 'ACTIVE' ? '#10b981' : 'rgba(255,255,255,0.9)',
                    fontFamily: "'JetBrains Mono', monospace"
                  }}>
                    {entry.sharpe.toFixed(2)}
                  </div>
                  {entry.sharpeChange && (
                    <div style={{
                      fontSize: '10px',
                      fontWeight: '700',
                      color: '#10b981',
                      background: 'rgba(16,185,129,0.1)',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      marginTop: '2px',
                      fontFamily: "'JetBrains Mono', monospace"
                    }}>
                      +{entry.sharpeChange}%
                    </div>
                  )}
                </div>
              </div>

              {/* Trigger */}
              <div style={{
                fontSize: '11px',
                color: 'rgba(255,255,255,0.5)',
                marginBottom: '10px',
                lineHeight: '1.4',
                fontFamily: "'DM Sans', sans-serif"
              }}>
                {entry.trigger}
              </div>

              {/* Weight bars */}
              <WeightBars weights={entry.weights} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

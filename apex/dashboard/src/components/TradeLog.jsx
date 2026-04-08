/**
 * APEX Trade Log Component
 * 
 * ENGR. FATIMA AL-RASHID: VP of Interface at APEX
 * Real-time trade log with expandable details and on-chain tracking
 */

import React, { useState, useEffect, useRef } from 'react';

// Status color mapping
const getStatusColor = (status) => {
  const colors = {
    'FILLED': '#10b981',      // green
    'PENDING': '#F59E0B',     // amber
    'CANCELLED': '#6b7280',   // grey
    'FAILED': '#ef4444'       // red
  };
  return colors[status] || '#6b7280';
};

// PnL formatting
const formatPnL = (pnl) => {
  const value = parseFloat(pnl);
  const color = value >= 0 ? '#F5A623' : '#ef4444';
  const sign = value >= 0 ? '+' : '';
  return {
    text: `${sign}${value.toFixed(2)}`,
    color
  };
};

// Time formatting
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
};

// Trade Row Component
const TradeRow = ({ trade, isExpanded, isFlashing, onToggle, onFlashEnd }) => {
  const [flashTimeout, setFlashTimeout] = useState(null);
  const pnl = formatPnL(trade.pnl);

  useEffect(() => {
    if (isFlashing) {
      const timeout = setTimeout(() => {
        onFlashEnd(trade.id);
      }, 500);
      setFlashTimeout(timeout);
    }
    
    return () => {
      if (flashTimeout) {
        clearTimeout(flashTimeout);
      }
    };
  }, [isFlashing, onFlashEnd, trade.id]);

  const handleChainLinkClick = () => {
    if (trade.onChainHash) {
      window.open(`https://sepolia.basescan.org/tx/${trade.onChainHash}`, '_blank');
    }
  };

  return (
    <>
      <tr
        onClick={() => onToggle(trade.id)}
        style={{
          backgroundColor: isFlashing ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
          cursor: 'pointer',
          transition: 'background-color 0.3s ease',
          fontFamily: 'DM Sans, sans-serif'
        }}
        onMouseOver={(e) => {
          if (!isFlashing) {
            e.currentTarget.style.backgroundColor = 'rgba(26, 86, 219, 0.1)';
          }
        }}
        onMouseOut={(e) => {
          if (!isFlashing) {
            e.currentTarget.style.backgroundColor = 'transparent';
          }
        }}
      >
        <td style={{ 
          padding: '0.75rem', 
          fontSize: '0.875rem',
          fontFamily: 'JetBrains Mono, monospace',
          color: '#9ca3af',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          {formatTime(trade.timestamp)}
        </td>
        
        <td style={{ 
          padding: '0.75rem', 
          fontSize: '0.875rem',
          fontWeight: 500,
          color: 'white',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          {trade.symbol}
        </td>
        
        <td style={{ 
          padding: '0.75rem', 
          fontSize: '0.875rem',
          fontWeight: 600,
          color: trade.side === 'BUY' ? '#10b981' : '#ef4444',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          {trade.side}
        </td>
        
        <td style={{ 
          padding: '0.75rem', 
          fontSize: '0.875rem',
          fontFamily: 'JetBrains Mono, monospace',
          color: 'white',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          {trade.quantity}
        </td>
        
        <td style={{ 
          padding: '0.75rem', 
          fontSize: '0.875rem',
          fontFamily: 'JetBrains Mono, monospace',
          color: 'white',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          ${parseFloat(trade.price).toLocaleString()}
        </td>
        
        <td style={{ 
          padding: '0.75rem', 
          fontSize: '0.875rem',
          fontFamily: 'JetBrains Mono, monospace',
          fontWeight: 600,
          color: pnl.color,
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          {pnl.text}
        </td>
        
        <td style={{ 
          padding: '0.75rem', 
          fontSize: '0.875rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          {trade.onChainHash ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleChainLinkClick();
              }}
              style={{
                backgroundColor: 'transparent',
                border: 'none',
                color: '#F5A623',
                cursor: 'pointer',
                fontSize: '1rem',
                padding: 0,
                transition: 'color 0.2s ease'
              }}
              onMouseOver={(e) => e.target.style.color = '#F59E0B'}
              onMouseOut={(e) => e.target.style.color = '#F5A623'}
            >
              🔗
            </button>
          ) : (
            <span style={{ color: '#6b7280' }}>—</span>
          )}
        </td>
        
        <td style={{ 
          padding: '0.75rem', 
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <span style={{
            padding: '0.25rem 0.5rem',
            borderRadius: '12px',
            fontSize: '0.75rem',
            fontWeight: 500,
            backgroundColor: getStatusColor(trade.status),
            color: 'white'
          }}>
            {trade.status}
          </span>
        </td>
      </tr>
      
      {/* Expandable Detail Row */}
      {isExpanded && (
        <tr>
          <td colSpan="8" style={{
            padding: '1rem',
            backgroundColor: 'rgba(26, 86, 219, 0.05)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{
              fontFamily: 'DM Sans, sans-serif',
              color: 'white'
            }}>
              <h4 style={{
                fontFamily: 'Inter, sans-serif',
                fontWeight: 600,
                fontSize: '0.875rem',
                margin: '0 0 0.75rem 0',
                color: 'var(--apex-primary)'
              }}>
                Trade Reasoning Chain
              </h4>
              <div style={{
                fontSize: '0.875rem',
                lineHeight: '1.5',
                color: '#d1d5db',
                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                padding: '0.75rem',
                borderRadius: '6px',
                border: '1px solid rgba(26, 86, 219, 0.2)',
                maxHeight: '150px',
                overflowY: 'auto'
              }}>
                {trade.reasoning || 'No reasoning chain available for this trade.'}
              </div>
              
              {trade.metadata && (
                <div style={{
                  marginTop: '0.75rem',
                  fontSize: '0.75rem',
                  color: '#9ca3af',
                  fontFamily: 'JetBrains Mono, monospace'
                }}>
                  <div>Trade ID: {trade.id}</div>
                  <div>Strategy: {trade.metadata.strategy || 'Unknown'}</div>
                  <div>Confidence: {trade.metadata.confidence || 'N/A'}%</div>
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

// Summary Row Component
const SummaryRow = ({ trades }) => {
  const sessionPnL = trades.reduce((sum, trade) => sum + parseFloat(trade.pnl || 0), 0);
  const tradeCount = trades.length;
  const winningTrades = trades.filter(trade => parseFloat(trade.pnl) > 0).length;
  const winRate = tradeCount > 0 ? (winningTrades / tradeCount * 100) : 0;
  
  // Calculate average trade duration (mock data)
  const avgDuration = '2m 15s';

  const pnlDisplay = formatPnL(sessionPnL);

  return (
    <tr style={{
      backgroundColor: 'var(--apex-surface)',
      fontFamily: 'Inter, sans-serif',
      fontWeight: 600,
      fontSize: '0.875rem'
    }}>
      <td style={{ 
        padding: '1rem 0.75rem', 
        color: pnlDisplay.color,
        fontFamily: 'JetBrains Mono, monospace'
      }}>
        {pnlDisplay.text}
      </td>
      <td style={{ padding: '1rem 0.75rem', color: 'white' }}>
        {tradeCount}
      </td>
      <td style={{ padding: '1rem 0.75rem', color: 'white' }}>
        {winRate.toFixed(1)}%
      </td>
      <td style={{ 
        padding: '1rem 0.75rem', 
        color: 'white',
        fontFamily: 'JetBrains Mono, monospace'
      }}>
        {avgDuration}
      </td>
      <td colSpan="4"></td>
    </tr>
  );
};

// Main TradeLog Component
const TradeLog = ({ trades = [], paperMode = true, isConnected = true }) => {
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [flashingRows, setFlashingRows] = useState(new Set());
  const [displayTrades, setDisplayTrades] = useState([]);
  const maxItems = 20;

  // Toggle row expansion
  const toggleRowExpansion = (tradeId) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tradeId)) {
        newSet.delete(tradeId);
      } else {
        newSet.add(tradeId);
      }
      return newSet;
    });
  };

  // Handle flash animation end
  const handleFlashEnd = (tradeId) => {
    setFlashingRows(prev => {
      const newSet = new Set(prev);
      newSet.delete(tradeId);
      return newSet;
    });
  };

  // Update display trades and handle new trades
  useEffect(() => {
    const sortedTrades = [...trades].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    const limitedTrades = sortedTrades.slice(0, maxItems);
    
    // Identify new trades for flashing
    const newTradeIds = new Set(
      limitedTrades
        .filter(trade => !displayTrades.some(dt => dt.id === trade.id))
        .map(trade => trade.id)
    );
    
    setDisplayTrades(limitedTrades);
    setFlashingRows(newTradeIds);
  }, []);

  // Mock data for demonstration (remove in production)
  useEffect(() => {
    if (trades.length === 0) {
      const mockTrades = [
        {
          id: 'trade_001',
          timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
          symbol: 'BTC',
          side: 'BUY',
          quantity: '0.5234',
          price: '43250.50',
          pnl: '125.75',
          status: 'FILLED',
          onChainHash: '0x1234567890abcdef1234567890abcdef12345678',
          reasoning: 'Technical indicators show bullish momentum. RSI at 45, MACD crossing above signal line. Volume analysis confirms buyer interest. Risk management parameters satisfied.',
          metadata: { strategy: 'Technical Momentum', confidence: 85 }
        },
        {
          id: 'trade_002',
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          symbol: 'ETH',
          side: 'SELL',
          quantity: '2.1500',
          price: '2280.75',
          pnl: '-45.20',
          status: 'FILLED',
          onChainHash: '0xabcdef1234567890abcdef1234567890abcdef12',
          reasoning: 'Sentiment analysis turning bearish for ETH. News flow negative, social media sentiment declining. Taking profits at resistance level.',
          metadata: { strategy: 'Sentiment Reversal', confidence: 72 }
        },
        {
          id: 'trade_003',
          timestamp: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
          symbol: 'SOL',
          side: 'BUY',
          quantity: '15.7500',
          price: '98.25',
          pnl: '67.30',
          status: 'FILLED',
          onChainHash: null,
          reasoning: 'Breakout pattern detected on SOL. Volume spike confirms strength. Entry above key resistance level with stop loss below.',
          metadata: { strategy: 'Breakout Trading', confidence: 78 }
        },
        {
          id: 'trade_004',
          timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
          symbol: 'AVAX',
          side: 'BUY',
          quantity: '8.5000',
          price: '35.75',
          pnl: '0.00',
          status: 'PENDING',
          onChainHash: null,
          reasoning: 'Order placed for AVAX based on positive news flow. Partnership announcement expected. Awaiting execution.',
          metadata: { strategy: 'News-Based Trading', confidence: 65 }
        },
        {
          id: 'trade_005',
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
          symbol: 'MATIC',
          side: 'SELL',
          quantity: '25.0000',
          price: '0.85',
          pnl: '12.50',
          status: 'CANCELLED',
          onChainHash: null,
          reasoning: 'Order cancelled due to market conditions change. Risk parameters exceeded threshold.',
          metadata: { strategy: 'Risk Management', confidence: 100 }
        }
      ];
      setDisplayTrades(mockTrades);
    }
  }, []);

  return (
    <div style={{
      backgroundColor: 'var(--apex-surface)',
      borderRadius: '12px',
      padding: '1rem',
      fontFamily: 'DM Sans, sans-serif',
      color: 'white',
      position: 'relative'
    }}>
      {/* Paper Mode Banner */}
      {paperMode && (
        <div style={{
          backgroundColor: '#F59E0B',
          color: '#000',
          padding: '0.75rem',
          borderRadius: '8px',
          marginBottom: '1rem',
          fontFamily: 'Inter, sans-serif',
          fontWeight: 600,
          fontSize: '0.875rem',
          textAlign: 'center',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem'
        }}>
          ⚠ PAPER TRADING — No real funds at risk
        </div>
      )}

      {/* Connection Overlay */}
      {!isConnected && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10,
          borderRadius: '12px',
          backdropFilter: 'blur(4px)'
        }}>
          <div style={{
            color: 'white',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            fontSize: '0.875rem',
            textAlign: 'center'
          }}>
            Connection Lost
          </div>
        </div>
      )}

      {/* Trade Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '0.875rem'
        }}>
          <thead>
            <tr style={{
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              fontSize: '0.75rem',
              color: '#9ca3af',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Time</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Symbol</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Side</th>
              <th style={{ padding: '0.75rem', textAlign: 'right' }}>Qty</th>
              <th style={{ padding: '0.75rem', textAlign: 'right' }}>Price</th>
              <th style={{ padding: '0.75rem', textAlign: 'right' }}>PnL</th>
              <th style={{ padding: '0.75rem', textAlign: 'center' }}>On-Chain</th>
              <th style={{ padding: '0.75rem', textAlign: 'center' }}>Status</th>
            </tr>
          </thead>
          
          <tbody>
            {displayTrades.map((trade) => (
              <TradeRow
                key={trade.id}
                trade={trade}
                isExpanded={expandedRows.has(trade.id)}
                isFlashing={flashingRows.has(trade.id)}
                onToggle={toggleRowExpansion}
                onFlashEnd={handleFlashEnd}
              />
            ))}
            
            {/* Summary Row */}
            <tr>
              <td colSpan="8" style={{ padding: 0, height: '1px' }}></td>
            </tr>
            <tr>
              <td colSpan="8" style={{ padding: 0, height: '1px', backgroundColor: 'rgba(255, 255, 255, 0.1)' }}></td>
            </tr>
            <tr>
              <td colSpan="8" style={{ padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#9ca3af', fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
                SESSION SUMMARY
              </td>
            </tr>
            <SummaryRow trades={displayTrades} />
          </tbody>
        </table>
      </div>

      {/* Empty State */}
      {displayTrades.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '3rem 1rem',
          color: '#9ca3af',
          fontFamily: 'DM Sans, sans-serif'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📊</div>
          <div style={{ fontSize: '1rem' }}>
            No trades yet today
          </div>
        </div>
      )}
    </div>
  );
};

export default TradeLog;

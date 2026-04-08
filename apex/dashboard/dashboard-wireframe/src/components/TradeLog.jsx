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
        className={`trade-row ${isFlashing ? 'flashing' : ''}`}
      >
        <td className="td-mono">
          {formatTime(trade.timestamp)}
        </td>
        
        <td>
          {trade.symbol}
        </td>
        
        <td>
          <span className={`side-${trade.side.toLowerCase()}`}>
            {trade.side}
          </span>
        </td>
        
        <td className="td-mono">
          {trade.quantity}
        </td>
        
        <td className="td-mono">
          ${parseFloat(trade.price).toLocaleString()}
        </td>
        
        <td className={`pnl-${pnl.text.startsWith('+') ? 'pos' : pnl.text.startsWith('-') ? 'neg' : 'neu'}`}>
          {pnl.text}
        </td>
        
        <td>
          {trade.onChainHash ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleChainLinkClick();
              }}
              className="chain-link"
            >
              🔗
            </button>
          ) : (
            <span style={{ color: '#6b7280' }}>—</span>
          )}
        </td>
        
        <td>
          <span className={`pill pill-${trade.status.toLowerCase()}`}>
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
    <div className="card">
      {/* Paper Mode Banner */}
      {paperMode && (
        <div className="paper-strip">
          ⚠ PAPER TRADING — No real funds at risk
        </div>
      )}

      {/* Connection Overlay */}
      {!isConnected && (
        <div className="connection-overlay">
          <div className="connection-lost">
            Connection Lost
          </div>
        </div>
      )}

      {/* Trade Table */}
      <div className="table-wrap">
        <table className="trade-table">
          <thead>
            <tr className="table-header">
              <th>Time</th>
              <th>Symbol</th>
              <th>Side</th>
              <th>Qty</th>
              <th>Price</th>
              <th>PnL</th>
              <th>On-Chain</th>
              <th>Status</th>
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
              <td colSpan="8" className="summary-separator"></td>
            </tr>
            <tr>
              <td colSpan="8" className="summary-separator summary-separator-light"></td>
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

/**
 * APEX Performance Analytics Component
 * Comprehensive performance metrics and analytics
 */

import React, { useState, useEffect } from 'react';

const PerformanceAnalytics = () => {
  const [timeframe, setTimeframe] = useState('24H');
  const [performanceData, setPerformanceData] = useState({
    totalPnL: 12543.67,
    sharpeRatio: 1.84,
    maxDrawdown: -12.3,
    winRate: 68.5,
    totalTrades: 342,
    avgTradeSize: 8750.00,
    bestTrade: 2340.50,
    worstTrade: -890.25,
    dailyData: [
      { date: '2026-04-01', pnl: 450.25, trades: 12 },
      { date: '2026-04-02', pnl: 890.50, trades: 18 },
      { date: '2026-04-03', pnl: -234.75, trades: 8 },
      { date: '2026-04-04', pnl: 1234.00, trades: 24 },
      { date: '2026-04-05', pnl: 567.80, trades: 15 },
      { date: '2026-04-06', pnl: 1890.25, trades: 32 },
      { date: '2026-04-07', pnl: 399.00, trades: 11 },
    ],
    assetPerformance: [
      { asset: 'BTC', pnl: 5432.10, trades: 145, winRate: 72.3 },
      { asset: 'ETH', pnl: 3210.75, trades: 98, winRate: 65.2 },
      { asset: 'SOL', pnl: 1890.50, trades: 67, winRate: 71.4 },
      { asset: 'MATIC', pnl: 890.32, trades: 32, winRate: 58.9 },
    ],
    agentPerformance: [
      { agent: 'Dr. Zara Okafor', pnl: 4532.00, trades: 89, winRate: 78.5 },
      { agent: 'Dr. Jabari Mensah', pnl: 2340.50, trades: 67, winRate: 62.3 },
      { agent: 'ENGR. Marcus Oduya', pnl: 3210.75, trades: 112, winRate: 69.8 },
      { agent: 'Dr. Sipho Nkosi', pnl: 1456.42, trades: 45, winRate: 64.2 },
      { agent: 'Dr. Priya Nair', pnl: 1004.00, trades: 29, winRate: 71.1 },
    ]
  });

  const [selectedMetric, setSelectedMetric] = useState('pnl');

  const timeframes = ['1H', '4H', '24H', '7D', '30D', 'ALL'];

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${value.toFixed(1)}%`;
  };

  const getMetricColor = (value, isPositive = true) => {
    if (isPositive) {
      return value >= 0 ? '#00ff88' : '#ff4444';
    }
    return value >= 0 ? '#00ff88' : '#ff4444';
  };

  return (
    <div style={{ color: 'white' }}>
      
      {/* Header with Controls */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '24px' 
      }}>
        <h2 style={{ margin: 0, color: '#fff' }}>Performance Analytics</h2>
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <select 
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            style={{
              padding: '8px 12px',
              backgroundColor: '#2a2a2a',
              border: '1px solid #444',
              borderRadius: '6px',
              color: '#fff',
              fontSize: '12px'
            }}
          >
            <option value="pnl">P&L</option>
            <option value="trades">Trades</option>
            <option value="winrate">Win Rate</option>
            <option value="sharpe">Sharpe Ratio</option>
          </select>
          
          <div style={{ display: 'flex', gap: '4px' }}>
            {timeframes.map(tf => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                style={{
                  padding: '6px 12px',
                  backgroundColor: timeframe === tf ? '#00ff88' : '#2a2a2a',
                  border: 'none',
                  borderRadius: '4px',
                  color: timeframe === tf ? '#000' : '#ccc',
                  fontSize: '11px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '20px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '8px' }}>Total P&L</div>
          <div style={{ 
            fontSize: '24px', 
            fontWeight: '700',
            color: getMetricColor(performanceData.totalPnL)
          }}>
            {formatCurrency(performanceData.totalPnL)}
          </div>
        </div>
        
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '20px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '8px' }}>Sharpe Ratio</div>
          <div style={{ 
            fontSize: '24px', 
            fontWeight: '700',
            color: getMetricColor(performanceData.sharpeRatio)
          }}>
            {performanceData.sharpeRatio.toFixed(2)}
          </div>
        </div>
        
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '20px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '8px' }}>Max Drawdown</div>
          <div style={{ 
            fontSize: '24px', 
            fontWeight: '700',
            color: getMetricColor(performanceData.maxDrawdown)
          }}>
            {formatPercent(performanceData.maxDrawdown)}
          </div>
        </div>
        
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '20px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '8px' }}>Win Rate</div>
          <div style={{ 
            fontSize: '24px', 
            fontWeight: '700',
            color: getMetricColor(performanceData.winRate)
          }}>
            {formatPercent(performanceData.winRate)}
          </div>
        </div>
      </div>

      {/* Performance Chart Placeholder */}
      <div style={{
        backgroundColor: '#1a1a1a',
        border: '1px solid #333',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px'
      }}>
        <h3 style={{ color: '#fff', marginBottom: '16px' }}>Performance Chart</h3>
        <div style={{
          height: '300px',
          backgroundColor: '#2a2a2a',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#888',
          fontSize: '14px'
        }}>
          📊 Chart visualization will be rendered here
        </div>
      </div>

      {/* Detailed Tables */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '24px' 
      }}>
        
        {/* Asset Performance */}
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '20px'
        }}>
          <h3 style={{ color: '#fff', marginBottom: '16px' }}>Asset Performance</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #333' }}>
                <th style={{ textAlign: 'left', padding: '8px', color: '#888', fontSize: '12px' }}>Asset</th>
                <th style={{ textAlign: 'right', padding: '8px', color: '#888', fontSize: '12px' }}>P&L</th>
                <th style={{ textAlign: 'right', padding: '8px', color: '#888', fontSize: '12px' }}>Trades</th>
                <th style={{ textAlign: 'right', padding: '8px', color: '#888', fontSize: '12px' }}>Win Rate</th>
              </tr>
            </thead>
            <tbody>
              {performanceData.assetPerformance.map((asset, index) => (
                <tr key={asset.asset} style={{ borderBottom: '1px solid #333' }}>
                  <td style={{ padding: '8px', color: '#fff', fontSize: '12px', fontWeight: '600' }}>
                    {asset.asset}
                  </td>
                  <td style={{ 
                    padding: '8px', 
                    textAlign: 'right', 
                    fontSize: '12px',
                    color: getMetricColor(asset.pnl)
                  }}>
                    {formatCurrency(asset.pnl)}
                  </td>
                  <td style={{ padding: '8px', textAlign: 'right', fontSize: '12px', color: '#ccc' }}>
                    {asset.trades}
                  </td>
                  <td style={{ 
                    padding: '8px', 
                    textAlign: 'right', 
                    fontSize: '12px',
                    color: getMetricColor(asset.winRate)
                  }}>
                    {formatPercent(asset.winRate)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Agent Performance */}
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '20px'
        }}>
          <h3 style={{ color: '#fff', marginBottom: '16px' }}>Agent Performance</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #333' }}>
                <th style={{ textAlign: 'left', padding: '8px', color: '#888', fontSize: '12px' }}>Agent</th>
                <th style={{ textAlign: 'right', padding: '8px', color: '#888', fontSize: '12px' }}>P&L</th>
                <th style={{ textAlign: 'right', padding: '8px', color: '#888', fontSize: '12px' }}>Trades</th>
                <th style={{ textAlign: 'right', padding: '8px', color: '#888', fontSize: '12px' }}>Win Rate</th>
              </tr>
            </thead>
            <tbody>
              {performanceData.agentPerformance.map((agent, index) => (
                <tr key={agent.agent} style={{ borderBottom: '1px solid #333' }}>
                  <td style={{ padding: '8px', color: '#fff', fontSize: '12px' }}>
                    <div style={{ fontWeight: '600', marginBottom: '2px' }}>
                      {agent.agent.split(' ').slice(0, 2).join(' ')}
                    </div>
                    <div style={{ fontSize: '10px', color: '#888' }}>
                      {agent.agent.split(' ').slice(2).join(' ')}
                    </div>
                  </td>
                  <td style={{ 
                    padding: '8px', 
                    textAlign: 'right', 
                    fontSize: '12px',
                    color: getMetricColor(agent.pnl)
                  }}>
                    {formatCurrency(agent.pnl)}
                  </td>
                  <td style={{ padding: '8px', textAlign: 'right', fontSize: '12px', color: '#ccc' }}>
                    {agent.trades}
                  </td>
                  <td style={{ 
                    padding: '8px', 
                    textAlign: 'right', 
                    fontSize: '12px',
                    color: getMetricColor(agent.winRate)
                  }}>
                    {formatPercent(agent.winRate)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Additional Stats */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '16px',
        marginTop: '24px'
      }}>
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '16px'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Total Trades</div>
          <div style={{ fontSize: '18px', fontWeight: '600', color: '#fff' }}>
            {performanceData.totalTrades}
          </div>
        </div>
        
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '16px'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Avg Trade Size</div>
          <div style={{ fontSize: '18px', fontWeight: '600', color: '#fff' }}>
            {formatCurrency(performanceData.avgTradeSize)}
          </div>
        </div>
        
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '16px'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Best Trade</div>
          <div style={{ 
            fontSize: '18px', 
            fontWeight: '600',
            color: '#00ff88'
          }}>
            {formatCurrency(performanceData.bestTrade)}
          </div>
        </div>
        
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '12px',
          padding: '16px'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Worst Trade</div>
          <div style={{ 
            fontSize: '18px', 
            fontWeight: '600',
            color: '#ff4444'
          }}>
            {formatCurrency(performanceData.worstTrade)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceAnalytics;

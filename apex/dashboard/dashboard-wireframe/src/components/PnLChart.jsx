/**
 * APEX PnL Chart Component
 * 
 * ENGR. FATIMA AL-RASHID: VP of Interface at APEX
 * PnL curve with Sharpe ratio overlay using Recharts ComposedChart
 */

import React, { useState, useEffect, useMemo } from 'react';
import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

// Time filtering utilities
const filterDataByTimeframe = (data, timeframe) => {
  if (!data || data.length === 0) return [];
  
  const now = new Date();
  let cutoff = new Date();
  
  switch (timeframe) {
    case '1H':
      cutoff.setHours(now.getHours() - 1);
      break;
    case '4H':
      cutoff.setHours(now.getHours() - 4);
      break;
    case '24H':
      cutoff.setDate(now.getDate() - 1);
      break;
    case 'ALL':
      // Return all data
      return data;
    default:
      return data;
  }
  
  return data.filter(item => new Date(item.timestamp) >= cutoff);
};

// Calculate cumulative PnL
const calculateCumulativePnL = (trades) => {
  if (!trades || trades.length === 0) return [];
  
  const sortedTrades = [...trades].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  const cumulative = [];
  let runningPnL = 0;
  
  sortedTrades.forEach(trade => {
    runningPnL += parseFloat(trade.pnl || 0);
    cumulative.push({
      timestamp: trade.timestamp,
      cumulativePnL: runningPnL,
      sharpe: trade.sharpe || 0
    });
  });
  
  return cumulative;
};

// Calculate Sharpe color
const getSharpeColor = (sharpe) => {
  if (sharpe > 1.0) return '#10b981';  // green
  if (sharpe >= 0.5) return '#F59E0B'; // amber
  return '#ef4444'; // red
};

// Custom tooltip
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const pnlPayload = payload.find(p => p.dataKey === 'cumulativePnL');
    const sharpePayload = payload.find(p => p.dataKey === 'sharpe');
    
    return (
      <div style={{
        backgroundColor: 'var(--apex-surface)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        borderRadius: '8px',
        padding: '0.75rem',
        fontFamily: 'DM Sans, sans-serif',
        color: 'white',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
      }}>
        <p style={{ 
          margin: '0 0 0.5rem 0', 
          fontSize: '0.875rem', 
          fontWeight: 500,
          fontFamily: 'JetBrains Mono, monospace'
        }}>
          {new Date(label).toLocaleString()}
        </p>
        {pnlPayload && (
          <p style={{ 
            margin: '0 0 0.25rem 0', 
            fontSize: '0.875rem',
            color: pnlPayload.value >= 0 ? '#F5A623' : '#ef4444',
            fontFamily: 'JetBrains Mono, monospace',
            fontWeight: 600
          }}>
            PnL: ${pnlPayload.value.toFixed(2)}
          </p>
        )}
        {sharpePayload && (
          <p style={{ 
            margin: 0, 
            fontSize: '0.875rem',
            color: '#1a56db',
            fontFamily: 'JetBrains Mono, monospace',
            fontWeight: 600
          }}>
            Sharpe: {sharpePayload.value.toFixed(3)}
          </p>
        )}
      </div>
    );
  }
  return null;
};

// Stat Card Component
const StatCard = ({ label, value, color, isLarge = false }) => (
  <div style={{
    backgroundColor: 'rgba(26, 86, 219, 0.1)',
    border: '1px solid rgba(26, 86, 219, 0.2)',
    borderRadius: '8px',
    padding: '1rem',
    textAlign: 'center',
    flex: 1
  }}>
    <div style={{
      fontSize: isLarge ? '2rem' : '1.25rem',
      fontFamily: 'JetBrains Mono, monospace',
      fontWeight: 700,
      color: color,
      marginBottom: '0.25rem',
      lineHeight: 1
    }}>
      {value}
    </div>
    <div style={{
      fontSize: '0.75rem',
      color: '#9ca3af',
      fontFamily: 'DM Sans, sans-serif',
      fontWeight: 500,
      textTransform: 'uppercase',
      letterSpacing: '0.05em'
    }}>
      {label}
    </div>
  </div>
);

// Timeframe Button Component
const TimeframeButton = ({ active, onClick, children }) => (
  <button
    onClick={onClick}
    style={{
      backgroundColor: active ? 'var(--apex-primary)' : 'transparent',
      color: active ? 'white' : '#9ca3af',
      border: active ? '1px solid var(--apex-primary)' : '1px solid #374151',
      padding: '0.5rem 1rem',
      borderRadius: '6px',
      fontFamily: 'Inter, sans-serif',
      fontWeight: 500,
      fontSize: '0.875rem',
      cursor: 'pointer',
      transition: 'all 0.2s ease'
    }}
    onMouseOver={(e) => {
      if (!active) {
        e.target.style.backgroundColor = 'rgba(26, 86, 219, 0.1)';
        e.target.style.color = 'white';
      }
    }}
    onMouseOut={(e) => {
      if (!active) {
        e.target.style.backgroundColor = 'transparent';
        e.target.style.color = '#9ca3af';
      }
    }}
  >
    {children}
  </button>
);

// Main PnLChart Component
const PnLChart = ({ 
  trades = [], 
  sharpeHistory = [], 
  timeframe = '24H',
  performanceData = null,
  isConnected = true 
}) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState(timeframe);
  const [chartData, setChartData] = useState([]);
  const [stats, setStats] = useState({
    todayPnL: 0,
    currentSharpe: 0,
    maxDrawdown: 0
  });

  // Process data when trades or timeframe changes
  useEffect(() => {
    // Generate mock data if no trades provided
    let processedTrades = trades;
    if (trades.length === 0) {
      // Generate mock cumulative PnL data as specified
      const mockData = Array.from({length: 24}, (_, i) => ({
        time: `${String(i).padStart(2,'0')}:00`,
        pnl: Math.random() * 400 + i * 15,
        sharpe: 0.8 + Math.random() * 0.8
      }));
      
      processedTrades = mockData.map((item, index) => ({
        timestamp: new Date(Date.now() - (23 - index) * 60 * 60 * 1000).toISOString(),
        cumulativePnL: item.pnl,
        sharpe: item.sharpe
      }));
    }

    // Filter by timeframe
    const filteredTrades = filterDataByTimeframe(processedTrades, selectedTimeframe);
    
    // Calculate cumulative PnL
    const cumulativeData = calculateCumulativePnL(filteredTrades);
    
    // Format data for chart
    const formattedData = cumulativeData.map(item => ({
      ...item,
      timestamp: new Date(item.timestamp).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      }),
      displayTime: new Date(item.timestamp).getTime()
    }));

    setChartData(formattedData);

    // Calculate stats
    if (formattedData.length > 0) {
      const latestPnL = formattedData[formattedData.length - 1].cumulativePnL;
      const latestSharpe = formattedData[formattedData.length - 1].sharpe;
      
      // Calculate max drawdown
      let maxPnL = 0;
      let maxDrawdown = 0;
      formattedData.forEach(item => {
        if (item.cumulativePnL > maxPnL) {
          maxPnL = item.cumulativePnL;
        }
        const drawdown = maxPnL - item.cumulativePnL;
        if (drawdown > maxDrawdown) {
          maxDrawdown = drawdown;
        }
      });

      setStats({
        todayPnL: latestPnL,
        currentSharpe: latestSharpe,
        maxDrawdown: maxDrawdown
      });
    }
  }, []);

  // Use performance data if available (only when no trades data)
  useEffect(() => {
    if (performanceData && (!trades || trades.length === 0)) {
      setStats({
        todayPnL: parseFloat(performanceData.daily_pnl) || 0,
        currentSharpe: parseFloat(performanceData.sharpe) || 0,
        maxDrawdown: parseFloat(performanceData.drawdown) || 0
      });
    }
  }, []);

  return (
    <div style={{
      backgroundColor: 'var(--apex-surface)',
      borderRadius: '12px',
      padding: '1.5rem',
      fontFamily: 'DM Sans, sans-serif',
      color: 'white',
      position: 'relative'
    }}>
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

      {/* Header Stats */}
      <div style={{ 
        display: 'flex', 
        gap: '1rem', 
        marginBottom: '1.5rem' 
      }}>
        <StatCard 
          label="Today's PnL" 
          value={`$${stats.todayPnL.toFixed(2)}`}
          color={stats.todayPnL >= 0 ? '#F5A623' : '#ef4444'}
          isLarge={true}
          style={{ fontSize: '28px' }}
        />
        <StatCard 
          label="Current Sharpe" 
          value={stats.currentSharpe.toFixed(3)}
          color={getSharpeColor(stats.currentSharpe)}
          style={{ fontSize: '18px' }}
        />
        <StatCard 
          label="Max Drawdown" 
          value={`-${stats.maxDrawdown.toFixed(2)}`}
          color="#ef4444"
          style={{ fontSize: '18px' }}
        />
      </div>

      {/* Timeframe Selector */}
      <div style={{ 
        display: 'flex', 
        gap: '0.5rem', 
        marginBottom: '1.5rem',
        justifyContent: 'center'
      }}>
        {['1H', '4H', '24H', 'ALL'].map((tf) => (
          <TimeframeButton
            key={tf}
            active={selectedTimeframe === tf}
            onClick={() => setSelectedTimeframe(tf)}
          >
            {tf}
          </TimeframeButton>
        ))}
      </div>

      {/* Chart */}
      <div style={{ height: '300px', width: '100%' }}>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData}>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="rgba(255, 255, 255, 0.1)"
              />
              
              <XAxis 
                dataKey="timestamp"
                stroke="#9ca3af"
                fontSize="0.75rem"
                fontFamily="JetBrains Mono, monospace"
              />
              
              <YAxis 
                yAxisId="left"
                stroke="#9ca3af"
                fontSize="0.75rem"
                fontFamily="JetBrains Mono, monospace"
                label={{ 
                  value: 'Cumulative PnL ($)', 
                  angle: -90, 
                  position: 'insideLeft',
                  style: { fill: '#9ca3af', fontSize: '0.75rem' }
                }}
              />
              
              <YAxis 
                yAxisId="right"
                orientation="right"
                stroke="#9ca3af"
                fontSize="0.75rem"
                fontFamily="JetBrains Mono, monospace"
                label={{ 
                  value: 'Sharpe Ratio', 
                  angle: 90, 
                  position: 'insideRight',
                  style: { fill: '#9ca3af', fontSize: '0.75rem' }
                }}
              />
              
              <Tooltip content={<CustomTooltip />} />
              
              {/* Zero Line */}
              <ReferenceLine 
                yAxisId="left"
                y={0} 
                stroke="white" 
                strokeDasharray="5 5"
                strokeWidth={2}
              />
              
              {/* PnL Area */}
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="cumulativePnL"
                fill="#f59e0b"
                fillOpacity={0.3}
                stroke="#f59e0b"
                strokeWidth={2}
              />
              
              {/* Sharpe Line */}
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="sharpe"
                stroke="#22d3ee"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        ) : (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: '#9ca3af',
            fontFamily: 'DM Sans, sans-serif'
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📈</div>
              <div>No data available for selected timeframe</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PnLChart;

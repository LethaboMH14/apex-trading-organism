/**
 * APEX Dashboard - Wireframe Version
 * Multi-agent trading dashboard with full functionality
 */

import React, { useState, useEffect, useCallback } from 'react';
import { AgentFeed, ReputationScore, TradeLog, PnLChart } from './components';
import AgentManagement from './components/AgentManagement';
import Settings from './components/Settings';
import PerformanceAnalytics from './components/PerformanceAnalytics';
import ReputationSystem from './components/ReputationSystem';
// Import new Board theme components
import AgentList from './components/AgentList.jsx';
import PerformanceCard from './components/PerformanceCard.jsx';
import TradesPanel from './components/TradesPanel.jsx';
import ReputationCard from './components/ReputationCard.jsx';
import SystemStatus from './components/SystemStatus.jsx';
import StrategyTimeline from './components/StrategyTimeline.jsx';

// API Configuration
const API_BASE = 'http://localhost:3001';
const WS_URL = 'ws://localhost:3002';

// Mock Data for Board Theme Components
const mockAgents = [
  { id: 1, name: 'Alpha Trader', role: 'Scalping Bot', status: 'executing', confidence: 87, addressShort: '0x1a2b...3c4d' },
  { id: 2, name: 'Beta Strategy', role: 'Arbitrage', status: 'validated', confidence: 92, addressShort: '0x5e6f...7a8b' },
  { id: 3, name: 'Gamma Market', role: 'Market Maker', status: 'learning', confidence: 73, addressShort: '0x9c0d...1e2f' },
  { id: 4, name: 'Delta Hedge', role: 'Hedging Bot', status: 'executing', confidence: 81, addressShort: '0x3b4c...5d6e' },
  { id: 5, name: 'Epsilon AI', role: 'Prediction', status: 'validated', confidence: 95, addressShort: '0x7f8g...9h0i' }
];

const mockMetrics = {
  todayPnl: 1247.89,
  currentSharpe: 1.84,
  maxDrawdown: '-2.3%'
};

const mockTrades = [
  { id: 1, time: '09:42:15', symbol: 'BTC/USDT', side: 'BUY', qty: '0.124', price: '43,256', pnl: '+124.50', onChainTx: '0xabc123', status: 'filled' },
  { id: 2, time: '09:38:22', symbol: 'ETH/USDT', side: 'SELL', qty: '2.5', price: '2,245', pnl: '+89.30', onChainTx: null, status: 'filled' },
  { id: 3, time: '09:35:10', symbol: 'SOL/USDT', side: 'BUY', qty: '45', price: '98.45', pnl: '-23.20', onChainTx: '0xdef456', status: 'pending' },
  { id: 4, time: '09:31:45', symbol: 'MATIC/USDT', side: 'SELL', qty: '850', price: '0.92', pnl: '+45.60', onChainTx: null, status: 'filled' },
  { id: 5, time: '09:28:33', symbol: 'AVAX/USDT', side: 'BUY', qty: '12', price: '35.78', pnl: '+67.80', onChainTx: '0xghi789', status: 'filled' }
];

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Dashboard Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '2rem',
          backgroundColor: '#1a1a1a',
          color: 'white',
          fontFamily: 'Inter, sans-serif',
          fontWeight: 700,
          textAlign: 'center',
          borderRadius: '8px',
          margin: '1rem'
        }}>
          Component Error: {this.props.fallbackName}
          <br />
          <small style={{ fontWeight: 400, fontFamily: 'DM Sans, sans-serif' }}>
            {this.state.error?.message}
          </small>
        </div>
      );
    }

    return this.props.children;
  }
}

// Live Stats Bar Component
const LiveStatsBar = ({ systemStatus }) => {
  const [trades, setTrades] = useState(41);
  const [proofs, setProofs] = useState(19);
  const [sharpe, setSharpe] = useState(1.12);
  const [uptime, setUptime] = useState('0h 0m');
  const [startTime] = useState(() => Date.now());

  // Use real data if available, otherwise use animated mock data
  const useRealData = systemStatus && systemStatus.apexConnected;
  const realTrades = systemStatus?.tradesExecuted;
  const realProofs = systemStatus?.onChainProofs;
  const realSharpe = systemStatus?.currentSharpe;
  const realUptime = systemStatus?.uptime;

  useEffect(() => {
    if (useRealData) {
      // Use real data from API
      if (realTrades !== undefined) setTrades(realTrades);
      if (realProofs !== undefined) setProofs(realProofs);
      if (realSharpe !== undefined) setSharpe(parseFloat(realSharpe));
      if (realUptime !== undefined) setUptime(realUptime);
    } else {
      // Use animated mock data when offline
      const tradesInterval = setInterval(() => {
        setTrades(prev => prev + 1);
      }, 8000);

      const proofsInterval = setInterval(() => {
        setProofs(prev => prev + 1);
      }, 15000);

      const sharpeInterval = setInterval(() => {
        setSharpe(prev => {
          const change = (Math.random() - 0.5) * 0.04;
          const newValue = prev + change;
          return Math.max(0.8, Math.min(1.5, newValue));
        });
      }, 12000);

      const uptimeInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const hours = Math.floor(elapsed / 3600000);
        const minutes = Math.floor((elapsed % 3600000) / 60000);
        setUptime(`${hours}h ${minutes}m`);
      }, 1000);

      return () => {
        clearInterval(tradesInterval);
        clearInterval(proofsInterval);
        clearInterval(sharpeInterval);
        clearInterval(uptimeInterval);
      };
    }
  }, [systemStatus, startTime, realTrades, realProofs, realSharpe, realUptime]);

  return (
    <div className="live-stats-bar" style={{
      position: 'sticky',
      top: '48px',
      height: '36px',
      background: 'rgba(0,0,0,0.4)',
      borderBottom: '1px solid rgba(255,255,255,0.05)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 16px',
      zIndex: 90
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: '11px'
      }}>
        {/* Trades Executed */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span style={{ marginRight: '4px' }}>⚡</span>
          <span style={{ color: 'rgba(255,255,255,0.35)' }}>Trades Executed:</span>
          <span style={{ color: 'rgba(255,255,255,0.9)' }}>{trades}</span>
        </div>

        {/* Divider */}
        <div style={{
          width: '1px',
          height: '20px',
          background: 'rgba(255,255,255,0.08)'
        }} />

        {/* On-Chain Proofs */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span style={{ marginRight: '4px' }}>🔗</span>
          <span style={{ color: 'rgba(255,255,255,0.35)' }}>On-Chain Proofs:</span>
          <span style={{ color: 'rgba(255,255,255,0.9)' }}>{proofs}</span>
        </div>

        {/* Divider */}
        <div style={{
          width: '1px',
          height: '20px',
          background: 'rgba(255,255,255,0.08)'
        }} />

        {/* Sharpe Ratio */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span style={{ marginRight: '4px' }}>📈</span>
          <span style={{ color: 'rgba(255,255,255,0.35)' }}>Sharpe:</span>
          <span style={{ color: '#22d3ee' }}>{sharpe.toFixed(2)}</span>
        </div>

        {/* Divider */}
        <div style={{
          width: '1px',
          height: '20px',
          background: 'rgba(255,255,255,0.08)'
        }} />

        {/* Uptime */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span style={{ marginRight: '4px' }}>⏱</span>
          <span style={{ color: 'rgba(255,255,255,0.35)' }}>Uptime:</span>
          <span style={{ color: 'rgba(255,255,255,0.9)' }}>{uptime}</span>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const [wsConnected, setWsConnected] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {
        setWsConnected(true);
        setError(null);
      };
      
      ws.onclose = () => {
        setWsConnected(false);
      };
      
      ws.onerror = () => {
        setWsConnected(false);
        setError('Connection failed');
      };
      
      return ws;
    } catch (err) {
      setError('WebSocket connection failed');
      console.error('WebSocket error:', err);
    }
  }, []);

  // Fetch initial data
  const fetchInitialData = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/system-status`);
      if (!response.ok) throw new Error('System status fetch failed');
      
      const data = await response.json();
      setSystemStatus(data);
    } catch (err) {
      setError('Backend connection failed');
      console.error('Fetch error:', err);
    }
  }, []);

  // Initialize WebSocket and fetch data
  useEffect(() => {
    const ws = connectWebSocket();
    fetchInitialData();
    
    return () => {
      if (ws) ws.close();
    };
  }, [connectWebSocket, fetchInitialData]);

  // Navigation items
  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'agents', label: 'Agents', icon: '🤖' },
    { id: 'trades', label: 'Trades', icon: '💱' },
    { id: 'performance', label: 'Performance', icon: '📈' },
    { id: 'reputation', label: 'Reputation', icon: '⭐' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  return (
    <div className="app-shell">
      
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        
        {/* Logo */}
        <div className="sidebar-brand">
          <div className="sidebar-logo">A</div>
          <div>
            <div className="sidebar-brand-name">APEX</div>
            <div className="sidebar-brand-sub">Multi-Agent Trading</div>
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="sidebar-nav">
          {navigationItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`nav-item ${activeView === item.id ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
        
        {/* System Status */}
        <div className="sidebar-footer">
          <div className="system-status-indicator">
            <div className={`status-dot ${wsConnected ? 'online' : 'offline'}`}></div>
            <span className="status-label">
              {wsConnected ? 'Connected' : 'Offline'}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className={`main-area ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        
        {/* Top Bar */}
        <header className="topbar">
          <div className="topbar-left">
            <button 
              className="sidebar-toggle"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              aria-label="Toggle sidebar"
            >
              ☰
            </button>
            <div className="topbar-page-title">
              {navigationItems.find(item => item.id === activeView)?.label || 'Dashboard'}
            </div>
          </div>
          
          <div className="topbar-actions">
            <div className={`topbar-chip ${wsConnected ? 'connected' : 'disconnected'}`}>
              <div className="topbar-chip-dot"></div>
              {wsConnected ? 'Live' : 'Offline'}
            </div>
            
            <button 
              onClick={() => setActiveView('settings')}
              className="topbar-btn"
            >
              ⚙️ Settings
            </button>
          </div>
        </header>

        {/* Live Stats Bar */}
        <LiveStatsBar systemStatus={systemStatus} />

        {/* Dynamic Content Area */}
        <div className="page">
          {error && (
            <div className="alert-banner warning">
              ⚠️ {error}
            </div>
          )}

          {activeView === 'dashboard' && (
            <div className="dashboard">
              <div className="dashboard-inner">
                {/* Left Column - Agent Activity */}
                <aside className="col-left">
                  <h2 className="section-title">Agent Activity</h2>
                  <ErrorBoundary fallbackName="Agent List">
                    <AgentList agents={mockAgents} />
                  </ErrorBoundary>
                </aside>

                {/* Center Column - Performance + Trades */}
                <main className="col-center">
                  <ErrorBoundary fallbackName="Performance">
                    <PerformanceCard metrics={mockMetrics} />
                  </ErrorBoundary>
                  
                  <ErrorBoundary fallbackName="Trades">
                    <TradesPanel rows={mockTrades} />
                  </ErrorBoundary>
                </main>

                {/* Right Column - Reputation + System Status */}
                <aside className="col-right">
                  <ErrorBoundary fallbackName="Reputation">
                    <ReputationCard score={85} validations={140} tradesOnChain={93} />
                  </ErrorBoundary>
                  
                  <ErrorBoundary fallbackName="System Status">
                    <SystemStatus mode="PAPER" activeSymbols={5} />
                  </ErrorBoundary>
                </aside>
              </div>
            </div>
          )}

          {activeView === 'agents' && (
            <ErrorBoundary fallbackName="Agent Management">
              <AgentManagement />
            </ErrorBoundary>
          )}

          {activeView === 'trades' && (
            <ErrorBoundary fallbackName="Trades">
              <div className="card">
                <h3 className="card-title">Trade History</h3>
                <TradeLog wsConnected={wsConnected} />
              </div>
            </ErrorBoundary>
          )}

          {activeView === 'performance' && (
            <ErrorBoundary fallbackName="Performance Analytics">
              <PerformanceAnalytics />
              <StrategyTimeline />
            </ErrorBoundary>
          )}

          {activeView === 'reputation' && (
            <ErrorBoundary fallbackName="Reputation System">
              <ReputationSystem />
            </ErrorBoundary>
          )}

          {activeView === 'settings' && (
            <ErrorBoundary fallbackName="Settings">
              <Settings />
            </ErrorBoundary>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;

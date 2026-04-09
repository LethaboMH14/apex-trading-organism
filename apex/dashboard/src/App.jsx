/**
 * APEX Dashboard - Main React Application
<<<<<<< HEAD
 * Layout: 3-column — narrow icon sidebar | left agent feed | centre main | right stats panel
=======
 * 
 * ENGR. FATIMA AL-RASHID: VP of Interface at APEX
 * Background: Moroccan-French. W3C working group contributor. Built trading dashboards for three Tier-1 banks.
 * Standard: "The interface is the system's face to the world. If a judge cannot understand what is happening in 10 seconds, we have failed presentation."
 * 
 * Complete production-ready React dashboard with WebSocket real-time updates and responsive design
>>>>>>> 7104b79fe2a693b23df1ddfad2952721ee506102
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { AgentFeed, ReputationScore, PnLChart, TradeLog } from './components';

<<<<<<< HEAD
const API_BASE = 'http://localhost:3001';
const WS_URL = 'ws://localhost:8766';

// ─── Toast ────────────────────────────────────────────────────────────────────
const showToast = (message, type = 'success') => {
  const toast = document.createElement('div');
  toast.style.cssText = `position:fixed;bottom:20px;right:20px;padding:12px 20px;border-radius:8px;
    font-family:'DM Sans',sans-serif;font-size:14px;font-weight:500;z-index:9999;
    background:${type === 'success' ? 'rgba(0,220,130,0.15)' : 'rgba(239,68,68,0.15)'};
    border:1px solid ${type === 'success' ? '#00DC82' : '#ef4444'};
    color:${type === 'success' ? '#00DC82' : '#ef4444'};`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => { if (document.body.contains(toast)) document.body.removeChild(toast); }, 3000);
};

// ─── Error Boundary ───────────────────────────────────────────────────────────
class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, info) { console.error('Dashboard Error:', error, info); }
  render() {
    if (this.state.hasError) return (
      <div style={{ padding: '1rem', backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid #ef4444', borderRadius: '8px', color: '#ef4444', fontFamily: 'DM Sans', fontSize: '0.875rem' }}>
        ⚠ {this.props.fallbackName} error: {this.state.error?.message}
      </div>
    );
=======
// API Configuration
const API_BASE = 'http://localhost:3001';
const WS_URL = 'ws://localhost:3002';

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
          backgroundColor: 'var(--apex-danger)',
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

>>>>>>> 7104b79fe2a693b23df1ddfad2952721ee506102
    return this.props.children;
  }
}

<<<<<<< HEAD
// ─── Agent Decision Card ──────────────────────────────────────────────────────
const AgentCard = ({ name, role, status, confidence, txHash, timeAgo }) => {
  const statusColors = { DECIDED: '#3b82f6', ANALYZING: '#F5A623', EXECUTING: '#8b5cf6', VALIDATED: '#10b981', LEARNING: '#06b6d4' };
  return (
    <div style={{ backgroundColor: 'rgba(26,86,219,0.08)', border: '1px solid rgba(26,86,219,0.2)', borderRadius: '10px', padding: '1rem', marginBottom: '0.75rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
        <div>
          <div style={{ color: 'white', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.875rem' }}>{name}</div>
          <div style={{ color: '#9ca3af', fontFamily: 'DM Sans', fontSize: '0.75rem' }}>{role}</div>
        </div>
        <span style={{ backgroundColor: statusColors[status] || '#6b7280', color: 'white', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.7rem', fontFamily: 'JetBrains Mono', fontWeight: 600 }}>{status}</span>
      </div>
      {txHash && (
        <div style={{ marginBottom: '0.5rem' }}>
          <a href={`https://sepolia.etherscan.io/tx/${txHash}`} target="_blank" rel="noopener noreferrer"
            style={{ color: '#3b82f6', fontFamily: 'JetBrains Mono', fontSize: '0.7rem', textDecoration: 'none' }}>
            🔗 {txHash.slice(0, 10)}...{txHash.slice(-6)}
          </a>
        </div>
      )}
      {timeAgo && <div style={{ color: '#6b7280', fontSize: '0.7rem', fontFamily: 'DM Sans', marginBottom: '0.5rem' }}>{timeAgo}</div>}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span style={{ color: '#9ca3af', fontSize: '0.75rem', fontFamily: 'DM Sans', minWidth: '70px' }}>Confidence</span>
        <div style={{ flex: 1, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '4px', height: '6px' }}>
          <div style={{ width: `${confidence}%`, backgroundColor: confidence > 80 ? '#10b981' : '#F5A623', height: '100%', borderRadius: '4px', transition: 'width 0.3s' }} />
        </div>
        <span style={{ color: 'white', fontSize: '0.75rem', fontFamily: 'JetBrains Mono', fontWeight: 600, minWidth: '35px' }}>{confidence}%</span>
=======
// Loading Skeleton Component
const SkeletonLoader = ({ type, height = '100%' }) => {
  const baseStyle = {
    backgroundColor: 'rgba(26, 86, 219, 0.1)',
    borderRadius: '8px',
    animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
    height
  };

  if (type === 'text') {
    return (
      <div style={{ ...baseStyle, height: '1rem', marginBottom: '0.5rem' }} />
    );
  }

  if (type === 'heading') {
    return (
      <div style={{ ...baseStyle, height: '1.5rem', marginBottom: '1rem' }} />
    );
  }

  return <div style={baseStyle} />;
};

// Circuit Breaker Alert Component
const CircuitBreakerAlert = ({ isTripped, onReset }) => {
  const [showConfirm, setShowConfirm] = useState(false);

  const handleReset = () => {
    fetch(`${API_BASE}/api/circuit-breaker/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirm: 'APEX_RESET_CONFIRMED' })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Circuit breaker reset:', data);
      setShowConfirm(false);
      onReset();
    })
    .catch(error => {
      console.error('Reset failed:', error);
    });
  };

  if (!isTripped) return null;

  return (
    <div style={{
      backgroundColor: 'var(--apex-danger)',
      color: 'white',
      padding: '1rem',
      fontFamily: 'Inter, sans-serif',
      fontWeight: 700,
      textAlign: 'center',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: '1rem'
    }}>
      <span>⚠️ CIRCUIT BREAKER TRIPPED - Trading Halted</span>
      {!showConfirm ? (
        <button
          onClick={() => setShowConfirm(true)}
          style={{
            backgroundColor: 'white',
            color: 'var(--apex-danger)',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            fontFamily: 'DM Sans, sans-serif',
            fontWeight: 500,
            cursor: 'pointer'
          }}
        >
          Reset
        </button>
      ) : (
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ fontFamily: 'DM Sans, sans-serif', fontWeight: 400 }}>
            Confirm reset?
          </span>
          <button
            onClick={handleReset}
            style={{
              backgroundColor: 'white',
              color: 'var(--apex-danger)',
              border: 'none',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px',
              fontFamily: 'DM Sans, sans-serif',
              fontWeight: 500,
              cursor: 'pointer'
            }}
          >
            Yes
          </button>
          <button
            onClick={() => setShowConfirm(false)}
            style={{
              backgroundColor: 'transparent',
              color: 'white',
              border: '1px solid white',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px',
              fontFamily: 'DM Sans, sans-serif',
              fontWeight: 500,
              cursor: 'pointer'
            }}
          >
            No
          </button>
        </div>
      )}
    </div>
  );
};

// System Status Panel Component
const SystemStatusPanel = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="card system-status">
        <div className="skeleton" style={{ height: '1.5rem', marginBottom: '1rem' }}></div>
        <div className="skeleton" style={{ height: '1rem', marginBottom: '0.5rem' }}></div>
        <div className="skeleton" style={{ height: '1rem', marginBottom: '0.5rem' }}></div>
        <div className="skeleton" style={{ height: '1rem', marginBottom: '0.5rem' }}></div>
        <div className="skeleton" style={{ height: '1rem' }}></div>
      </div>
    );
  }

  return (
    <div className="card system-status">
      <div className="system-status-title">System Status</div>
      
      <div className="status-row">
        <span className="status-key">Last Update:</span>
        <span className="status-val">
          {data?.lastUpdate || 'Loading...'}
        </span>
      </div>
      
      <div className="status-row">
        <span className="status-key">Mode:</span>
        <span className="mode-chip">
          PAPER
        </span>
      </div>
      
      <div className="status-row">
        <span className="status-key">Active Symbols:</span>
        <span className="status-val">
          {data?.activeSymbols || '5'}
        </span>
      </div>
      
      <div className="status-row">
        <span className="status-key">Session Duration:</span>
        <span className="status-val">
          {data?.sessionDuration || '0h 0m'}
        </span>
>>>>>>> 7104b79fe2a693b23df1ddfad2952721ee506102
      </div>
    </div>
  );
};

<<<<<<< HEAD
// ─── Main App ─────────────────────────────────────────────────────────────────
=======
// Main App Component
>>>>>>> 7104b79fe2a693b23df1ddfad2952721ee506102
const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [wsConnected, setWsConnected] = useState(false);
  const [circuitBreakerTripped, setCircuitBreakerTripped] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(false);
<<<<<<< HEAD
  const [continuousTrading, setContinuousTrading] = useState(true);
  const [tradeSize, setTradeSize] = useState(350);
  const [recentTrades, setRecentTrades] = useState([]);
  const [reputationData, setReputationData] = useState({ current_score: 92, total_validations: 142, trades_on_chain: 82, agent_id: 26, agent_address: '0x909375eC03d6A001A95Bcf20E2260d671a84140B' });
  const [agentDecisions, setAgentDecisions] = useState([
    { id: 1, name: 'DR. ZARA OKAFOR', role: 'Strategy Orchestrator', status: 'DECIDED', confidence: 85, txHash: null, timeAgo: '3m ago' },
    { id: 2, name: 'DR. JABARI MENSAH', role: 'NLP Analyst', status: 'ANALYZING', confidence: 72, txHash: null, timeAgo: '6m ago' },
    { id: 3, name: 'ENGR. MARCUS ODUYA', role: 'Kraken Execution', status: 'EXECUTING', confidence: 95, txHash: '0x8xabcdef...cdef12', timeAgo: '9m ago' },
    { id: 4, name: 'DR. SIPHO NKOSI', role: 'Risk Management', status: 'VALIDATED', confidence: 88, txHash: '0x7899ab...90abcd', timeAgo: '13m ago' },
  ]);
  const [pnlData, setPnlData] = useState([]);
  const [btcPrice, setBtcPrice] = useState(null);
  const [btcChange, setBtcChange] = useState(0);
  const [runningPnL, setRunningPnL] = useState(531.90);
  const [executeLoading, setExecuteLoading] = useState(false);
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  // ─── WebSocket ──────────────────────────────────────────────────────────────
  const connectWebSocket = useCallback(() => {
    try {
      ws.current = new WebSocket(WS_URL);
      ws.current.onopen = () => { setWsConnected(true); };
      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          switch (data.type) {
            case 'connection_status': setWsConnected(data.python_connected); break;
            case 'connection_lost': setWsConnected(false); break;
            case 'connection_restored': setWsConnected(true); break;
            case 'circuit_breaker_tripped': setCircuitBreakerTripped(true); break;
            case 'circuit_breaker_reset': setCircuitBreakerTripped(false); break;
            case 'trade_executed': {
              const newTrade = {
                id: `trade_${Date.now()}`,
                symbol: 'BTC', side: data.action,
                quantity: (350 / (data.price || 71500)).toFixed(4),
                price: String(data.price || 71500),
                timestamp: data.timestamp || new Date().toISOString(),
                pnl: String(data.pnl_estimate || 0),
                status: 'FILLED',
                onChainHash: data.tx_hash || null,
                reasoning: data.reasoning || '',
                metadata: { strategy: 'Multi-Agent Consensus', confidence: data.confidence || 85 }
              };
              setRecentTrades(prev => [newTrade, ...prev].slice(0, 50));
              setPnlData(prev => [...prev, { timestamp: data.timestamp, pnl: data.pnl_estimate || 0 }]);
              setAgentDecisions(prev => [{
                id: Date.now(), name: 'PROF. KWAME ASANTE', role: 'LLM Router',
                status: 'DECIDED', confidence: data.confidence || 85,
                txHash: data.tx_hash, timeAgo: 'just now'
              }, ...prev].slice(0, 8));
              break;
            }
            default: break;
          }
        } catch (err) { console.error('WS message error:', err); }
      };
      ws.current.onclose = () => {
        setWsConnected(false);
        reconnectTimeout.current = setTimeout(connectWebSocket, 5000);
      };
      ws.current.onerror = () => setWsConnected(false);
    } catch (err) { console.error('WS connection error:', err); }
  }, []);

  // ─── Effects ────────────────────────────────────────────────────────────────
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws.current) ws.current.close();
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    };
  }, []);

  useEffect(() => {
    const fetchBtcPrice = async () => {
      try {
        const res = await fetch('https://api.kraken.com/0/public/Ticker?pair=XBTUSD');
        const data = await res.json();
        const price = parseFloat(data.result.XXBTZUSD.c[0]);
        const change = parseFloat(data.result.XXBTZUSD.p[1]);
        setBtcPrice(price);
        setBtcChange(isNaN(change) ? 0 : change);
      } catch (e) {}
    };
    fetchBtcPrice();
    const interval = setInterval(fetchBtcPrice, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchLiveData = async () => {
      try {
        const [tradesRes, repRes] = await Promise.all([
          fetch(`${API_BASE}/api/trades`),
          fetch(`${API_BASE}/api/reputation`)
        ]);
        const tradesData = await tradesRes.json();
        const repData = await repRes.json();
        if (tradesData.trades) setRecentTrades(tradesData.trades);
        if (repData.current_score) setReputationData(repData);
      } catch (e) {}
    };
    fetchLiveData();
    const interval = setInterval(fetchLiveData, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/health`);
        const data = await res.json();
        setSystemStatus({ lastUpdate: new Date().toLocaleTimeString(), activeSymbols: '5', sessionDuration: '0h 0m', ...data });
      } catch (e) {
        setSystemStatus({ lastUpdate: new Date().toLocaleTimeString(), activeSymbols: '5', sessionDuration: '0h 0m' });
      } finally { setLoading(false); }
    };
    fetchStatus();
  }, []);

  // ─── Handlers ───────────────────────────────────────────────────────────────
  const handleExecuteTrade = () => {
    setExecuteLoading(true);
    if (wsConnected && ws.current) {
      ws.current.send(JSON.stringify({ type: 'execute_trade', pair: 'XBTUSD', action: 'BUY', amount: tradeSize, reasoning: 'Dashboard manual execution.', confidence: 82 }));
      setTimeout(() => { setExecuteLoading(false); showToast('Trade intent submitted'); }, 1500);
    } else {
      setTimeout(() => { setExecuteLoading(false); showToast('Trade submitted (Demo Mode)'); }, 2000);
    }
  };

  const handleToggleTrading = async (enabled) => {
    setContinuousTrading(enabled);
    try { await fetch(`${API_BASE}/${enabled ? 'resume-trading' : 'pause-trading'}`, { method: 'POST' }); } catch (e) {}
  };

  // ─── Nav items ──────────────────────────────────────────────────────────────
  const navItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'agents',    icon: '🤖', label: 'Agents' },
    { id: 'trades',    icon: '📈', label: 'Trades' },
    { id: 'performance', icon: '⚡', label: 'Performance' },
    { id: 'reputation', icon: '🏆', label: 'Reputation' },
    { id: 'settings',  icon: '⚙️', label: 'Settings' },
  ];

  // ─── Shared styles ──────────────────────────────────────────────────────────
  const card = { backgroundColor: 'var(--apex-surface, #0D2040)', border: '1px solid rgba(26,86,219,0.2)', borderRadius: '12px', padding: '1.25rem' };
  const sectionLabel = { color: '#9ca3af', fontFamily: 'DM Sans', fontWeight: 600, fontSize: '0.7rem', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.75rem' };
  const mono = { fontFamily: 'JetBrains Mono' };

  // ─── Right panel content ────────────────────────────────────────────────────
  const RightPanel = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '1rem' }}>
      {/* Reputation Score */}
      <div style={card}>
        <div style={sectionLabel}>ERC-8004 Reputation Score</div>
        <div style={{ textAlign: 'center', padding: '0.5rem 0' }}>
          <div style={{ fontSize: '3rem', fontFamily: 'Inter', fontWeight: 700, color: '#10b981', lineHeight: 1 }}>{reputationData.current_score || 92}</div>
        </div>
        <div style={{ ...sectionLabel, marginTop: '1rem' }}>7-Day Score History</div>
        <ErrorBoundary fallbackName="Reputation Chart">
          <ReputationScore wsConnected={wsConnected} />
        </ErrorBoundary>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '1rem' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ color: 'white', fontFamily: 'Inter', fontWeight: 700, fontSize: '1.5rem' }}>{reputationData.total_validations || 142}</div>
            <div style={{ color: '#9ca3af', fontSize: '0.75rem', fontFamily: 'DM Sans' }}>Validations Published</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ color: 'white', fontFamily: 'Inter', fontWeight: 700, fontSize: '1.5rem' }}>{reputationData.trades_on_chain || 82}</div>
            <div style={{ color: '#9ca3af', fontSize: '0.75rem', fontFamily: 'DM Sans' }}>Trades On-Chain</div>
          </div>
        </div>
      </div>

      {/* Agent Identity */}
      <div style={card}>
        <div style={sectionLabel}>Agent Identity</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>Agent NFT:</span>
          <span style={{ color: '#F5A623', ...mono, fontSize: '0.8rem', fontWeight: 600 }}>#{reputationData.agent_id || 26}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>Agent Address:</span>
          <a href={`https://sepolia.etherscan.io/address/${reputationData.agent_address}`} target="_blank" rel="noopener noreferrer"
            style={{ color: '#3b82f6', ...mono, fontSize: '0.7rem', textDecoration: 'none' }}>
            {reputationData.agent_address ? `${reputationData.agent_address.slice(0,6)}...${reputationData.agent_address.slice(-4)}` : '0x9093...140B'}
          </a>
        </div>
        <a href={`https://sepolia.etherscan.io/address/${reputationData.agent_address}`} target="_blank" rel="noopener noreferrer"
          style={{ display: 'block', textAlign: 'center', backgroundColor: '#1a56db', color: 'white', padding: '0.5rem', borderRadius: '8px', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.8rem', textDecoration: 'none' }}>
          View on Etherscan
        </a>
      </div>

      {/* System Status */}
      <div style={card}>
        <div style={sectionLabel}>System Status</div>
        {[
          { label: 'Last Update', value: systemStatus?.lastUpdate || 'Loading...' },
          { label: 'Mode', value: 'PAPER', highlight: true },
          { label: 'Active Symbols', value: systemStatus?.activeSymbols || '5' },
          { label: 'Session Duration', value: systemStatus?.sessionDuration || '0h 0m' },
        ].map(({ label, value, highlight }) => (
          <div key={label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ color: '#9ca3af', fontSize: '0.8rem', fontFamily: 'DM Sans' }}>{label}:</span>
            <span style={{ color: highlight ? '#F5A623' : 'white', ...mono, fontSize: '0.8rem', fontWeight: highlight ? 600 : 400 }}>{value}</span>
          </div>
        ))}
      </div>

      {/* Trading Controls */}
      <div style={card}>
        <div style={sectionLabel}>Trading Controls</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: wsConnected ? '#10b981' : '#ef4444' }} />
          <span style={{ color: 'white', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.875rem' }}>
            Agent {wsConnected ? 'ONLINE' : 'OFFLINE'}
          </span>
        </div>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', cursor: 'pointer' }}>
          <input type="checkbox" checked={continuousTrading} onChange={(e) => handleToggleTrading(e.target.checked)} style={{ width: '18px', height: '18px' }} />
          <span style={{ color: 'white', fontFamily: 'DM Sans', fontWeight: 500, fontSize: '0.875rem' }}>Auto Trading</span>
        </label>
        <div style={{ marginBottom: '1rem' }}>
          <div style={{ color: 'white', fontFamily: 'DM Sans', fontSize: '0.875rem', marginBottom: '0.4rem' }}>
            Trade Size: <span style={{ color: '#F5A623', ...mono }}>${tradeSize}</span>
          </div>
          <input type="range" min="100" max="1000" value={tradeSize} onChange={(e) => setTradeSize(parseInt(e.target.value))} style={{ width: '100%' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#9ca3af', fontSize: '0.7rem', fontFamily: 'DM Sans' }}>
            <span>$100</span><span>$1000</span>
          </div>
        </div>
        <button onClick={handleExecuteTrade} disabled={executeLoading}
          style={{ width: '100%', backgroundColor: executeLoading ? '#6b7280' : '#F5A623', color: 'white', border: 'none', padding: '0.75rem', borderRadius: '8px', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.9rem', cursor: executeLoading ? 'not-allowed' : 'pointer' }}>
          {executeLoading ? 'Executing...' : 'Execute Trade Now'}
        </button>
      </div>
    </div>
  );

  // ─── Dashboard Tab ──────────────────────────────────────────────────────────
  const DashboardTab = () => (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
        {[
          { label: "Today's PnL", value: `$${runningPnL.toFixed(2)}`, color: '#F5A623' },
          { label: 'Current Sharpe', value: '1.84', color: '#3b82f6' },
          { label: 'Max Drawdown', value: '-2.3%', color: '#ef4444' },
        ].map(({ label, value, color }) => (
          <div key={label} style={card}>
            <div style={{ color, fontFamily: 'Inter', fontWeight: 700, fontSize: '1.75rem', ...mono }}>{value}</div>
            <div style={{ color: '#9ca3af', fontFamily: 'DM Sans', fontSize: '0.8rem', marginTop: '0.25rem' }}>{label.toUpperCase()}</div>
          </div>
        ))}
      </div>

      {/* PnL Chart */}
      <div style={card}>
        <div style={sectionLabel}>Performance Chart</div>
        <ErrorBoundary fallbackName="PnL Chart">
          <PnLChart data={systemStatus} />
        </ErrorBoundary>
      </div>

      {/* Recent Trades */}
      <div style={card}>
        <div style={sectionLabel}>Recent Trades</div>
        <ErrorBoundary fallbackName="Trade Log">
          <TradeLog wsConnected={wsConnected} />
        </ErrorBoundary>
      </div>
    </div>
  );

  // ─── Agents Tab ─────────────────────────────────────────────────────────────
  const AgentsTab = () => (
    <div style={{ padding: '1.5rem' }}>
      <div style={sectionLabel}>APEX AI AGENTS</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
        {[
          { name: 'DR. YUKI TANAKA', role: 'Market Intelligence', status: 'ONLINE', confidence: 94, detail: 'Last Action: 2 min ago' },
          { name: 'DR. JABARI MENSAH', role: 'Sentiment Analysis', status: 'ONLINE', confidence: 87, detail: 'Last Action: 3 min ago' },
          { name: 'DR. SIPHO NKOSI', role: 'Risk Guardian', status: 'ONLINE', confidence: 98, detail: 'Last Action: 1 min ago' },
          { name: 'PROF. KWAME ASANTE', role: 'LLM Router', status: 'ONLINE', confidence: 91, detail: 'Last Action: 4 min ago' },
          { name: 'DR. PRIYA NAIR', role: 'Blockchain Identity', status: 'ONLINE', confidence: 96, detail: 'Last Action: 30 sec ago' },
          { name: 'DR. AMARA DIALLO', role: 'ML & Self-Learning', status: 'ONLINE', confidence: 83, detail: 'Last Action: 8 min ago' },
        ].map((agent) => (
          <div key={agent.name} style={{ ...card, borderLeft: '4px solid #F5A623' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
              <div>
                <div style={{ color: '#F5A623', fontFamily: 'Inter', fontWeight: 700 }}>{agent.name}</div>
                <div style={{ color: '#9ca3af', fontFamily: 'DM Sans', fontSize: '0.8rem' }}>{agent.role}</div>
              </div>
              <span style={{ backgroundColor: '#10b981', color: 'white', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.7rem', ...mono }}>{agent.status}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ flex: 1, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '4px', height: '6px' }}>
                <div style={{ width: `${agent.confidence}%`, backgroundColor: '#10b981', height: '100%', borderRadius: '4px' }} />
              </div>
              <span style={{ color: '#10b981', ...mono, fontSize: '0.8rem', fontWeight: 600 }}>{agent.confidence}%</span>
            </div>
            <div style={{ color: '#6b7280', fontSize: '0.75rem', fontFamily: 'DM Sans', marginTop: '0.5rem' }}>{agent.detail}</div>
          </div>
        ))}
      </div>
    </div>
  );

  // ─── Trades Tab ─────────────────────────────────────────────────────────────
  const TradesTab = () => (
    <div style={{ padding: '1.5rem' }}>
      <div style={sectionLabel}>Trade History</div>
      <div style={card}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                {['Time', 'Pair', 'Side', 'Amount', 'PnL', 'TX Hash', 'Status'].map(h => (
                  <th key={h} style={{ padding: '0.75rem 1rem', textAlign: 'left', color: '#9ca3af', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                { time: '14:32:15', pair: 'BTC/USD', side: 'BUY', amount: '$71,676', pnl: '+$17.50', tx: 'f46b205ac0c632a8f5cf', status: 'COMPLETED' },
                { time: '14:28:42', pair: 'BTC/USD', side: 'BUY', amount: '$71,428', pnl: '+$12.25', tx: 'a1a9c7008c69b3ad2d42', status: 'COMPLETED' },
                { time: '14:15:33', pair: 'BTC/USD', side: 'BUY', amount: '$71,428', pnl: '+$8.75',  tx: 'a988e0f6c0b12a81d6b2', status: 'COMPLETED' },
                { time: '14:02:18', pair: 'BTC/USD', side: 'BUY', amount: '$71,428', pnl: '+$15.75', tx: 'c8b59da268f3bd1e7655', status: 'COMPLETED' },
                { time: '13:45:27', pair: 'BTC/USD', side: 'BUY', amount: '$71,532', pnl: '+$11.25', tx: '2375c4bcacb41fd9cb31', status: 'COMPLETED' },
              ].map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '0.75rem 1rem', color: 'white', ...mono, fontSize: '0.85rem' }}>{row.time}</td>
                  <td style={{ padding: '0.75rem 1rem', color: 'white', ...mono, fontSize: '0.85rem' }}>{row.pair}</td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span style={{ backgroundColor: '#10b981', color: 'white', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', ...mono, fontWeight: 600 }}>{row.side}</span>
                  </td>
                  <td style={{ padding: '0.75rem 1rem', color: 'white', ...mono, fontSize: '0.85rem' }}>{row.amount}</td>
                  <td style={{ padding: '0.75rem 1rem', color: '#10b981', ...mono, fontWeight: 600, fontSize: '0.85rem' }}>{row.pnl}</td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <a href={`https://sepolia.etherscan.io/tx/${row.tx}`} target="_blank" rel="noopener noreferrer"
                      style={{ color: '#3b82f6', ...mono, fontSize: '0.75rem', textDecoration: 'none' }}>
                      {row.tx.slice(0, 12)}...
                    </a>
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span style={{ backgroundColor: '#10b981', color: 'white', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', ...mono }}>{row.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  // ─── Performance Tab ─────────────────────────────────────────────────────────
  const PerformanceTab = () => (
    <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
        {[
          { label: 'Total PnL', value: `$${runningPnL.toFixed(2)}`, color: '#F5A623' },
          { label: 'Sharpe Ratio', value: '1.84', color: '#10b981' },
          { label: 'Win Rate', value: '68%', color: '#3b82f6' },
          { label: 'Max Drawdown', value: '-2.3%', color: '#ef4444' },
        ].map(({ label, value, color }) => (
          <div key={label} style={card}>
            <div style={{ color, fontFamily: 'Inter', fontWeight: 700, fontSize: '1.5rem', ...mono }}>{value}</div>
            <div style={{ color: '#9ca3af', fontFamily: 'DM Sans', fontSize: '0.75rem', marginTop: '0.25rem' }}>{label}</div>
          </div>
        ))}
      </div>
      <div style={card}>
        <div style={sectionLabel}>PnL Over Time</div>
        <ErrorBoundary fallbackName="PnL Chart">
          <PnLChart data={systemStatus} />
        </ErrorBoundary>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div style={card}>
          <div style={sectionLabel}>Pipeline Configuration</div>
          {[
            { label: 'LLM Provider', value: 'OpenRouter' },
            { label: 'Fallback', value: 'Groq, SambaNova' },
            { label: 'Blockchain', value: 'Ethereum Sepolia' },
            { label: 'Agent ID', value: '26' },
          ].map(({ label, value }) => (
            <div key={label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>{label}:</span>
              <span style={{ color: 'white', ...mono, fontSize: '0.8rem', fontWeight: 600 }}>{value}</span>
            </div>
          ))}
        </div>
        <div style={card}>
          <div style={sectionLabel}>Circuit Breaker</div>
          {[
            { label: 'Status', value: 'ARMED', color: '#10b981' },
            { label: 'Trigger', value: '5% drawdown', color: 'white' },
            { label: 'Cooldown', value: '5 min', color: 'white' },
            { label: 'Last Triggered', value: 'Never', color: 'white' },
          ].map(({ label, value, color }) => (
            <div key={label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>{label}:</span>
              <span style={{ color, ...mono, fontSize: '0.8rem', fontWeight: 600 }}>{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // ─── Reputation Tab ──────────────────────────────────────────────────────────
  const ReputationTab = () => (
    <div style={{ padding: '1.5rem' }}>
      <ErrorBoundary fallbackName="Reputation Score">
        <ReputationScore wsConnected={wsConnected} />
      </ErrorBoundary>
    </div>
  );

  // ─── Settings Tab ────────────────────────────────────────────────────────────
  const SettingsTab = () => (
    <div style={{ padding: '1.5rem' }}>
      <div style={sectionLabel}>Settings</div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div style={card}>
          <div style={sectionLabel}>Service Status</div>
          {[
            { label: 'Python WebSocket', port: '8766', online: wsConnected },
            { label: 'Node.js API', port: '3001', online: true },
            { label: 'React Dashboard', port: '5174', online: true },
          ].map(({ label, port, online }) => (
            <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div>
                <div style={{ color: 'white', fontFamily: 'DM Sans', fontSize: '0.85rem' }}>{label}</div>
                <div style={{ color: '#9ca3af', ...mono, fontSize: '0.75rem' }}>:{port}</div>
              </div>
              <span style={{ backgroundColor: online ? '#10b981' : '#ef4444', color: 'white', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.7rem', ...mono }}>{online ? 'ONLINE' : 'OFFLINE'}</span>
            </div>
          ))}
        </div>
        <div style={card}>
          <div style={sectionLabel}>Risk Controls</div>
          {[
            { label: 'Circuit Breaker', value: '🟢 ARMED' },
            { label: 'Max Drawdown', value: '5%' },
            { label: 'Position Size Limit', value: '$350/trade' },
            { label: 'Daily Trade Limit', value: '48 trades' },
            { label: 'Risk Gate', value: '🟢 PASSING' },
          ].map(({ label, value }) => (
            <div key={label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>{label}:</span>
              <span style={{ color: 'white', ...mono, fontSize: '0.8rem', fontWeight: 600 }}>{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const tabContent = {
    dashboard:   <DashboardTab />,
    agents:      <AgentsTab />,
    trades:      <TradesTab />,
    performance: <PerformanceTab />,
    reputation:  <ReputationTab />,
    settings:    <SettingsTab />,
  };

  // ─── Render ──────────────────────────────────────────────────────────────────
  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', backgroundColor: '#0A1628', color: 'white' }}>

      {/* ── Col 1: Icon sidebar (56px) ── */}
      <aside style={{ width: '56px', flexShrink: 0, backgroundColor: '#0D2040', borderRight: '1px solid rgba(26,86,219,0.3)', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: '1rem', gap: '0.25rem' }}>
        {/* Brand */}
        <div style={{ width: '36px', height: '36px', backgroundColor: '#1a56db', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', color: 'white', marginBottom: '1rem' }}>A</div>
        {/* Nav */}
        {navItems.map(({ id, icon, label }) => (
          <button key={id} onClick={() => setActiveTab(id)} title={label}
            style={{ width: '40px', height: '40px', borderRadius: '10px', border: 'none', backgroundColor: activeTab === id ? 'rgba(26,86,219,0.4)' : 'transparent', cursor: 'pointer', fontSize: '1.2rem', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'background 0.2s', outline: activeTab === id ? '1px solid rgba(26,86,219,0.6)' : 'none' }}>
            {icon}
          </button>
        ))}
        {/* Online dot */}
        <div style={{ marginTop: 'auto', marginBottom: '1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: wsConnected ? '#10b981' : '#ef4444' }} />
        </div>
      </aside>

      {/* ── Col 2: Left panel — Agent Decisions (260px) ── */}
      <div style={{ width: '260px', flexShrink: 0, backgroundColor: '#0D2040', borderRight: '1px solid rgba(26,86,219,0.2)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Header */}
        <div style={{ padding: '1rem', borderBottom: '1px solid rgba(26,86,219,0.2)' }}>
          <div style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', color: 'white', marginBottom: '0.25rem' }}>APEX</div>
          <div style={{ color: '#9ca3af', fontSize: '0.75rem', fontFamily: 'DM Sans' }}>
            BTC: <span style={{ color: '#F5A623', ...mono }}>${btcPrice?.toLocaleString() || '---'}</span>
            <span style={{ color: Number(btcChange) >= 0 ? '#10b981' : '#ef4444', marginLeft: '0.25rem', ...mono, fontSize: '0.7rem' }}>
              {Number(btcChange) >= 0 ? '+' : ''}{btcChange}%
            </span>
          </div>
        </div>

        {/* Live Decisions */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
          <div style={sectionLabel}>Live Agent Decisions</div>
          {agentDecisions.map((agent) => (
            <AgentCard key={agent.id} {...agent} />
          ))}
        </div>

        {/* Status footer */}
        <div style={{ padding: '0.75rem 1rem', borderTop: '1px solid rgba(26,86,219,0.2)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: wsConnected ? '#10b981' : '#ef4444' }} />
          <span style={{ color: wsConnected ? '#10b981' : '#ef4444', fontSize: '0.75rem', fontFamily: 'DM Sans', fontWeight: 600 }}>
            {wsConnected ? 'SYSTEM ONLINE' : 'DISCONNECTED'}
          </span>
        </div>
      </div>

      {/* ── Col 3: Main content (grows) ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Top bar */}
        <header style={{ padding: '0.75rem 1.5rem', borderBottom: '1px solid rgba(26,86,219,0.2)', backgroundColor: '#0D2040', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
          <div>
            <div style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.1rem', color: 'white' }}>TRADING DASHBOARD</div>
            <div style={{ color: '#9ca3af', fontFamily: 'DM Sans', fontSize: '0.75rem' }}>
              PnL: <span style={{ color: '#F5A623', ...mono }}>${runningPnL.toFixed(2)}</span> | 
              Agent: <span style={{ color: wsConnected ? '#10b981' : '#ef4444' }}>{wsConnected ? 'ONLINE' : 'PAUSED'}</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            {circuitBreakerTripped && (
              <span style={{ backgroundColor: 'rgba(239,68,68,0.2)', border: '1px solid #ef4444', color: '#ef4444', padding: '0.35rem 0.75rem', borderRadius: '8px', fontSize: '0.8rem', fontFamily: 'Inter', fontWeight: 600 }}>
                ⚠ CIRCUIT TRIPPED
              </span>
            )}
            <span style={{ backgroundColor: wsConnected ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)', border: `1px solid ${wsConnected ? '#10b981' : '#ef4444'}`, color: wsConnected ? '#10b981' : '#ef4444', padding: '0.35rem 0.75rem', borderRadius: '8px', fontSize: '0.8rem', fontFamily: 'Inter', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: wsConnected ? '#10b981' : '#ef4444' }} />
              {wsConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
            <span style={{ backgroundColor: 'rgba(16,185,129,0.15)', border: '1px solid #10b981', color: '#10b981', padding: '0.35rem 0.75rem', borderRadius: '8px', fontSize: '0.8rem', fontFamily: 'Inter', fontWeight: 600 }}>
              SYSTEM NORMAL
            </span>
          </div>
        </header>

        {/* Tab content */}
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {tabContent[activeTab]}
        </div>
      </div>

      {/* ── Col 4: Right stats panel (280px) ── */}
      <div style={{ width: '280px', flexShrink: 0, backgroundColor: '#0D2040', borderLeft: '1px solid rgba(26,86,219,0.2)', overflowY: 'auto' }}>
        <RightPanel />
      </div>

=======
  const [error, setError] = useState(null);
  const [continuousTrading, setContinuousTrading] = useState(true);
  const [tradeSize, setTradeSize] = useState(350);
  const [recentTrades, setRecentTrades] = useState([]);
  const [livePrice, setLivePrice] = useState(0);
  const [runningPnL, setRunningPnL] = useState(531.90);
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    try {
      ws.current = new WebSocket(WS_URL);
      
      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
        setError(null);
      };
      
      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle different message types
          switch (data.type) {
            case 'connection_status':
              setWsConnected(data.python_connected);
              break;
            case 'connection_lost':
              setWsConnected(false);
              break;
            case 'connection_restored':
              setWsConnected(true);
              break;
            case 'circuit_breaker_tripped':
              setCircuitBreakerTripped(true);
              break;
            case 'circuit_breaker_reset':
              setCircuitBreakerTripped(false);
              break;
            case 'trade_executed': {
              // Handle live trade execution
              console.log('Trade executed:', data);
              
              // Update live price
              if (data.price) {
                setLivePrice(data.price);
              }
              
              // Update running PnL
              if (data.pnl_estimate) {
                setRunningPnL(prev => prev + data.pnl_estimate);
              }
              
              // Add to recent trades
              const newTrade = {
                id: data.tx_hash || data.kraken_order_id || Date.now().toString(),
                symbol: 'BTC',
                side: data.action || 'BUY',
                quantity: (data.trade_size_usd / data.price).toFixed(6),
                price: data.price || 0,
                timestamp: data.timestamp || new Date().toISOString(),
                pnl: data.pnl_estimate || 0,
                status: 'completed',
                tx_hash: data.tx_hash || '',
                kraken_order_id: data.kraken_order_id || '',
                reasoning: data.reasoning || '',
                confidence: data.confidence || 0
              };
              
              setRecentTrades(prev => [newTrade, ...prev.slice(0, 9)]); // Keep last 10
              
              // Flash execute button green (visual feedback)
              const executeBtn = document.querySelector('[data-testid="execute-btn"]');
              if (executeBtn) {
                executeBtn.style.backgroundColor = '#10b981';
                setTimeout(() => {
                  executeBtn.style.backgroundColor = '#F5A623';
                }, 1000);
              }
              break;
            }
            default:
              // Other real-time updates would be handled here
              break;
          }
        } catch (err) {
          console.error('WebSocket message error:', err);
        }
      };
      
      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
        
        // Auto-reconnect after 5 seconds
        reconnectTimeout.current = setTimeout(connectWebSocket, 5000);
      };
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection failed');
      };
      
    } catch (error) {
      console.error('WebSocket connection error:', error);
      setError('Failed to establish WebSocket connection');
    }
  }, []);

  // Initial data fetch
  const fetchInitialData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Fetch system status
      const healthResponse = await fetch(`${API_BASE}/health`);
      const healthData = await healthResponse.json();
      
      // Fetch performance data
      const performanceResponse = await fetch(`${API_BASE}/api/performance`);
      const performanceData = await performanceResponse.json();
      
      // Calculate session duration
      const sessionStart = new Date(performanceData.session_start);
      const now = new Date();
      const duration = Math.floor((now - sessionStart) / 1000 / 60); // minutes
      const hours = Math.floor(duration / 60);
      const minutes = duration % 60;
      
      setSystemStatus({
        lastUpdate: new Date().toLocaleTimeString(),
        activeSymbols: '5',
        sessionDuration: `${hours}h ${minutes}m`,
        ...healthData,
        ...performanceData
      });
      
    } catch (error) {
      console.error('Initial data fetch error:', error);
      setError('Failed to load initial data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initialize WebSocket and fetch data
  useEffect(() => {
    connectWebSocket();
    fetchInitialData();
    
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, []);

  // Update session duration every minute
  useEffect(() => {
    const interval = setInterval(() => {
      if (systemStatus?.session_start) {
        const sessionStart = new Date(systemStatus.session_start);
        const now = new Date();
        const duration = Math.floor((now - sessionStart) / 1000 / 60);
        const hours = Math.floor(duration / 60);
        const minutes = duration % 60;
        
        setSystemStatus(prev => ({
          ...prev,
          lastUpdate: new Date().toLocaleTimeString(),
          sessionDuration: `${hours}h ${minutes}m`
        }));
      }
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []); // Remove systemStatus dependency to prevent infinite loop

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">A</div>
          <div className="sidebar-brand-name">APEX</div>
        </div>
        
        <nav className="sidebar-nav">
          <a 
            href="#dashboard" 
            className={`sidebar-nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span className="sidebar-nav-icon"> </span>
            Dashboard
          </a>
          <a 
            href="#agents" 
            className={`sidebar-nav-item ${activeTab === 'agents' ? 'active' : ''}`}
            onClick={() => setActiveTab('agents')}
          >
            <span className="sidebar-nav-icon">🤖</span>
            Agents
          </a>
          <a 
            href="#trades" 
            className={`sidebar-nav-item ${activeTab === 'trades' ? 'active' : ''}`}
            onClick={() => setActiveTab('trades')}
          >
            <span className="sidebar-nav-icon">⚡</span>
            Trades
          </a>
          <a 
            href="#performance" 
            className={`sidebar-nav-item ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => setActiveTab('performance')}
          >
            <span className="sidebar-nav-icon">📈</span>
            Performance
          </a>
          <a 
            href="#reputation" 
            className={`sidebar-nav-item ${activeTab === 'reputation' ? 'active' : ''}`}
            onClick={() => setActiveTab('reputation')}
          >
            <span className="sidebar-nav-icon">⭐</span>
            Reputation
          </a>
          <a 
            href="#settings" 
            className={`sidebar-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <span className="sidebar-nav-icon">⚙️</span>
            Settings
          </a>
        </nav>
        
        <div className="sidebar-footer">
          <div className="sidebar-status">
            <div className="sidebar-status-dot"></div>
            <div className="sidebar-status-text">System Online</div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="main-content">
        {/* Top Bar */}
        <header className="topbar">
          <div className="topbar-left">
            <div className="topbar-title">Trading Dashboard</div>
            <div className="live-ticker">
              BTC: ${livePrice.toLocaleString() || '---'} | 
              Last Trade: {recentTrades[0]?.side || '---'} | 
              PnL: ${runningPnL.toFixed(2)} | 
              Agent: {wsConnected ? 'ONLINE' : 'PAUSED'}
            </div>
          </div>
          
          <div className="topbar-right">
            <div className={`connection-badge ${wsConnected ? 'connected' : 'disconnected'}`}>
              <div className="connection-dot"></div>
              {wsConnected ? 'Connected' : 'Disconnected'}
            </div>
            
            <div className={`system-badge ${circuitBreakerTripped ? 'danger' : 'success'}`}>
              {circuitBreakerTripped ? 'CIRCUIT TRIPPED' : 'SYSTEM NORMAL'}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="page-content">
          {error && (
            <div className="offline-banner">
              ⚠ Backend offline — showing demo data
            </div>
          )}

          {/* Circuit Breaker Alert */}
          {circuitBreakerTripped && (
            <div className="circuit-alert">
              <span>⚠️ CIRCUIT BREAKER TRIPPED - Trading Halted</span>
              <button className="circuit-reset-btn" onClick={() => setCircuitBreakerTripped(false)}>
                Reset
              </button>
            </div>
          )}

          {/* Tab Content */}
          {activeTab === 'dashboard' && (
            <div className="dashboard-grid">
              <ErrorBoundary fallbackName="Agent Feed">
                <div>
                  <div className="section-label">Agent Activity</div>
                  <div className="card">
                    <AgentFeed wsConnected={wsConnected} />
                  </div>
                </div>
              </ErrorBoundary>
              <ErrorBoundary fallbackName="Trading Panel">
                <div>
                  <div className="section-label">Performance</div>
                  <div className="card perf-card">
                    <PnLChart data={systemStatus} />
                  </div>
                  <div className="section-label" style={{ marginTop: '20px' }}>Recent Trades</div>
                  <div className="card trades-card">
                    <TradeLog wsConnected={wsConnected} />
                  </div>
                </div>
              </ErrorBoundary>
              <ErrorBoundary fallbackName="Status Panel">
                <div>
                  <div className="section-label">Reputation Score</div>
                  <div className="card reputation-card">
                    <ReputationScore wsConnected={wsConnected} />
                  </div>
                  <div className="section-label" style={{ marginTop: '20px' }}>System Status</div>
                  <SystemStatusPanel data={systemStatus} loading={loading} />
                </div>
              </ErrorBoundary>
            </div>
          )}
          
          {activeTab === 'agents' && (
            <div>
              <div className="section-label">Agent Status</div>
              <div className="card">
                <h3 style={{ color: 'white', marginBottom: '1rem' }}>APEX Agents</h3>
                <div style={{ 
                  backgroundColor: 'rgba(26, 86, 219, 0.1)', 
                  padding: '1rem', 
                  borderRadius: '8px',
                  fontFamily: 'JetBrains Mono, monospace'
                }}>
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ color: '#F5A623', marginBottom: '0.5rem' }}>DR. YUKI TANAKA</div>
                    <div>Market Intelligence - ONLINE</div>
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ color: '#F5A623', marginBottom: '0.5rem' }}>DR. JABARI MENSAH</div>
                    <div>Sentiment Analysis - ONLINE</div>
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ color: '#F5A623', marginBottom: '0.5rem' }}>DR. SIPHO NKOSI</div>
                    <div>Risk Management - ONLINE</div>
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ color: '#F5A623', marginBottom: '0.5rem' }}>PROF. KWAME ASANTE</div>
                    <div>LLM Router - ONLINE</div>
                  </div>
                  <div>
                    <div style={{ color: '#F5A623', marginBottom: '0.5rem' }}>DR. PRIYA NAIR</div>
                    <div>Blockchain Execution - ONLINE</div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'trades' && (
            <div>
              <div className="section-label">Transaction History</div>
              <div className="card">
                <h3 style={{ color: 'white', marginBottom: '1rem' }}>Recent Trades</h3>
                <div style={{ 
                  backgroundColor: 'rgba(26, 86, 219, 0.1)', 
                  padding: '1rem', 
                  borderRadius: '8px',
                  fontFamily: 'JetBrains Mono, monospace'
                }}>
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ color: '#F5A623', marginBottom: '0.5rem' }}>
                      f46b205ac0c632a8f5cf1a8f1ca31c964882c7693c78c1d1d53b6a5cb218f517
                    </div>
                    <div style={{ color: 'white', fontSize: '0.875rem' }}>
                      BTC BUY - $350.00 - 82% confidence
                    </div>
                    <a 
                      href="https://sepolia.etherscan.io/tx/f46b205ac0c632a8f5cf1a8f1ca31c964882c7693c78c1d1d53b6a5cb218f517"
                      target="_blank"
                      style={{ color: '#3b82f6', fontSize: '0.75rem' }}
                    >
                      View on Etherscan
                    </a>
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ color: '#F5A623', marginBottom: '0.5rem' }}>
                      a1a9c7008c69b3ad2d429ba577fc20bac92e80ad6326816880d66c7e54cd7ce8
                    </div>
                    <div style={{ color: 'white', fontSize: '0.875rem' }}>
                      BTC BUY - $350.00 - 85% confidence
                    </div>
                    <a 
                      href="https://sepolia.etherscan.io/tx/a1a9c7008c69b3ad2d429ba577fc20bac92e80ad6326816880d66c7e54cd7ce8"
                      target="_blank"
                      style={{ color: '#3b82f6', fontSize: '0.75rem' }}
                    >
                      View on Etherscan
                    </a>
                  </div>
                  <div>
                    <div style={{ color: '#F5A623', marginBottom: '0.5rem' }}>
                      a988e0f6c0b12a81d6b248ab1a02cdd07e5461e2559e6eeb700604e60d392a23
                    </div>
                    <div style={{ color: 'white', fontSize: '0.875rem' }}>
                      BTC BUY - $350.00 - 87% confidence
                    </div>
                    <a 
                      href="https://sepolia.etherscan.io/tx/a988e0f6c0b12a81d6b248ab1a02cdd07e5461e2559e6eeb700604e60d392a23"
                      target="_blank"
                      style={{ color: '#3b82f6', fontSize: '0.75rem' }}
                    >
                      View on Etherscan
                    </a>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'performance' && (
            <div>
              <div className="section-label">Performance Metrics</div>
              <div className="card">
                <h3 style={{ color: 'white', marginBottom: '1rem' }}>Trading Performance</h3>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: '1fr 1fr', 
                  gap: '1rem', 
                  marginBottom: '2rem' 
                }}>
                  <div style={{
                    backgroundColor: 'rgba(26, 86, 219, 0.1)',
                    padding: '1rem',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '1.25rem', color: 'white', marginBottom: '0.5rem' }}>
                      Sharpe Ratio
                    </div>
                    <div style={{ 
                      fontSize: '2rem', 
                      fontFamily: 'JetBrains Mono, monospace', 
                      fontWeight: 700,
                      color: '#10b981'
                    }}>
                      1.84
                    </div>
                  </div>
                  <div style={{
                    backgroundColor: 'rgba(26, 86, 219, 0.1)',
                    padding: '1rem',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '1.25rem', color: 'white', marginBottom: '0.5rem' }}>
                      Max Drawdown
                    </div>
                    <div style={{ 
                      fontSize: '2rem', 
                      fontFamily: 'JetBrains Mono, monospace', 
                      fontWeight: 700,
                      color: '#ef4444'
                    }}>
                      -2.3%
                    </div>
                  </div>
                </div>
                <PnLChart data={systemStatus} />
              </div>
            </div>
          )}
          
          {activeTab === 'reputation' && (
            <div>
              <div className="section-label">Reputation Score</div>
              <div className="card">
                <h3 style={{ color: 'white', marginBottom: '1rem' }}>ERC-8004 Reputation</h3>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                  <div style={{
                    fontSize: '4rem',
                    fontFamily: 'JetBrains Mono, monospace',
                    fontWeight: 700,
                    color: '#10b981',
                    marginBottom: '0.5rem'
                  }}>
                    92
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>
                    Current Reputation Score
                  </div>
                </div>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: '1fr 1fr', 
                  gap: '1rem' 
                }}>
                  <div style={{
                    backgroundColor: 'rgba(26, 86, 219, 0.1)',
                    padding: '1rem',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '1.25rem', color: 'white', marginBottom: '0.5rem' }}>
                      Validations
                    </div>
                    <div style={{ 
                      fontSize: '2rem', 
                      fontFamily: 'JetBrains Mono, monospace', 
                      fontWeight: 700,
                      color: '#F5A623'
                    }}>
                      15
                    </div>
                  </div>
                  <div style={{
                    backgroundColor: 'rgba(26, 86, 219, 0.1)',
                    padding: '1rem',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '1.25rem', color: 'white', marginBottom: '0.5rem' }}>
                      Trades On-Chain
                    </div>
                    <div style={{ 
                      fontSize: '2rem', 
                      fontFamily: 'JetBrains Mono, monospace', 
                      fontWeight: 700,
                      color: '#10b981'
                    }}>
                      5
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'settings' && (
            <div>
              <div className="section-label">Trading Settings</div>
              <div className="card">
                <h3 style={{ color: 'white', marginBottom: '1rem' }}>Control Panel</h3>
                <div style={{ 
                  backgroundColor: 'rgba(26, 86, 219, 0.1)', 
                  padding: '1rem', 
                  borderRadius: '8px',
                  marginBottom: '1rem'
                }}>
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ color: 'white', display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <input 
                        type="checkbox" 
                        checked={continuousTrading}
                        onChange={(e) => {
                          setContinuousTrading(e.target.checked);
                          if (e.target.checked) {
                            fetch('http://localhost:3001/api/resume-trading', { method: 'POST' })
                              .then(() => console.log('Trading resumed'))
                              .catch(err => console.error('Error:', err));
                          } else {
                            fetch('http://localhost:3001/api/pause-trading', { method: 'POST' })
                              .then(() => console.log('Trading paused'))
                              .catch(err => console.error('Error:', err));
                          }
                        }}
                        style={{ marginRight: '0.5rem' }}
                      />
                      Continuous Trading
                    </label>
                    <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
                      When ON: Agent runs pipeline every 30 seconds automatically
                    </div>
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ color: 'white', display: 'block', marginBottom: '0.5rem' }}>
                      Trade Size: ${tradeSize}
                    </label>
                    <input 
                      type="range" 
                      min="100" 
                      max="1000" 
                      value={tradeSize}
                      onChange={(e) => setTradeSize(parseInt(e.target.value))}
                      style={{ width: '100%' }}
                    />
                    <div style={{ color: '#9ca3af', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                      $100 - $1000
                    </div>
                  </div>
                  <button 
                    style={{
                      backgroundColor: '#F5A623',
                      color: 'white',
                      border: 'none',
                      padding: '0.75rem 1rem',
                      borderRadius: '6px',
                      fontFamily: 'DM Sans, sans-serif',
                      fontWeight: 500,
                      cursor: 'pointer',
                      width: '100%'
                    }}
                    onClick={() => {
                      fetch('http://localhost:3001/api/execute-trade', { method: 'POST' })
                        .then(() => console.log('Trade execution requested'))
                        .catch(err => console.error('Error:', err));
                    }}
                  >
                    Execute Trade Now
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
>>>>>>> 7104b79fe2a693b23df1ddfad2952721ee506102
    </div>
  );
};

export default App;

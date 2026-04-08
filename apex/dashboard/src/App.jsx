/**
 * APEX Dashboard - Main React Application
 * 
 * ENGR. FATIMA AL-RASHID: VP of Interface at APEX
 * Background: Moroccan-French. W3C working group contributor. Built trading dashboards for three Tier-1 banks.
 * Standard: "The interface is the system's face to the world. If a judge cannot understand what is happening in 10 seconds, we have failed presentation."
 * 
 * Complete production-ready React dashboard with WebSocket real-time updates and responsive design
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { AgentFeed, ReputationScore, TradeLog, PnLChart } from './components';

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

    return this.props.children;
  }
}

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
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const [wsConnected, setWsConnected] = useState(false);
  const [circuitBreakerTripped, setCircuitBreakerTripped] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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
          <a href="#dashboard" className="sidebar-nav-item active">
            <span className="sidebar-nav-icon">📊</span>
            Dashboard
          </a>
          <a href="#agents" className="sidebar-nav-item">
            <span className="sidebar-nav-icon">🤖</span>
            Agents
          </a>
          <a href="#trades" className="sidebar-nav-item">
            <span className="sidebar-nav-icon">💱</span>
            Trades
          </a>
          <a href="#reputation" className="sidebar-nav-item">
            <span className="sidebar-nav-icon">⭐</span>
            Reputation
          </a>
          <a href="#settings" className="sidebar-nav-item">
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

          {/* Dashboard Grid */}
          <div className="dashboard-grid">
            {/* Column 1: Agent Feed */}
            <ErrorBoundary fallbackName="Agent Feed">
              <div>
                <div className="section-label">Agent Activity</div>
                {loading ? (
                  <div className="card">
                    <div className="skeleton" style={{ height: '200px' }}></div>
                  </div>
                ) : (
                  <div className="card">
                    <div className="card-header">
                      <h3 className="card-title">Live Agent Decisions</h3>
                    </div>
                    <AgentFeed wsConnected={wsConnected} />
                  </div>
                )}
              </div>
            </ErrorBoundary>

            {/* Column 2: Performance & Trades */}
            <ErrorBoundary fallbackName="Trading Panel">
              <div>
                <div className="section-label">Performance</div>
                {loading ? (
                  <div className="card perf-card">
                    <div className="skeleton" style={{ height: '300px' }}></div>
                  </div>
                ) : (
                  <div className="card perf-card">
                    <PnLChart data={systemStatus} />
                  </div>
                )}
                
                <div className="section-label" style={{ marginTop: '20px' }}>Recent Trades</div>
                {loading ? (
                  <div className="card trades-card">
                    <div className="skeleton" style={{ height: '250px' }}></div>
                  </div>
                ) : (
                  <div className="card trades-card">
                    <TradeLog wsConnected={wsConnected} />
                  </div>
                )}
              </div>
            </ErrorBoundary>

            {/* Column 3: Reputation & Status */}
            <ErrorBoundary fallbackName="Status Panel">
              <div>
                <div className="section-label">Reputation Score</div>
                {loading ? (
                  <div className="card reputation-card">
                    <div className="skeleton" style={{ height: '200px' }}></div>
                  </div>
                ) : (
                  <div className="card reputation-card">
                    <ReputationScore wsConnected={wsConnected} />
                  </div>
                )}
                
                <div className="section-label" style={{ marginTop: '20px' }}>System Status</div>
                <SystemStatusPanel data={systemStatus} loading={loading} />
              </div>
            </ErrorBoundary>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;

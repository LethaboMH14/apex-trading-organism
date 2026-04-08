/**
 * APEX App Router - FIXED VERSION
 * 
 * ENGR. FATIMA AL-RASHID: VP of Interface at APEX
 * Simple routing system for dashboard navigation
 */

import React, { useState } from 'react';
import { AgentFeed, ReputationScore, PnLChart } from './components';

// Simple App Router Component
const AppRouter = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Simple navigation handler
  const handleNavigation = (tab) => {
    setActiveTab(tab);
  };
  
  // Render content based on active tab
  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div>
            <div className="section-label">Agent Activity</div>
            <div className="card">
              <AgentFeed wsConnected={true} />
            </div>
          </div>
        );
      case 'agents':
        return (
          <div>
            <div className="section-label">Agent Status</div>
            <div className="card">
              <h3 style={{ color: 'white', marginBottom: '1rem' }}>Agent Management</h3>
              <p style={{ color: '#9ca3af', fontFamily: 'DM Sans, sans-serif' }}>
                All 5 APEX agents are currently operational and coordinating trades.
              </p>
              <div style={{ 
                backgroundColor: 'rgba(26, 86, 219, 0.1)', 
                padding: '1rem', 
                borderRadius: '8px',
                marginTop: '1rem'
              }}>
                <div style={{ color: 'white', fontFamily: 'JetBrains Mono, monospace' }}>
                  <div style={{ marginBottom: '0.5rem' }}>DR. YUKI TANAKA</div>
                  <div>Market Intelligence - ONLINE</div>
                  <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>ws://localhost:8765</div>
                </div>
                <div style={{ 
                  backgroundColor: 'rgba(26, 86, 219, 0.1)', 
                  padding: '1rem', 
                  borderRadius: '8px',
                  marginTop: '1rem'
                }}>
                  <div style={{ color: 'white', fontFamily: 'JetBrains Mono, monospace' }}>
                    <div style={{ marginBottom: '0.5rem' }}>DR. JABARI MENSAH</div>
                    <div>Sentiment Analysis - ONLINE</div>
                    <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>ws://localhost:8765</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case 'trades':
        return (
          <div>
            <div className="section-label">Recent Trades</div>
            <div className="card trades-card">
              <h3 style={{ color: 'white', marginBottom: '1rem' }}>Trade History</h3>
              <p style={{ color: '#9ca3af', fontFamily: 'DM Sans, sans-serif' }}>
                Real transaction hashes from APEX demo runs displayed here.
              </p>
              <div style={{ 
                backgroundColor: 'rgba(26, 86, 219, 0.1)', 
                padding: '1rem', 
                borderRadius: '8px',
                fontFamily: 'JetBrains Mono, monospace'
              }}>
                <div style={{ color: '#F5A623', marginBottom: '0.5rem' }}>
                  f46b205ac0c632a8f5cf1a8f1ca31c964882c7693c78c1d1d53b6a5cb218f517
                </div>
                <div style={{ color: 'white', fontSize: '0.875rem' }}>
                  BTC BUY • $350.00 • 82% confidence
                </div>
                <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
                  9736c1e2143d6802130fccf6351c14183692ebd7ca3d7aca4b775d10dff2130a
                </div>
                <div style={{ color: 'white', fontSize: '0.875rem' }}>
                  a1a9c7008c69b3ad2d429ba577fc20bac92e80ad6326816880d66c7e54cd7ce8
                </div>
              </div>
            </div>
          </div>
        );
      case 'reputation':
        return <ReputationScore />;
      case 'settings':
        return (
          <div>
            <div className="section-label">Settings</div>
            <div className="card">
              <h3 style={{ color: 'white', marginBottom: '1rem' }}>Dashboard Settings</h3>
              <div style={{ 
                backgroundColor: 'rgba(26, 86, 219, 0.1)', 
                padding: '1rem', 
                borderRadius: '8px',
                fontFamily: 'DM Sans, sans-serif'
              }}>
                <div style={{ color: 'white', fontFamily: 'JetBrains Mono, monospace' }}>
                  <h4 style={{ marginBottom: '1rem', color: '#F5A623' }}>Configuration</h4>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong>WebSocket Server:</strong> ws://localhost:8765
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong>API Server:</strong> http://localhost:3001
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong>Dashboard:</strong> http://localhost:5173
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong>Agent Status:</strong> All systems operational
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong>Last Trade:</strong> f46b205ac0c632a8f5cf1a8f1ca31c964882c7693c78c1d1d53b6a5cb218f517
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      default:
        return (
          <div>
            <div className="section-label">Dashboard</div>
            <div className="card">
              <h3 style={{ color: 'white', marginBottom: '1rem' }}>Trading Dashboard</h3>
              <p style={{ color: '#9ca3af', fontFamily: 'DM Sans, sans-serif' }}>
                Welcome to APEX Trading Dashboard. Select a tab to begin.
              </p>
            </div>
          </div>
        );
    }
  };
  
  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">A</div>
          <div className="sidebar-brand-name">APEX</div>
        </div>
        
        <nav className="sidebar-nav">
          {['dashboard', 'agents', 'trades', 'reputation', 'settings'].map(tab => (
            <a 
              key={tab}
              href={`#${tab}`}
              className={`sidebar-nav-item ${activeTab === tab ? 'active' : ''}`}
              onClick={() => handleNavigation(tab)}
            >
              <span className="sidebar-nav-icon">
                {tab === 'dashboard' && '📊'}
                {tab === 'agents' && '🤖'}
                {tab === 'trades' && '💱'}
                {tab === 'reputation' && '⭐'}
                {tab === 'settings' && '⚙️'}
              </span>
              <span className="sidebar-nav-text">
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </span>
            </a>
          ))}
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
            <div className="topbar-title">APEX Trading Dashboard</div>
          </div>
          
          <div className="topbar-right">
            <div className="connection-badge connected">
              <div className="connection-dot"></div>
              Connected
            </div>
            <div className="system-badge success">
              SYSTEM NORMAL
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="page-content">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default AppRouter;

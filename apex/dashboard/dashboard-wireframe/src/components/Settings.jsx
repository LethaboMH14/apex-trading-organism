/**
 * APEX Settings Component
 * Full settings interface with configuration options
 */

import React, { useState } from 'react';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    // General Settings
    wsUrl: 'ws://localhost:3002',
    apiUrl: 'http://localhost:3001',
    theme: 'dark',
    language: 'en',
    
    // Trading Settings
    autoTrading: true,
    maxTradeSize: 10000,
    riskLevel: 'medium',
    stopLoss: 5,
    takeProfit: 15,
    
    // Notification Settings
    emailNotifications: true,
    pushNotifications: true,
    tradeAlerts: true,
    systemAlerts: true,
    
    // Security Settings
    twoFactorAuth: false,
    sessionTimeout: 30,
    apiAccess: false,
    
    // Agent Settings
    agentTimeout: 60,
    maxConcurrentAgents: 5,
    agentLogLevel: 'info'
  });

  const [showSaveConfirm, setShowSaveConfirm] = useState(false);

  const handleSettingChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const saveSettings = () => {
    // In a real app, this would save to backend
    console.log('Saving settings:', settings);
    setShowSaveConfirm(true);
    setTimeout(() => setShowSaveConfirm(false), 3000);
  };

  const resetSettings = () => {
    // Reset to defaults
    setSettings({
      wsUrl: 'ws://localhost:3002',
      apiUrl: 'http://localhost:3001',
      theme: 'dark',
      language: 'en',
      autoTrading: true,
      maxTradeSize: 10000,
      riskLevel: 'medium',
      stopLoss: 5,
      takeProfit: 15,
      emailNotifications: true,
      pushNotifications: true,
      tradeAlerts: true,
      systemAlerts: true,
      twoFactorAuth: false,
      sessionTimeout: 30,
      apiAccess: false,
      agentTimeout: 60,
      maxConcurrentAgents: 5,
      agentLogLevel: 'info'
    });
  };

  const tabs = [
    { id: 'general', label: 'General', icon: '⚙️' },
    { id: 'trading', label: 'Trading', icon: '💱' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'security', label: 'Security', icon: '🔒' },
    { id: 'agents', label: 'Agents', icon: '🤖' }
  ];

  return (
    <div className="page">
      
      {/* Header */}
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={resetSettings}
            className="btn-secondary"
          >
            Reset to Defaults
          </button>
          <button
            onClick={saveSettings}
            className="btn-primary"
          >
            Save Settings
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="settings-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`settings-tab ${activeTab === tab.id ? 'active' : ''}`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="settings-grid">
        
        {/* General Settings */}
        {activeTab === 'general' && (
          <div className="settings-section">
            <h3 className="settings-section-title">API Configuration</h3>
            
            <div className="form-group">
              <label className="form-label">WebSocket URL</label>
              <input 
                type="text" 
                value={settings.wsUrl}
                onChange={(e) => handleSettingChange('general', 'wsUrl', e.target.value)}
                className="form-input"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">API Base URL</label>
              <input 
                type="text" 
                value={settings.apiUrl}
                onChange={(e) => handleSettingChange('general', 'apiUrl', e.target.value)}
                className="form-input"
              />
            </div>
            
            <div className="settings-section">
              <h3 className="settings-section-title">Appearance</h3>
              
              <div className="form-group">
                <label className="form-label">Theme</label>
                <select 
                  value={settings.theme}
                  onChange={(e) => handleSettingChange('general', 'theme', e.target.value)}
                  className="form-select"
                >
                  <option value="dark">Dark</option>
                  <option value="light">Light</option>
                  <option value="auto">Auto</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">Language</label>
                <select 
                  value={settings.language}
                  onChange={(e) => handleSettingChange('general', 'language', e.target.value)}
                  className="form-select"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Trading Settings */}
        {activeTab === 'trading' && (
          <div className="settings-section">
            <h3 className="settings-section-title">Trading Configuration</h3>
            
            <div className="form-group">
              <label className="form-label">
                <input 
                  type="checkbox" 
                  checked={settings.autoTrading}
                  onChange={(e) => handleSettingChange('trading', 'autoTrading', e.target.checked)}
                  style={{ marginRight: '8px' }} 
                />
                Enable Auto Trading
              </label>
            </div>
            
            <div className="form-group">
              <label className="form-label">Max Trade Size ($)</label>
              <input 
                type="number" 
                value={settings.maxTradeSize}
                onChange={(e) => handleSettingChange('trading', 'maxTradeSize', parseInt(e.target.value))}
                className="form-input"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Risk Level</label>
              <select 
                value={settings.riskLevel}
                onChange={(e) => handleSettingChange('trading', 'riskLevel', e.target.value)}
                className="form-select"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            
            <div className="settings-section">
              <h3 className="settings-section-title">Risk Management</h3>
              
              <div className="form-group">
                <label className="form-label">Stop Loss (%)</label>
                <input 
                  type="number" 
                  value={settings.stopLoss}
                  onChange={(e) => handleSettingChange('trading', 'stopLoss', parseInt(e.target.value))}
                  className="form-input"
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Take Profit (%)</label>
                <input 
                  type="number" 
                  value={settings.takeProfit}
                  onChange={(e) => handleSettingChange('trading', 'takeProfit', parseInt(e.target.value))}
                  className="form-input"
                />
              </div>
            </div>
          </div>
        )}

        {/* Notification Settings */}
        {activeTab === 'notifications' && (
          <div className="settings-section">
            <h3 className="settings-section-title">Notification Preferences</h3>
            
            <div className="form-group">
              <label className="form-label">
                <input 
                  type="checkbox" 
                  checked={settings.emailNotifications}
                  onChange={(e) => handleSettingChange('notifications', 'emailNotifications', e.target.checked)}
                  style={{ marginRight: '8px' }} 
                />
                Email Notifications
              </label>
            </div>
            
            <div className="form-group">
              <label className="form-label">
                <input 
                  type="checkbox" 
                  checked={settings.pushNotifications}
                  onChange={(e) => handleSettingChange('notifications', 'pushNotifications', e.target.checked)}
                  style={{ marginRight: '8px' }} 
                />
                Push Notifications
              </label>
            </div>
            
            <div className="form-group">
              <label className="form-label">
                <input 
                  type="checkbox" 
                  checked={settings.tradeAlerts}
                  onChange={(e) => handleSettingChange('notifications', 'tradeAlerts', e.target.checked)}
                  style={{ marginRight: '8px' }} 
                />
                Trade Alerts
              </label>
            </div>
            
            <div className="form-group">
              <label className="form-label">
                <input 
                  type="checkbox" 
                  checked={settings.systemAlerts}
                  onChange={(e) => handleSettingChange('notifications', 'systemAlerts', e.target.checked)}
                  style={{ marginRight: '8px' }} 
                />
                System Alerts
              </label>
            </div>
          </div>
        )}

        {/* Security Settings */}
        {activeTab === 'security' && (
          <div className="settings-section">
            <h3 className="settings-section-title">Authentication</h3>
            
            <div className="form-group">
              <label className="form-label">
                <input 
                  type="checkbox" 
                  checked={settings.twoFactorAuth}
                  onChange={(e) => handleSettingChange('security', 'twoFactorAuth', e.target.checked)}
                  style={{ marginRight: '8px' }} 
                />
                Two-Factor Authentication
              </label>
            </div>
            
            <div className="form-group">
              <label className="form-label">Session Timeout (minutes)</label>
              <input 
                type="number" 
                value={settings.sessionTimeout}
                onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value))}
                className="form-input"
              />
            </div>
            
            <div className="settings-section">
              <h3 className="settings-section-title">API Access</h3>
              
              <div className="form-group">
                <label className="form-label">
                  <input 
                    type="checkbox" 
                    checked={settings.apiAccess}
                    onChange={(e) => handleSettingChange('security', 'apiAccess', e.target.checked)}
                    style={{ marginRight: '8px' }} 
                  />
                  Enable API Access
                </label>
              </div>
              
              {settings.apiAccess && (
                <div className="form-group">
                  <label className="form-label">API Key</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input 
                      type="text" 
                      value="sk_live_1234567890abcdef"
                      readOnly
                      className="form-input"
                      style={{ fontFamily: 'monospace', fontSize: '11px' }}
                    />
                    <button className="btn-secondary">
                      Copy
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Agent Settings */}
        {activeTab === 'agents' && (
          <div className="settings-section">
            <h3 className="settings-section-title">Agent Configuration</h3>
            
            <div className="form-group">
              <label className="form-label">Agent Timeout (seconds)</label>
              <input 
                type="number" 
                value={settings.agentTimeout}
                onChange={(e) => handleSettingChange('agents', 'agentTimeout', parseInt(e.target.value))}
                className="form-input"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Max Concurrent Agents</label>
              <input 
                type="number" 
                value={settings.maxConcurrentAgents}
                onChange={(e) => handleSettingChange('agents', 'maxConcurrentAgents', parseInt(e.target.value))}
                className="form-input"
              />
            </div>
            
            <div className="settings-section">
              <h3 className="settings-section-title">Logging</h3>
              
              <div className="form-group">
                <label className="form-label">Agent Log Level</label>
                <select 
                  value={settings.agentLogLevel}
                  onChange={(e) => handleSettingChange('agents', 'agentLogLevel', e.target.value)}
                  className="form-select"
                >
                  <option value="debug">Debug</option>
                  <option value="info">Info</option>
                  <option value="warn">Warning</option>
                  <option value="error">Error</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Save Confirmation */}
      {showSaveConfirm && (
        <div className="alert-banner" style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          backgroundColor: 'var(--green)',
          color: '#000',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: '600',
          zIndex: 1000
        }}>
          ✅ Settings saved successfully!
        </div>
      )}
    </div>
  );
};

export default Settings;

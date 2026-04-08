/**
 * APEX Agent Management Component
 * Full agent management interface with CRUD operations
 */

import React, { useState, useEffect } from 'react';

const AgentManagement = () => {
  const [agents, setAgents] = useState([
    {
      id: 'agent-1',
      name: 'Dr. Zara Okafor',
      role: 'Strategy Orchestrator',
      status: 'active',
      confidence: 92,
      address: '0x1234567890abcdef0123456789abcdef01234567',
      lastActive: '2 minutes ago',
      performance: '+$399.00',
      trades: 47
    },
    {
      id: 'agent-2',
      name: 'Dr. Jabari Mensah',
      role: 'NLP Analyst',
      status: 'analyzing',
      confidence: 78,
      address: '0xabcdef0123456789abcdef0123456789abcdef01',
      lastActive: '5 minutes ago',
      performance: '+$125.50',
      trades: 23
    },
    {
      id: 'agent-3',
      name: 'ENGR. Marcus Oduya',
      role: 'Kraken Execution',
      status: 'executing',
      confidence: 95,
      address: '0x5678901234abcdef5678901234abcdef56789012',
      lastActive: '1 minute ago',
      performance: '+$856.25',
      trades: 89
    },
    {
      id: 'agent-4',
      name: 'Dr. Sipho Nkosi',
      role: 'Risk Management',
      status: 'monitoring',
      confidence: 88,
      address: '0x3456789012abcdef3456789012abcdef34567890',
      lastActive: '3 minutes ago',
      performance: '-$45.75',
      trades: 15
    },
    {
      id: 'agent-5',
      name: 'Dr. Priya Nair',
      role: 'ERC-8004 & On-Chain',
      status: 'learning',
      confidence: 67,
      address: '0x7890123456abcdef7890123456abcdef78901234',
      lastActive: '10 minutes ago',
      performance: '+$234.80',
      trades: 31
    }
  ]);

  const [selectedAgent, setSelectedAgent] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [filter, setFilter] = useState('all');

  const handleAgentAction = (agentId, action) => {
    setAgents(prev => prev.map(agent => {
      if (agent.id === agentId) {
        switch (action) {
          case 'pause':
            return { ...agent, status: 'paused' };
          case 'start':
            return { ...agent, status: 'active' };
          case 'configure':
            setSelectedAgent(agent);
            break;
          case 'delete':
            return null;
          default:
            return agent;
        }
      }
      return agent;
    }).filter(Boolean));
  };

  const filteredAgents = agents.filter(agent => {
    if (filter === 'all') return true;
    return agent.status === filter;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'green';
      case 'executing': return 'green';
      case 'analyzing': return 'gold';
      case 'monitoring': return 'green';
      case 'learning': return 'purple';
      case 'paused': return 'red';
      default: return 'gray';
    }
  };

  return (
    <div className="page">
      
      {/* Header with Controls */}
      <div className="page-header">
        <h1 className="page-title">Agent Management</h1>
        <div style={{ display: 'flex', gap: '12px' }}>
          <select 
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="form-select"
            style={{ width: 'auto' }}
          >
            <option value="all">All Agents</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="learning">Learning</option>
          </select>
          
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary"
          >
            + Add Agent
          </button>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="agents-grid">
        {filteredAgents.map(agent => (
          <div 
            key={agent.id}
            className="agent-mgmt-card"
          >
            {/* Agent Info */}
            <div className="mgmt-top">
              <div>
                <h3 className="mgmt-name">{agent.name}</h3>
                <p className="mgmt-role">{agent.role}</p>
                <p className="mgmt-addr">
                  {agent.address.slice(0, 10)}...{agent.address.slice(-8)}
                </p>
              </div>
              <div className={`online-dot ${getStatusColor(agent.status)}`}></div>
            </div>

            {/* Metrics */}
            <div className="mgmt-stats">
              <div className="mgmt-stat">
                <span className="mgmt-stat-label">Performance</span>
                <span className={`mgmt-stat-val ${agent.performance.startsWith('+') ? 'pos' : 'neg'}`}>
                  {agent.performance}
                </span>
              </div>
              <div className="mgmt-stat">
                <span className="mgmt-stat-label">Trades</span>
                <span className="mgmt-stat-val">{agent.trades}</span>
              </div>
              <div className="mgmt-stat">
                <span className="mgmt-stat-label">Confidence</span>
                <span className="mgmt-stat-val">{agent.confidence}%</span>
              </div>
              <div className="mgmt-stat">
                <span className="mgmt-stat-label">Last Active</span>
                <span className="mgmt-stat-val">{agent.lastActive}</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mgmt-actions">
              <button
                onClick={() => handleAgentAction(agent.id, 'configure')}
                className="btn-secondary"
              >
                Configure
              </button>
              
              <button
                onClick={() => handleAgentAction(agent.id, agent.status === 'paused' ? 'start' : 'pause')}
                className={agent.status === 'paused' ? 'btn-secondary' : 'btn-danger'}
              >
                {agent.status === 'paused' ? 'Start' : 'Pause'}
              </button>
              
              <button
                onClick={() => handleAgentAction(agent.id, 'delete')}
                className="btn-danger"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Add Agent Modal */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3 style={{ color: 'var(--t1)', marginBottom: '20px' }}>Add New Agent</h3>
            
            <div className="form-group">
              <label className="form-label">Agent Name</label>
              <input 
                type="text" 
                placeholder="Enter agent name"
                className="form-input"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Role</label>
              <select className="form-select">
                <option>Strategy Orchestrator</option>
                <option>NLP Analyst</option>
                <option>Execution Manager</option>
                <option>Risk Manager</option>
                <option>On-Chain Validator</option>
              </select>
            </div>
            
            <div className="settings-actions">
              <button
                onClick={() => setShowAddModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowAddModal(false)}
                className="btn-primary"
              >
                Add Agent
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Agent Configuration Modal */}
      {selectedAgent && (
        <div className="modal-overlay">
          <div className="modal">
            <h3 style={{ color: 'var(--t1)', marginBottom: '20px' }}>
              Configure: {selectedAgent.name}
            </h3>
            
            <div className="form-group">
              <label className="form-label">Confidence Threshold</label>
              <input 
                type="range" 
                min="0" 
                max="100" 
                defaultValue={selectedAgent.confidence}
                className="form-input"
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--t3)' }}>
                <span>0%</span>
                <span>{selectedAgent.confidence}%</span>
                <span>100%</span>
              </div>
            </div>
            
            <div className="form-group">
              <label className="form-label">
                <input type="checkbox" defaultChecked style={{ marginRight: '8px' }} />
                Enable auto-trading
              </label>
            </div>
            
            <div className="form-group">
              <label className="form-label">
                <input type="checkbox" defaultChecked style={{ marginRight: '8px' }} />
                Send notifications
              </label>
            </div>
            
            <div className="form-group">
              <label className="form-label">Trading Strategy</label>
              <select className="form-select">
                <option>Momentum Following</option>
                <option>Mean Reversion</option>
                <option>Arbitrage</option>
                <option>Market Making</option>
              </select>
            </div>
            
            <div className="settings-actions">
              <button
                onClick={() => setSelectedAgent(null)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => setSelectedAgent(null)}
                className="btn-primary"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentManagement;

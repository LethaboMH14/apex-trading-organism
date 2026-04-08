/**
 * APEX Reputation System Component
 * Comprehensive reputation scoring and validation system
 */

import React, { useState, useEffect } from 'react';

const ReputationSystem = () => {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [timeframe, setTimeframe] = useState('7D');
  const [reputationData, setReputationData] = useState({
    overallScore: 87.5,
    trend: '+2.3%',
    lastUpdated: '2 minutes ago',
    agents: [
      {
        id: 'agent-1',
        name: 'Dr. Zara Okafor',
        role: 'Strategy Orchestrator',
        score: 92.3,
        trend: '+1.2%',
        validations: 145,
        onChainTrades: 89,
        lastValidation: '5 minutes ago',
        history: [
          { date: '2026-04-01', score: 91.1 },
          { date: '2026-04-02', score: 91.8 },
          { date: '2026-04-03', score: 90.5 },
          { date: '2026-04-04', score: 91.9 },
          { date: '2026-04-05', score: 92.1 },
          { date: '2026-04-06', score: 91.7 },
          { date: '2026-04-07', score: 92.3 },
        ],
        factors: {
          accuracy: 94.2,
          consistency: 89.7,
          profitability: 91.5,
          riskManagement: 88.9,
          compliance: 95.1
        }
      },
      {
        id: 'agent-2',
        name: 'Dr. Jabari Mensah',
        role: 'NLP Analyst',
        score: 78.6,
        trend: '+3.4%',
        validations: 98,
        onChainTrades: 67,
        lastValidation: '12 minutes ago',
        history: [
          { date: '2026-04-01', score: 76.2 },
          { date: '2026-04-02', score: 77.1 },
          { date: '2026-04-03', score: 76.8 },
          { date: '2026-04-04', score: 77.5 },
          { date: '2026-04-05', score: 77.9 },
          { date: '2026-04-06', score: 78.2 },
          { date: '2026-04-07', score: 78.6 },
        ],
        factors: {
          accuracy: 82.3,
          consistency: 76.5,
          profitability: 74.8,
          riskManagement: 79.2,
          compliance: 85.1
        }
      },
      {
        id: 'agent-3',
        name: 'ENGR. Marcus Oduya',
        role: 'Kraken Execution',
        score: 89.7,
        trend: '+0.8%',
        validations: 167,
        onChainTrades: 112,
        lastValidation: '3 minutes ago',
        history: [
          { date: '2026-04-01', score: 89.2 },
          { date: '2026-04-02', score: 89.5 },
          { date: '2026-04-03', score: 88.9 },
          { date: '2026-04-04', score: 89.8 },
          { date: '2026-04-05', score: 89.4 },
          { date: '2026-04-06', score: 89.6 },
          { date: '2026-04-07', score: 89.7 },
        ],
        factors: {
          accuracy: 91.5,
          consistency: 88.2,
          profitability: 92.1,
          riskManagement: 87.6,
          compliance: 90.8
        }
      },
      {
        id: 'agent-4',
        name: 'Dr. Sipho Nkosi',
        role: 'Risk Management',
        score: 85.4,
        trend: '-1.2%',
        validations: 134,
        onChainTrades: 45,
        lastValidation: '8 minutes ago',
        history: [
          { date: '2026-04-01', score: 86.7 },
          { date: '2026-04-02', score: 86.2 },
          { date: '2026-04-03', score: 85.9 },
          { date: '2026-04-04', score: 85.1 },
          { date: '2026-04-05', score: 85.6 },
          { date: '2026-04-06', score: 85.8 },
          { date: '2026-04-07', score: 85.4 },
        ],
        factors: {
          accuracy: 87.3,
          consistency: 84.9,
          profitability: 83.2,
          riskManagement: 91.8,
          compliance: 88.5
        }
      },
      {
        id: 'agent-5',
        name: 'Dr. Priya Nair',
        role: 'ERC-8004 & On-Chain',
        score: 91.2,
        trend: '+2.8%',
        validations: 189,
        onChainTrades: 31,
        lastValidation: '6 minutes ago',
        history: [
          { date: '2026-04-01', score: 89.5 },
          { date: '2026-04-02', score: 90.1 },
          { date: '2026-04-03', score: 90.8 },
          { date: '2026-04-04', score: 90.5 },
          { date: '2026-04-05', score: 91.0 },
          { date: '2026-04-06', score: 90.9 },
          { date: '2026-04-07', score: 91.2 },
        ],
        factors: {
          accuracy: 93.7,
          consistency: 90.4,
          profitability: 88.9,
          riskManagement: 89.2,
          compliance: 96.3
        }
      }
    ]
  });

  const timeframes = ['24H', '7D', '30D', '90D', 'ALL'];

  const getScoreColor = (score) => {
    if (score >= 90) return '#00ff88';
    if (score >= 80) return '#00aaff';
    if (score >= 70) return '#ffaa00';
    return '#ff4444';
  };

  const getTrendColor = (trend) => {
    return trend.startsWith('+') ? '#00ff88' : '#ff4444';
  };

  const getFactorColor = (score) => {
    if (score >= 90) return '#00ff88';
    if (score >= 80) return '#00aaff';
    if (score >= 70) return '#ffaa00';
    return '#ff4444';
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
        <h2 style={{ margin: 0, color: '#fff' }}>Reputation System</h2>
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
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

      {/* Overall Score Card */}
      <div style={{
        backgroundColor: '#1a1a1a',
        border: '1px solid #333',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '14px', color: '#888', marginBottom: '8px' }}>System Reputation Score</div>
        <div style={{ 
          fontSize: '48px', 
          fontWeight: '700',
          color: getScoreColor(reputationData.overallScore),
          marginBottom: '8px'
        }}>
          {reputationData.overallScore.toFixed(1)}
        </div>
        <div style={{ 
          fontSize: '16px',
          color: getTrendColor(reputationData.trend),
          marginBottom: '4px'
        }}>
          {reputationData.trend}
        </div>
        <div style={{ fontSize: '12px', color: '#888' }}>
          Last updated: {reputationData.lastUpdated}
        </div>
      </div>

      {/* Agent Reputation Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
        gap: '16px',
        marginBottom: '24px'
      }}>
        {reputationData.agents.map(agent => (
          <div 
            key={agent.id}
            onClick={() => setSelectedAgent(agent)}
            style={{
              backgroundColor: '#1a1a1a',
              border: '1px solid #333',
              borderRadius: '12px',
              padding: '20px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <h3 style={{ 
                  color: '#fff', 
                  margin: '0 0 4px 0',
                  fontSize: '14px',
                  fontWeight: '600'
                }}>
                  {agent.name.split(' ').slice(0, 2).join(' ')}
                </h3>
                <p style={{ 
                  color: '#888', 
                  fontSize: '11px', 
                  margin: 0 
                }}>
                  {agent.name.split(' ').slice(2).join(' ')}
                </p>
                <p style={{ 
                  color: '#ccc', 
                  fontSize: '12px', 
                  margin: '4px 0 0 0' 
                }}>
                  {agent.role}
                </p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ 
                  fontSize: '24px', 
                  fontWeight: '700',
                  color: getScoreColor(agent.score)
                }}>
                  {agent.score.toFixed(1)}
                </div>
                <div style={{ 
                  fontSize: '12px',
                  color: getTrendColor(agent.trend)
                }}>
                  {agent.trend}
                </div>
              </div>
            </div>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: '1fr 1fr', 
              gap: '12px',
              fontSize: '11px'
            }}>
              <div>
                <div style={{ color: '#888', marginBottom: '2px' }}>Validations</div>
                <div style={{ color: '#fff', fontWeight: '600' }}>{agent.validations}</div>
              </div>
              <div>
                <div style={{ color: '#888', marginBottom: '2px' }}>On-Chain Trades</div>
                <div style={{ color: '#fff', fontWeight: '600' }}>{agent.onChainTrades}</div>
              </div>
            </div>
            
            <div style={{ 
              marginTop: '12px',
              paddingTop: '12px',
              borderTop: '1px solid #333',
              fontSize: '10px',
              color: '#888'
            }}>
              Last validation: {agent.lastValidation}
            </div>
          </div>
        ))}
      </div>

      {/* Agent Detail Modal */}
      {selectedAgent && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: '#1a1a1a',
            border: '1px solid #333',
            borderRadius: '12px',
            padding: '24px',
            width: '600px',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ color: '#fff', margin: 0 }}>
                {selectedAgent.name}
              </h3>
              <button
                onClick={() => setSelectedAgent(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#888',
                  fontSize: '20px',
                  cursor: 'pointer'
                }}
              >
                ×
              </button>
            </div>
            
            {/* Score Overview */}
            <div style={{
              backgroundColor: '#2a2a2a',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '20px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '14px', color: '#888', marginBottom: '8px' }}>Reputation Score</div>
              <div style={{ 
                fontSize: '36px', 
                fontWeight: '700',
                color: getScoreColor(selectedAgent.score),
                marginBottom: '4px'
              }}>
                {selectedAgent.score.toFixed(1)}
              </div>
              <div style={{ 
                fontSize: '16px',
                color: getTrendColor(selectedAgent.trend)
              }}>
                {selectedAgent.trend}
              </div>
            </div>
            
            {/* Reputation Factors */}
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ color: '#00ff88', marginBottom: '12px' }}>Reputation Factors</h4>
              <div style={{ display: 'grid', gap: '12px' }}>
                {Object.entries(selectedAgent.factors).map(([key, value]) => (
                  <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ 
                      fontSize: '12px', 
                      color: '#ccc',
                      textTransform: 'capitalize'
                    }}>
                      {key.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{
                        width: '60px',
                        height: '6px',
                        backgroundColor: '#333',
                        borderRadius: '3px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${value}%`,
                          height: '100%',
                          backgroundColor: getFactorColor(value)
                        }}></div>
                      </div>
                      <span style={{ 
                        fontSize: '12px', 
                        fontWeight: '600',
                        color: getFactorColor(value),
                        minWidth: '35px',
                        textAlign: 'right'
                      }}>
                        {value.toFixed(1)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* History Chart Placeholder */}
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ color: '#00ff88', marginBottom: '12px' }}>Score History</h4>
              <div style={{
                height: '150px',
                backgroundColor: '#2a2a2a',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#888',
                fontSize: '12px'
              }}>
                📈 Score history chart will be rendered here
              </div>
            </div>
            
            {/* Actions */}
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setSelectedAgent(null)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#444',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '12px',
                  color: '#fff',
                  cursor: 'pointer'
                }}
              >
                Close
              </button>
              <button
                onClick={() => setSelectedAgent(null)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#00ff88',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#000',
                  cursor: 'pointer'
                }}
              >
                Validate Agent
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReputationSystem;

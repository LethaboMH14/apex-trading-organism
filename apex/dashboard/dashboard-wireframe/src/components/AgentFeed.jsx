/**
 * APEX Agent Feed Component
 * Live feed of agent decisions with real-time updates and expandable reasoning chains
 */

import React, { useState, useEffect } from 'react';

// Time ago utility
const timeAgo = (timestamp) => {
  const now = new Date();
  const past = new Date(timestamp);
  const diffInSeconds = Math.floor((now - past) / 1000);
  
  if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
};

// Individual Decision Card
const DecisionCard = ({ decision, isExpanded, onToggle }) => {
  const hasReasoning = decision.reasoning && decision.reasoning.length > 0;
  const hasHash = decision.onChainHash && decision.onChainHash.length > 0;
  
  const handleHashClick = () => {
    if (hasHash) {
      window.open(`https://sepolia.basescan.org/tx/${decision.onChainHash}`, '_blank');
    }
  };

  return (
    <div 
      className={`agent-card ${decision.action.toLowerCase()}`}
      data-status={decision.action.toLowerCase()}
    >
      <div className="agent-card-header">
        <div>
          <div className="agent-name">{decision.agentName}</div>
          <div className="agent-role">{decision.role}</div>
        </div>
        <div className={`status-pill ${decision.action.toLowerCase()}`}>
          {decision.action}
        </div>
      </div>
      
      <div className="agent-meta">
        <div className="agent-time">{timeAgo(decision.timestamp)}</div>
        {hasHash && (
          <span className="hash-badge" onClick={handleHashClick}>
            🔗 {decision.onChainHash.slice(0, 8)}...{decision.onChainHash.slice(-6)}
          </span>
        )}
      </div>
      
      <div className="conf-row">
        <span className="conf-label">Confidence</span>
        <div className="conf-track">
          <div 
            className={`conf-fill ${decision.confidence >= 80 ? 'high' : decision.confidence >= 60 ? 'medium' : 'low'}`}
            style={{ width: `${decision.confidence}%` }}
          ></div>
        </div>
        <span className="conf-value">{decision.confidence}%</span>
      </div>
      
      {hasReasoning && (
        <div style={{ marginTop: '8px' }}>
          <button className="reasoning-toggle" onClick={onToggle}>
            📝 {isExpanded ? 'Hide' : 'Show'} Reasoning
          </button>
          {isExpanded && (
            <div style={{ 
              marginTop: '8px', 
              padding: '8px', 
              backgroundColor: 'rgba(255,255,255,0.03)', 
              borderRadius: '6px', 
              fontSize: '11px', 
              color: 'rgba(255,255,255,0.7)',
              lineHeight: '1.4'
            }}>
              {decision.reasoning}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Main AgentFeed Component
const AgentFeed = ({ decisions = [], maxItems = 50, isConnected = true }) => {
  const [displayDecisions, setDisplayDecisions] = useState([]);
  const [expandedCards, setExpandedCards] = useState(new Set());

  // Update display decisions when props change
  useEffect(() => {
    const sortedDecisions = [...decisions].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    const limitedDecisions = sortedDecisions.slice(0, maxItems);
    setDisplayDecisions(limitedDecisions);
  }, []);

  // Mock data for demonstration (remove in production)
  useEffect(() => {
    if (decisions.length === 0) {
      const mockDecisions = [
        {
          id: '1',
          agentName: 'DR. ZARA OKAFOR',
          role: 'Strategy Orchestrator',
          department: 'strategy',
          action: 'DECIDED',
          confidence: 85,
          timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
          reasoning: 'Market conditions indicate bullish momentum on BTC based on technical analysis and sentiment scoring. Risk parameters within acceptable range.',
          onChainHash: '0x1234567890abcdef1234567890abcdef12345678'
        },
        {
          id: '2',
          agentName: 'DR. JABARI MENSAH',
          role: 'NLP Analyst',
          department: 'data',
          action: 'ANALYZING',
          confidence: 72,
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          reasoning: 'Processing news sentiment for major cryptocurrencies. Current sentiment shows positive bias for ETH, neutral for BTC.',
          onChainHash: null
        },
        {
          id: '3',
          agentName: 'ENGR. MARCUS ODUYA',
          role: 'Kraken Execution',
          department: 'execution',
          action: 'EXECUTING',
          confidence: 95,
          timestamp: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
          reasoning: 'Executing BTC buy order at current market price. Order size: 0.5 BTC. Expected slippage: <0.1%.',
          onChainHash: '0xabcdef1234567890abcdef1234567890abcdef12'
        },
        {
          id: '4',
          agentName: 'DR. SIPHO NKOSI',
          role: 'Risk Management',
          department: 'risk',
          action: 'VALIDATED',
          confidence: 88,
          timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
          reasoning: 'Risk assessment complete. Current position size within 2% of portfolio limit. Drawdown at acceptable levels.',
          onChainHash: '0x7890abcdef1234567890abcdef1234567890abcd'
        },
        {
          id: '5',
          agentName: 'DR. PRIYA NAIR',
          role: 'ERC-8004 & On-Chain',
          department: 'trust',
          action: 'LEARNING',
          confidence: 67,
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
          reasoning: 'Analyzing validation patterns for reputation scoring. Recent trades show high success rate, recommending reputation increase.',
          onChainHash: null
        }
      ];
      setDisplayDecisions(mockDecisions);
    }
  }, []);

  const toggleCardExpansion = (cardId) => {
    setExpandedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(cardId)) {
        newSet.delete(cardId);
      } else {
        newSet.add(cardId);
      }
      return newSet;
    });
  };

  return (
    <div className="agent-feed">
      {/* Connection Overlay */}
      {!isConnected && (
        <div className="feed-paused">
          <div style={{ color: 'white', fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: '1rem', textAlign: 'center', padding: '1rem' }}>
            <div style={{ marginBottom: '0.5rem' }}>⏸️</div>
            LIVE FEED PAUSED
          </div>
        </div>
      )}

      {/* Feed Content */}
      <div style={{
        maxHeight: '600px',
        overflowY: 'auto',
        paddingRight: '0.5rem'
      }}>
        {displayDecisions.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3rem 1rem',
            color: '#9ca3af',
            fontFamily: 'DM Sans, sans-serif'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🤖</div>
            <div style={{ fontSize: '1rem' }}>
              Waiting for first agent decision...
            </div>
          </div>
        ) : (
          displayDecisions.map((decision) => (
            <DecisionCard
              key={decision.id}
              decision={decision}
              isExpanded={expandedCards.has(decision.id)}
              onToggle={() => toggleCardExpansion(decision.id)}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default AgentFeed;

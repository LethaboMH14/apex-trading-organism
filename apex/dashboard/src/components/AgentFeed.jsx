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
  }, [decisions, maxItems]);

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

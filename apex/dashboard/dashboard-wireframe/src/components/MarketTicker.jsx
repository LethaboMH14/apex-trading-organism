/**
 * APEX Market Ticker Component
 * 
 * Shows live BTC, ETH, SOL prices from Kraken API
 */
import React, { useState, useEffect } from 'react';

const MarketTicker = () => {
  const [prices, setPrices] = useState({
    BTC: { price: 0, change: 0 },
    ETH: { price: 0, change: 0 },
    SOL: { price: 0, change: 0 }
  });
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const response = await fetch('https://api.kraken.com/0/public/Ticker?pair=XBTUSD,ETHUSD,SOLUSD');
        if (!response.ok) throw new Error('Failed to fetch prices');
        
        const data = await response.json();
        
        if (data.error) {
          // Show last known prices silently on error
          console.warn('Kraken API error:', data.error);
          return;
        }

        const newPrices = {
          BTC: {
            price: parseFloat(data.result.XBTUSD.c[0]) || 0,
            change: parseFloat(data.result.XBTUSD.c[0]) - parseFloat(data.result.XBTUSD.o[0]) || 0
          },
          ETH: {
            price: parseFloat(data.result.ETHUSD.c[0]) || 0,
            change: parseFloat(data.result.ETHUSD.c[0]) - parseFloat(data.result.ETHUSD.o[0]) || 0
          },
          SOL: {
            price: parseFloat(data.result.SOLUSD.c[0]) || 0,
            change: parseFloat(data.result.SOLUSD.c[0]) - parseFloat(data.result.SOLUSD.o[0]) || 0
          }
        };

        setPrices(newPrices);
        setError(false);
      } catch (err) {
        console.error('Error fetching prices:', err);
        setError(true);
      }
    };

    // Fetch immediately
    fetchPrices();
    
    // Then fetch every 30 seconds
    const interval = setInterval(fetchPrices, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{
      backgroundColor: 'rgba(255, 255, 255, 0.02)',
      border: '1px solid rgba(255, 255, 255, 0.05)',
      borderRadius: '8px',
      padding: '12px',
      margin: '12px 10px'
    }}>
      <div style={{
        fontSize: '10px',
        fontWeight: '600',
        color: '#8B949E',
        textTransform: 'uppercase',
        letterSpacing: '0.06em',
        marginBottom: '8px',
        fontFamily: 'Inter, sans-serif'
      }}>
        LIVE MARKETS
      </div>
      
      {Object.entries(prices).map(([symbol, data]) => (
        <div key={symbol} style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 0',
          borderBottom: '1px solid rgba(255, 255, 255, 0.03)'
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '700',
            color: '#FFFFFF',
            fontFamily: 'JetBrains Mono, monospace',
            minWidth: '25px'
          }}>
            {symbol}
          </div>
          <div style={{
            fontSize: '10px',
            fontWeight: '500',
            color: '#8B949E',
            fontFamily: 'JetBrains Mono, monospace'
          }}>
            ${data.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: data.price < 1 ? 4 : 2 })}
          </div>
          <div style={{
            fontSize: '9px',
            fontWeight: '600',
            color: data.change >= 0 ? '#00D4AA' : '#FF6B6B',
            fontFamily: 'JetBrains Mono, monospace',
            display: 'flex',
            alignItems: 'center',
            gap: '2px'
          }}>
            {data.change >= 0 ? '▲' : '▼'}
            {Math.abs(data.change).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: Math.abs(data.change) < 1 ? 4 : 2 })}
          </div>
        </div>
      ))}
      
      {error && (
        <div style={{
          fontSize: '9px',
          color: '#FF6B6B',
          textAlign: 'center',
          padding: '4px 0',
          fontFamily: 'Inter, sans-serif'
        }}>
          Connection Error
        </div>
      )}
    </div>
  );
};

export default MarketTicker;

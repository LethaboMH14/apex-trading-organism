"""
APEX Data - Market Intelligence Pipeline

DR. YUKI TANAKA: VP of Market Intelligence at APEX.

Background: Japanese-South African. UCT PhD Quantitative Finance. Built the first real-time 
crypto sentiment model used by a JSE-listed fund.

This module implements complete market data pipeline for APEX, ingesting from multiple 
sources including PRISM API (Strykr), Kraken market data, and on-chain signals. 
All data is validated, cleaned, and aggregated for trading decisions.

Author: DR. YUKI TANAKA
Standard: "A signal that cannot be explained is a signal that cannot be trusted."
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from urllib.parse import urljoin
import aiohttp
import pandas as pd
from pydantic import BaseModel, Field, validator

# APEX imports
from dotenv import load_dotenv, find_dotenv
from apex_llm_router import ask_kwame

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables with override
load_dotenv(find_dotenv(), override=True)


class AssetSignal(BaseModel):
    """Model for individual asset trading signal."""
    symbol: str = Field(..., description="Trading symbol")
    price_signal: str = Field(..., description="Price signal: BUY/SELL/HOLD")
    signal_strength: float = Field(..., ge=-1.0, le=1.0, description="Signal strength -1 to 1")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level 0 to 1")
    risk_metrics: Dict[str, float] = Field(default_factory=dict, description="Risk metrics")
    timestamp: datetime = Field(default_factory=datetime.now, description="Signal timestamp")


class PortfolioSignal(BaseModel):
    """Model for portfolio-level signals."""
    signals: List[AssetSignal] = Field(..., description="List of asset signals")
    portfolio_score: float = Field(ge=-1.0, le=1.0, description="Overall portfolio score")
    rebalance_recommendation: Optional[str] = Field(None, description="Rebalancing recommendation")
    timestamp: datetime = Field(default_factory=datetime.now, description="Signal timestamp")


class RiskMetrics(BaseModel):
    """Model for asset risk metrics."""
    symbol: str = Field(..., description="Asset symbol")
    volatility: float = Field(..., ge=0.0, description="Price volatility")
    var_95: float = Field(..., ge=0.0, description="95% Value at Risk")
    correlation_btc: float = Field(ge=-1.0, le=1.0, description="Correlation with BTC")
    max_drawdown: float = Field(..., le=0.0, description="Maximum drawdown")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    timestamp: datetime = Field(default_factory=datetime.now, description="Metrics timestamp")


class PrismAPIClient:
    """
    PRISM API Client - Strykr AI-powered market intelligence.
    
    Interfaces with PRISM API to get AI-generated trading signals, risk metrics,
    and portfolio recommendations. Includes rate limiting and response validation.
    """
    
    def __init__(self):
        """Initialize PRISM API client."""
        self.base_url = os.getenv("PRISM_API_URL", "https://api.prism.strykr.ai")
        self.api_key = os.getenv("PRISM_API_KEY", "")
        self.promo_code = os.getenv("PRISM_PROMO_CODE", "LABLAB")
        
        # Rate limiting
        self.rate_limiter = {
            "requests": 0,
            "window_start": time.time(),
            "max_requests_per_second": 10
        }
        
        # HTTP session
        self.session = None
        
        logger.info(f"🔮 PRISM API client initialized")
        logger.info(f"🌐 Base URL: {self.base_url}")
        logger.info(f"🔑 API Key configured: {'✅' if self.api_key else '❌'}")
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make authenticated request to PRISM API with rate limiting.
        
        Args:
            endpoint: API endpoint to call
            params: Optional query parameters
            
        Returns:
            API response dictionary
        """
        # Rate limiting check
        current_time = time.time()
        window_duration = current_time - self.rate_limiter["window_start"]
        
        if window_duration >= 1.0:
            self.rate_limiter["requests"] = 0
            self.rate_limiter["window_start"] = current_time
        
        if self.rate_limiter["requests"] >= self.rate_limiter["max_requests_per_second"]:
            wait_time = 1.0 - window_duration
            logger.warning(f"⏱️ Rate limit reached, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            return self._make_request(endpoint, params)
        
        self.rate_limiter["requests"] += 1
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = urljoin(self.base_url, endpoint)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Promo-Code": self.promo_code,
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"📨 PRISM API response: {len(str(data))} bytes")
                    return data
                else:
                    logger.error(f"❌ PRISM API error: {response.status} - {await response.text()}")
                    return {"error": f"HTTP {response.status}", "message": await response.text()}
                    
        except asyncio.TimeoutError:
            logger.error("❌ PRISM API request timeout")
            return {"error": "timeout", "message": "Request timeout"}
        except Exception as e:
            logger.error(f"❌ PRISM API request failed: {e}")
            return {"error": "request_failed", "message": str(e)}
    
    async def get_asset_signals(self, symbol: str) -> AssetSignal:
        """
        Get AI-powered trading signal for specific asset.
        
        Args:
            symbol: Trading symbol (e.g., "BTC", "ETH")
            
        Returns:
            AssetSignal object with trading recommendation
        """
        logger.info(f"📡 Getting PRISM signal for {symbol}")
        
        params = {
            "symbol": symbol,
            "timeframe": "1h",
            "include_risk": "true",
            "include_sentiment": "true"
        }
        
        response = await self._make_request("v1/signals/asset", params)
        
        if "error" in response:
            # Return default signal on error
            return AssetSignal(
                symbol=symbol,
                price_signal="HOLD",
                signal_strength=0.0,
                confidence=0.0,
                risk_metrics={},
                timestamp=datetime.now()
            )
        
        # Parse successful response
        data = response.get("data", {})
        return AssetSignal(
            symbol=symbol,
            price_signal=data.get("signal", "HOLD"),
            signal_strength=float(data.get("strength", 0.0)),
            confidence=float(data.get("confidence", 0.0)),
            risk_metrics=data.get("risk_metrics", {}),
            timestamp=datetime.now()
        )
    
    async def get_portfolio_signals(self, symbols: List[str]) -> PortfolioSignal:
        """
        Get portfolio-level signals for multiple assets.
        
        Args:
            symbols: List of trading symbols
            
        Returns:
            PortfolioSignal with aggregated recommendations
        """
        logger.info(f"📊 Getting PRISM portfolio signals for {len(symbols)} symbols")
        
        params = {
            "symbols": ",".join(symbols),
            "timeframe": "1h",
            "include_rebalance": "true",
            "optimization_goal": "sharpe_max"
        }
        
        response = await self._make_request("v1/signals/portfolio", params)
        
        if "error" in response:
            # Return default portfolio signal on error
            return PortfolioSignal(
                signals=[AssetSignal(symbol=s, price_signal="HOLD", signal_strength=0.0, confidence=0.0, risk_metrics={}) for s in symbols],
                portfolio_score=0.0,
                rebalance_recommendation=None,
                timestamp=datetime.now()
            )
        
        # Parse successful response
        data = response.get("data", {})
        signals_data = data.get("signals", [])
        
        asset_signals = []
        for signal_data in signals_data:
            asset_signals.append(AssetSignal(
                symbol=signal_data.get("symbol", ""),
                price_signal=signal_data.get("signal", "HOLD"),
                signal_strength=float(signal_data.get("strength", 0.0)),
                confidence=float(signal_data.get("confidence", 0.0)),
                risk_metrics=signal_data.get("risk_metrics", {}),
                timestamp=datetime.now()
            ))
        
        return PortfolioSignal(
            signals=asset_signals,
            portfolio_score=float(data.get("portfolio_score", 0.0)),
            rebalance_recommendation=data.get("rebalance_recommendation"),
            timestamp=datetime.now()
        )
    
    async def get_risk_metrics(self, symbol: str) -> RiskMetrics:
        """
        Get comprehensive risk metrics for an asset.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            RiskMetrics object with comprehensive risk analysis
        """
        logger.info(f"📈 Getting PRISM risk metrics for {symbol}")
        
        params = {
            "symbol": symbol,
            "timeframe": "1d",
            "lookback_days": 30,
            "include_var": "true"
        }
        
        response = await self._make_request("v1/risk/metrics", params)
        
        if "error" in response:
            # Return default risk metrics on error
            return RiskMetrics(
                symbol=symbol,
                volatility=0.0,
                var_95=0.0,
                correlation_btc=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                timestamp=datetime.now()
            )
        
        # Parse successful response
        data = response.get("data", {})
        risk_data = data.get("risk_metrics", {})
        
        return RiskMetrics(
            symbol=symbol,
            volatility=float(risk_data.get("volatility", 0.0)),
            var_95=float(risk_data.get("var_95", 0.0)),
            correlation_btc=float(risk_data.get("correlation_btc", 0.0)),
            max_drawdown=float(risk_data.get("max_drawdown", 0.0)),
            sharpe_ratio=float(risk_data.get("sharpe_ratio", 0.0)),
            timestamp=datetime.now()
        )


class KrakenDataFeed:
    """
    Kraken Data Feed - Real-time market data from Kraken exchange.
    
    Provides access to Kraken public market data including tickers, OHLCV data,
    order book, and recent trades. No API key required for public endpoints.
    """
    
    def __init__(self):
        """Initialize Kraken data feed."""
        self.base_url = "https://api.kraken.com/0/public"
        self.session = None
        
        # Supported trading pairs
        self.supported_pairs = ["XBTUSD", "ETHUSD", "SOLUSD"]
        
        logger.info("🦑 Kraken data feed initialized")
        logger.info(f"📊 Supported pairs: {', '.join(self.supported_pairs)}")
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make request to Kraken API.
        
        Args:
            endpoint: API endpoint to call
            params: Optional query parameters
            
        Returns:
            API response dictionary
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = urljoin(self.base_url, endpoint)
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("error"):
                        error = data["error"]
                        logger.error(f"❌ Kraken API error: {error}")
                        return {"error": error}
                    return data
                else:
                    logger.error(f"❌ Kraken API HTTP error: {response.status}")
                    return {"error": f"HTTP {response.status}"}
                    
        except asyncio.TimeoutError:
            logger.error("❌ Kraken API request timeout")
            return {"error": "timeout"}
        except Exception as e:
            logger.error(f"❌ Kraken API request failed: {e}")
            return {"error": "request_failed", "message": str(e)}
    
    async def get_ticker(self, pair: str) -> Dict[str, Any]:
        """
        Get current ticker information for trading pair.
        
        Args:
            pair: Trading pair (e.g., "XBTUSD")
            
        Returns:
            Dictionary with ticker data
        """
        logger.debug(f"📈 Getting Kraken ticker for {pair}")
        
        response = await self._make_request("Ticker", params={"pair": pair})
        
        if "error" in response:
            return {}
        
        result = response.get("result", {})
        if pair in result:
            ticker_data = result[pair]
            return {
                "pair": pair,
                "bid": float(ticker_data.get("b", [])[0][0]),
                "ask": float(ticker_data.get("a", [])[0][0]),
                "last": float(ticker_data.get("c", [])[0][0]),
                "volume": float(ticker_data.get("v", [])[0][0]),
                "vwap": float(ticker_data.get("p", [])[0][0]),
                "low": float(ticker_data.get("l", [])[0][0]),
                "high": float(ticker_data.get("h", [])[0][0]),
                "timestamp": datetime.now()
            }
        
        return {}
    
    async def get_ohlcv(self, pair: str, interval: int = 60, count: int = 100) -> pd.DataFrame:
        """
        Get OHLCV data for analysis.
        
        Args:
            pair: Trading pair
            interval: Timeframe in minutes (default: 60)
            count: Number of data points (default: 100)
            
        Returns:
            Pandas DataFrame with OHLCV data
        """
        logger.debug(f"📊 Getting Kraken OHLCV for {pair}, {interval}m, {count} candles")
        
        params = {
            "pair": pair,
            "interval": f"{interval}",
            "since": int((datetime.now() - timedelta(hours=count * interval / 60)).timestamp())
        }
        
        response = await self._make_request("OHLC", params=params)
        
        if "error" in response:
            return pd.DataFrame()
        
        result = response.get("result", {})
        if pair in result:
            ohlcv_data = result[pair]
            
            # Convert to DataFrame
            df_data = []
            for timestamp, ohlcv in zip(ohlcv_data, range(len(ohlcv_data))):
                df_data.append({
                    "timestamp": datetime.fromtimestamp(int(timestamp)),
                    "open": float(ohlcv[1]),
                    "high": float(ohlcv[2]),
                    "low": float(ohlcv[3]),
                    "close": float(ohlcv[4]),
                    "volume": float(ohlcv[5])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index("timestamp", inplace=True)
            
            logger.info(f"📊 Retrieved {len(df)} OHLCV records for {pair}")
            return df
        
        return pd.DataFrame()
    
    async def get_order_book(self, pair: str, depth: int = 10) -> Dict[str, Any]:
        """
        Get current order book for trading pair.
        
        Args:
            pair: Trading pair
            depth: Order book depth (default: 10)
            
        Returns:
            Dictionary with order book data
        """
        logger.debug(f"📚 Getting Kraken order book for {pair}, depth {depth}")
        
        params = {"pair": pair, "count": depth}
        response = await self._make_request("Depth", params=params)
        
        if "error" in response:
            return {}
        
        result = response.get("result", {})
        if pair in result:
            book_data = result[pair]
            
            return {
                "pair": pair,
                "bids": book_data.get("bids", [])[:depth],
                "asks": book_data.get("asks", [])[:depth],
                "timestamp": datetime.now()
            }
        
        return {}


class SignalAggregator:
    """
    Signal Aggregator - Combines multiple data sources into unified signals.
    
    Aggregates signals from PRISM AI, Kraken price data, and other sources
    to generate composite trading signals with confidence scoring.
    """
    
    def __init__(self):
        """Initialize signal aggregator."""
        self.prism_client = PrismAPIClient()
        self.kraken_feed = KrakenDataFeed()
        
        # Configurable weights (can be adjusted via environment)
        self.weights = {
            "price_momentum": float(os.getenv("APEX_WEIGHT_PRICE_MOMENTUM", "0.4")),
            "prism_ai_signal": float(os.getenv("APEX_WEIGHT_PRISM_AI", "0.4")),
            "volume_anomaly": float(os.getenv("APEX_WEIGHT_VOLUME_ANOMALY", "0.2"))
        }
        
        logger.info("📊 Signal Aggregator initialized")
        logger.info(f"⚖️ Weights: {self.weights}")
    
    async def compute_composite_score(self, symbol: str) -> float:
        """
        Compute composite trading score for an asset.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Composite score from -1.0 (bearish) to +1.0 (bullish)
        """
        logger.debug(f"🧮 Computing composite score for {symbol}")
        
        try:
            # Get current price data
            ticker = await self.kraken_feed.get_ticker(f"{symbol}USD")
            if not ticker:
                logger.warning(f"⚠️ No ticker data for {symbol}")
                return 0.0
            
            current_price = ticker["last"]
            previous_close = ticker.get("vwap", current_price)  # Fallback to current price
            
            # Calculate price momentum (simple)
            price_change = (current_price - previous_close) / previous_close
            price_momentum = max(-1.0, min(1.0, price_change * 10))  # Normalize to -1 to 1
            
            # Get PRISM AI signal
            prism_signal = await self.prism_client.get_asset_signals(symbol)
            prism_score = prism_signal.signal_strength * prism_signal.confidence
            
            # Get volume data (simplified)
            volume_score = 0.0
            if ticker["volume"] > 0:
                # Simple volume anomaly detection
                volume_score = min(1.0, ticker["volume"] / 1000000)  # Normalize
            
            # Calculate composite score
            composite_score = (
                self.weights["price_momentum"] * price_momentum +
                self.weights["prism_ai_signal"] * prism_score +
                self.weights["volume_anomaly"] * volume_score
            )
            
            # Ensure score is in valid range
            composite_score = max(-1.0, min(1.0, composite_score))
            
            logger.debug(f"📊 {symbol} composite score: {composite_score:.3f}")
            logger.debug(f"📊 Components: momentum={price_momentum:.3f}, prism={prism_score:.3f}, volume={volume_score:.3f}")
            
            return composite_score
            
        except Exception as e:
            logger.error(f"❌ Failed to compute composite score for {symbol}: {e}")
            return 0.0
    
    async def get_aggregated_signals(self, symbols: List[str]) -> Dict[str, AssetSignal]:
        """
        Get aggregated signals for multiple symbols.
        
        Args:
            symbols: List of trading symbols
            
        Returns:
            Dictionary mapping symbols to AssetSignal objects
        """
        logger.info(f"📊 Getting aggregated signals for {len(symbols)} symbols")
        
        signals = {}
        
        # Process symbols in parallel
        tasks = [self.compute_composite_score(symbol) for symbol in symbols]
        scores = await asyncio.gather(*tasks, return_exceptions=True)
        
        for symbol, score_result in zip(symbols, scores):
            if isinstance(score_result, Exception):
                logger.error(f"❌ Failed to get signal for {symbol}: {score_result}")
                signals[symbol] = AssetSignal(
                    symbol=symbol,
                    price_signal="HOLD",
                    signal_strength=0.0,
                    confidence=0.0,
                    risk_metrics={},
                    timestamp=datetime.now()
                )
            else:
                # Convert score to signal
                if score_result > 0.3:
                    price_signal = "BUY"
                    signal_strength = score_result
                elif score_result < -0.3:
                    price_signal = "SELL"
                    signal_strength = abs(score_result)
                else:
                    price_signal = "HOLD"
                    signal_strength = 0.0
                
                confidence = abs(score_result)
                
                signals[symbol] = AssetSignal(
                    symbol=symbol,
                    price_signal=price_signal,
                    signal_strength=signal_strength,
                    confidence=confidence,
                    risk_metrics=await self.prism_client.get_risk_metrics(symbol),
                    timestamp=datetime.now()
                )
        
        logger.info(f"📊 Generated {len(signals)} aggregated signals")
        return signals


class DataPipeline:
    """
    Data Pipeline - Orchestrates all data collection for APEX.
    
    Coordinates PRISM API, Kraken data feed, and signal aggregation to provide
    unified market intelligence for trading decisions. Saves results to database.
    """
    
    def __init__(self):
        """Initialize the data pipeline."""
        self.prism_client = PrismAPIClient()
        self.kraken_feed = KrakenDataFeed()
        self.aggregator = SignalAggregator()
        
        # Load configured symbols
        symbols_str = os.getenv("APEX_SYMBOLS", "XBTUSD,ETHUSD,SOLUSD")
        self.symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]
        
        logger.info(f"🔧 Data Pipeline initialized")
        logger.info(f"📊 Monitoring symbols: {', '.join(self.symbols)}")
    
    async def run_cycle(self) -> Dict[str, Any]:
        """
        Run a complete data collection cycle.
        
        Returns:
            Dictionary containing all collected signals and metadata
        """
        cycle_start = time.time()
        logger.info("🔄 Starting data collection cycle")
        
        try:
            # Get aggregated signals for all configured symbols
            signals = await self.aggregator.get_aggregated_signals(self.symbols)
            
            # Get portfolio-level analysis from PRISM
            portfolio_signal = await self.prism_client.get_portfolio_signals(self.symbols)
            
            # Get market data from Kraken
            market_data = {}
            for symbol in self.symbols:
                pair = f"{symbol}USD"
                ticker = await self.kraken_feed.get_ticker(pair)
                if ticker:
                    market_data[symbol] = ticker
            
            # Compile results
            results = {
                "cycle_type": "data_collection",
                "timestamp": datetime.now().isoformat(),
                "symbols": self.symbols,
                "asset_signals": {symbol: asdict(signals[symbol]) for symbol in self.symbols},
                "portfolio_signal": asdict(portfolio_signal),
                "market_data": market_data,
                "signal_count": len(signals),
                "duration": time.time() - cycle_start
            }
            
            logger.info(f"✅ Data cycle completed in {results['duration']:.2f}s")
            logger.info(f"📊 Generated {results['signal_count']} signals for {len(self.symbols)} symbols")
            
            return results
            
        except Exception as e:
            duration = time.time() - cycle_start
            logger.error(f"❌ Data cycle failed after {duration:.2f}s: {e}")
            
            return {
                "cycle_type": "data_collection",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "duration": duration,
                "symbols": self.symbols
            }
    
    async def get_real_time_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time price for a specific symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with current price data
        """
        pair = f"{symbol}USD"
        ticker = await self.kraken_feed.get_ticker(pair)
        
        if ticker:
            return {
                "symbol": symbol,
                "price": ticker["last"],
                "bid": ticker["bid"],
                "ask": ticker["ask"],
                "volume": ticker["volume"],
                "timestamp": ticker["timestamp"]
            }
        else:
            return {
                "symbol": symbol,
                "error": "No price data available"
            }


# Main execution function
async def main():
    """Main entry point for APEX data pipeline."""
    logger.info("📊 Starting APEX Data Pipeline")
    
    try:
        # Initialize data pipeline
        pipeline = DataPipeline()
        
        # Run a single data collection cycle
        logger.info("🔄 Running data collection cycle...")
        results = await pipeline.run_cycle()
        
        # Display results
        print("\n" + "="*60)
        print("📊 APEX DATA PIPELINE RESULTS")
        print("="*60)
        print(f"🕐 Timestamp: {results['timestamp']}")
        print(f"📊 Symbols: {', '.join(results['symbols'])}")
        print(f"📡 Signals Generated: {results['signal_count']}")
        print(f"⏱️ Duration: {results['duration']:.2f}s")
        
        if "error" not in results:
            print("\n📈 ASSET SIGNALS:")
            for symbol, signal in results["asset_signals"].items():
                print(f"  {symbol}: {signal['price_signal']} "
                      f"(strength: {signal['signal_strength']:.2f}, "
                      f"confidence: {signal['confidence']:.2f})")
            
            print("\n📊 PORTFOLIO SIGNAL:")
            portfolio = results["portfolio_signal"]
            print(f"  Score: {portfolio['portfolio_score']:.2f}")
            print(f"  Recommendation: {portfolio.get('rebalance_recommendation', 'None')}")
            
            print("\n📈 MARKET DATA:")
            for symbol, data in results["market_data"].items():
                if "error" not in data:
                    print(f"  {symbol}: ${data['last']:.2f} "
                          f"(Vol: {data['volume']:.0f})")
        else:
            print(f"\n❌ ERROR: {results['error']}")
        
        print("="*60)
        
    except KeyboardInterrupt:
        logger.info("🛑 Data pipeline stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error in data pipeline: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("🏁 APEX Data Pipeline shutdown complete")


if __name__ == "__main__":
    """
    Entry point for APEX data pipeline.
    
    Run this module directly to execute data collection:
    $ python apex-data.py
    """
    asyncio.run(main())

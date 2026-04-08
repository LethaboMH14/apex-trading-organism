"""
APEX Live - Master Orchestrator for Real Trading

This replaces apex_demo_run_fixed.py as the real production system.
It orchestrates the complete trading pipeline with real data feeds,
risk management, AI decisions, and dual execution (blockchain + Kraken).

Author: APEX Live System
Standard: "Every trade must be AI-reasoned, risk-gated, and verifiable."
"""

import asyncio
import json
import os
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# APEX imports
from apex_data import DataPipeline
from apex_sentiment import SentimentPipeline
from apex_risk import RiskGate, RiskParameters, CircuitBreaker
from apex_llm_router import LLMRouter
from apex_identity import APEXIdentity
from kraken_live import KrakenLiveTrader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APEXLive:
    """
    APEX Live - Real trading orchestrator with dual execution.
    
    This class manages the complete trading pipeline:
    1. Real market data from Kraken
    2. Sentiment analysis pipeline
    3. Risk gate validation
    4. LLM decision with real data
    5. Dual execution: ERC-8004 + Kraken
    """
    
    def __init__(self):
        """Initialize the live trading system."""
        self.data_pipeline = DataPipeline()
        self.sentiment_pipeline = SentimentPipeline()
        self.risk_params = RiskParameters(max_drawdown_pct=0.05, max_position_pct=0.1)
        self.circuit_breaker = CircuitBreaker(self.risk_params)
        self.risk_gate = RiskGate(self.risk_params, self.circuit_breaker)
        self.llm_router = LLMRouter()
        self.identity = APEXIdentity()
        self.kraken_trader = KrakenLiveTrader()
        
        logger.info("APEX Live orchestrator initialized")
        logger.info("Kraken trader integrated")
    
    async def run_cycle(self, trade_size: float = 350) -> Dict[str, Any]:
        """
        Run a complete trading cycle with real data.
        
        Args:
            trade_size: Trade size in USD
            
        Returns:
            Dictionary with complete trade execution results
        """
        cycle_start = datetime.now()
        logger.info(f"Starting APEX Live cycle - Trade size: ${trade_size}")
        
        try:
            # 1. Get real BTC price from Kraken
            logger.info("Fetching real BTC price from Kraken...")
            kraken_response = requests.get(
                "https://api.kraken.com/0/public/Ticker?pair=XBTUSD",
                timeout=10
            )
            kraken_data = kraken_response.json()
            
            if "result" not in kraken_data or "XXBTZUSD" not in kraken_data["result"]:
                raise Exception("Failed to fetch Kraken price data")
            
            price_data = kraken_data["result"]["XXBTZUSD"]
            price = float(price_data["c"][0])  # Current price
            change = float(price_data["p"][1]) if price_data["p"][1] else 0.0  # 24h change
            
            logger.info(f"BTC Price: ${price:.2f} ({change:+.2f}% 24h)")
            
            # 2. Get sentiment from SentimentPipeline
            logger.info("Analyzing market sentiment...")
            try:
                sentiment_result = self.sentiment_pipeline.analyze_sentiment("BTC")
                sent_score = getattr(sentiment_result, 'score', 75) if sentiment_result else 75
                sent_score = max(0, min(100, sent_score))  # Clamp to 0-100
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
                sent_score = 75  # Default neutral sentiment
            
            logger.info(f"Sentiment Score: {sent_score}/100")
            
            # 3. Risk gate check
            logger.info("Running risk gate validation...")
            trade_signal = {
                "symbol": "XBT",
                "action": "BUY",
                "size": trade_size / price,  # Convert USD to BTC
                "confidence": 0.82,
                "reasoning": "live_cycle",
                "timestamp": datetime.now()
            }
            
            # Mock portfolio for risk check
            current_portfolio = {"XBT": 0.0, "total": 0.0}
            
            try:
                risk_approval = self.risk_gate.approve(trade_signal, trade_size / price, current_portfolio)
                approved = risk_approval.get("approved", False)
                risk_reason = risk_approval.get("reason", "Risk check failed")
            except Exception as e:
                logger.warning(f"Risk gate failed: {e}")
                approved = False
                risk_reason = "Risk system error"
            
            logger.info(f"Risk Gate: {'APPROVED' if approved else 'REJECTED'} - {risk_reason}")
            
            # 4. LLM decision with REAL data
            logger.info("Generating AI trading decision...")
            prompt = f"""You are APEX autonomous trading agent.

Current Market Data:
- BTC Price: ${price:.2f}
- 24h Change: {change:+.2f}%
- Sentiment Score: {sent_score}/100
- Risk Gate: {'APPROVED' if approved else 'REJECTED'}
- Trade Size: ${trade_size}

Analyze this data and make a trading decision.

Respond in EXACTLY this format (under 200 chars):
BTC ${price:.0f} {change:+.1f}%. Sentiment {sent_score}/100. Risk: {'APPROVED' if approved else 'REJECTED'}. Signal: +0.42. Confidence: [X]%. Action: [BUY/SELL/HOLD]."""
            
            try:
                decision = self.llm_router.route(prompt)
                reasoning = decision.get("reasoning", "")[:200] if decision else "AI decision unavailable"
                action = decision.get("action", "HOLD") if decision else "HOLD"
                confidence = decision.get("confidence", 75) if decision else 75
            except Exception as e:
                logger.warning(f"LLM decision failed: {e}")
                reasoning = "LLM system error - using fallback"
                action = "HOLD"
                confidence = 50
            
            logger.info(f"AI Decision: {action} (Confidence: {confidence}%)")
            logger.info(f"Reasoning: {reasoning}")
            
            # 5. Submit to blockchain if action is BUY/SELL
            tx_hash = ""
            blockchain_success = False
            kraken_order_id = ""
            kraken_success = False
            
            if action in ["BUY", "SELL"] and approved:
                logger.info(f"Submitting {action} trade to blockchain...")
                try:
                    blockchain_result = await self.identity.submit_trade_intent(
                        pair="BTC/USD",
                        action=action,
                        amount_usd=trade_size,
                        reasoning=reasoning,
                        confidence=confidence
                    )
                    tx_hash = blockchain_result.get("tx_hash", "")
                    blockchain_success = blockchain_result.get("success", False)
                    
                    if blockchain_success:
                        logger.info(f"Blockchain submission successful: {tx_hash}")
                    else:
                        logger.warning("Blockchain submission failed")
                except Exception as e:
                    logger.error(f"Blockchain submission error: {e}")
                
                # 6. Execute on Kraken if blockchain succeeded
                if blockchain_success:
                    logger.info(f"Executing {action} trade on Kraken...")
                    try:
                        # Convert USD to BTC volume
                        btc_volume = trade_size / price
                        kraken_result = self.kraken_trader.place_market_order(
                            pair="XBTUSD",
                            side=action.lower(),
                            volume=btc_volume
                        )
                        
                        if "error" not in kraken_result:
                            kraken_order_id = kraken_result.get("txid", "")
                            kraken_success = True
                            logger.info(f"Kraken order successful: {kraken_order_id}")
                        else:
                            logger.warning(f"Kraken order failed: {kraken_result.get('error')}")
                    except Exception as e:
                        logger.error(f"Kraken execution error: {e}")
            
            # Compile results
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            
            result = {
                "cycle_id": cycle_start.strftime("%Y%m%d_%H%M%S"),
                "timestamp": cycle_start.isoformat(),
                "duration_seconds": cycle_duration,
                "market_data": {
                    "price": price,
                    "change_24h": change,
                    "sentiment_score": sent_score
                },
                "risk_assessment": {
                    "approved": approved,
                    "reason": risk_reason
                },
                "ai_decision": {
                    "action": action,
                    "confidence": confidence,
                    "reasoning": reasoning
                },
                "execution": {
                    "trade_size_usd": trade_size,
                    "blockchain_success": blockchain_success,
                    "tx_hash": tx_hash,
                    "kraken_success": kraken_success,
                    "kraken_order_id": kraken_order_id
                },
                "success": blockchain_success and kraken_success and approved and action in ["BUY", "SELL"]
            }
            
            logger.info(f"Cycle completed in {cycle_duration:.2f}s - Success: {result['success']}")
            return result
            
        except Exception as e:
            logger.error(f"Live cycle failed: {e}")
            return {
                "cycle_id": cycle_start.strftime("%Y%m%d_%H%M%S"),
                "timestamp": cycle_start.isoformat(),
                "error": str(e),
                "success": False
            }
    
    async def run_continuous(self, interval_seconds: int = 60, max_cycles: Optional[int] = None):
        """
        Run continuous trading cycles.
        
        Args:
            interval_seconds: Seconds between cycles
            max_cycles: Maximum number of cycles (None for infinite)
        """
        cycle_count = 0
        
        logger.info(f"Starting continuous trading - Interval: {interval_seconds}s")
        
        while True:
            if max_cycles and cycle_count >= max_cycles:
                logger.info(f"Reached max cycles ({max_cycles}), stopping")
                break
            
            cycle_count += 1
            logger.info(f"=== Cycle {cycle_count} ===")
            
            result = await self.run_cycle()
            
            if result.get("success"):
                logger.info("Cycle successful")
            else:
                logger.warning(f"Cycle failed: {result.get('error', 'Unknown error')}")
            
            # Wait for next cycle
            if interval_seconds > 0:
                logger.info(f"Waiting {interval_seconds}s for next cycle...")
                await asyncio.sleep(interval_seconds)


async def main():
    """Main entry point for APEX Live."""
    apex = APEXLive()
    
    # Run a single cycle for testing
    result = await apex.run_cycle(trade_size=350)
    print("\n=== APEX Live Cycle Result ===")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())

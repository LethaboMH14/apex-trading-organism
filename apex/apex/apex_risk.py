"""
APEX Risk Management - Risk Control & Circuit Breaker System

DR. SIPHO NKOSI: VP of Risk Management at APEX.

Background: South African, Johannesburg. UCT PhD Risk Engineering. Former Chief Risk Officer 
at a JSE-listed asset manager.

This module implements complete risk management system for APEX including drawdown monitoring,
circuit breakers, position limits, and volatility-adjusted sizing. DR. SIPHO has veto power 
over all trading decisions and can halt trading at any time.

Author: DR. SIPHO NKOSI
Standard: "The job is not to make money. The job is to not lose it."
"""

import asyncio
import json
import logging
import math
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

# APEX imports
from dotenv import load_dotenv, find_dotenv
from apex_llm_router import ask_sipho

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv(find_dotenv(), override=True)


@dataclass
class RiskParameters:
    """Risk management parameters with environment variable loading."""
    max_daily_loss_pct: float = 0.05  # 5% hard daily loss limit
    max_position_pct: float = 0.10   # 10% per symbol position limit
    max_total_exposure_pct: float = 0.30  # 30% total exposure limit
    max_drawdown_pct: float = 0.08   # 8% drawdown triggers circuit breaker
    min_confidence_threshold: float = 0.65  # Minimum confidence for trades
    volatility_lookback_days: int = 20  # Volatility calculation period
    atr_period: int = 14  # Average True Range period
    target_risk_pct: float = 0.01  # 1% portfolio risk per ATR
    
    def __post_init__(self):
        """Load parameters from environment variables."""
        self.max_daily_loss_pct = float(os.getenv("APEX_MAX_DAILY_LOSS_PCT", self.max_daily_loss_pct))
        self.max_position_pct = float(os.getenv("APEX_MAX_POSITION_PCT", self.max_position_pct))
        self.max_total_exposure_pct = float(os.getenv("APEX_MAX_TOTAL_EXPOSURE_PCT", self.max_total_exposure_pct))
        self.max_drawdown_pct = float(os.getenv("APEX_MAX_DRAWDOWN_PCT", self.max_drawdown_pct))
        self.min_confidence_threshold = float(os.getenv("APEX_MIN_CONFIDENCE_THRESHOLD", self.min_confidence_threshold))
        self.volatility_lookback_days = int(os.getenv("APEX_VOLATILITY_LOOKBACK_DAYS", self.volatility_lookback_days))
        self.atr_period = int(os.getenv("APEX_ATR_PERIOD", self.atr_period))
        self.target_risk_pct = float(os.getenv("APEX_TARGET_RISK_PCT", self.target_risk_pct))
        
        logger.info(f"🛡️ Risk parameters loaded: max_drawdown={self.max_drawdown_pct:.1%}")


@dataclass
class RiskStatus:
    """Risk status tracking."""
    current_drawdown_pct: float
    max_drawdown_pct: float
    daily_loss_pct: float
    total_exposure_pct: float
    status: str  # "normal"|"warning"|"critical"|"circuit_breaker"
    timestamp: datetime
    alerts: List[str]


class DrawdownMonitor:
    """Monitor portfolio drawdown and risk status."""
    
    def __init__(self, risk_params: RiskParameters):
        """Initialize drawdown monitor."""
        self.risk_params = risk_params
        self.peak_balance = 0.0
        self.daily_start_balance = 0.0
        self.current_balance = 0.0
        self.status_history: List[RiskStatus] = []
        
        logger.info("📉 DrawdownMonitor initialized")
    
    def update(self, current_balance: float, peak_balance: float) -> Dict[str, Any]:
        """
        Update drawdown monitoring and return risk status.
        
        Args:
            current_balance: Current portfolio balance
            peak_balance: Historical peak balance
            
        Returns:
            Dictionary with drawdown metrics and status
        """
        self.current_balance = current_balance
        self.peak_balance = max(self.peak_balance, peak_balance)
        
        # Calculate drawdown
        if self.peak_balance > 0:
            current_drawdown_pct = (self.peak_balance - current_balance) / self.peak_balance
        else:
            current_drawdown_pct = 0.0
        
        # Calculate daily loss
        if self.daily_start_balance > 0:
            daily_loss_pct = (self.daily_start_balance - current_balance) / self.daily_start_balance
        else:
            daily_loss_pct = 0.0
        
        # Determine status
        status = self._determine_status(current_drawdown_pct, daily_loss_pct)
        
        # Create status record
        risk_status = RiskStatus(
            current_drawdown_pct=current_drawdown_pct,
            max_drawdown_pct=self.risk_params.max_drawdown_pct,
            daily_loss_pct=daily_loss_pct,
            total_exposure_pct=0.0,  # Would be calculated from positions
            status=status,
            timestamp=datetime.now(),
            alerts=self._generate_alerts(current_drawdown_pct, daily_loss_pct, status)
        )
        
        self.status_history.append(risk_status)
        
        # Log status changes
        if len(self.status_history) > 1:
            prev_status = self.status_history[-2].status
            if prev_status != status:
                logger.warning(f"🚨 Risk status changed: {prev_status} → {status}")
        
        return {
            "current_drawdown_pct": current_drawdown_pct,
            "max_drawdown_pct": self.risk_params.max_drawdown_pct,
            "daily_loss_pct": daily_loss_pct,
            "status": status,
            "alerts": risk_status.alerts,
            "timestamp": risk_status.timestamp.isoformat()
        }
    
    def _determine_status(self, current_drawdown_pct: float, daily_loss_pct: float) -> str:
        """Determine risk status based on thresholds."""
        # Check circuit breaker conditions
        if (current_drawdown_pct >= self.risk_params.max_drawdown_pct or
            daily_loss_pct >= self.risk_params.max_daily_loss_pct):
            return "circuit_breaker"
        
        # Check critical level (80% of max drawdown)
        if current_drawdown_pct >= self.risk_params.max_drawdown_pct * 0.8:
            return "critical"
        
        # Check warning level (50% of max drawdown)
        if current_drawdown_pct >= self.risk_params.max_drawdown_pct * 0.5:
            return "warning"
        
        return "normal"
    
    def _generate_alerts(self, current_drawdown_pct: float, daily_loss_pct: float, status: str) -> List[str]:
        """Generate appropriate alerts based on risk status."""
        alerts = []
        
        if status == "circuit_breaker":
            if current_drawdown_pct >= self.risk_params.max_drawdown_pct:
                alerts.append(f"Max drawdown exceeded: {current_drawdown_pct:.1%}")
            if daily_loss_pct >= self.risk_params.max_daily_loss_pct:
                alerts.append(f"Daily loss limit exceeded: {daily_loss_pct:.1%}")
        
        elif status == "critical":
            alerts.append(f"Critical drawdown level: {current_drawdown_pct:.1%}")
        
        elif status == "warning":
            alerts.append(f"Drawdown warning: {current_drawdown_pct:.1%}")
        
        return alerts
    
    def reset_daily(self, new_start_balance: float):
        """Reset daily tracking for new trading day."""
        self.daily_start_balance = new_start_balance
        logger.info(f"📅 Daily tracking reset: ${new_start_balance:.2f}")


class CircuitBreaker:
    """Circuit breaker system for trading halt."""
    
    def __init__(self, risk_params: RiskParameters):
        """Initialize circuit breaker."""
        self.risk_params = risk_params
        self.is_open = False
        self.trip_history: List[Dict[str, Any]] = []
        self.consecutive_failures = 0
        self.api_error_count = 0
        self.total_api_calls = 0
        
        logger.info("⚡ CircuitBreaker initialized")
    
    def trip(self, reason: str, websocket_broker=None, database=None):
        """
        Trip circuit breaker and halt all trading.
        
        Args:
            reason: Reason for tripping the breaker
            websocket_broker: Optional WebSocket broker for broadcasting
            database: Optional database for saving event
        """
        if not self.is_open:
            self.is_open = True
            trip_event = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "status": "tripped",
                "consecutive_failures": self.consecutive_failures,
                "api_error_rate": self.api_error_count / max(self.total_api_calls, 1)
            }
            
            self.trip_history.append(trip_event)
            
            logger.error(f"🚨 CIRCUIT BREAKER TRIPPED: {reason}")
            
            # Broadcast alert
            if websocket_broker:
                asyncio.create_task(websocket_broker.broadcast_error(
                    Exception(f"Circuit breaker tripped: {reason}"),
                    "risk_management"
                ))
            
            # Save to database
            if database:
                asyncio.create_task(database.save_decision({
                    "type": "circuit_breaker_trip",
                    "reason": reason,
                    "timestamp": datetime.now(),
                    "severity": "critical"
                }))
    
    def reset(self, confirmation: str = "") -> bool:
        """
        Reset circuit breaker with explicit confirmation.
        
        Args:
            confirmation: Required confirmation string "APEX_RESET_CONFIRMED"
            
        Returns:
            True if reset successful, False otherwise
        """
        if confirmation != "APEX_RESET_CONFIRMED":
            logger.warning("⚠️ Invalid confirmation for circuit breaker reset")
            return False
        
        if self.is_open:
            self.is_open = False
            self.consecutive_failures = 0
            self.api_error_count = 0
            self.total_api_calls = 0
            
            logger.info("✅ Circuit breaker reset - trading resumed")
            return True
        
        return False
    
    def check_conditions(self, drawdown_status: Dict[str, Any], daily_loss_pct: float) -> bool:
        """Check if circuit breaker should be tripped."""
        # Auto-trip conditions
        if drawdown_status["status"] == "circuit_breaker":
            self.trip(f"Drawdown limit exceeded: {drawdown_status['current_drawdown_pct']:.1%}")
            return True
        
        if daily_loss_pct >= self.risk_params.max_daily_loss_pct:
            self.trip(f"Daily loss limit exceeded: {daily_loss_pct:.1%}")
            return True
        
        if self.consecutive_failures >= 3:
            self.trip("3 consecutive failed orders")
            return True
        
        if self.total_api_calls > 0 and (self.api_error_count / self.total_api_calls) > 0.2:
            self.trip("API error rate exceeded 20%")
            return True
        
        return False
    
    def record_failure(self):
        """Record a trading failure."""
        self.consecutive_failures += 1
        logger.warning(f"⚠️ Trading failure recorded: {self.consecutive_failures} consecutive")
    
    def record_api_error(self):
        """Record an API error."""
        self.api_error_count += 1
        self.total_api_calls += 1
        logger.debug(f"🔌 API error recorded: {self.api_error_count}/{self.total_api_calls}")
    
    def record_api_success(self):
        """Record a successful API call."""
        self.total_api_calls += 1
        if self.consecutive_failures > 0:
            self.consecutive_failures = 0


class RiskGate:
    """
    Risk gate for trade approval with veto power.
    
    DR. SIPHO NKOSI has veto power over all trading decisions and can reject 
    any signal regardless of other approvals. This is documented explicitly as 
    the risk management override mechanism.
    """
    
    def __init__(self, risk_params: RiskParameters, circuit_breaker: CircuitBreaker):
        """Initialize risk gate."""
        self.risk_params = risk_params
        self.circuit_breaker = circuit_breaker
        self.approval_history: List[Dict[str, Any]] = []
        
        logger.info("🚪 RiskGate initialized - DR. SIPHO has veto power")
    
    def approve(self, signal: Dict[str, Any], proposed_size: float, current_exposure: Dict[str, float]) -> Dict[str, Any]:
        """
        Approve or reject trading signal with comprehensive risk checks.
        
        Args:
            signal: Trading signal with metadata
            proposed_size: Proposed position size
            current_exposure: Current exposure by symbol and total
            
        Returns:
            Dictionary with approval decision and reasoning
        """
        approval_result = {
            "approved": False,
            "reason": "",
            "adjusted_size": proposed_size,
            "risk_checks": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Check circuit breaker status
        if self.circuit_breaker.is_open:
            approval_result["reason"] = "Circuit breaker is open - trading halted"
            self._record_approval(signal, approval_result)
            return approval_result
        
        # Check confidence threshold
        signal_confidence = signal.get("confidence", 0.0)
        if signal_confidence < self.risk_params.min_confidence_threshold:
            approval_result["reason"] = f"Signal confidence {signal_confidence:.2f} below threshold {self.risk_params.min_confidence_threshold:.2f}"
            self._record_approval(signal, approval_result)
            return approval_result
        
        # Check position limit
        symbol = signal.get("symbol", "")
        current_symbol_exposure = current_exposure.get(symbol, 0.0)
        max_symbol_exposure = self.risk_params.max_position_pct
        
        if current_symbol_exposure + proposed_size > max_symbol_exposure:
            # Adjust size to fit within limit
            adjusted_size = max_symbol_exposure - current_symbol_exposure
            if adjusted_size <= 0:
                approval_result["reason"] = f"Symbol position limit exceeded: {current_symbol_exposure:.2%} + {proposed_size:.2%} > {max_symbol_exposure:.2%}"
                self._record_approval(signal, approval_result)
                return approval_result
            else:
                approval_result["adjusted_size"] = adjusted_size
                approval_result["risk_checks"]["position_adjusted"] = True
                logger.info(f"📏 Position size adjusted: {proposed_size:.2%} → {adjusted_size:.2%}")
        
        # Check total exposure
        total_exposure = sum(current_exposure.values())
        max_total_exposure = self.risk_params.max_total_exposure_pct
        
        if total_exposure + approval_result["adjusted_size"] > max_total_exposure:
            # Adjust size to fit within total limit
            adjusted_size = max_total_exposure - total_exposure
            if adjusted_size <= 0:
                approval_result["reason"] = f"Total exposure limit exceeded: {total_exposure:.2%} + {proposed_size:.2%} > {max_total_exposure:.2%}"
                self._record_approval(signal, approval_result)
                return approval_result
            else:
                approval_result["adjusted_size"] = adjusted_size
                approval_result["risk_checks"]["total_exposure_adjusted"] = True
                logger.info(f"📏 Total exposure adjusted: {proposed_size:.2%} → {adjusted_size:.2%}")
        
        # DR. SIPHO's veto power - final discretionary check
        veto_reason = self._apply_veto_power(signal, current_exposure)
        if veto_reason:
            approval_result["reason"] = f"DR. SIPHO veto: {veto_reason}"
            approval_result["risk_checks"]["veto_applied"] = True
            self._record_approval(signal, approval_result)
            return approval_result
        
        # All checks passed
        approval_result["approved"] = True
        approval_result["reason"] = "All risk checks passed"
        
        self._record_approval(signal, approval_result)
        logger.info(f"✅ Risk gate approved: {symbol} {approval_result['adjusted_size']:.2%}")
        
        return approval_result
    
    def _apply_veto_power(self, signal: Dict[str, Any], current_exposure: Dict[str, float]) -> Optional[str]:
        """
        Apply DR. SIPHO's discretionary veto power.
        
        This is the final risk override where DR. SIPHO can reject any signal
        based on qualitative factors not captured by quantitative limits.
        """
        # Example veto conditions (would be more sophisticated in production)
        
        # Veto if too many positions in same sector
        symbol = signal.get("symbol", "")
        if symbol in ["BTC", "ETH"] and current_exposure.get("BTC", 0) + current_exposure.get("ETH", 0) > 0.15:
            return "High crypto concentration risk"
        
        # Veto if signal is too aggressive given market conditions
        signal_strength = signal.get("signal_strength", 0.0)
        if abs(signal_strength) > 0.9:
            return "Signal strength too aggressive - risk of overtrading"
        
        # Veto if recent performance is poor
        # (Would check actual recent performance in production)
        
        return None
    
    def _record_approval(self, signal: Dict[str, Any], result: Dict[str, Any]):
        """Record approval decision for audit trail."""
        approval_record = {
            "signal": signal,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self.approval_history.append(approval_record)


class VolatilityAdjustedSizer:
    """Volatility-adjusted position sizing using ATR."""
    
    def __init__(self, risk_params: RiskParameters):
        """Initialize volatility-adjusted sizer."""
        self.risk_params = risk_params
        logger.info("📏 VolatilityAdjustedSizer initialized")
    
    def compute_atr(self, ohlcv: pd.DataFrame, period: int = None) -> float:
        """
        Compute Average True Range (ATR) from OHLCV data.
        
        Args:
            ohlcv: DataFrame with OHLCV data
            period: ATR calculation period
            
        Returns:
            ATR value
        """
        if period is None:
            period = self.risk_params.atr_period
        
        if len(ohlcv) < period:
            logger.warning(f"⚠️ Insufficient data for ATR: {len(ohlcv)} < {period}")
            return 0.0
        
        # Calculate True Range
        high_low = ohlcv['high'] - ohlcv['low']
        high_close = abs(ohlcv['high'] - ohlcv['close'].shift(1))
        low_close = abs(ohlcv['low'] - ohlcv['close'].shift(1))
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # Calculate ATR
        atr = true_range.rolling(window=period).mean().iloc[-1]
        
        logger.debug(f"📏 ATR({period}): {atr:.4f}")
        return atr
    
    def adjust_size(self, base_size: float, atr: float, target_risk_pct: float = None) -> float:
        """
        Adjust position size based on volatility.
        
        Args:
            base_size: Base position size
            atr: Average True Range
            target_risk_pct: Target risk percentage per ATR move
            
        Returns:
            Volatility-adjusted position size
        """
        if target_risk_pct is None:
            target_risk_pct = self.risk_params.target_risk_pct
        
        if atr <= 0:
            logger.warning("⚠️ Invalid ATR value, returning base size")
            return base_size
        
        # Adjust size so that 1 ATR move = target_risk_pct of portfolio
        # Size = (Target Risk % * Portfolio Value) / ATR
        # Simplified: adjust base_size by volatility factor
        
        volatility_factor = target_risk_pct / atr
        adjusted_size = base_size * volatility_factor
        
        # Ensure size is reasonable
        adjusted_size = max(0.01, min(adjusted_size, base_size * 2.0))
        
        logger.debug(f"📏 Size adjusted: {base_size:.4f} → {adjusted_size:.4f} (ATR: {atr:.4f})")
        return adjusted_size


async def main():
    """Main execution function demonstrating risk system."""
    logger.info("🚀 Starting APEX Risk Management System")
    
    try:
        # Initialize components
        risk_params = RiskParameters()
        drawdown_monitor = DrawdownMonitor(risk_params)
        circuit_breaker = CircuitBreaker(risk_params)
        risk_gate = RiskGate(risk_params, circuit_breaker)
        vol_sizer = VolatilityAdjustedSizer(risk_params)
        
        print("\n" + "="*60)
        print("🛡️ APEX RISK MANAGEMENT DEMO")
        print("="*60)
        print(f"📊 Max Drawdown: {risk_params.max_drawdown_pct:.1%}")
        print(f"💰 Max Daily Loss: {risk_params.max_daily_loss_pct:.1%}")
        print(f"📏 Max Position: {risk_params.max_position_pct:.1%}")
        print(f"🌐 Max Total Exposure: {risk_params.max_total_exposure_pct:.1%}")
        print(f"🎯 Min Confidence: {risk_params.min_confidence_threshold:.1%}")
        
        # Demonstrate drawdown monitoring
        print(f"\n📉 Drawdown Monitoring:")
        current_balance = 95000.0
        peak_balance = 100000.0
        
        status = drawdown_monitor.update(current_balance, peak_balance)
        print(f"  Current Drawdown: {status['current_drawdown_pct']:.1%}")
        print(f"  Status: {status['status']}")
        print(f"  Alerts: {status['alerts']}")
        
        # Demonstrate circuit breaker trip
        print(f"\n⚡ Circuit Breaker Demo:")
        print(f"  Is Open: {circuit_breaker.is_open}")
        
        # Trip circuit breaker
        circuit_breaker.trip("Demo trip - excessive drawdown")
        print(f"  After Trip: {circuit_breaker.is_open}")
        
        # Demonstrate risk gate rejection
        print(f"\n🚪 Risk Gate Demo:")
        signal = {
            "symbol": "BTC",
            "side": "buy",
            "confidence": 0.5,  # Below threshold
            "signal_strength": 0.8
        }
        
        current_exposure = {"BTC": 0.05, "ETH": 0.08}
        proposed_size = 0.08
        
        result = risk_gate.approve(signal, proposed_size, current_exposure)
        print(f"  Approved: {result['approved']}")
        print(f"  Reason: {result['reason']}")
        print(f"  Adjusted Size: {result['adjusted_size']:.2%}")
        
        # Demonstrate volatility adjustment
        print(f"\n📏 Volatility Adjustment Demo:")
        
        # Mock OHLCV data
        dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
        ohlcv_data = pd.DataFrame({
            'open': np.random.normal(50000, 1000, 20),
            'high': np.random.normal(51000, 1000, 20),
            'low': np.random.normal(49000, 1000, 20),
            'close': np.random.normal(50000, 1000, 20),
            'volume': np.random.normal(1000, 200, 20)
        }, index=dates)
        
        atr = vol_sizer.compute_atr(ohlcv_data)
        base_size = 0.05
        adjusted_size = vol_sizer.adjust_size(base_size, atr)
        
        print(f"  Base Size: {base_size:.2%}")
        print(f"  ATR: {atr:.2f}")
        print(f"  Adjusted Size: {adjusted_size:.2%}")
        
        print("="*60)
        print("🛡️ Risk Management System Demo Complete")
        
    except Exception as e:
        logger.error(f"💥 Risk system error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

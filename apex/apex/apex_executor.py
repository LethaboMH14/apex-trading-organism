"""
APEX Execution - Trading Execution Engine

ENGR. MARCUS ODUYA: VP of Execution at APEX.

Background: Nigerian-British. UCL MSc Algorithmic Trading Systems. Built HFT execution systems 
for two London prop firms.

This module implements complete trading execution engine for APEX including Kraken CLI 
integration, position sizing, order lifecycle management, and PnL tracking. All operations 
are designed for paper trading with explicit safety checks.

Author: ENGR. MARCUS ODUYA
Standard: "Every order must be intentional. No ghost trades, no partial fills left open, no missed exits."
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal
import numpy as np

# APEX imports
from dotenv import load_dotenv, find_dotenv
from apex_llm_router import ask_marcus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv(find_dotenv(), override=True)


@dataclass
class OrderFill:
    """Order fill data structure."""
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp: datetime
    status: str
    paper_mode: bool
    fill_type: str = "market"


@dataclass
class Position:
    """Position tracking data structure."""
    symbol: str
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    timestamp: datetime


@dataclass
class RiskParams:
    """Risk management parameters."""
    max_position_pct: float = 0.1  # Max 10% per position
    max_total_exposure: float = 0.3  # Max 30% total exposure
    kelly_fraction: float = 0.25  # Fraction of Kelly to use
    max_daily_loss: float = 0.02  # Max 2% daily loss
    confidence_threshold: float = 0.6  # Minimum confidence for trades


class KrakenCLIWrapper:
    """Kraken CLI wrapper for trading execution."""
    
    def __init__(self):
        """Initialize Kraken CLI wrapper."""
        self.cli_path = os.getenv("KRAKEN_CLI_PATH", "kraken")
        self.api_key = os.getenv("KRAKEN_API_KEY", "")
        self.api_secret = os.getenv("KRAKEN_API_SECRET", "")
        self.paper_mode = os.getenv("APEX_PAPER_MODE", "true").lower() == "true"
        
        # Safety check
        if not self.paper_mode:
            logger.warning("🚨 LIVE TRADING MODE ENABLED - MANUAL VERIFICATION REQUIRED")
            if input("Type 'CONFIRM' to enable live trading: ") != "CONFIRM":
                logger.error("❌ Live trading not confirmed - switching to paper mode")
                self.paper_mode = True
        
        logger.info(f"⚡ KrakenCLIWrapper initialized - Paper Mode: {self.paper_mode}")
    
    async def _run_cli_command(self, command: List[str]) -> Dict[str, Any]:
        """Execute Kraken CLI command with timeout."""
        try:
            # Add API credentials to command
            full_command = [
                self.cli_path,
                "--api-key", self.api_key,
                "--api-secret", self.api_secret
            ] + command
            
            logger.debug(f"🔧 Executing: {' '.join(full_command)}")
            
            # Run command with timeout
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    return response
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response", "stdout": result.stdout}
            else:
                return {
                    "error": f"CLI Error: {result.stderr}",
                    "returncode": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {"error": "Command timeout after 10 seconds"}
        except Exception as e:
            return {"error": f"Command execution failed: {str(e)}"}
    
    async def place_order(self, symbol: str, side: str, quantity: float, order_type: str = "market") -> OrderFill:
        """Place order via Kraken CLI or simulate in paper mode."""
        logger.info(f"📈 Placing {side} order: {quantity} {symbol}")
        
        if self.paper_mode:
            # Paper trading simulation
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Mock market price (would get from market data in production)
            mock_price = 50000.0 if symbol == "BTC" else 3000.0 if symbol == "ETH" else 100.0
            
            order_id = f"paper_{int(time.time() * 1000)}"
            
            fill = OrderFill(
                order_id=order_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=mock_price,
                timestamp=datetime.now(),
                status="filled",
                paper_mode=True,
                fill_type=order_type
            )
            
            logger.info(f"✅ Paper order filled: {order_id} at ${mock_price}")
            return fill
        else:
            # Live trading
            command = [
                "order",
                "place",
                "--pair", f"{symbol}USD",
                "--type", order_type,
                "--side", side,
                "--volume", str(quantity)
            ]
            
            response = await self._run_cli_command(command)
            
            if "error" in response:
                logger.error(f"❌ Order failed: {response['error']}")
                raise Exception(f"Order placement failed: {response['error']}")
            
            # Parse successful response
            order_data = response.get("result", {})
            order_id = order_data.get("txid", "unknown")
            
            # Get fill price
            price = float(order_data.get("price", [0.0])[0])
            
            fill = OrderFill(
                order_id=order_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                timestamp=datetime.now(),
                status="filled",
                paper_mode=False,
                fill_type=order_type
            )
            
            logger.info(f"✅ Live order filled: {order_id} at ${price}")
            return fill
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel open order."""
        logger.info(f"❌ Cancelling order: {order_id}")
        
        if self.paper_mode:
            logger.info(f"✅ Paper order cancelled: {order_id}")
            return True
        else:
            command = ["order", "cancel", "--txid", order_id]
            response = await self._run_cli_command(command)
            
            if "error" in response:
                logger.error(f"❌ Cancel failed: {response['error']}")
                return False
            
            logger.info(f"✅ Order cancelled: {order_id}")
            return True
    
    async def get_open_orders(self) -> List[Dict[str, Any]]:
        """Get list of open orders."""
        if self.paper_mode:
            # Return empty list for paper mode
            return []
        else:
            command = ["order", "open"]
            response = await self._run_cli_command(command)
            
            if "error" in response:
                logger.error(f"❌ Failed to get open orders: {response['error']}")
                return []
            
            return response.get("result", {}).get("open", [])
    
    async def get_account_balance(self) -> Dict[str, float]:
        """Get account balance."""
        if self.paper_mode:
            # Mock balance for paper mode
            return {
                "USD": 10000.0,
                "BTC": 0.1,
                "ETH": 2.0,
                "SOL": 50.0
            }
        else:
            command = ["balance"]
            response = await self._run_cli_command(command)
            
            if "error" in response:
                logger.error(f"❌ Failed to get balance: {response['error']}")
                return {}
            
            return response.get("result", {})


class PositionSizer:
    """Position sizing calculator using Kelly Criterion."""
    
    def __init__(self):
        """Initialize position sizer."""
        self.risk_params = RiskParams()
        logger.info("📏 PositionSizer initialized")
    
    def compute_size(self, signal_strength: float, risk_params: Dict[str, Any], account_balance: float) -> float:
        """
        Compute position size using Kelly Criterion with risk limits.
        
        Args:
            signal_strength: Signal strength (-1 to 1)
            risk_params: Risk management parameters
            account_balance: Available account balance
            
        Returns:
            Position size in base currency units
        """
        logger.debug(f"📏 Computing position size: signal={signal_strength:.3f}, balance=${account_balance:.2f}")
        
        # Kelly Criterion calculation
        win_rate = max(0.5, 0.5 + abs(signal_strength) * 0.3)  # Estimate win rate from signal
        avg_win = abs(signal_strength) * 0.05  # 5% average win for strong signals
        avg_loss = 0.02  # 2% average loss
        
        kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly_fraction = max(0, kelly_fraction)  # No negative Kelly
        
        # Apply Kelly fraction parameter
        kelly_size = kelly_fraction * self.risk_params.kelly_fraction
        
        # Convert to position size
        max_position_value = account_balance * self.risk_params.max_position_pct
        position_value = account_balance * kelly_size
        
        # Apply hard caps
        position_value = min(position_value, max_position_value)
        
        # Convert to base currency units (assuming USD pairs)
        mock_price = 50000.0  # Would get from market data
        position_size = position_value / mock_price
        
        # Document sizing decision
        sizing_log = {
            "signal_strength": signal_strength,
            "win_rate_estimate": win_rate,
            "kelly_fraction": kelly_fraction,
            "kelly_size": kelly_size,
            "max_position_value": max_position_value,
            "position_value": position_value,
            "position_size": position_size,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug(f"📏 Sizing decision: {sizing_log}")
        logger.info(f"📏 Position size: {position_size:.6f} units (${position_value:.2f})")
        
        return position_size


class OrderLifecycleManager:
    """Manages order lifecycle from submission to completion."""
    
    def __init__(self, kraken_cli: KrakenCLIWrapper):
        """Initialize order lifecycle manager."""
        self.kraken_cli = kraken_cli
        self.open_orders: Dict[str, OrderFill] = {}
        self.positions: Dict[str, Position] = {}
        self.monitoring_task = None
        
        logger.info("🔄 OrderLifecycleManager initialized")
    
    async def submit_order(self, signal: Dict[str, Any], risk_approval: Dict[str, Any]) -> OrderFill:
        """Submit order with risk validation."""
        logger.info(f"📤 Submitting order: {signal}")
        
        # Validate risk approval
        if not risk_approval.get("approved", False):
            raise ValueError("Risk approval required for order submission")
        
        # Extract order details from signal
        symbol = signal.get("symbol", "BTC")
        side = signal.get("side", "buy")
        quantity = signal.get("quantity", 0.001)
        order_type = signal.get("order_type", "market")
        
        # Submit order
        fill = await self.kraken_cli.place_order(symbol, side, quantity, order_type)
        
        # Track order
        self.open_orders[fill.order_id] = fill
        
        # Update position
        self._update_position(fill)
        
        logger.info(f"✅ Order submitted and tracked: {fill.order_id}")
        return fill
    
    def _update_position(self, fill: OrderFill):
        """Update position based on fill."""
        symbol = fill.symbol
        
        if symbol not in self.positions:
            self.positions[symbol] = Position(
                symbol=symbol,
                size=0.0,
                entry_price=0.0,
                current_price=fill.price,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                timestamp=fill.timestamp
            )
        
        position = self.positions[symbol]
        
        # Update position size
        if fill.side == "buy":
            position.size += fill.quantity
            if position.size > 0:
                # Update entry price for long position
                total_value = position.size * position.entry_price + fill.quantity * fill.price
                position.entry_price = total_value / position.size
        else:
            position.size -= fill.quantity
            if position.size < 0:
                # Update entry price for short position
                total_value = abs(position.size) * position.entry_price + fill.quantity * fill.price
                position.entry_price = total_value / abs(position.size)
        
        position.current_price = fill.price
        position.timestamp = fill.timestamp
        
        logger.debug(f"📊 Position updated: {symbol} size={position.size:.6f}")
    
    async def monitor_fills(self):
        """Monitor open orders for fills."""
        logger.info("👁️ Starting order monitoring")
        
        while True:
            try:
                # Get current open orders from exchange
                exchange_orders = await self.kraken_cli.get_open_orders()
                exchange_order_ids = {order.get("txid") for order in exchange_orders}
                
                # Check for filled orders
                filled_orders = []
                for order_id, order in self.open_orders.items():
                    if order_id not in exchange_order_ids and order.status == "open":
                        # Order was filled
                        order.status = "filled"
                        filled_orders.append(order_id)
                        logger.info(f"✅ Order filled: {order_id}")
                
                # Remove filled orders from tracking
                for order_id in filled_orders:
                    del self.open_orders[order_id]
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Order monitoring error: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def close_position(self, symbol: str, reason: str) -> OrderFill:
        """Close position at market."""
        logger.info(f"🔄 Closing position: {symbol} - {reason}")
        
        if symbol not in self.positions:
            logger.warning(f"⚠️ No position found for {symbol}")
            return None
        
        position = self.positions[symbol]
        
        if abs(position.size) < 0.0001:
            logger.warning(f"⚠️ Position already closed: {symbol}")
            return None
        
        # Determine closing side
        close_side = "sell" if position.size > 0 else "buy"
        close_quantity = abs(position.size)
        
        # Place closing order
        fill = await self.kraken_cli.place_order(symbol, close_side, close_quantity, "market")
        
        # Update position
        if position.size > 0:
            position.realized_pnl += position.size * (fill.price - position.entry_price)
        else:
            position.realized_pnl += abs(position.size) * (position.entry_price - fill.price)
        
        position.size = 0.0
        position.unrealized_pnl = 0.0
        
        logger.info(f"✅ Position closed: {symbol} - PnL: ${position.realized_pnl:.2f}")
        return fill
    
    def start_monitoring(self):
        """Start order monitoring task."""
        if self.monitoring_task is None:
            self.monitoring_task = asyncio.create_task(self.monitor_fills())
            logger.info("👁️ Order monitoring started")


class PnLTracker:
    """Track and calculate PnL for trading operations."""
    
    def __init__(self):
        """Initialize PnL tracker."""
        self.trades: List[OrderFill] = []
        self.session_start = datetime.now()
        self.daily_pnl = 0.0
        
        logger.info("💰 PnLTracker initialized")
    
    def record_trade(self, fill: OrderFill):
        """Record completed trade."""
        self.trades.append(fill)
        logger.info(f"📝 Trade recorded: {fill.order_id}")
    
    def get_session_pnl(self) -> Dict[str, float]:
        """Calculate session PnL."""
        realized_pnl = 0.0
        unrealized_pnl = 0.0
        
        # Calculate realized PnL from completed trades
        for trade in self.trades:
            if trade.status == "filled":
                # Simplified PnL calculation
                if trade.side == "sell":
                    realized_pnl += trade.quantity * trade.price
                else:
                    realized_pnl -= trade.quantity * trade.price
        
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_pnl": realized_pnl + unrealized_pnl,
            "session_duration": session_duration,
            "trade_count": len(self.trades)
        }
    
    def get_daily_pnl(self) -> float:
        """Get daily PnL."""
        # Filter trades from today
        today = datetime.now().date()
        today_trades = [trade for trade in self.trades if trade.timestamp.date() == today]
        
        daily_pnl = 0.0
        for trade in today_trades:
            if trade.side == "sell":
                daily_pnl += trade.quantity * trade.price
            else:
                daily_pnl -= trade.quantity * trade.price
        
        return daily_pnl
    
    async def broadcast_pnl_update(self, websocket_broker=None):
        """Broadcast PnL updates via WebSocket."""
        pnl_data = self.get_session_pnl()
        
        if websocket_broker:
            await websocket_broker.broadcast_trade_update({
                "type": "pnl_update",
                "data": pnl_data,
                "timestamp": datetime.now().isoformat()
            })
        
        logger.info(f"💰 PnL Update: ${pnl_data['total_pnl']:.2f}")


async def main():
    """Main execution function."""
    logger.info("🚀 Starting APEX Execution Engine")
    
    try:
        # Initialize components
        kraken_cli = KrakenCLIWrapper()
        position_sizer = PositionSizer()
        order_manager = OrderLifecycleManager(kraken_cli)
        pnl_tracker = PnLTracker()
        
        # Get account balance
        balance = await kraken_cli.get_account_balance()
        logger.info(f"💰 Account balance: {balance}")
        
        # Mock signal for demonstration
        signal = {
            "symbol": "BTC",
            "side": "buy",
            "quantity": 0.001,
            "order_type": "market",
            "signal_strength": 0.7
        }
        
        # Mock risk approval
        risk_approval = {
            "approved": True,
            "max_size": 0.01,
            "confidence": 0.8
        }
        
        # Compute position size
        position_size = position_sizer.compute_size(
            signal["signal_strength"],
            risk_approval,
            balance.get("USD", 10000.0)
        )
        
        # Update signal with computed size
        signal["quantity"] = position_size
        
        print("\n" + "="*60)
        print("⚡ APEX EXECUTION ENGINE DEMO")
        print("="*60)
        print(f"📊 Paper Mode: {kraken_cli.paper_mode}")
        print(f"💰 Account Balance: ${balance.get('USD', 0):.2f}")
        print(f"📏 Computed Position Size: {position_size:.6f} BTC")
        print(f"📈 Signal: {signal['side']} {signal['quantity']:.6f} {signal['symbol']}")
        
        # Submit order
        fill = await order_manager.submit_order(signal, risk_approval)
        pnl_tracker.record_trade(fill)
        
        print(f"✅ Order Filled:")
        print(f"  Order ID: {fill.order_id}")
        print(f"  Symbol: {fill.symbol}")
        print(f"  Side: {fill.side}")
        print(f"  Quantity: {fill.quantity:.6f}")
        print(f"  Price: ${fill.price:.2f}")
        print(f"  Status: {fill.status}")
        print(f"  Paper Mode: {fill.paper_mode}")
        
        # Get session PnL
        session_pnl = pnl_tracker.get_session_pnl()
        print(f"\n💰 Session PnL: ${session_pnl['total_pnl']:.2f}")
        print(f"📊 Trade Count: {session_pnl['trade_count']}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"💥 Execution engine error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

"""
Kraken Live Trading Interface

Real Kraken CLI integration for live trading execution.
This handles actual order placement, balance management, and PnL tracking.

Author: ENGR. MARCUS ODUYA - Execution VP at APEX
Standard: "Every order must be intentional. No ghost trades, no partial fills left open, no missed exits."
"""

import subprocess
import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KrakenLiveTrader:
    """
    Real Kraken trading interface using Kraken CLI.
    
    This class provides:
    - Real order placement via Kraken CLI
    - Balance management
    - PnL tracking
    - Connection testing
    """
    
    def __init__(self):
        """Initialize Kraken live trader."""
        self.api_key = os.getenv("KRAKEN_API_KEY")
        self.api_secret = os.getenv("KRAKEN_API_SECRET")
        self.cli_path = os.getenv("KRAKEN_CLI_PATH", "kraken")
        
        logger.info("KrakenLiveTrader initialized")
        logger.info(f"CLI Path: {self.cli_path}")
        logger.info(f"API Key configured: {'Yes' if self.api_key else 'No'}")
    
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance."""
        try:
            logger.info("Fetching account balance...")
            result = subprocess.run(
                [self.cli_path, "balance"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                balance_data = json.loads(result.stdout)
                logger.info("Balance fetched successfully")
                return balance_data
            else:
                error_msg = f"CLI error: {result.stderr}"
                logger.error(f"Balance fetch failed: {error_msg}")
                return {"error": error_msg}
                
        except subprocess.TimeoutExpired:
            error_msg = "Balance fetch timed out"
            logger.error(error_msg)
            return {"error": error_msg}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def place_market_order(self, pair: str, side: str, volume: float) -> Dict[str, Any]:
        """
        Place real market order via Kraken CLI.
        
        Args:
            pair: Trading pair (e.g., "XBTUSD")
            side: "buy" or "sell"
            volume: Order volume in base currency
            
        Returns:
            Order result with order ID and details
        """
        try:
            logger.info(f"Placing {side} market order: {volume} {pair}")
            
            result = subprocess.run(
                [self.cli_path, "order", "add",
                 "--pair", pair,
                 "--type", side,
                 "--ordertype", "market", 
                 "--volume", str(volume)],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                order_data = json.loads(result.stdout)
                logger.info(f"Order placed successfully: {order_data.get('txid', 'Unknown')}")
                return order_data
            else:
                error_msg = f"CLI error: {result.stderr}"
                logger.error(f"Order placement failed: {error_msg}")
                return {"error": error_msg}
                
        except subprocess.TimeoutExpired:
            error_msg = "Order placement timed out"
            logger.error(error_msg)
            return {"error": error_msg}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_pnl(self) -> Dict[str, Any]:
        """Get current PnL from trade history."""
        try:
            logger.info("Fetching PnL data...")
            result = subprocess.run(
                [self.cli_path, "trades", "history"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                pnl_data = json.loads(result.stdout)
                
                # Calculate simple PnL from trade history
                total_pnl = 0.0
                trade_count = 0
                
                if "trades" in pnl_data:
                    for trade in pnl_data["trades"]:
                        if "cost" in trade and "fee" in trade:
                            # Simple PnL calculation (cost + fee)
                            pnl = float(trade.get("cost", 0)) + float(trade.get("fee", 0))
                            total_pnl += pnl
                            trade_count += 1
                
                result_data = {
                    "total_pnl": total_pnl,
                    "trade_count": trade_count,
                    "raw_data": pnl_data
                }
                
                logger.info(f"PnL calculated: ${total_pnl:.2f} from {trade_count} trades")
                return result_data
            else:
                error_msg = f"CLI error: {result.stderr}"
                logger.error(f"PnL fetch failed: {error_msg}")
                return {"error": error_msg}
                
        except subprocess.TimeoutExpired:
            error_msg = "PnL fetch timed out"
            logger.error(error_msg)
            return {"error": error_msg}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def test_connection(self) -> bool:
        """Test if Kraken CLI is working and authenticated."""
        try:
            logger.info("Testing Kraken CLI connection...")
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"Kraken CLI working: {version}")
                
                # Test authentication with balance call
                balance_test = self.get_balance()
                if "error" not in balance_test:
                    logger.info("Kraken API authentication successful")
                    return True
                else:
                    logger.warning("CLI working but authentication failed")
                    return False
            else:
                logger.error(f"Kraken CLI not working: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Kraken CLI test timed out")
            return False
        except FileNotFoundError:
            logger.error(f"Kraken CLI not found at: {self.cli_path}")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_ticker(self, pair: str = "XBTUSD") -> Dict[str, Any]:
        """Get real-time ticker data."""
        try:
            logger.info(f"Fetching ticker for {pair}...")
            result = subprocess.run(
                [self.cli_path, "ticker", "--pair", pair],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                ticker_data = json.loads(result.stdout)
                logger.info(f"Ticker fetched for {pair}")
                return ticker_data
            else:
                error_msg = f"CLI error: {result.stderr}"
                logger.error(f"Ticker fetch failed: {error_msg}")
                return {"error": error_msg}
                
        except subprocess.TimeoutExpired:
            error_msg = "Ticker fetch timed out"
            logger.error(error_msg)
            return {"error": error_msg}
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg)
            return {"error": error_msg}


# Test function for development
def test_kraken_connection():
    """Test Kraken connection and show results."""
    print("=== Kraken Live Trading Test ===")
    
    trader = KrakenLiveTrader()
    
    # Test connection
    print("\n1. Testing connection...")
    connected = trader.test_connection()
    print(f"Connected: {connected}")
    
    if connected:
        # Get balance
        print("\n2. Getting balance...")
        balance = trader.get_balance()
        print(f"Balance: {json.dumps(balance, indent=2)}")
        
        # Get ticker
        print("\n3. Getting BTC ticker...")
        ticker = trader.get_ticker("XBTUSD")
        print(f"Ticker: {json.dumps(ticker, indent=2)}")
        
        # Get PnL
        print("\n4. Getting PnL...")
        pnl = trader.get_pnl()
        print(f"PnL: {json.dumps(pnl, indent=2)}")
    else:
        print("Connection failed - skipping further tests")


if __name__ == "__main__":
    test_kraken_connection()

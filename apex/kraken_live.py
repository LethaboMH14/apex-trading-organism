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
        # Check if we're running in WSL and use direct path
        if os.path.exists("/home/userlethabomh14/.cargo/bin/kraken"):
            self.kraken_cmd = ["/home/userlethabomh14/.cargo/bin/kraken"]
        else:
            # Fallback to WSL path
            self.kraken_cmd = [
                "wsl", "-e", 
                "/home/userlethabomh14/.cargo/bin/kraken"
            ]
        
        logger.info("KrakenLiveTrader initialized")
        logger.info(f"CLI Path: wsl")
        logger.info(f"API Key configured: {'Yes' if self.api_key else 'No'}")
    
    def _run(self, args):
        """Run kraken CLI command through WSL"""
        import subprocess
        try:
            result = subprocess.run(
                self.kraken_cmd + args,
                capture_output=True, text=True, timeout=30,
                env={
                    **os.environ,
                    "KRAKEN_API_KEY": self.api_key,
                    "KRAKEN_API_SECRET": self.api_secret
                }
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), 1
    
    def test_connection(self):
        stdout, stderr, code = self._run(["--version"])
        return code == 0, stdout.strip()
    
    def get_balance(self):
        stdout, stderr, code = self._run(["balance"])
        if code == 0:
            try:
                import json
                return json.loads(stdout)
            except:
                return {"raw": stdout}
        return {"error": stderr}
    
    def place_market_order(self, pair, side, volume):
        """Place real market order"""
        if side == "buy":
            stdout, stderr, code = self._run([
                "order", "buy", pair, str(volume), "--type", "market", "-o", "json"
            ])
        elif side == "sell":
            stdout, stderr, code = self._run([
                "order", "sell", pair, str(volume), "--type", "market", "-o", "json"
            ])
        else:
            return {"error": f"Invalid side: {side}"}
        
        if code == 0:
            try:
                import json
                return json.loads(stdout)
            except:
                return {"raw": stdout}
        return {"error": stderr}
    
    def get_pnl(self) -> Dict[str, Any]:
        """Get current PnL from trade history."""
        stdout, stderr, code = self._run(["trades", "history"])
        if code == 0:
            try:
                import json
                pnl_data = json.loads(stdout)
                
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
            except:
                return {"raw": stdout}
        return {"error": stderr}
    
    def test_connection(self):
        """Test if Kraken CLI is working and authenticated."""
        try:
            logger.info("Testing Kraken CLI connection...")
            stdout, stderr, code = self._run(["--version"])
            
            if code == 0:
                version = stdout.strip()
                logger.info(f"Kraken CLI working: {version}")
                
                # Test authentication with balance call
                balance_test = self.get_balance()
                if "error" not in balance_test:
                    logger.info("Kraken API authentication successful")
                    return True, version
                else:
                    logger.warning("CLI working but authentication failed")
                    return False, version
            else:
                logger.error(f"Kraken CLI not working: {stderr}")
                return False, "CLI not found"
        except subprocess.TimeoutExpired:
            logger.error("Kraken CLI test timed out")
            return False, "Test timed out"
        except FileNotFoundError:
            logger.error(f"Kraken CLI not found at: {self.cli_path}")
            return False, "CLI not found"
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False, "Unknown error"
    
    def get_ticker(self, pair: str = "XBTUSD") -> Dict[str, Any]:
        """Get real-time ticker data."""
        try:
            logger.info(f"Fetching ticker for {pair}...")
            result = subprocess.run(
                self.kraken_cmd + ["ticker", "--pair", pair],
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

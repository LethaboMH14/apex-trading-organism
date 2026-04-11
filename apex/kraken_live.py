"""
Kraken Live/Paper Trading Interface
ENGR. MARCUS ODUYA - Execution VP at APEX
Toggle PAPER_MODE=true in .env for paper trading (no real money needed)
Toggle PAPER_MODE=false for live trading (requires funded Kraken account)
"""

import subprocess
import json
import os
import logging
from typing import Dict, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KrakenLiveTrader:
    def __init__(self):
        self.api_key = os.getenv("KRAKEN_API_KEY", "")
        self.api_secret = os.getenv("KRAKEN_API_SECRET", "")
        self.paper_mode = os.getenv("PAPER_MODE", "true").lower() == "true"
        self.kraken_bin = "/home/userlethabomh14/.cargo/bin/kraken"
        self._paper_initialized = False
        
        mode = "PAPER" if self.paper_mode else "LIVE"
        logger.info(f"KrakenLiveTrader initialized | Mode: {mode}")
        
        if self.paper_mode and not self._paper_initialized:
            self._ensure_paper_initialized()

    def _run(self, args: list, include_auth: bool = False) -> tuple:
        """Run kraken CLI via WSL."""
        cmd = ["wsl", "-e", self.kraken_bin] + args
        env = dict(os.environ)
        if include_auth and self.api_key:
            env["KRAKEN_API_KEY"] = self.api_key
            env["KRAKEN_API_SECRET"] = self.api_secret
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=30, env=env, encoding='utf-8', errors='replace'
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "", "timeout", 1
        except Exception as e:
            return "", str(e), 1

    def _ensure_paper_initialized(self):
        """Ensure paper account is initialized - reset if balance < $300."""
        stdout, stderr, code = self._run(["paper", "status"])

        # Try to parse balance from status output
        try:
            import json as _json
            data = _json.loads(stdout)
            usd = float(data.get("USD", data.get("usd", 0)))
            if usd >= 300:
                logger.info(f"Paper account OK: ${usd:.2f} available")
                self._paper_initialized = True
                return
            else:
                logger.warning(f"Paper balance low: ${usd:.2f} — resetting to $10,000")
        except Exception:
            # If we can't parse, check raw text
            if "not initialized" not in stdout.lower() and code == 0:
                logger.info("Paper account status OK — skipping init")
                self._paper_initialized = True
                return

        # Reset and reinitialize
        logger.info("Resetting paper account to $10,000...")
        self._run(["paper", "reset"])
        import time as _time
        _time.sleep(2)
        stdout2, stderr2, code2 = self._run(
            ["paper", "init", "--balance", "10000"]
        )
        if code2 == 0:
            logger.info("Paper account reset to $10,000 ✅")
            self._paper_initialized = True
        else:
            logger.warning(f"Paper reset failed: {stderr2}")

    def test_connection(self) -> tuple:
        """Test if Kraken CLI is working."""
        stdout, stderr, code = self._run(["--version"])
        if code == 0:
            logger.info(f"Kraken CLI OK: {stdout}")
            return True, stdout
        return False, stderr

    def get_balance(self) -> Dict[str, Any]:
        """Get balance — paper or live."""
        if self.paper_mode:
            stdout, stderr, code = self._run(["paper", "balance", "-o", "json"])
        else:
            stdout, stderr, code = self._run(["balance", "-o", "json"], include_auth=True)
        
        if code == 0 and stdout:
            try:
                data = json.loads(stdout)
                data["mode"] = "paper" if self.paper_mode else "live"
                return data
            except json.JSONDecodeError:
                return {"raw": stdout, "mode": "paper" if self.paper_mode else "live"}
        return {"error": stderr, "mode": "paper" if self.paper_mode else "live"}

    def place_market_order(self, pair: str, side: str, volume: float) -> Dict[str, Any]:
        """Place market order — paper or live."""
        # Ensure paper balance is sufficient before attempting order
        if self.paper_mode:
            self._ensure_paper_initialized()

        # Normalize pair: XBTUSD -> BTCUSD for paper mode
        paper_pair = pair.replace("XBT", "BTC")
        live_pair = pair

        # Enforce minimum volume
        volume = max(round(volume, 6), 0.0001)

        if self.paper_mode:
            # Try different pair formats - Kraken paper CLI is strict about format
            pair_formats = [paper_pair, pair, pair.replace("XBT", "BTC"), "BTC/USD" if "BTC" in pair.upper() or "XBT" in pair.upper() else pair]
            stdout, stderr, code = "", "", 1
            for fmt in pair_formats:
                stdout, stderr, code = self._run([
                    "paper", side.lower(), fmt, str(volume), "-o", "json"
                ])
                logger.info(f"Kraken paper attempt: pair={fmt} vol={volume} | stdout={stdout[:100]} | stderr={stderr[:100]} | code={code}")
                if code == 0 and stdout:
                    break
            if code != 0:
                # Try without -o json flag as fallback
                stdout, stderr, code = self._run([
                    "paper", side.lower(), paper_pair, str(volume)
                ])
                logger.info(f"Kraken paper fallback (no json flag): stdout={stdout[:100]} | stderr={stderr[:100]} | code={code}")
        else:
            stdout, stderr, code = self._run([
                "order", side.lower(), live_pair, str(volume),
                "--type", "market", "-o", "json"
            ], include_auth=True)
        
        if code == 0 and stdout:
            try:
                data = json.loads(stdout)
                data["success"] = True
                data["mode"] = "paper" if self.paper_mode else "live"
                logger.info(f"{'[PAPER]' if self.paper_mode else '[LIVE]'} {side.upper()} {volume} {pair}")
                return data
            except json.JSONDecodeError:
                return {"success": True, "raw": stdout, "mode": "paper" if self.paper_mode else "live"}
        
        logger.warning(f"Order failed: {stderr}")
        return {"success": False, "error": stderr, "mode": "paper" if self.paper_mode else "live"}

    def get_paper_status(self) -> Dict[str, Any]:
        """Get full paper trading status including P&L."""
        stdout, stderr, code = self._run(["paper", "status", "-o", "json"])
        if code == 0 and stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                return {"raw": stdout}
        return {"error": stderr}

    def get_paper_history(self) -> Dict[str, Any]:
        """Get paper trade history."""
        stdout, stderr, code = self._run(["paper", "history", "-o", "json"])
        if code == 0 and stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                return {"raw": stdout}
        return {"error": stderr}

    def get_ticker(self, pair: str = "BTCUSD") -> Dict[str, Any]:
        """Get live ticker — works without auth."""
        stdout, stderr, code = self._run(["ticker", pair, "-o", "json"])
        if code == 0 and stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                return {"raw": stdout}
        return {"error": stderr}

    def get_pnl(self) -> Dict[str, Any]:
        """Get PnL from paper or live trade history."""
        if self.paper_mode:
            status = self.get_paper_status()
            return {
                "mode": "paper",
                "pnl_data": status,
                "success": "error" not in status
            }
        stdout, stderr, code = self._run(["trades", "history", "-o", "json"], include_auth=True)
        if code == 0 and stdout:
            try:
                return {"mode": "live", "raw": json.loads(stdout), "success": True}
            except json.JSONDecodeError:
                return {"mode": "live", "raw": stdout, "success": True}
        return {"error": stderr, "success": False}


def test_kraken_connection():
    trader = KrakenLiveTrader()
    print(f"\nMode: {'PAPER' if trader.paper_mode else 'LIVE'}")
    
    ok, ver = trader.test_connection()
    print(f"CLI Connected: {ok} ({ver})")
    
    balance = trader.get_balance()
    print(f"Balance: {json.dumps(balance, indent=2)}")
    
    if trader.paper_mode:
        print("\nPlacing test paper BUY order (0.001 BTC)...")
        order = trader.place_market_order("BTCUSD", "buy", 0.001)
        print(f"Order result: {json.dumps(order, indent=2)}")
        
        status = trader.get_paper_status()
        print(f"Paper P&L status: {json.dumps(status, indent=2)}")


if __name__ == "__main__":
    test_kraken_connection()

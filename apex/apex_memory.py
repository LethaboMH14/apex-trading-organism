#!/usr/bin/env python3
"""
APEX Memory System - Trade history and learning
Tracks past trades to inform future decisions.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

MEMORY_FILE = "trade_memory.jsonl"


def log_trade(
    action: str,
    price: float,
    confidence: int,
    outcome: bool,
    reasoning: str,
    tx_hash: str = "",
    pair: str = "BTC"
) -> None:
    """Log a completed trade to memory."""
    trade_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "price": price,
        "confidence": confidence,
        "outcome": outcome,
        "reasoning": reasoning[:200],  # Truncate reasoning
        "tx_hash": tx_hash,
        "pair": pair
    }
    
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(trade_entry) + "\n")


def load_recent_trades(n: int = 10) -> List[Dict]:
    """Load the last n trades from memory."""
    if not Path(MEMORY_FILE).exists():
        return []
    
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        trades = [json.loads(line) for line in lines]
        return trades[-n:]  # Return last n trades
    except Exception as e:
        print(f"Error loading trade memory: {e}")
        return []


def get_memory_count() -> int:
    """Get total number of trades in memory."""
    if not Path(MEMORY_FILE).exists():
        return 0
    
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return len(f.readlines())
    except Exception as e:
        print(f"Error counting trade memory: {e}")
        return 0


def analyze_recent_bias(n: int = 3) -> Optional[str]:
    """
    Analyze recent trades for bias.
    Returns 'BUY' or 'SELL' if a bias is detected, None otherwise.
    """
    recent_trades = load_recent_trades(n)
    if len(recent_trades) < n:
        return None
    
    # Check if all recent trades were the same action
    actions = [trade["action"] for trade in recent_trades]
    if all(action == "BUY" for action in actions):
        # Check if price dropped (simple heuristic)
        first_price = recent_trades[0]["price"]
        last_price = recent_trades[-1]["price"]
        if last_price < first_price:
            return "SELL"  # Bias toward SELL if all BUYs and price dropped
    
    if all(action == "SELL" for action in actions):
        # Check if price rose
        first_price = recent_trades[0]["price"]
        last_price = recent_trades[-1]["price"]
        if last_price > first_price:
            return "BUY"  # Bias toward BUY if all SELLs and price rose
    
    return None


def format_trades_for_prompt(trades: List[Dict]) -> str:
    """Format trades for inclusion in AI prompt."""
    if not trades:
        return "No recent trade history available."
    
    formatted = []
    for i, trade in enumerate(reversed(trades), 1):
        formatted.append(
            f"{i}. {trade['action']} {trade['pair']} @ ${trade['price']:.2f} "
            f"(confidence: {trade['confidence']}%, outcome: {'SUCCESS' if trade['outcome'] else 'FAILED'})"
        )
    
    return "\n".join(formatted)


def get_win_rate(n: int = 10) -> float:
    """Calculate win rate for last n trades."""
    trades = load_recent_trades(n)
    if not trades:
        return 0.0
    
    wins = sum(1 for trade in trades if trade["outcome"])
    return (wins / len(trades)) * 100

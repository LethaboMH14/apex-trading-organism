"""
APEX NLP - Advanced News Impact & Narrative Analysis

DR. JABARI MENSAH: VP of Social Intelligence at APEX.
Background: Jamaican-American. Stanford PhD Computational Social Science.
Standard: "The market is a story told by humans. Before numbers move, words have already moved."
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp
import numpy as np

from dotenv import load_dotenv, find_dotenv
from apex_llm_router import ask_jabari

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv(find_dotenv(), override=True)


class NarrativeShiftDetector:
    """Detects narrative shifts in sentiment over time windows."""
    
    def __init__(self):
        self.sentiment_history = {}
        logger.info("🔍 NarrativeShiftDetector initialized")
    
    def detect_shift(self, symbol: str) -> Dict[str, Any]:
        """Detect narrative shift by comparing 1h vs 24h sentiment."""
        # Mock data for demo
        current_1h = np.random.normal(50, 10)
        baseline_24h = np.random.normal(50, 5)
        
        shift_magnitude = abs(current_1h - baseline_24h)
        shift_detected = shift_magnitude > 15
        
        if shift_detected:
            direction = "bullish_shift" if current_1h > baseline_24h else "bearish_shift"
        else:
            direction = "stable"
        
        confidence = min(shift_magnitude / 20, 1.0)
        
        return {
            "shift_detected": shift_detected,
            "direction": direction,
            "magnitude": shift_magnitude,
            "confidence": confidence,
            "current_1h": current_1h,
            "baseline_24h": baseline_24h
        }


class NewsImpactScorer:
    """Scores news articles for expected price impact."""
    
    def __init__(self):
        self.api_key = os.getenv("BYTEPLUS_API_KEY", "")
        logger.info("📊 NewsImpactScorer initialized")
    
    async def score_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Score individual article for sentiment and impact."""
        # Mock scoring
        sentiment = np.random.uniform(-1, 1)
        relevance = np.random.uniform(0.5, 1.0)
        price_impact = sentiment * relevance
        
        # Time decay calculation
        hours_old = 2
        time_decay = 0.5 ** (hours_old / 2)
        decayed_impact = price_impact * time_decay
        
        return {
            "sentiment": sentiment,
            "relevance_to_symbol": relevance,
            "expected_price_impact": price_impact,
            "time_decay_factor": time_decay,
            "decayed_impact": decayed_impact
        }
    
    async def aggregate_impact(self, articles: List[Dict], symbol: str) -> float:
        """Aggregate impacts from multiple articles."""
        if not articles:
            return 0.0
        
        scores = []
        for article in articles:
            score = await self.score_article(article)
            scores.append(score["decayed_impact"])
        
        return np.mean(scores)


class SocialSignalExtractor:
    """Extracts social signals from text."""
    
    def __init__(self):
        # Keywords for signal detection
        self.whale_keywords = ["whale", "large holder", "institutional", "accumulation"]
        self.exchange_keywords = ["exchange inflow", "outflow", "listing", "delisting"]
        self.regulatory_keywords = ["regulation", "sec", "compliance", "ban", "approval"]
        self.technical_keywords = ["support", "resistance", "$", "level", "breakout"]
        
        logger.info("📡 SocialSignalExtractor initialized")
    
    def extract_signals(self, text: str) -> Dict[str, Any]:
        """Extract various signal types from text."""
        text_lower = text.lower()
        
        # Signal detection
        whale_signals = self._detect_signals(text_lower, self.whale_keywords)
        exchange_signals = self._detect_signals(text_lower, self.exchange_keywords)
        regulatory_signals = self._detect_signals(text_lower, self.regulatory_keywords)
        technical_signals = self._detect_signals(text_lower, self.technical_keywords)
        
        return {
            "whale_mentions": whale_signals,
            "exchange_flow_signals": exchange_signals,
            "regulatory_keywords": regulatory_signals,
            "technical_level_mentions": technical_signals
        }
    
    def _detect_signals(self, text: str, keywords: List[str]) -> Dict[str, Any]:
        """Detect specific keyword signals."""
        matches = []
        for keyword in keywords:
            if keyword in text:
                matches.append(keyword)
        
        confidence = len(matches) / len(keywords) if keywords else 0
        
        return {
            "matches": matches,
            "confidence": confidence,
            "count": len(matches)
        }


class ReasonChainBuilder:
    """Builds human-readable reasoning chains."""
    
    def __init__(self):
        logger.info("🔗 ReasonChainBuilder initialized")
    
    def build(self, signals: Dict, sentiment: Dict, narrative: Dict) -> str:
        """Build reasoning chain from NLP analysis."""
        # Extract key insights
        signal_summary = self._summarize_signals(signals)
        sentiment_summary = self._summarize_sentiment(sentiment)
        narrative_summary = self._summarize_narrative(narrative)
        
        # Determine recommendation
        recommendation = self._determine_recommendation(sentiment, narrative)
        
        # Build chain
        chain = f"Signals: {signal_summary}. Sentiment: {sentiment_summary}. Narrative: {narrative_summary}. NLP Recommendation: {recommendation}."
        
        return chain
    
    def _summarize_signals(self, signals: Dict) -> str:
        """Summarize detected signals."""
        active_signals = []
        for signal_type, data in signals.items():
            if data.get("count", 0) > 0:
                active_signals.append(signal_type.replace("_", " "))
        
        return ", ".join(active_signals) if active_signals else "no significant signals"
    
    def _summarize_sentiment(self, sentiment: Dict) -> str:
        """Summarize sentiment analysis."""
        score = sentiment.get("sentiment", 0)
        if score > 0.3:
            return f"bullish sentiment ({score:.2f})"
        elif score < -0.3:
            return f"bearish sentiment ({score:.2f})"
        else:
            return f"neutral sentiment ({score:.2f})"
    
    def _summarize_narrative(self, narrative: Dict) -> str:
        """Summarize narrative analysis."""
        if narrative.get("shift_detected"):
            return f"{narrative.get('direction')} detected ({narrative.get('magnitude', 0):.1f} points)"
        else:
            return "stable narrative"
    
    def _determine_recommendation(self, sentiment: Dict, narrative: Dict) -> str:
        """Determine trading recommendation."""
        sentiment_score = sentiment.get("sentiment", 0)
        narrative_shift = narrative.get("magnitude", 0)
        narrative_direction = narrative.get("direction", "stable")
        
        # Combined scoring
        total_score = sentiment_score * 0.6 + (narrative_shift / 20) * 0.4
        
        if narrative_direction == "bullish_shift":
            total_score += 0.2
        elif narrative_direction == "bearish_shift":
            total_score -= 0.2
        
        confidence = min(abs(total_score) * 100, 95)
        
        if total_score > 0.3:
            return f"BUY with {confidence:.0f}% confidence"
        elif total_score < -0.3:
            return f"SELL with {confidence:.0f}% confidence"
        else:
            return f"HOLD with {confidence:.0f}% confidence"


async def main():
    """Main execution function."""
    logger.info("🚀 Starting APEX NLP Pipeline")
    
    try:
        # Initialize components
        shift_detector = NarrativeShiftDetector()
        impact_scorer = NewsImpactScorer()
        signal_extractor = SocialSignalExtractor()
        reason_builder = ReasonChainBuilder()
        
        # Sample news article
        sample_article = {
            "title": "Major Exchange Announces BTC Listing",
            "summary": "A leading cryptocurrency exchange announced it will list Bitcoin trading pairs, potentially driving significant inflows. Whale accumulation has been observed in recent days.",
            "url": "https://example.com/news",
            "published_at": datetime.now()
        }
        
        print("\n" + "="*60)
        print("📰 APEX NLP PIPELINE DEMO")
        print("="*60)
        
        # Extract signals
        text = f"{sample_article['title']} {sample_article['summary']}"
        signals = signal_extractor.extract_signals(text)
        print(f"📡 Extracted Signals: {signals}")
        
        # Score impact
        impact = await impact_scorer.score_article(sample_article)
        print(f"📊 Article Impact: {impact}")
        
        # Detect narrative shift
        shift = shift_detector.detect_shift("BTC")
        print(f"🔍 Narrative Shift: {shift}")
        
        # Build reasoning chain
        reason_chain = reason_builder.build(signals, impact, shift)
        print(f"\n🔗 Reason Chain: {reason_chain}")
        
        print("="*60)
        print("🚀 NLP Pipeline Demo Complete")
        
    except Exception as e:
        logger.error(f"💥 NLP pipeline error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

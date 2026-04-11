"""
APEX Sentiment Analysis - Social Intelligence Pipeline

DR. JABARI MENSAH: VP of Social Intelligence at APEX.

Background: Jamaican-American. Stanford PhD Computational Social Science. Built Twitter-based 
alpha signal models used by two hedge funds.

This module implements complete sentiment analysis pipeline for APEX, ingesting 
crypto news from multiple sources and analyzing sentiment using BytePlus ModelArk API. 
All results are validated, scored, and stored for trading decisions.

Author: DR. JABARI MENSAH
Standard: "The market is a story told by humans. Before numbers move, words have already moved."
"""

import asyncio
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from urllib.parse import urljoin
import aiohttp
from pydantic import BaseModel, Field, validator

# APEX imports
from dotenv import load_dotenv, find_dotenv
from apex_llm_router import LLMRouter, LLMProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables with override
load_dotenv(find_dotenv(), override=True)


class SentimentResult(BaseModel):
    """Model for sentiment analysis result."""
    symbol: str = Field(..., description="Asset symbol")
    score: float = Field(..., ge=-100.0, le=100.0, description="Sentiment score -100 to 100")
    label: str = Field(..., description="Sentiment label: bearish/neutral/bullish")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level 0 to 1")
    article_count: int = Field(..., ge=0, description="Number of articles analyzed")
    narrative_tags: List[str] = Field(default_factory=list, description="Detected narrative themes")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")


class NarrativeAnalysis(BaseModel):
    """Model for narrative theme analysis."""
    themes: List[str] = Field(..., description="Detected narrative themes")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Theme confidence")
    risk_level: str = Field(..., description="Risk level: low/medium/high")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")


class NewsArticle(BaseModel):
    """Model for individual news article."""
    title: str = Field(..., description="Article title")
    summary: str = Field(..., description="Article summary")
    url: str = Field(..., description="Article URL")
    source: str = Field(..., description="News source")
    published_at: datetime = Field(..., description="Publication timestamp")
    symbol_mentions: List[str] = Field(default_factory=list, description="Mentioned symbols")


class GroqSentimentAnalyzer:
    """
    Groq Sentiment Analyzer - Uses Groq LLM for sentiment analysis.
    
    Replaces BytePlus NLP client with Groq-based sentiment analysis
    to avoid 401 errors. Uses the LLM router for Groq access.
    """
    
    def __init__(self):
        """Initialize Groq sentiment analyzer."""
        self.llm_router = LLMRouter()
        logger.info("🧠 Groq Sentiment Analyzer initialized")
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a text using Groq.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        logger.debug(f"📝 Analyzing sentiment: {len(text)} characters")
        
        prompt = f"""Analyze the sentiment of this text and return a JSON response with:
- score: a number from 0 to 100 (0 = very bearish, 50 = neutral, 100 = very bullish)
- label: "bearish", "neutral", or "bullish"
- confidence: a number from 0 to 1

Text: {text}

Return only valid JSON, no other text."""
        
        try:
            response = await self.llm_router.call(
                "DR_JABARI",
                [{"role": "user", "content": prompt}]
            )
            
            if response and response.get("response"):
                # Try to parse JSON from response
                import re
                json_match = re.search(r'\{[^}]+\}', response["response"])
                if json_match:
                    import json
                    result = json.loads(json_match.group())
                    return {
                        "score": float(result.get("score", 50.0)),
                        "label": result.get("label", "neutral"),
                        "confidence": float(result.get("confidence", 0.5))
                    }
        except Exception as e:
            logger.warning(f"Groq sentiment analysis failed: {e}")
        
        # Return default sentiment on error
        return {
            "score": 50.0,
            "label": "neutral",
            "confidence": 0.5
        }
    
    async def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple texts in batch using Groq.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        logger.info(f"📊 Batch analyzing {len(texts)} texts with Groq")
        
        results = []
        
        # Analyze each text individually (Groq doesn't have batch endpoint)
        for i, text in enumerate(texts):
            logger.debug(f"📦 Processing text {i+1}/{len(texts)}")
            result = await self.analyze_sentiment(text)
            results.append({
                "text": text,
                "score": result["score"],
                "label": result["label"],
                "confidence": result["confidence"]
            })
        
        logger.info(f"✅ Batch analysis complete: {len(results)} results")
        return results
    
    async def classify_narrative(self, texts: List[str]) -> NarrativeAnalysis:
        """
        Classify narrative themes in texts using Groq.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            NarrativeAnalysis with detected themes and risk level
        """
        logger.info(f"🔍 Classifying narrative themes in {len(texts)} texts")
        
        combined_text = "\n\n".join(texts[:5])  # Limit to 5 texts to avoid token limits
        
        prompt = f"""Analyze these news articles and identify key narrative themes. Return JSON with:
- themes: list of 3-5 main themes (e.g., "regulation", "adoption", "security", "market sentiment", "technology")
- confidence: number from 0 to 1

Articles:
{combined_text}

Return only valid JSON, no other text."""
        
        try:
            response = await self.llm_router.call(
                "DR_JABARI",
                [{"role": "user", "content": prompt}]
            )
            
            if response and response.get("response"):
                import re
                json_match = re.search(r'\{[^}]+\}', response["response"])
                if json_match:
                    import json
                    result = json.loads(json_match.group())
                    themes = result.get("themes", ["general"])
                    
                    # Determine risk level
                    risk_indicators = [theme for theme in themes if "risk" in theme.lower() or "regulation" in theme.lower()]
                    risk_level = "high" if risk_indicators else "medium" if len(themes) > 3 else "low"
                    
                    return NarrativeAnalysis(
                        themes=themes,
                        confidence=float(result.get("confidence", 0.5)),
                        risk_level=risk_level,
                        timestamp=datetime.now()
                    )
        except Exception as e:
            logger.warning(f"Groq narrative classification failed: {e}")
        
        # Return default analysis on error
        return NarrativeAnalysis(
            themes=["general"],
            confidence=0.5,
            risk_level="medium",
            timestamp=datetime.now()
        )


class CryptoNewsAggregator:
    """
    Crypto News Aggregator - Collects crypto news from multiple sources.
    
    Fetches news from CoinDesk, Decrypt, CoinTelegraph, and The Block RSS feeds.
    Filters for symbol mentions and deduplicates by URL. Provides 
    comprehensive coverage of crypto market news.
    """
    
    def __init__(self):
        """Initialize crypto news aggregator."""
        self.sources = {
            "coindesk": "https://www.coindesk.com/arc/outbound-rss.xml",
            "decrypt": "https://decrypt.co/feed",
            "cointelegraph": "https://cointelegraph.com/rss"
        }
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Charset": "utf-8",
        }
        
        logger.info("📰 Crypto News Aggregator initialized")
        logger.info(f"📊 News sources: {', '.join(self.sources.keys())}")
    
    async def _fetch_rss_feed(self, source_name: str, url: str) -> List[NewsArticle]:
        """
        Fetch and parse RSS feed from a news source.
        
        Args:
            source_name: Name of the news source
            url: RSS feed URL
            
        Returns:
            List of NewsArticle objects
        """
        logger.debug(f"📡 Fetching {source_name} RSS feed")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text(encoding='utf-8')
                        
                        # Parse RSS content
                        articles = []
                        
                        # Simple RSS parsing (would use xml.etree in production)
                        items = re.findall(r'<item[^>]*>(.*?)</item>', content, re.DOTALL)
                        
                        for item in items[:20]:  # Limit to 20 most recent
                            # Extract title
                            title_match = re.search(r'<title[^>]*>(.*?)</title>', item)
                            title = title_match.group(1).strip() if title_match else "No Title"
                            
                            # Extract summary
                            summary_match = re.search(r'<description[^>]*>(.*?)</description>', item)
                            summary = summary_match.group(1).strip() if summary_match else "No Summary"
                            
                            # Extract link
                            link_match = re.search(r'<link[^>]*>(.*?)</link>', item)
                            url = link_match.group(1).strip() if link_match else ""
                            
                            # Extract publication date
                            date_match = re.search(r'<pubDate[^>]*>(.*?)</pubDate>', item)
                            try:
                                pub_date = datetime.fromisoformat(date_match.group(1).strip())
                            except:
                                pub_date = datetime.now()
                            
                            articles.append(NewsArticle(
                                title=title,
                                summary=summary,
                                url=url,
                                source=source_name,
                                published_at=pub_date,
                                symbol_mentions=[]
                            ))
                        
                        logger.info(f"📰 Fetched {len(articles)} articles from {source_name}")
                        return articles
                    
                    else:
                        logger.error(f"❌ Failed to fetch {source_name}: HTTP {response.status}")
                        return []
                        
        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout fetching {source_name}")
            return []
        except Exception as e:
            logger.error(f"❌ Error fetching {source_name}: {e}")
            return []
    
    async def get_recent_news(self, symbol: str, hours: int = 4) -> List[NewsArticle]:
        """
        Get recent news mentioning a specific symbol.
        
        Args:
            symbol: Trading symbol to filter for
            hours: How many hours back to look
            
        Returns:
            List of NewsArticle objects mentioning the symbol
        """
        logger.info(f"🔍 Getting recent news for {symbol} (last {hours} hours)")
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        all_articles = []
        
        # Fetch from all sources
        tasks = []
        for source_name, url in self.sources.items():
            task = self._fetch_rss_feed(source_name, url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for source_name, articles in zip(self.sources.keys(), results):
            if isinstance(articles, list):
                all_articles.extend(articles)
        
        # Filter by symbol and time
        symbol_articles = []
        
        # Map trading symbols to common news keywords
        symbol_keywords = {
            'XBTUSD': ['XBTUSD', 'Bitcoin', 'BTC', 'bitcoin'],
            'ETHUSD': ['ETHUSD', 'Ethereum', 'ETH', 'ethereum'],
            'SOLUSD': ['SOLUSD', 'Solana', 'SOL', 'solana']
        }
        
        # Get keywords for this symbol (default to symbol itself if not mapped)
        keywords = symbol_keywords.get(symbol, [symbol])
        
        for article in all_articles:
            # Check if article mentions any of the symbol's keywords (case-insensitive)
            article_text = article.title + ' ' + article.summary
            for keyword in keywords:
                keyword_pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                if keyword_pattern.search(article_text):
                    article.symbol_mentions.append(symbol)
                    symbol_articles.append(article)
                    break  # Only add article once even if it matches multiple keywords
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_articles = []
        for article in symbol_articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        logger.info(f"📰 Found {len(unique_articles)} articles mentioning {symbol}")
        return unique_articles
    
    async def get_all_recent_news(self, hours: int = 4) -> List[NewsArticle]:
        """
        Get all recent crypto news from all sources.
        
        Args:
            hours: How many hours back to look
            
        Returns:
            List of NewsArticle objects from all sources
        """
        logger.info(f"📰 Getting all recent crypto news (last {hours} hours)")
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        all_articles = []
        
        # Fetch from all sources
        tasks = []
        for source_name, url in self.sources.items():
            task = self._fetch_rss_feed(source_name, url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for source_name, articles in zip(self.sources.keys(), results):
            if isinstance(articles, list):
                all_articles.extend(articles)
        
        # Remove duplicates and filter by time
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.url not in seen_urls and article.published_at >= cutoff_time:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        logger.info(f"📰 Found {len(unique_articles)} total articles")
        return unique_articles


class SentimentPipeline:
    """
    Sentiment Pipeline - Orchestrates sentiment analysis for APEX.
    
    Combines crypto news aggregation with Groq LLM analysis to provide 
    comprehensive market sentiment intelligence. Scores and stores results for 
    trading decisions and risk assessment.
    """
    
    def __init__(self):
        """Initialize sentiment pipeline."""
        self.nlp_client = GroqSentimentAnalyzer()
        self.news_aggregator = CryptoNewsAggregator()
        
        logger.info("🧠 Sentiment Pipeline initialized with Groq")
    
    async def score_symbol(self, symbol: str) -> SentimentResult:
        """
        Calculate sentiment score for a specific symbol.
        
        Args:
            symbol: Trading symbol to score
            
        Returns:
            SentimentResult with aggregated sentiment analysis
        """
        logger.info(f"📈 Calculating sentiment score for {symbol}")
        
        try:
            # Get recent news mentioning the symbol
            news_articles = await self.news_aggregator.get_recent_news(symbol, hours=6)
            
            if not news_articles:
                return SentimentResult(
                    symbol=symbol,
                    score=0.0,
                    label="neutral",
                    confidence=0.0,
                    article_count=0,
                    narrative_tags=[],
                    timestamp=datetime.now()
                )
            
            # Extract text content for analysis
            news_texts = []
            for article in news_articles:
                text = f"{article.title}. {article.summary}"
                news_texts.append(text)
            
            # Analyze sentiment with BytePlus
            sentiment_results = await self.nlp_client.batch_analyze(news_texts)
            
            # Aggregate scores
            total_score = 0.0
            weighted_confidence = 0.0
            valid_results = [r for r in sentiment_results if "error" not in r]
            
            if valid_results:
                for result, text in zip(valid_results, news_texts):
                    # Weight by article recency (more recent = higher weight)
                    hours_ago = (datetime.now() - news_articles[valid_results.index(result)].published_at).total_seconds() / 3600
                    recency_weight = max(0.1, 1.0 - (hours_ago / 24))  # Decay over 24 hours
                    
                    total_score += result["score"] * result["confidence"] * recency_weight
                    weighted_confidence += result["confidence"] * recency_weight
                
                # Normalize scores
                if weighted_confidence > 0:
                    final_score = total_score / weighted_confidence
                    final_confidence = weighted_confidence / len(valid_results)
                else:
                    final_score = 0.0
                    final_confidence = 0.0
            
                # Determine label
                if final_score > 0.1:
                    label = "bullish"
                elif final_score < -0.1:
                    label = "bearish"
                else:
                    label = "neutral"
            
                # Get narrative themes
                all_texts = [article.title + '. ' + article.summary for article in news_articles]
                narrative_analysis = await self.nlp_client.classify_narrative(all_texts)
            
                return SentimentResult(
                    symbol=symbol,
                    score=final_score,
                    label=label,
                    confidence=final_confidence,
                    article_count=len(valid_results),
                    narrative_tags=narrative_analysis.themes,
                    timestamp=datetime.now()
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to score symbol {symbol}: {e}")
            return SentimentResult(
                symbol=symbol,
                score=0.0,
                label="neutral",
                confidence=0.0,
                article_count=0,
                narrative_tags=[],
                timestamp=datetime.now()
            )
    
    async def run_cycle(self) -> Dict[str, Any]:
        """
        Run a complete sentiment analysis cycle.
        
        Returns:
            Dictionary containing cycle results and metadata
        """
        cycle_start = time.time()
        logger.info("🔄 Starting sentiment analysis cycle")
        
        try:
            # Get configured symbols from environment
            symbols_str = os.getenv("APEX_SYMBOLS", "XBTUSD,ETHUSD,SOLUSD")
            symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]
            
            # Analyze each symbol
            results = {}
            for symbol in symbols:
                results[symbol] = await self.score_symbol(symbol)
            
            # Compile cycle results
            cycle_results = {
                "cycle_type": "sentiment_analysis",
                "timestamp": datetime.now().isoformat(),
                "symbols": symbols,
                "symbol_scores": {symbol: asdict(results[symbol]) for symbol in symbols},
                "duration": time.time() - cycle_start,
                "articles_analyzed": sum(result.article_count for result in results.values()),
                "avg_confidence": sum(result.confidence for result in results.values()) / len(results) if results else 0
            }
            
            logger.info(f"✅ Sentiment cycle completed in {cycle_results['duration']:.2f}s")
            logger.info(f"📰 Analyzed {cycle_results['articles_analyzed']} articles")
            logger.info(f"📊 Average confidence: {cycle_results['avg_confidence']:.2f}")
            
            return cycle_results
            
        except Exception as e:
            duration = time.time() - cycle_start
            logger.error(f"❌ Sentiment cycle failed after {duration:.2f}s: {e}")
            
            return {
                "cycle_type": "sentiment_analysis",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "duration": duration,
                "symbols": symbols,
                "symbol_scores": {}
            }


# Main execution function
async def main():
    """Main entry point for APEX sentiment pipeline."""
    logger.info("🧠 Starting APEX Sentiment Pipeline")
    
    try:
        # Initialize sentiment pipeline
        pipeline = SentimentPipeline()
        
        # Run a single sentiment analysis cycle
        logger.info("🔄 Running sentiment analysis cycle...")
        results = await pipeline.run_cycle()
        
        # Display results
        print("\n" + "="*60)
        print("🧠 APEX SENTIMENT ANALYSIS RESULTS")
        print("="*60)
        print(f"🕐 Timestamp: {results['timestamp']}")
        print(f"📊 Symbols Analyzed: {', '.join(results['symbols'])}")
        print(f"📰 Articles Analyzed: {results['articles_analyzed']}")
        print(f"⏱️ Duration: {results['duration']:.2f}s")
        
        if "error" not in results:
            print("\n📈 SYMBOL SENTIMENT SCORES:")
            for symbol, score_data in results["symbol_scores"].items():
                print(f"  {symbol}: {score_data['label']} "
                      f"(Score: {score_data['score']:.2f}, "
                      f"Confidence: {score_data['confidence']:.2f}, "
                      f"Articles: {score_data['article_count']})")
            
            print("\n📋 NARRATIVE THEMES DETECTED:")
            for symbol, score_data in results["symbol_scores"].items():
                if score_data["narrative_tags"]:
                    themes = ", ".join(score_data["narrative_tags"][:3])
                    print(f"  {symbol}: {themes}")
        else:
            print(f"\n❌ ERROR: {results['error']}")
        
        print("="*60)
        
    except KeyboardInterrupt:
        logger.info("🛑 Sentiment pipeline stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error in sentiment pipeline: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("🏁 APEX Sentiment Pipeline shutdown complete")


if __name__ == "__main__":
    """
    Entry point for APEX sentiment pipeline.
    
    Run this module directly to execute sentiment analysis:
    $ python apex-sentiment.py
    """
    asyncio.run(main())

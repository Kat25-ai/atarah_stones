"""
AI Engine for the Fundamental News Trading Dashboard
Advanced AI capabilities for market analysis and signal generation
"""

import openai
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import json
import logging
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from config import AI_CONFIG, API_KEYS
from models import (
    EconomicEvent, NewsItem, SentimentAnalysis, TradingSignal,
    MarketData, EventImpact, SentimentType, TradeType
)

logger = logging.getLogger(__name__)

class AITradingEngine:
    """Advanced AI engine for trading analysis and signal generation"""
    
    def __init__(self):
        self.openai_client = None
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.setup_openai()
        
    def setup_openai(self):
        """Setup OpenAI client if API key is available"""
        api_key = API_KEYS.get('OPENAI_API_KEY')
        if api_key and api_key != '':
            try:
                openai.api_key = api_key
                self.openai_client = openai
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.info("OpenAI API key not provided - using basic AI features only")
    
    def analyze_market_context(self, events: List[EconomicEvent], news: List[NewsItem]) -> Dict:
        """Analyze overall market context using AI"""
        
        # Basic analysis without OpenAI
        context = {
            'high_impact_events': len([e for e in events if e.is_high_impact]),
            'avg_safety_score': np.mean([e.safety_score for e in events]) if events else 50,
            'news_sentiment': self._analyze_news_sentiment_batch(news),
            'market_bias': 'neutral',
            'volatility_expectation': 'medium',
            'trading_recommendation': 'cautious'
        }
        
        # Enhanced analysis with OpenAI if available
        if self.openai_client:
            try:
                enhanced_context = self._get_openai_market_analysis(events, news)
                context.update(enhanced_context)
            except Exception as e:
                logger.warning(f"OpenAI analysis failed, using basic analysis: {e}")
        
        return context
    
    def _analyze_news_sentiment_batch(self, news: List[NewsItem]) -> Dict:
        """Analyze sentiment for a batch of news items"""
        if not news:
            return {
                'overall_sentiment': 0.0,
                'sentiment_strength': 0.0,
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0
            }
        
        sentiments = []
        sentiment_counts = {'bullish': 0, 'bearish': 0, 'neutral': 0}
        
        for item in news:
            text = f"{item.title} {item.summary}"
            
            # TextBlob analysis
            blob = TextBlob(text)
            textblob_score = blob.sentiment.polarity
            
            # VADER analysis
            vader_scores = self.vader_analyzer.polarity_scores(text)
            vader_score = vader_scores['compound']
            
            # Combined score
            combined_score = (textblob_score + vader_score) / 2
            sentiments.append(combined_score)
            
            # Count sentiment types
            if combined_score > 0.1:
                sentiment_counts['bullish'] += 1
            elif combined_score < -0.1:
                sentiment_counts['bearish'] += 1
            else:
                sentiment_counts['neutral'] += 1
        
        return {
            'overall_sentiment': np.mean(sentiments),
            'sentiment_strength': np.std(sentiments),
            'bullish_count': sentiment_counts['bullish'],
            'bearish_count': sentiment_counts['bearish'],
            'neutral_count': sentiment_counts['neutral']
        }
    
    def _get_openai_market_analysis(self, events: List[EconomicEvent], news: List[NewsItem]) -> Dict:
        """Get enhanced market analysis using OpenAI"""
        
        # Prepare context for OpenAI
        events_summary = []
        for event in events[:5]:  # Limit to top 5 events
            events_summary.append({
                'event': event.event,
                'currency': event.currency,
                'impact': event.impact.value,
                'time_until': event.time_until_event,
                'safety_score': event.safety_score
            })
        
        news_summary = []
        for item in news[:5]:  # Limit to top 5 news items
            news_summary.append({
                'title': item.title,
                'source': item.source,
                'relevance': item.relevance
            })
        
        prompt = f"""
        As an expert forex analyst, analyze the current market conditions based on:
        
        Upcoming Economic Events:
        {json.dumps(events_summary, indent=2)}
        
        Recent Financial News:
        {json.dumps(news_summary, indent=2)}
        
        Provide analysis in JSON format with:
        - market_bias: "bullish", "bearish", or "neutral"
        - volatility_expectation: "low", "medium", or "high"
        - trading_recommendation: "aggressive", "normal", "cautious", or "avoid"
        - key_risks: list of main risks
        - opportunities: list of potential opportunities
        - confidence_level: 0-100
        
        Focus on practical trading insights.
        """
        
        try:
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert forex market analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            # Try to parse JSON response
            try:
                return json.loads(analysis_text)
            except json.JSONDecodeError:
                # If not valid JSON, extract key information
                return self._parse_openai_response(analysis_text)
                
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return {}
    
    def _parse_openai_response(self, response_text: str) -> Dict:
        """Parse OpenAI response if not in JSON format"""
        analysis = {}
        
        # Simple keyword extraction
        text_lower = response_text.lower()
        
        if 'bullish' in text_lower:
            analysis['market_bias'] = 'bullish'
        elif 'bearish' in text_lower:
            analysis['market_bias'] = 'bearish'
        else:
            analysis['market_bias'] = 'neutral'
        
        if 'high volatility' in text_lower or 'volatile' in text_lower:
            analysis['volatility_expectation'] = 'high'
        elif 'low volatility' in text_lower:
            analysis['volatility_expectation'] = 'low'
        else:
            analysis['volatility_expectation'] = 'medium'
        
        if 'avoid' in text_lower:
            analysis['trading_recommendation'] = 'avoid'
        elif 'cautious' in text_lower:
            analysis['trading_recommendation'] = 'cautious'
        elif 'aggressive' in text_lower:
            analysis['trading_recommendation'] = 'aggressive'
        else:
            analysis['trading_recommendation'] = 'normal'
        
        return analysis
    
    def generate_trading_signals(
        self, 
        events: List[EconomicEvent], 
        market_data: Dict[str, MarketData],
        news_sentiment: Dict
    ) -> List[TradingSignal]:
        """Generate AI-powered trading signals"""
        
        signals = []
        
        # Focus on major currency pairs
        major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']
        
        for pair in major_pairs:
            if pair not in market_data:
                continue
                
            signal = self._generate_pair_signal(pair, events, market_data[pair], news_sentiment)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _generate_pair_signal(
        self, 
        pair: str, 
        events: List[EconomicEvent], 
        market_data: MarketData,
        news_sentiment: Dict
    ) -> Optional[TradingSignal]:
        """Generate signal for a specific currency pair"""
        
        # Get relevant events for this pair
        base_currency = pair[:3]
        quote_currency = pair[3:]
        
        relevant_events = [
            e for e in events 
            if e.currency in [base_currency, quote_currency] and e.time_until_event <= 24
        ]
        
        if not relevant_events:
            return None
        
        # Calculate signal components
        event_score = self._calculate_event_score(relevant_events, base_currency, quote_currency)
        sentiment_score = news_sentiment.get('overall_sentiment', 0)
        safety_score = np.mean([e.safety_score for e in relevant_events])
        
        # Combine scores
        combined_score = (event_score * 0.5) + (sentiment_score * 0.3) + ((safety_score - 50) / 50 * 0.2)
        
        # Determine signal type
        if combined_score > 0.3 and safety_score > 40:
            signal_type = TradeType.BUY
            confidence = min(95, 50 + abs(combined_score) * 100)
        elif combined_score < -0.3 and safety_score > 40:
            signal_type = TradeType.SELL
            confidence = min(95, 50 + abs(combined_score) * 100)
        else:
            signal_type = TradeType.HOLD
            confidence = 50
        
        # Generate reason
        reason = self._generate_signal_reason(relevant_events, sentiment_score, event_score)
        
        return TradingSignal(
            pair=pair,
            signal=signal_type,
            confidence=confidence,
            reason=reason,
            safety_score=int(safety_score),
            entry_price=market_data.price,
            timestamp=datetime.now()
        )
    
    def _calculate_event_score(self, events: List[EconomicEvent], base_currency: str, quote_currency: str) -> float:
        """Calculate event impact score for currency pair"""
        base_score = 0
        quote_score = 0
        
        for event in events:
            impact_multiplier = {'High': 1.0, 'Medium': 0.6, 'Low': 0.3}.get(event.impact.value, 0.5)
            
            # Simple scoring based on event type and currency
            event_score = 0
            
            if 'rate' in event.event.lower() or 'interest' in event.event.lower():
                event_score = 0.8 * impact_multiplier
            elif 'gdp' in event.event.lower():
                event_score = 0.7 * impact_multiplier
            elif 'employment' in event.event.lower() or 'payroll' in event.event.lower():
                event_score = 0.9 * impact_multiplier
            elif 'inflation' in event.event.lower() or 'cpi' in event.event.lower():
                event_score = 0.6 * impact_multiplier
            else:
                event_score = 0.4 * impact_multiplier
            
            # Apply to appropriate currency
            if event.currency == base_currency:
                base_score += event_score
            elif event.currency == quote_currency:
                quote_score -= event_score  # Negative for quote currency strength
        
        return base_score + quote_score
    
    def _generate_signal_reason(self, events: List[EconomicEvent], sentiment_score: float, event_score: float) -> str:
        """Generate human-readable reason for the signal"""
        reasons = []
        
        if events:
            high_impact_events = [e for e in events if e.is_high_impact]
            if high_impact_events:
                event_names = [e.event for e in high_impact_events[:2]]
                reasons.append(f"High-impact events: {', '.join(event_names)}")
        
        if abs(sentiment_score) > 0.2:
            sentiment_desc = "positive" if sentiment_score > 0 else "negative"
            reasons.append(f"Strong {sentiment_desc} news sentiment")
        
        if abs(event_score) > 0.3:
            event_desc = "supportive" if event_score > 0 else "negative"
            reasons.append(f"Economic events are {event_desc}")
        
        if not reasons:
            reasons.append("Mixed signals - holding position recommended")
        
        return "; ".join(reasons)
    
    def analyze_correlation_matrix(self, pairs: List[str], historical_data: Dict) -> np.ndarray:
        """Analyze currency pair correlations"""
        if not historical_data:
            # Return mock correlation matrix
            n = len(pairs)
            correlation_matrix = np.random.rand(n, n)
            correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
            np.fill_diagonal(correlation_matrix, 1)
            return correlation_matrix
        
        # Calculate actual correlations if historical data is available
        price_data = []
        for pair in pairs:
            if pair in historical_data:
                prices = historical_data[pair].get('prices', [])
                if len(prices) > 10:
                    returns = np.diff(np.log(prices))
                    price_data.append(returns)
        
        if len(price_data) >= 2:
            # Ensure all arrays have the same length
            min_length = min(len(data) for data in price_data)
            price_data = [data[:min_length] for data in price_data]
            
            correlation_matrix = np.corrcoef(price_data)
            return correlation_matrix
        
        # Fallback to mock data
        n = len(pairs)
        correlation_matrix = np.random.rand(n, n)
        correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
        np.fill_diagonal(correlation_matrix, 1)
        return correlation_matrix
    
    def get_ai_insights(self, market_context: Dict) -> List[str]:
        """Generate AI-powered market insights"""
        insights = []
        
        # Safety-based insights
        avg_safety = market_context.get('avg_safety_score', 50)
        if avg_safety < 40:
            insights.append("🚨 Market conditions are risky - consider reducing position sizes")
        elif avg_safety > 70:
            insights.append("✅ Market conditions are favorable for trading")
        
        # Event-based insights
        high_impact_count = market_context.get('high_impact_events', 0)
        if high_impact_count > 2:
            insights.append("⚠️ Multiple high-impact events ahead - expect increased volatility")
        
        # Sentiment-based insights
        sentiment = market_context.get('news_sentiment', {})
        overall_sentiment = sentiment.get('overall_sentiment', 0)
        
        if overall_sentiment > 0.3:
            insights.append("📈 Strong bullish sentiment detected across financial news")
        elif overall_sentiment < -0.3:
            insights.append("📉 Strong bearish sentiment detected across financial news")
        
        # Volatility insights
        volatility_expectation = market_context.get('volatility_expectation', 'medium')
        if volatility_expectation == 'high':
            insights.append("🌊 High volatility expected - use wider stops and smaller positions")
        
        # Trading recommendation
        recommendation = market_context.get('trading_recommendation', 'normal')
        if recommendation == 'avoid':
            insights.append("🛑 Current conditions suggest avoiding new trades")
        elif recommendation == 'aggressive':
            insights.append("🎯 Market conditions favor more aggressive trading strategies")
        
        # Default insight if none generated
        if not insights:
            insights.append("📊 Market conditions are mixed - maintain standard risk management")
        
        return insights
    
    def calculate_risk_score(self, events: List[EconomicEvent], market_data: Dict) -> int:
        """Calculate overall market risk score"""
        if not events:
            return 50
        
        # Base risk from events
        event_risk = 0
        for event in events:
            if event.is_high_impact:
                event_risk += 30
            elif event.impact == EventImpact.MEDIUM:
                event_risk += 15
            else:
                event_risk += 5
        
        # Normalize event risk
        event_risk = min(50, event_risk)
        
        # Market volatility risk
        volatility_risk = 0
        if market_data:
            avg_volatility = np.mean([data.change_percent for data in market_data.values()])
            volatility_risk = min(30, abs(avg_volatility) * 10)
        
        # Calculate final risk score (0-100, where 100 is maximum risk)
        total_risk = event_risk + volatility_risk
        
        # Convert to safety score (inverse of risk)
        safety_score = max(0, 100 - total_risk)
        
        return int(safety_score)

# Export the AI engine
__all__ = ['AITradingEngine']
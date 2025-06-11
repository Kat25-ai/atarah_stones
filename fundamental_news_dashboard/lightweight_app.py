"""
Lightweight CPU-only version of the Fundamental News Trading Dashboard
Optimized for performance and minimal resource usage
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import json
import sqlite3
from typing import Dict, List, Optional
import time
import threading
import queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lightweight configuration
LIGHTWEIGHT_CONFIG = {
    'MAX_NEWS_ITEMS': 10,
    'MAX_EVENTS': 5,
    'REFRESH_INTERVAL': 60,  # seconds
    'CACHE_DURATION': 300,   # 5 minutes
    'ENABLE_REAL_TIME': True,
    'CPU_OPTIMIZED': True
}

class LightweightNewsMonitor:
    """Lightweight real-time news monitoring system"""
    
    def __init__(self):
        self.news_queue = queue.Queue()
        self.is_monitoring = False
        self.monitor_thread = None
        self.cache = {}
        self.last_update = datetime.now()
    
    def start_monitoring(self):
        """Start real-time news monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Real-time news monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time news monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Real-time news monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Check for new news every 30 seconds
                news_items = self._fetch_latest_news()
                if news_items:
                    for item in news_items:
                        self.news_queue.put(item)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _fetch_latest_news(self) -> List[Dict]:
        """Fetch latest financial news (lightweight implementation)"""
        # Check cache first
        cache_key = "latest_news"
        if cache_key in self.cache:
            cache_time, cached_data = self.cache[cache_key]
            if (datetime.now() - cache_time).seconds < LIGHTWEIGHT_CONFIG['CACHE_DURATION']:
                return cached_data
        
        # Mock news data for demonstration
        mock_news = [
            {
                'title': f'Market Update {datetime.now().strftime("%H:%M")}',
                'summary': 'Real-time market analysis and economic indicators update',
                'source': 'Financial Wire',
                'timestamp': datetime.now(),
                'sentiment': np.random.choice(['bullish', 'bearish', 'neutral']),
                'impact': np.random.choice(['high', 'medium', 'low'])
            }
        ]
        
        # Cache the result
        self.cache[cache_key] = (datetime.now(), mock_news)
        return mock_news
    
    def get_recent_news(self, limit: int = 10) -> List[Dict]:
        """Get recent news items from queue"""
        news_items = []
        try:
            while not self.news_queue.empty() and len(news_items) < limit:
                news_items.append(self.news_queue.get_nowait())
        except queue.Empty:
            pass
        
        # If no real-time news, return cached news
        if not news_items:
            return self._fetch_latest_news()[:limit]
        
        return news_items

class LightweightSentimentAnalyzer:
    """CPU-optimized sentiment analysis"""
    
    def __init__(self):
        # Simple keyword-based sentiment analysis for CPU efficiency
        self.bullish_keywords = [
            'growth', 'increase', 'rise', 'up', 'positive', 'strong', 'boost',
            'gain', 'improve', 'bullish', 'optimistic', 'recovery'
        ]
        self.bearish_keywords = [
            'decline', 'fall', 'drop', 'down', 'negative', 'weak', 'loss',
            'decrease', 'bearish', 'pessimistic', 'recession', 'crisis'
        ]
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Fast keyword-based sentiment analysis"""
        text_lower = text.lower()
        
        bullish_count = sum(1 for word in self.bullish_keywords if word in text_lower)
        bearish_count = sum(1 for word in self.bearish_keywords if word in text_lower)
        
        if bullish_count > bearish_count:
            sentiment = 'bullish'
            score = min(1.0, (bullish_count - bearish_count) / 10)
            color = 'green'
        elif bearish_count > bullish_count:
            sentiment = 'bearish'
            score = -min(1.0, (bearish_count - bullish_count) / 10)
            color = 'red'
        else:
            sentiment = 'neutral'
            score = 0.0
            color = 'gray'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': abs(score),
            'color': color
        }

class LightweightEventMonitor:
    """Lightweight economic event monitoring"""
    
    def __init__(self):
        self.events_cache = {}
    
    def get_upcoming_events(self, hours_ahead: int = 24) -> List[Dict]:
        """Get upcoming economic events"""
        # Mock events for demonstration
        events = [
            {
                'time': datetime.now() + timedelta(hours=2),
                'currency': 'USD',
                'event': 'Employment Data',
                'impact': 'High',
                'forecast': '3.7%',
                'previous': '3.8%',
                'safety_score': self._calculate_safety_score('High', 2)
            },
            {
                'time': datetime.now() + timedelta(hours=6),
                'currency': 'EUR',
                'event': 'ECB Speech',
                'impact': 'Medium',
                'forecast': 'N/A',
                'previous': 'N/A',
                'safety_score': self._calculate_safety_score('Medium', 6)
            },
            {
                'time': datetime.now() + timedelta(hours=12),
                'currency': 'GBP',
                'event': 'Retail Sales',
                'impact': 'Medium',
                'forecast': '0.3%',
                'previous': '0.1%',
                'safety_score': self._calculate_safety_score('Medium', 12)
            }
        ]
        
        return [e for e in events if (e['time'] - datetime.now()).total_seconds() / 3600 <= hours_ahead]
    
    def _calculate_safety_score(self, impact: str, hours_until: float) -> int:
        """Calculate safety score for an event"""
        base_score = 70
        
        # Impact adjustment
        if impact == 'High':
            base_score -= 30
        elif impact == 'Medium':
            base_score -= 15
        else:
            base_score -= 5
        
        # Time adjustment
        if hours_until < 1:
            base_score -= 20
        elif hours_until < 4:
            base_score -= 10
        
        return max(0, min(100, base_score))

def create_lightweight_dashboard():
    """Create the lightweight dashboard interface"""
    
    # Initialize components
    news_monitor = LightweightNewsMonitor()
    sentiment_analyzer = LightweightSentimentAnalyzer()
    event_monitor = LightweightEventMonitor()
    
    # Start real-time monitoring
    if LIGHTWEIGHT_CONFIG['ENABLE_REAL_TIME']:
        news_monitor.start_monitoring()
    
    # Page configuration
    st.set_page_config(
        page_title="Lightweight Trading Dashboard",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for lightweight theme
    st.markdown("""
    <style>
        .main-header {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            color: #2E86AB;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 0.8rem;
            border-radius: 8px;
            border-left: 4px solid #2E86AB;
            margin: 0.5rem 0;
        }
        .news-alert {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 0.8rem;
            margin: 0.5rem 0;
        }
        .real-time-indicator {
            position: fixed;
            top: 10px;
            right: 10px;
            background-color: #28a745;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            z-index: 1000;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Real-time indicator
    st.markdown('<div class="real-time-indicator">🟢 LIVE</div>', unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">⚡ Lightweight Trading Dashboard</h1>', unsafe_allow_html=True)
    
    # Auto-refresh mechanism
    if st.button("🔄 Refresh", key="refresh_btn"):
        st.rerun()
    
    # Main content in columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Real-time news feed
        st.subheader("📰 Real-Time News Feed")
        
        recent_news = news_monitor.get_recent_news(limit=LIGHTWEIGHT_CONFIG['MAX_NEWS_ITEMS'])
        
        for news in recent_news:
            sentiment_data = sentiment_analyzer.analyze_sentiment(news['title'] + ' ' + news.get('summary', ''))
            
            st.markdown(f"""
            <div class="news-alert">
                <h4 style="color: {sentiment_data['color']};">{news['title']}</h4>
                <p><small>{news['source']} | {news['timestamp'].strftime('%H:%M:%S')}</small></p>
                <p><strong>Sentiment:</strong> 
                   <span style="color: {sentiment_data['color']};">
                       {sentiment_data['sentiment'].upper()} ({sentiment_data['score']:.2f})
                   </span>
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Economic events
        st.subheader("📅 Upcoming Events")
        
        events = event_monitor.get_upcoming_events()
        
        for event in events:
            time_until = (event['time'] - datetime.now()).total_seconds() / 3600
            
            # Color coding based on safety score
            if event['safety_score'] >= 70:
                card_color = "#d4edda"
            elif event['safety_score'] >= 40:
                card_color = "#fff3cd"
            else:
                card_color = "#f8d7da"
            
            st.markdown(f"""
            <div class="metric-card" style="background-color: {card_color};">
                <h4>{event['event']} ({event['currency']})</h4>
                <p><strong>Time:</strong> {event['time'].strftime('%H:%M')} ({time_until:.1f}h)</p>
                <p><strong>Impact:</strong> {event['impact']} | <strong>Safety:</strong> {event['safety_score']}/100</p>
                <p><strong>Forecast:</strong> {event['forecast']} | <strong>Previous:</strong> {event['previous']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Market safety gauge
        st.subheader("🛡️ Market Safety")
        
        # Calculate overall safety
        if events:
            overall_safety = np.mean([e['safety_score'] for e in events])
        else:
            overall_safety = 50
        
        # Simple gauge using metric
        st.metric("Safety Score", f"{overall_safety:.0f}/100")
        
        # Safety recommendation
        if overall_safety >= 70:
            st.success("✅ Safe to trade")
        elif overall_safety >= 40:
            st.warning("⚠️ Trade with caution")
        else:
            st.error("🚨 High risk - avoid trading")
        
        # Sentiment summary
        st.subheader("📊 Sentiment Summary")
        
        if recent_news:
            sentiments = [sentiment_analyzer.analyze_sentiment(news['title']) for news in recent_news]
            
            bullish_count = sum(1 for s in sentiments if s['sentiment'] == 'bullish')
            bearish_count = sum(1 for s in sentiments if s['sentiment'] == 'bearish')
            neutral_count = len(sentiments) - bullish_count - bearish_count
            
            # Simple bar chart
            sentiment_data = pd.DataFrame({
                'Sentiment': ['Bullish', 'Bearish', 'Neutral'],
                'Count': [bullish_count, bearish_count, neutral_count]
            })
            
            fig = px.bar(sentiment_data, x='Sentiment', y='Count', 
                        color='Sentiment',
                        color_discrete_map={'Bullish': 'green', 'Bearish': 'red', 'Neutral': 'gray'})
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Quick stats
        st.subheader("📈 Quick Stats")
        st.metric("Active Events", len(events))
        st.metric("News Items", len(recent_news))
        st.metric("Last Update", datetime.now().strftime('%H:%M:%S'))
    
    # Auto-refresh mechanism (removed infinite loop)
    if LIGHTWEIGHT_CONFIG['ENABLE_REAL_TIME']:
        # Use Streamlit's built-in auto-refresh instead of infinite loop
        st.markdown("""
        <script>
            setTimeout(function(){
                window.location.reload(1);
            }, 60000);
        </script>
        """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    try:
        create_lightweight_dashboard()
    except Exception as e:
        st.error(f"Dashboard error: {e}")
        logger.error(f"Dashboard error: {e}")

if __name__ == "__main__":
    main()
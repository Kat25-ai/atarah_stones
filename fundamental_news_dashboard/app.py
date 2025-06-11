import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import pytz
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
import time
import sqlite3
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Fundamental News Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .safety-high {
        background-color: #d4edda;
        border-left-color: #28a745;
    }
    .safety-medium {
        background-color: #fff3cd;
        border-left-color: #ffc107;
    }
    .safety-low {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
    .news-item {
        background-color: #ffffff;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class NewsAnalyzer:
    """AI-powered news sentiment analyzer"""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using multiple methods"""
        # TextBlob analysis
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        textblob_subjectivity = blob.sentiment.subjectivity
        
        # VADER analysis
        vader_scores = self.vader_analyzer.polarity_scores(text)
        
        # Combined sentiment score
        combined_score = (textblob_polarity + vader_scores['compound']) / 2
        
        # Classification
        if combined_score >= 0.1:
            sentiment = "Bullish"
            color = "green"
        elif combined_score <= -0.1:
            sentiment = "Bearish"
            color = "red"
        else:
            sentiment = "Neutral"
            color = "gray"
            
        return {
            'sentiment': sentiment,
            'score': combined_score,
            'confidence': abs(combined_score),
            'color': color,
            'textblob_polarity': textblob_polarity,
            'vader_compound': vader_scores['compound'],
            'subjectivity': textblob_subjectivity
        }

class ForexFactoryParser:
    """Parse economic events from Forex Factory"""
    
    def __init__(self):
        self.base_url = "https://www.forexfactory.com"
        
    def get_economic_calendar(self, days_ahead: int = 7) -> List[Dict]:
        """Fetch economic calendar data"""
        # Mock data for demonstration (in production, you'd scrape Forex Factory)
        mock_events = [
            {
                'time': datetime.now() + timedelta(hours=2),
                'currency': 'USD',
                'event': 'Non-Farm Payrolls',
                'impact': 'High',
                'forecast': '200K',
                'previous': '180K',
                'actual': None,
                'safety_score': 25
            },
            {
                'time': datetime.now() + timedelta(hours=6),
                'currency': 'EUR',
                'event': 'ECB Interest Rate Decision',
                'impact': 'High',
                'forecast': '4.50%',
                'previous': '4.50%',
                'actual': None,
                'safety_score': 15
            },
            {
                'time': datetime.now() + timedelta(days=1),
                'currency': 'GBP',
                'event': 'GDP Growth Rate',
                'impact': 'Medium',
                'forecast': '0.2%',
                'previous': '0.1%',
                'actual': None,
                'safety_score': 60
            },
            {
                'time': datetime.now() + timedelta(days=2),
                'currency': 'JPY',
                'event': 'Core CPI',
                'impact': 'Medium',
                'forecast': '2.8%',
                'previous': '2.7%',
                'actual': None,
                'safety_score': 45
            }
        ]
        return mock_events

class MarketSafetyAnalyzer:
    """Analyze market safety conditions"""
    
    def calculate_safety_score(self, event: Dict, market_data: Dict = None) -> int:
        """Calculate safety score (0-100) for trading around an event"""
        base_score = 50
        
        # Impact adjustment
        impact_scores = {'High': -30, 'Medium': -15, 'Low': -5}
        base_score += impact_scores.get(event['impact'], 0)
        
        # Time until event
        time_until = (event['time'] - datetime.now()).total_seconds() / 3600
        if time_until < 1:
            base_score -= 20
        elif time_until < 4:
            base_score -= 10
        
        # Market volatility (mock calculation)
        if market_data:
            volatility = market_data.get('volatility', 0.5)
            base_score -= int(volatility * 20)
        
        return max(0, min(100, base_score))
    
    def get_risk_level(self, safety_score: int) -> Tuple[str, str]:
        """Get risk level and color based on safety score"""
        if safety_score >= 70:
            return "Low Risk", "green"
        elif safety_score >= 40:
            return "Medium Risk", "orange"
        else:
            return "High Risk", "red"

class NewsDataProvider:
    """Fetch financial news from various sources"""
    
    def get_financial_news(self, limit: int = 10) -> List[Dict]:
        """Fetch latest financial news"""
        # Mock news data (in production, integrate with news APIs)
        mock_news = [
            {
                'title': 'Federal Reserve Signals Potential Rate Cuts Amid Economic Uncertainty',
                'summary': 'The Federal Reserve indicated possible interest rate reductions in response to slowing economic indicators and inflation concerns.',
                'source': 'Reuters',
                'url': 'https://reuters.com/example',
                'published': datetime.now() - timedelta(hours=1),
                'relevance': 'High'
            },
            {
                'title': 'European Central Bank Maintains Hawkish Stance on Inflation',
                'summary': 'ECB officials continue to emphasize the need for restrictive monetary policy to combat persistent inflation pressures.',
                'source': 'Bloomberg',
                'url': 'https://bloomberg.com/example',
                'published': datetime.now() - timedelta(hours=3),
                'relevance': 'High'
            },
            {
                'title': 'UK GDP Growth Exceeds Expectations in Latest Quarter',
                'summary': 'British economy shows resilience with stronger than anticipated growth figures, boosting GBP outlook.',
                'source': 'Financial Times',
                'url': 'https://ft.com/example',
                'published': datetime.now() - timedelta(hours=5),
                'relevance': 'Medium'
            }
        ]
        return mock_news[:limit]

def initialize_database():
    """Initialize SQLite database for storing trade data"""
    conn = sqlite3.connect('trading_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            event_name TEXT,
            currency_pair TEXT,
            trade_type TEXT,
            entry_price REAL,
            exit_price REAL,
            profit_loss REAL,
            safety_score INTEGER,
            sentiment_score REAL
        )
    ''')
    
    conn.commit()
    conn.close()

def main():
    """Main dashboard application"""
    
    # Initialize components
    news_analyzer = NewsAnalyzer()
    forex_parser = ForexFactoryParser()
    safety_analyzer = MarketSafetyAnalyzer()
    news_provider = NewsDataProvider()
    
    # Initialize database
    initialize_database()
    
    # Header
    st.markdown('<h1 class="main-header">📈 Fundamental News Trading Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Dashboard Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=False)
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Time zone selection
    timezone = st.sidebar.selectbox(
        "Select Timezone",
        ["UTC", "GMT+2", "EST", "PST"],
        index=1
    )
    
    # Currency filter
    currencies = st.sidebar.multiselect(
        "Filter Currencies",
        ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"],
        default=["USD", "EUR", "GBP"]
    )
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Economic Calendar", 
        "📰 News Sentiment", 
        "🛡️ Market Safety", 
        "📚 Trading Rules",
        "🤖 AI Insights"
    ])
    
    # Tab 1: Economic Calendar
    with tab1:
        st.header("High-Impact Economic Events")
        
        # Get economic events
        events = forex_parser.get_economic_calendar()
        
        # Filter by selected currencies
        filtered_events = [e for e in events if e['currency'] in currencies]
        
        if filtered_events:
            # Create events dataframe
            events_df = pd.DataFrame(filtered_events)
            events_df['time_str'] = events_df['time'].dt.strftime('%Y-%m-%d %H:%M')
            
            # Display events in cards
            for idx, event in enumerate(filtered_events):
                safety_score = safety_analyzer.calculate_safety_score(event)
                risk_level, risk_color = safety_analyzer.get_risk_level(safety_score)
                
                # Determine card style based on safety score
                if safety_score >= 70:
                    card_class = "safety-high"
                elif safety_score >= 40:
                    card_class = "safety-medium"
                else:
                    card_class = "safety-low"
                
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card {card_class}">
                        <h4>{event['event']}</h4>
                        <p><strong>{event['currency']}</strong> | {event['time'].strftime('%H:%M')}</p>
                        <p>Impact: <strong>{event['impact']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.metric("Forecast", event['forecast'])
                    st.metric("Previous", event['previous'])
                
                with col3:
                    st.metric("Safety Score", f"{safety_score}/100")
                    st.markdown(f"<span style='color: {risk_color}'><strong>{risk_level}</strong></span>", 
                              unsafe_allow_html=True)
                
                with col4:
                    if event['actual']:
                        st.metric("Actual", event['actual'])
                    else:
                        st.info("Pending")
                
                st.divider()
        else:
            st.info("No events found for selected currencies.")
    
    # Tab 2: News Sentiment Analysis
    with tab2:
        st.header("Financial News Sentiment Analysis")
        
        # Get latest news
        news_items = news_provider.get_financial_news(limit=5)
        
        # Analyze sentiment for each news item
        for news in news_items:
            sentiment_data = news_analyzer.analyze_sentiment(news['title'] + " " + news['summary'])
            
            st.markdown(f"""
            <div class="news-item">
                <h4>{news['title']}</h4>
                <p>{news['summary']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                    <div>
                        <span style="color: {sentiment_data['color']}; font-weight: bold;">
                            {sentiment_data['sentiment']} ({sentiment_data['score']:.2f})
                        </span>
                        <br>
                        <small>{news['source']} | {news['published'].strftime('%H:%M')}</small>
                    </div>
                    <a href="{news['url']}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #1f77b4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px;">
                            Read More
                        </button>
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Sentiment summary chart
        st.subheader("Sentiment Overview")
        
        sentiments = [news_analyzer.analyze_sentiment(news['title'] + " " + news['summary']) 
                     for news in news_items]
        
        sentiment_counts = {'Bullish': 0, 'Bearish': 0, 'Neutral': 0}
        for s in sentiments:
            sentiment_counts[s['sentiment']] += 1
        
        fig = px.pie(
            values=list(sentiment_counts.values()),
            names=list(sentiment_counts.keys()),
            title="News Sentiment Distribution",
            color_discrete_map={'Bullish': 'green', 'Bearish': 'red', 'Neutral': 'gray'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: Market Safety Indicators
    with tab3:
        st.header("Market Safety Analysis")
        
        # Overall market safety gauge
        overall_safety = np.mean([safety_analyzer.calculate_safety_score(event) 
                                for event in filtered_events]) if filtered_events else 50
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = overall_safety,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Market Safety Score"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "lightcoral"},
                    {'range': [40, 70], 'color': "lightyellow"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Safety recommendations
        st.subheader("Trading Recommendations")
        
        if overall_safety >= 70:
            st.success("✅ **LOW RISK**: Market conditions are favorable for trading. Consider normal position sizes.")
        elif overall_safety >= 40:
            st.warning("⚠️ **MEDIUM RISK**: Exercise caution. Reduce position sizes and use tighter stops.")
        else:
            st.error("🚨 **HIGH RISK**: Avoid trading or use very small positions. High volatility expected.")
        
        # Historical volatility chart (mock data)
        st.subheader("Historical Volatility")
        
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        volatility = np.random.normal(0.5, 0.2, len(dates))
        volatility = np.clip(volatility, 0.1, 1.0)
        
        fig = px.line(x=dates, y=volatility, title="30-Day Volatility Trend")
        fig.update_layout(xaxis_title="Date", yaxis_title="Volatility")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: Trading Rules
    with tab4:
        st.header("Fundamental Trading Rules & Guidelines")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Core Principles")
            st.markdown("""
            **1. Event Classification**
            - 🔴 High Impact: NFP, Interest Rates, GDP
            - 🟡 Medium Impact: CPI, Retail Sales, PMI
            - 🟢 Low Impact: Minor economic indicators
            
            **2. Pre-Event Analysis**
            - Check consensus vs. previous data
            - Analyze market positioning
            - Review recent central bank communications
            
            **3. Risk Management**
            - Never risk more than 2% per trade
            - Use wider stops during high-impact events
            - Consider reducing position size 1 hour before major news
            """)
            
            st.subheader("⏰ Timing Rules")
            st.markdown("""
            **Before Event (1-4 hours)**
            - Monitor for early leaks or rumors
            - Check for unusual price action
            - Prepare for potential volatility
            
            **During Event (0-30 minutes)**
            - Wait for initial reaction to settle
            - Look for confirmation signals
            - Avoid trading the first 5 minutes
            
            **After Event (30+ minutes)**
            - Analyze if price confirms fundamentals
            - Look for continuation patterns
            - Consider scaling into positions
            """)
        
        with col2:
            st.subheader("🎯 Event-Specific Strategies")
            
            event_strategies = {
                "Non-Farm Payrolls": {
                    "description": "Monthly US employment data",
                    "typical_reaction": "Strong USD movement",
                    "strategy": "Wait for initial spike, then trade continuation",
                    "pairs": ["EURUSD", "GBPUSD", "USDJPY"]
                },
                "Interest Rate Decisions": {
                    "description": "Central bank rate announcements",
                    "typical_reaction": "High volatility, trend changes",
                    "strategy": "Focus on forward guidance, not just rate",
                    "pairs": ["All major pairs"]
                },
                "GDP Releases": {
                    "description": "Quarterly economic growth data",
                    "typical_reaction": "Medium-term trend influence",
                    "strategy": "Combine with other indicators",
                    "pairs": ["Currency-specific"]
                }
            }
            
            selected_event = st.selectbox("Select Event Type", list(event_strategies.keys()))
            
            if selected_event:
                strategy = event_strategies[selected_event]
                st.info(f"**{selected_event}**")
                st.write(f"📝 {strategy['description']}")
                st.write(f"📈 Typical Reaction: {strategy['typical_reaction']}")
                st.write(f"🎯 Strategy: {strategy['strategy']}")
                st.write(f"💱 Focus Pairs: {strategy['pairs']}")
        
        # Risk management calculator
        st.subheader("🧮 Position Size Calculator")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            account_balance = st.number_input("Account Balance ($)", value=10000, min_value=100)
            risk_percentage = st.slider("Risk Percentage (%)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)
        
        with col2:
            entry_price = st.number_input("Entry Price", value=1.1000, format="%.4f")
            stop_loss = st.number_input("Stop Loss", value=1.0950, format="%.4f")
        
        with col3:
            pip_value = st.number_input("Pip Value ($)", value=10.0, min_value=0.1)
            
        # Calculate position size
        risk_amount = account_balance * (risk_percentage / 100)
        stop_distance = abs(entry_price - stop_loss)
        position_size = risk_amount / (stop_distance * pip_value) if stop_distance > 0 else 0
        
        st.metric("Recommended Position Size", f"{position_size:.2f} lots")
        st.metric("Risk Amount", f"${risk_amount:.2f}")
    
    # Tab 5: AI Insights
    with tab5:
        st.header("🤖 AI-Powered Trading Insights")
        
        # Market sentiment analysis
        st.subheader("Market Sentiment Analysis")
        
        # Combine news sentiment with economic events
        news_items = news_provider.get_financial_news(limit=10)
        all_sentiments = [news_analyzer.analyze_sentiment(news['title'] + " " + news['summary']) 
                         for news in news_items]
        
        avg_sentiment = np.mean([s['score'] for s in all_sentiments])
        sentiment_strength = np.mean([s['confidence'] for s in all_sentiments])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Sentiment", f"{avg_sentiment:.3f}")
        with col2:
            st.metric("Sentiment Strength", f"{sentiment_strength:.3f}")
        with col3:
            market_bias = "Bullish" if avg_sentiment > 0.1 else "Bearish" if avg_sentiment < -0.1 else "Neutral"
            st.metric("Market Bias", market_bias)
        
        # AI Trading Signals
        st.subheader("AI Trading Signals")
        
        # Generate mock AI signals based on sentiment and events
        signals = []
        for event in filtered_events[:3]:
            safety_score = safety_analyzer.calculate_safety_score(event)
            
            # Simple signal generation logic
            if safety_score > 60 and avg_sentiment > 0.1:
                signal_type = "BUY"
                confidence = min(95, safety_score + sentiment_strength * 20)
            elif safety_score > 60 and avg_sentiment < -0.1:
                signal_type = "SELL"
                confidence = min(95, safety_score + sentiment_strength * 20)
            else:
                signal_type = "HOLD"
                confidence = 50
            
            signals.append({
                'pair': f"{event['currency']}USD",
                'signal': signal_type,
                'confidence': confidence,
                'reason': f"Based on {event['event']} and market sentiment",
                'safety_score': safety_score
            })
        
        # Display signals
        for signal in signals:
            color = "green" if signal['signal'] == "BUY" else "red" if signal['signal'] == "SELL" else "gray"
            
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <h4>{signal['pair']} - {signal['signal']}</h4>
                <p>Confidence: {signal['confidence']:.1f}%</p>
                <p>Safety Score: {signal['safety_score']}/100</p>
                <p><em>{signal['reason']}</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Market correlation matrix
        st.subheader("Currency Correlation Matrix")
        
        # Mock correlation data
        currencies = ['EUR', 'GBP', 'JPY', 'AUD', 'CAD']
        correlation_matrix = np.random.rand(len(currencies), len(currencies))
        correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
        np.fill_diagonal(correlation_matrix, 1)
        
        fig = px.imshow(
            correlation_matrix,
            x=currencies,
            y=currencies,
            color_continuous_scale='RdBu',
            title="Currency Pair Correlations"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # AI Recommendations
        st.subheader("AI Recommendations")
        
        recommendations = [
            "📈 Strong bullish sentiment detected in USD pairs - consider long positions",
            "⚠️ High volatility expected around NFP release - reduce position sizes",
            "🔄 EUR showing divergence from fundamentals - potential reversal opportunity",
            "📊 Correlation breakdown between GBP and EUR - pairs trading opportunity"
        ]
        
        for rec in recommendations:
            st.info(rec)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Fundamental News Trading Dashboard | Last Updated: {}</p>
        <p>⚠️ <strong>Disclaimer:</strong> This dashboard is for educational purposes only. 
        Always conduct your own analysis before making trading decisions.</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
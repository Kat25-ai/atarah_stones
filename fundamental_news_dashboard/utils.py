"""
Utility functions for the Fundamental News Trading Dashboard
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import requests
from bs4 import BeautifulSoup
import json
import logging
from config import DATABASE_CONFIG, TRADING_CONFIG, RISK_MANAGEMENT
from models import (
    EconomicEvent, NewsItem, SentimentAnalysis, MarketSafety, 
    TradingSignal, TradeRecord, MarketData, EventImpact, 
    SentimentType, RiskLevel, TradeType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manage SQLite database operations"""
    
    def __init__(self, db_name: str = None):
        self.db_name = db_name or DATABASE_CONFIG['DB_NAME']
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create trades table
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
                sentiment_score REAL,
                position_size REAL,
                duration_minutes INTEGER
            )
        ''')
        
        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                currency TEXT,
                event_name TEXT,
                impact TEXT,
                forecast TEXT,
                previous TEXT,
                actual TEXT,
                safety_score INTEGER
            )
        ''')
        
        # Create news table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                title TEXT,
                summary TEXT,
                source TEXT,
                url TEXT,
                sentiment_score REAL,
                sentiment_type TEXT,
                confidence REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_trade(self, trade: TradeRecord) -> int:
        """Save trade record to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                timestamp, event_name, currency_pair, trade_type,
                entry_price, exit_price, profit_loss, safety_score,
                sentiment_score, position_size, duration_minutes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade.timestamp, trade.event_name, trade.currency_pair,
            trade.trade_type, trade.entry_price, trade.exit_price,
            trade.profit_loss, trade.safety_score, trade.sentiment_score,
            trade.position_size, trade.duration_minutes
        ))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return trade_id
    
    def get_trades(self, limit: int = 100) -> List[TradeRecord]:
        """Get trade records from database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        trades = []
        for row in rows:
            trade = TradeRecord(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                event_name=row[2],
                currency_pair=row[3],
                trade_type=row[4],
                entry_price=row[5],
                exit_price=row[6],
                profit_loss=row[7],
                safety_score=row[8],
                sentiment_score=row[9],
                position_size=row[10],
                duration_minutes=row[11]
            )
            trades.append(trade)
        
        return trades
    
    def get_performance_stats(self) -> Dict:
        """Get trading performance statistics"""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query('SELECT * FROM trades', conn)
        conn.close()
        
        if df.empty:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_trade': 0,
                'best_trade': 0,
                'worst_trade': 0
            }
        
        stats = {
            'total_trades': len(df),
            'win_rate': (df['profit_loss'] > 0).mean() * 100,
            'total_pnl': df['profit_loss'].sum(),
            'avg_trade': df['profit_loss'].mean(),
            'best_trade': df['profit_loss'].max(),
            'worst_trade': df['profit_loss'].min()
        }
        
        return stats

class PositionSizeCalculator:
    """Calculate optimal position sizes based on risk management rules"""
    
    @staticmethod
    def calculate_position_size(
        account_balance: float,
        risk_percentage: float,
        entry_price: float,
        stop_loss: float,
        pip_value: float = 10.0,
        safety_score: int = 50,
        event_impact: EventImpact = EventImpact.MEDIUM
    ) -> Dict:
        """Calculate position size with risk management adjustments"""
        
        # Base risk amount
        base_risk = account_balance * (risk_percentage / 100)
        
        # Apply safety score modifier
        safety_modifier = 1.0
        if safety_score < RISK_MANAGEMENT['SAFETY_SCORE_THRESHOLDS']['MEDIUM_RISK']:
            safety_modifier = RISK_MANAGEMENT['POSITION_SIZE_MODIFIERS']['LOW_SAFETY_SCORE']
        
        # Apply event impact modifier
        impact_modifier = 1.0
        if event_impact == EventImpact.HIGH:
            impact_modifier = RISK_MANAGEMENT['POSITION_SIZE_MODIFIERS']['HIGH_IMPACT_EVENT']
        
        # Calculate adjusted risk
        adjusted_risk = base_risk * safety_modifier * impact_modifier
        
        # Calculate position size
        stop_distance = abs(entry_price - stop_loss)
        if stop_distance > 0:
            position_size = adjusted_risk / (stop_distance * pip_value)
        else:
            position_size = 0
        
        return {
            'position_size': round(position_size, 2),
            'risk_amount': adjusted_risk,
            'safety_modifier': safety_modifier,
            'impact_modifier': impact_modifier,
            'stop_distance': stop_distance
        }

class TechnicalAnalyzer:
    """Technical analysis utilities"""
    
    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> float:
        """Calculate historical volatility"""
        if len(prices) < period:
            return 0.5  # Default volatility
        
        returns = np.diff(np.log(prices))
        volatility = np.std(returns) * np.sqrt(252)  # Annualized
        return min(1.0, max(0.1, volatility))
    
    @staticmethod
    def calculate_support_resistance(prices: List[float]) -> Dict:
        """Calculate support and resistance levels"""
        if len(prices) < 10:
            return {'support': min(prices), 'resistance': max(prices)}
        
        # Simple pivot point calculation
        high = max(prices)
        low = min(prices)
        close = prices[-1]
        
        pivot = (high + low + close) / 3
        support1 = 2 * pivot - high
        resistance1 = 2 * pivot - low
        
        return {
            'pivot': pivot,
            'support': support1,
            'resistance': resistance1,
            'range': high - low
        }
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

class MarketDataProvider:
    """Provide market data from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_forex_rates(self, pairs: List[str]) -> Dict[str, MarketData]:
        """Get current forex rates (mock implementation)"""
        # Mock data - in production, integrate with real forex API
        mock_rates = {
            'EURUSD': 1.0850,
            'GBPUSD': 1.2650,
            'USDJPY': 149.50,
            'AUDUSD': 0.6750,
            'USDCAD': 1.3580,
            'USDCHF': 0.8920,
            'NZDUSD': 0.6150
        }
        
        market_data = {}
        for pair in pairs:
            if pair in mock_rates:
                price = mock_rates[pair]
                change = np.random.uniform(-0.005, 0.005) * price
                
                market_data[pair] = MarketData(
                    symbol=pair,
                    price=price,
                    change=change,
                    change_percent=(change / price) * 100,
                    volume=np.random.randint(1000000, 10000000),
                    bid=price - 0.0002,
                    ask=price + 0.0002,
                    spread=0.0004
                )
        
        return market_data
    
    def get_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical price data"""
        # Mock historical data
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = 1.0850 if 'EUR' in symbol else 1.2650
        
        prices = []
        current_price = base_price
        
        for _ in range(days):
            change = np.random.normal(0, 0.01)
            current_price *= (1 + change)
            prices.append(current_price)
        
        df = pd.DataFrame({
            'date': dates,
            'price': prices,
            'volume': np.random.randint(1000000, 5000000, days)
        })
        
        return df

class AlertManager:
    """Manage trading alerts and notifications"""
    
    def __init__(self):
        self.alerts = []
    
    def check_safety_alerts(self, current_score: int, previous_score: int) -> Optional[str]:
        """Check for safety score alerts"""
        threshold = 20  # Alert if safety drops by 20 points
        
        if previous_score - current_score >= threshold:
            return f"⚠️ Safety score dropped from {previous_score} to {current_score}"
        
        return None
    
    def check_event_alerts(self, events: List[EconomicEvent]) -> List[str]:
        """Check for upcoming high-impact events"""
        alerts = []
        alert_window = 60  # 60 minutes
        
        for event in events:
            if event.is_high_impact and event.time_until_event <= alert_window:
                alerts.append(f"🚨 High-impact event in {event.time_until_event:.0f} minutes: {event.event}")
        
        return alerts
    
    def check_sentiment_alerts(self, current_sentiment: float, previous_sentiment: float) -> Optional[str]:
        """Check for significant sentiment changes"""
        threshold = 0.3
        
        if abs(current_sentiment - previous_sentiment) >= threshold:
            direction = "improved" if current_sentiment > previous_sentiment else "deteriorated"
            return f"📊 Market sentiment {direction} significantly"
        
        return None

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage value"""
    return f"{value:.{decimals}f}%"

def calculate_pip_value(pair: str, account_currency: str = "USD", lot_size: float = 1.0) -> float:
    """Calculate pip value for currency pair"""
    # Simplified pip value calculation
    pip_values = {
        'EURUSD': 10.0,
        'GBPUSD': 10.0,
        'AUDUSD': 10.0,
        'NZDUSD': 10.0,
        'USDCAD': 7.35,
        'USDCHF': 11.2,
        'USDJPY': 0.067
    }
    
    return pip_values.get(pair, 10.0) * lot_size

def get_market_hours() -> Dict[str, Dict]:
    """Get trading session hours"""
    return {
        'Sydney': {'open': '22:00', 'close': '07:00', 'timezone': 'AEDT'},
        'Tokyo': {'open': '00:00', 'close': '09:00', 'timezone': 'JST'},
        'London': {'open': '08:00', 'close': '17:00', 'timezone': 'GMT'},
        'New York': {'open': '13:00', 'close': '22:00', 'timezone': 'EST'}
    }

def is_market_open(session: str = 'London') -> bool:
    """Check if specific trading session is open"""
    # Simplified market hours check
    current_hour = datetime.now().hour
    
    session_hours = {
        'Sydney': (22, 7),
        'Tokyo': (0, 9),
        'London': (8, 17),
        'New York': (13, 22)
    }
    
    if session in session_hours:
        open_hour, close_hour = session_hours[session]
        if open_hour > close_hour:  # Crosses midnight
            return current_hour >= open_hour or current_hour < close_hour
        else:
            return open_hour <= current_hour < close_hour
    
    return True

def validate_trade_setup(
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    trade_type: TradeType
) -> Dict[str, Union[bool, str, float]]:
    """Validate trade setup parameters"""
    
    errors = []
    
    # Check if prices are valid
    if entry_price <= 0:
        errors.append("Entry price must be positive")
    
    if stop_loss <= 0:
        errors.append("Stop loss must be positive")
    
    if take_profit <= 0:
        errors.append("Take profit must be positive")
    
    # Check trade direction logic
    if trade_type == TradeType.BUY:
        if stop_loss >= entry_price:
            errors.append("Stop loss must be below entry price for BUY trades")
        if take_profit <= entry_price:
            errors.append("Take profit must be above entry price for BUY trades")
    
    elif trade_type == TradeType.SELL:
        if stop_loss <= entry_price:
            errors.append("Stop loss must be above entry price for SELL trades")
        if take_profit >= entry_price:
            errors.append("Take profit must be below entry price for SELL trades")
    
    # Calculate risk-reward ratio
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    risk_reward_ratio = reward / risk if risk > 0 else 0
    
    # Check minimum risk-reward ratio
    if risk_reward_ratio < 1.0:
        errors.append(f"Risk-reward ratio ({risk_reward_ratio:.2f}) should be at least 1:1")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'risk_reward_ratio': risk_reward_ratio,
        'risk_amount': risk,
        'reward_amount': reward
    }

# Export utility functions
__all__ = [
    'DatabaseManager',
    'PositionSizeCalculator',
    'TechnicalAnalyzer',
    'MarketDataProvider',
    'AlertManager',
    'format_currency',
    'format_percentage',
    'calculate_pip_value',
    'get_market_hours',
    'is_market_open',
    'validate_trade_setup'
]
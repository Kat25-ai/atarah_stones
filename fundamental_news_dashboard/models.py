"""
Data models for the Fundamental News Trading Dashboard
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union
from enum import Enum

class EventImpact(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class SentimentType(Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"

class RiskLevel(Enum):
    LOW = "Low Risk"
    MEDIUM = "Medium Risk"
    HIGH = "High Risk"

class TradeType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class EconomicEvent:
    """Model for economic calendar events"""
    time: datetime
    currency: str
    event: str
    impact: EventImpact
    forecast: Optional[str] = None
    previous: Optional[str] = None
    actual: Optional[str] = None
    safety_score: int = 50
    volatility_expected: float = 0.5
    market_consensus: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.impact, str):
            self.impact = EventImpact(self.impact)
    
    @property
    def time_until_event(self) -> float:
        """Returns hours until event"""
        return (self.time - datetime.now()).total_seconds() / 3600
    
    @property
    def is_high_impact(self) -> bool:
        """Check if event is high impact"""
        return self.impact == EventImpact.HIGH
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'time': self.time.isoformat(),
            'currency': self.currency,
            'event': self.event,
            'impact': self.impact.value,
            'forecast': self.forecast,
            'previous': self.previous,
            'actual': self.actual,
            'safety_score': self.safety_score,
            'volatility_expected': self.volatility_expected,
            'market_consensus': self.market_consensus
        }

@dataclass
class NewsItem:
    """Model for financial news items"""
    title: str
    summary: str
    source: str
    url: str
    published: datetime
    relevance: str = "Medium"
    sentiment_score: Optional[float] = None
    sentiment_type: Optional[SentimentType] = None
    confidence: Optional[float] = None
    keywords: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.sentiment_type, str) and self.sentiment_type:
            self.sentiment_type = SentimentType(self.sentiment_type)
    
    @property
    def age_hours(self) -> float:
        """Returns age of news in hours"""
        return (datetime.now() - self.published).total_seconds() / 3600
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'summary': self.summary,
            'source': self.source,
            'url': self.url,
            'published': self.published.isoformat(),
            'relevance': self.relevance,
            'sentiment_score': self.sentiment_score,
            'sentiment_type': self.sentiment_type.value if self.sentiment_type else None,
            'confidence': self.confidence,
            'keywords': self.keywords
        }

@dataclass
class SentimentAnalysis:
    """Model for sentiment analysis results"""
    sentiment: SentimentType
    score: float
    confidence: float
    color: str
    textblob_polarity: float = 0.0
    vader_compound: float = 0.0
    subjectivity: float = 0.0
    
    def __post_init__(self):
        if isinstance(self.sentiment, str):
            self.sentiment = SentimentType(self.sentiment)
    
    @property
    def is_strong_sentiment(self) -> bool:
        """Check if sentiment is strong (high confidence)"""
        return self.confidence > 0.7
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'sentiment': self.sentiment.value,
            'score': self.score,
            'confidence': self.confidence,
            'color': self.color,
            'textblob_polarity': self.textblob_polarity,
            'vader_compound': self.vader_compound,
            'subjectivity': self.subjectivity
        }

@dataclass
class MarketSafety:
    """Model for market safety analysis"""
    safety_score: int
    risk_level: RiskLevel
    risk_color: str
    volatility: float = 0.5
    liquidity_score: int = 50
    correlation_risk: float = 0.3
    
    def __post_init__(self):
        if isinstance(self.risk_level, str):
            self.risk_level = RiskLevel(self.risk_level)
    
    @property
    def is_safe_to_trade(self) -> bool:
        """Check if conditions are safe for trading"""
        return self.safety_score >= 60
    
    @property
    def recommended_position_modifier(self) -> float:
        """Get recommended position size modifier"""
        if self.safety_score >= 70:
            return 1.0
        elif self.safety_score >= 40:
            return 0.7
        else:
            return 0.3
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'safety_score': self.safety_score,
            'risk_level': self.risk_level.value,
            'risk_color': self.risk_color,
            'volatility': self.volatility,
            'liquidity_score': self.liquidity_score,
            'correlation_risk': self.correlation_risk
        }

@dataclass
class TradingSignal:
    """Model for AI-generated trading signals"""
    pair: str
    signal: TradeType
    confidence: float
    reason: str
    safety_score: int
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if isinstance(self.signal, str):
            self.signal = TradeType(self.signal)
    
    @property
    def is_actionable(self) -> bool:
        """Check if signal is actionable (high confidence and safe)"""
        return self.confidence >= 70 and self.safety_score >= 40
    
    @property
    def risk_reward_ratio(self) -> Optional[float]:
        """Calculate risk-reward ratio if prices are available"""
        if all([self.entry_price, self.stop_loss, self.take_profit]):
            risk = abs(self.entry_price - self.stop_loss)
            reward = abs(self.take_profit - self.entry_price)
            return reward / risk if risk > 0 else None
        return None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'pair': self.pair,
            'signal': self.signal.value,
            'confidence': self.confidence,
            'reason': self.reason,
            'safety_score': self.safety_score,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'position_size': self.position_size,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class TradeRecord:
    """Model for trade records"""
    id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    event_name: str = ""
    currency_pair: str = ""
    trade_type: str = ""
    entry_price: float = 0.0
    exit_price: float = 0.0
    profit_loss: float = 0.0
    safety_score: int = 50
    sentiment_score: float = 0.0
    position_size: float = 0.0
    duration_minutes: int = 0
    
    @property
    def is_profitable(self) -> bool:
        """Check if trade was profitable"""
        return self.profit_loss > 0
    
    @property
    def return_percentage(self) -> float:
        """Calculate return percentage"""
        if self.entry_price > 0:
            return (self.profit_loss / (self.entry_price * self.position_size)) * 100
        return 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'event_name': self.event_name,
            'currency_pair': self.currency_pair,
            'trade_type': self.trade_type,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'profit_loss': self.profit_loss,
            'safety_score': self.safety_score,
            'sentiment_score': self.sentiment_score,
            'position_size': self.position_size,
            'duration_minutes': self.duration_minutes
        }

@dataclass
class MarketData:
    """Model for market data"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime = field(default_factory=datetime.now)
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None
    
    @property
    def is_bullish(self) -> bool:
        """Check if price movement is bullish"""
        return self.change > 0
    
    @property
    def spread_percentage(self) -> Optional[float]:
        """Calculate spread as percentage"""
        if self.bid and self.ask and self.price > 0:
            return ((self.ask - self.bid) / self.price) * 100
        return None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'price': self.price,
            'change': self.change,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'timestamp': self.timestamp.isoformat(),
            'bid': self.bid,
            'ask': self.ask,
            'spread': self.spread
        }

@dataclass
class DashboardState:
    """Model for dashboard state management"""
    last_update: datetime = field(default_factory=datetime.now)
    selected_currencies: List[str] = field(default_factory=lambda: ['USD', 'EUR', 'GBP'])
    timezone: str = "GMT+2"
    auto_refresh: bool = False
    refresh_interval: int = 30
    active_filters: Dict[str, Union[str, List[str]]] = field(default_factory=dict)
    
    def update_timestamp(self):
        """Update the last update timestamp"""
        self.last_update = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'last_update': self.last_update.isoformat(),
            'selected_currencies': self.selected_currencies,
            'timezone': self.timezone,
            'auto_refresh': self.auto_refresh,
            'refresh_interval': self.refresh_interval,
            'active_filters': self.active_filters
        }

# Utility functions for model validation and conversion

def validate_economic_event(data: Dict) -> bool:
    """Validate economic event data"""
    required_fields = ['time', 'currency', 'event', 'impact']
    return all(field in data for field in required_fields)

def validate_news_item(data: Dict) -> bool:
    """Validate news item data"""
    required_fields = ['title', 'summary', 'source', 'url', 'published']
    return all(field in data for field in required_fields)

def create_economic_event_from_dict(data: Dict) -> EconomicEvent:
    """Create EconomicEvent from dictionary"""
    if isinstance(data['time'], str):
        data['time'] = datetime.fromisoformat(data['time'])
    return EconomicEvent(**data)

def create_news_item_from_dict(data: Dict) -> NewsItem:
    """Create NewsItem from dictionary"""
    if isinstance(data['published'], str):
        data['published'] = datetime.fromisoformat(data['published'])
    return NewsItem(**data)
"""
Configuration settings for the Fundamental News Trading Dashboard
"""

import os
from typing import Dict, List

# API Configuration
API_KEYS = {
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
    'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
    'NEWS_API_KEY': os.getenv('NEWS_API_KEY', ''),
    'FOREX_FACTORY_API_KEY': os.getenv('FOREX_FACTORY_API_KEY', '')
}

# Trading Configuration
TRADING_CONFIG = {
    'DEFAULT_RISK_PERCENTAGE': 2.0,
    'MAX_RISK_PERCENTAGE': 5.0,
    'MIN_SAFETY_SCORE': 30,
    'HIGH_IMPACT_EVENTS': ['Non-Farm Payrolls', 'Interest Rate Decision', 'GDP', 'CPI'],
    'MAJOR_CURRENCIES': ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']
}

# News Sources Configuration
NEWS_SOURCES = {
    'REUTERS': {
        'url': 'https://www.reuters.com/markets/',
        'reliability': 0.9
    },
    'BLOOMBERG': {
        'url': 'https://www.bloomberg.com/markets',
        'reliability': 0.95
    },
    'FINANCIAL_TIMES': {
        'url': 'https://www.ft.com/markets',
        'reliability': 0.9
    },
    'MARKETWATCH': {
        'url': 'https://www.marketwatch.com/',
        'reliability': 0.8
    }
}

# Economic Events Configuration
ECONOMIC_EVENTS = {
    'HIGH_IMPACT': {
        'events': [
            'Non-Farm Payrolls',
            'Interest Rate Decision',
            'GDP Growth Rate',
            'Consumer Price Index',
            'Producer Price Index',
            'Unemployment Rate',
            'Retail Sales',
            'Industrial Production'
        ],
        'safety_modifier': -30,
        'volatility_expectation': 'High'
    },
    'MEDIUM_IMPACT': {
        'events': [
            'Manufacturing PMI',
            'Services PMI',
            'Consumer Confidence',
            'Trade Balance',
            'Housing Starts',
            'Durable Goods Orders'
        ],
        'safety_modifier': -15,
        'volatility_expectation': 'Medium'
    },
    'LOW_IMPACT': {
        'events': [
            'Building Permits',
            'Existing Home Sales',
            'Crude Oil Inventories',
            'Initial Jobless Claims'
        ],
        'safety_modifier': -5,
        'volatility_expectation': 'Low'
    }
}

# Currency Pair Configuration
CURRENCY_PAIRS = {
    'MAJOR': ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD'],
    'MINOR': ['EURGBP', 'EURJPY', 'EURCHF', 'EURAUD', 'EURCAD', 'GBPJPY', 'GBPCHF'],
    'EXOTIC': ['USDTRY', 'USDZAR', 'USDMXN', 'USDSEK', 'USDNOK', 'USDPLN']
}

# AI Model Configuration
AI_CONFIG = {
    'SENTIMENT_MODEL': 'vader',  # Options: 'vader', 'textblob', 'transformers'
    'CONFIDENCE_THRESHOLD': 0.6,
    'SENTIMENT_WEIGHTS': {
        'news_sentiment': 0.4,
        'economic_data': 0.4,
        'technical_analysis': 0.2
    }
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'REFRESH_INTERVAL': 30,  # seconds
    'MAX_NEWS_ITEMS': 20,
    'MAX_EVENTS_DISPLAY': 10,
    'CHART_HEIGHT': 400,
    'TIMEZONE_DEFAULT': 'GMT+2'
}

# Database Configuration
DATABASE_CONFIG = {
    'DB_NAME': 'trading_data.db',
    'BACKUP_INTERVAL': 24,  # hours
    'MAX_RECORDS': 10000
}

# Risk Management Rules
RISK_MANAGEMENT = {
    'SAFETY_SCORE_THRESHOLDS': {
        'LOW_RISK': 70,
        'MEDIUM_RISK': 40,
        'HIGH_RISK': 0
    },
    'POSITION_SIZE_MODIFIERS': {
        'HIGH_IMPACT_EVENT': 0.5,  # Reduce position size by 50%
        'LOW_SAFETY_SCORE': 0.3,  # Reduce position size by 70%
        'HIGH_VOLATILITY': 0.6    # Reduce position size by 40%
    },
    'STOP_LOSS_MULTIPLIERS': {
        'HIGH_IMPACT': 2.0,
        'MEDIUM_IMPACT': 1.5,
        'LOW_IMPACT': 1.0
    }
}

# Notification Settings
NOTIFICATION_CONFIG = {
    'ENABLE_ALERTS': True,
    'ALERT_THRESHOLDS': {
        'SAFETY_SCORE_DROP': 20,
        'HIGH_IMPACT_EVENT': 60,  # minutes before event
        'SENTIMENT_CHANGE': 0.3   # sentiment score change
    }
}

def get_config(section: str) -> Dict:
    """Get configuration for a specific section"""
    config_map = {
        'api': API_KEYS,
        'trading': TRADING_CONFIG,
        'news': NEWS_SOURCES,
        'events': ECONOMIC_EVENTS,
        'pairs': CURRENCY_PAIRS,
        'ai': AI_CONFIG,
        'dashboard': DASHBOARD_CONFIG,
        'database': DATABASE_CONFIG,
        'risk': RISK_MANAGEMENT,
        'notifications': NOTIFICATION_CONFIG
    }
    return config_map.get(section, {})

def validate_config() -> bool:
    """Validate that all required configuration is present"""
    required_keys = ['OPENAI_API_KEY']  # Add other required keys as needed
    
    missing_keys = []
    for key in required_keys:
        if not API_KEYS.get(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"Warning: Missing configuration keys: {missing_keys}")
        return False
    
    return True
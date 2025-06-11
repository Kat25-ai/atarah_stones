# 📈 Fundamental News Trading Dashboard

A comprehensive AI-powered trading dashboard that analyzes high-impact economic events, assesses market safety, and generates intelligent trade signals for fundamental news trading.

![Dashboard Preview](https://img.shields.io/badge/Status-Ready-green) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red)

## 🚀 Key Features

### 1. **High-Impact Events Monitor**
- Real-time economic calendar integration
- Safety score calculation (0-100) for each event
- Color-coded risk assessment system
- Event impact classification (High/Medium/Low)

### 2. **AI-Powered News Sentiment Analysis**
- Real-time sentiment scoring using multiple NLP models
- Bullish/bearish/neutral classification
- Confidence scoring and subjectivity analysis
- Direct links to source articles

### 3. **Market Safety Indicators**
- Algorithmic safety scoring system
- Visual risk classification (green/yellow/red)
- Historical volatility analysis
- Position size recommendations

### 4. **Fundamental Trading Rules**
- Core principles for news-based trading
- Event-specific trading strategies
- Risk management visualization
- Position size calculator

### 5. **AI Trading Insights**
- Machine learning-powered trade signals
- Currency correlation analysis
- Market sentiment aggregation
- Automated risk assessment

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Internet connection for real-time data

### Quick Start

1. **Clone or download the dashboard files**
   ```bash
   cd fundamental_news_dashboard
   ```

2. **Run the setup script**
   ```bash
   python run_dashboard.py
   ```
   
   This will automatically:
   - Check Python version compatibility
   - Install required packages
   - Set up the environment
   - Launch the dashboard

3. **Access the dashboard**
   - Open your browser and go to: `http://localhost:8501`
   - The dashboard will load with sample data

### Manual Installation

If you prefer manual setup:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

## 📊 Dashboard Sections

### Economic Calendar Tab
- **Live Events**: View upcoming high-impact economic events
- **Safety Scores**: Each event shows a calculated safety score
- **Risk Assessment**: Color-coded risk levels for trading decisions
- **Event Details**: Forecast vs. previous values with actual results

### News Sentiment Tab
- **Sentiment Analysis**: AI-powered analysis of financial news
- **Source Integration**: News from Reuters, Bloomberg, Financial Times
- **Sentiment Distribution**: Visual breakdown of market sentiment
- **Confidence Scoring**: Reliability metrics for each analysis

### Market Safety Tab
- **Overall Safety Gauge**: Real-time market safety indicator
- **Risk Recommendations**: Trading advice based on current conditions
- **Volatility Tracking**: Historical and current volatility metrics
- **Position Size Guidance**: Automated position sizing recommendations

### Trading Rules Tab
- **Core Principles**: Fundamental trading guidelines
- **Event Strategies**: Specific approaches for different event types
- **Risk Management**: Position sizing and stop-loss calculations
- **Timing Rules**: When to enter and exit trades around news events

### AI Insights Tab
- **Trading Signals**: AI-generated buy/sell/hold recommendations
- **Market Sentiment**: Aggregated sentiment analysis
- **Correlation Matrix**: Currency pair relationship analysis
- **Smart Recommendations**: Context-aware trading suggestions

## 🔧 Configuration

### API Keys (Optional)
For enhanced functionality, configure these API keys in your `.env` file:

```env
OPENAI_API_KEY=your_openai_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEWS_API_KEY=your_news_api_key_here
```

### Trading Settings
Customize your trading parameters:

- **Risk Percentage**: Default risk per trade (1-5%)
- **Account Balance**: Your trading account size
- **Preferred Currencies**: Focus on specific currency pairs
- **Timezone**: Adjust for your local time zone

## 📈 How to Use the Dashboard

### Before Trading
1. **Check Safety Score**: Review overall market safety (aim for 60+)
2. **Analyze Upcoming Events**: Focus on high-impact events
3. **Review News Sentiment**: Understand market bias
4. **Calculate Position Size**: Use the built-in calculator

### During Events
1. **Monitor Real-time Updates**: Watch for actual vs. forecast data
2. **Track Sentiment Changes**: Look for sentiment shifts
3. **Follow Safety Guidelines**: Respect the risk management rules
4. **Use Smaller Positions**: Reduce size during high-impact events

### After Events
1. **Review Trade Outcomes**: Analyze what worked
2. **Update Strategy**: Learn from market reactions
3. **Record Performance**: Use the built-in trade tracking
4. **Adjust Risk Parameters**: Refine your approach

## 🎯 Trading Strategies by Event Type

### High-Impact Events (NFP, Interest Rates, GDP)
- **Strategy**: Wait for initial volatility to settle
- **Position Size**: Reduce by 50%
- **Stop Loss**: Use wider stops (2x normal)
- **Timing**: Avoid first 5-10 minutes after release

### Medium-Impact Events (CPI, PMI, Retail Sales)
- **Strategy**: Trade continuation after initial move
- **Position Size**: Standard or slightly reduced
- **Stop Loss**: 1.5x normal stops
- **Timing**: Can trade sooner than high-impact events

### Low-Impact Events
- **Strategy**: Normal trading approach
- **Position Size**: Standard size
- **Stop Loss**: Normal stops
- **Timing**: Immediate trading possible

## 🛡️ Risk Management Features

### Automated Safety Scoring
- **Event Impact**: Adjusts for event importance
- **Market Volatility**: Considers current market conditions
- **Time Proximity**: Accounts for time until event
- **Historical Data**: Uses past market reactions

### Position Size Calculator
- **Risk-Based Sizing**: Calculates based on account risk
- **Safety Adjustments**: Reduces size for risky conditions
- **Event Modifiers**: Adjusts for event impact
- **Stop Loss Integration**: Considers stop distance

### Alert System
- **Safety Warnings**: Alerts when conditions deteriorate
- **Event Notifications**: Reminds of upcoming events
- **Sentiment Changes**: Flags significant sentiment shifts

## 📊 Data Sources

### Economic Data
- **Primary**: Forex Factory economic calendar
- **Backup**: Alpha Vantage economic indicators
- **Updates**: Real-time event data and results

### News Sources
- **Reuters**: High-reliability financial news
- **Bloomberg**: Market-moving news and analysis
- **Financial Times**: In-depth economic coverage
- **MarketWatch**: Real-time market updates

### Market Data
- **Forex Rates**: Real-time currency pair prices
- **Volatility**: Historical and implied volatility
- **Volume**: Trading volume indicators

## 🤖 AI Integration

### Sentiment Analysis Models
- **VADER**: Valence Aware Dictionary and sEntiment Reasoner
- **TextBlob**: Simple sentiment polarity analysis
- **Combined Scoring**: Weighted average of multiple models

### Signal Generation
- **Multi-factor Analysis**: Combines news, events, and technical data
- **Confidence Scoring**: Reliability metrics for each signal
- **Risk Assessment**: Integrated safety evaluation

### Machine Learning Features
- **Pattern Recognition**: Identifies recurring market patterns
- **Correlation Analysis**: Tracks currency pair relationships
- **Adaptive Learning**: Improves over time with more data

## 🔍 Troubleshooting

### Common Issues

**Dashboard won't start**
- Check Python version (3.8+ required)
- Install missing packages: `pip install -r requirements.txt`
- Check port availability (8501)

**No data showing**
- Verify internet connection
- Check API key configuration
- Review error messages in console

**Slow performance**
- Reduce refresh frequency
- Limit number of currency pairs
- Close other browser tabs

### Getting Help
- Check the console for error messages
- Verify all dependencies are installed
- Ensure proper file permissions
- Review the configuration settings

## 📝 Disclaimer

**Important**: This dashboard is for educational and informational purposes only. It is not financial advice. Always:

- Conduct your own analysis before trading
- Never risk more than you can afford to lose
- Consider consulting with a financial advisor
- Practice with demo accounts first
- Understand that past performance doesn't guarantee future results

## 🚀 Future Enhancements

### Planned Features
- **Real-time Price Alerts**: WebSocket integration for live alerts
- **Central Bank Speech Analysis**: NLP analysis of Fed/ECB speeches
- **Advanced Correlation Matrices**: Multi-timeframe correlation analysis
- **Trade Journal Integration**: Comprehensive trade tracking
- **Mobile Responsive Design**: Optimized for mobile devices
- **Custom Alert System**: Email/SMS notifications
- **Backtesting Module**: Historical strategy testing
- **Social Sentiment**: Twitter/Reddit sentiment integration

### API Integrations
- **Forex Factory**: Direct API integration
- **Economic Calendar APIs**: Multiple data sources
- **News APIs**: Expanded news coverage
- **Broker Integration**: Direct trading capabilities

## 📄 License

This project is provided as-is for educational purposes. Feel free to modify and adapt for your own use.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional data sources
- Enhanced AI models
- Better visualization
- Mobile optimization
- Performance improvements

---

**Happy Trading! 📈**

*Remember: The best traders are those who manage risk effectively and never stop learning.*
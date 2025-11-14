# TurboTrader-AI 🤖📈

**AI-powered multi-timeframe trading bot with Binance API integration, automated learning, and local Llama 3.1 AI analysis**

## Features

✨ **Multi-Timeframe Analysis**
- Analyzes 12 timeframes: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 1w
- Sigmoid normalization for consistent 0-100 scale scoring
- Weighted scoring: Price(70%), Volume(10%), RSI(10%), Volatility(10%)

🧠 **Local AI Integration**
- Uses Llama 3.1 8B (running locally via Ollama)
- Auto-learning from trading results
- Strategy optimization based on win/loss rate
- Improves decision-making over time

📊 **Technical Indicators**
- Price momentum (ROC)
- Volume analysis
- RSI (Relative Strength Index)
- Volatility calculation
- All normalized via sigmoid to 0-100 scale

🤝 **Binance Integration**
- Real-time market data fetching
- Automated order execution (BUY/SELL)
- Balance and position tracking
- Support for testnet and mainnet

📉 **Backtesting**
- Test strategies on historical data
- Configurable lookback period
- Win rate calculation
- Performance metrics

🔄 **Automated Trading**
- Scan all coins simultaneously
- Per-coin independent analysis
- Automatic position sizing
- Risk management built-in

## Installation

### Prerequisites
- Python 3.8+
- Binance account with API keys
- Llama 3.1 8B (Ollama installed and running)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Must78Must/TurboTrader-AI.git
   cd TurboTrader-AI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create `.env` file:
   ```
   BINANCE_API_KEY=your_api_key_here
   BINANCE_API_SECRET=your_api_secret_here
   BINANCE_TESTNET=True
   ```

4. **Start Llama 3.1 locally**
   ```bash
   ollama run llama2  # or llama-3.1 if available
   ```

## Usage

### Start Trading Bot
```bash
python main.py start
```

### Stop All Positions
```bash
python main.py stop
```

### Check Status
```bash
python main.py status
```

### Analyze a Coin
```bash
python main.py analyze --coin BTCUSDT
```

### Run Backtest
```bash
python main.py backtest --coin ETHUSDT --days 30
```

### Start with Specific Coins
```bash
python main.py start --coins BTCUSDT ETHUSDT BNBUSDT
```

## Configuration

Edit `config.py` to customize:

- **Trading Parameters**
  - `INITIAL_BALANCE_PERCENTAGE`: 10% of account
  - `TOP_COINS`: Coins to trade
  - `TIMEFRAMES`: Time periods to analyze
  - `BUY_THRESHOLD`: Score > 70 = BUY
  - `SELL_THRESHOLD`: Score < 30 = SELL

- **Weights**
  - `WEIGHT_PRICE`: 70%
  - `WEIGHT_VOLUME`: 10%
  - `WEIGHT_RSI`: 10%
  - `WEIGHT_VOLATILITY`: 10%

- **Llama AI**
  - `LLAMA_HOST`: localhost:11434
  - `LLAMA_MODEL`: llama-3.1

## Module Structure

```
TurboTrader-AI/
├── config.py                 # Configuration settings
├── indicators.py             # Technical analysis (Pine Script conversion)
├── binance_connector.py       # Binance API integration
├── ai_engine.py              # Llama AI integration
├── analyzer.py               # Multi-coin analyzer
├── backtest.py               # Backtesting engine
├── learning.py               # Auto-learning system
├── scanner.py                # Market scanner
├── executor.py               # Order execution
├── main.py                   # CLI controller
└── requirements.txt          # Python dependencies
```

## How It Works

1. **Data Collection**
   - Fetches OHLCV data for each coin from Binance
   - All 12 timeframes simultaneously

2. **Analysis**
   - Calculates technical indicators
   - Normalizes to 0-100 scale using sigmoid
   - Applies weighted scoring

3. **AI Decision**
   - Sends analysis to local Llama 3.1
   - Gets buy/sell recommendations
   - Learns from past trades

4. **Execution**
   - Places orders on Binance
   - Tracks positions
   - Manages risk

5. **Learning**
   - Records trade results
   - Updates win rate
   - Adjusts strategy weights

## Trading Strategy

- **BUY**: Combined score > 70 + AI confirmation
- **SELL**: Combined score < 30 + AI confirmation
- **NO LEVERAGE**: Long-only strategy (as per preference)
- **AUTO-SIZING**: Position size = Account% / Active coins

## Performance Monitoring

All trades logged to `trading_bot.log`:
- Entry/exit prices
- P&L calculations
- Strategy performance
- Error tracking

## Safety Features

✅ Testnet support for safe testing
✅ Manual approval for new coins
✅ Risk per trade limitation
✅ Balance tracking
✅ Position limit (5 concurrent)
✅ Automatic stop-loss calculation

## Roadmap

- [ ] Advanced backtest with Backtrader
- [ ] Web dashboard
- [ ] Database persistence
- [ ] Portfolio optimization
- [ ] Multi-exchange support
- [ ] Discord/Telegram alerts

## Support

For issues and questions:
1. Check logs in `trading_bot.log`
2. Review configuration in `config.py`
3. Ensure Llama is running: `ollama list`
4. Verify Binance API keys are correct

## Disclaimer

⚠️ **IMPORTANT**: This bot is for educational purposes. Use at your own risk. Always start with testnet before using real money. Cryptocurrency trading carries risks.

## License

MIT License - Feel free to use and modify

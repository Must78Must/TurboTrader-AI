# TurboTrader-AI Configuration
# ====================================

import os
from dotenv import load_dotenv

load_dotenv()

# Binance API Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'

# Trading Configuration
INITIAL_BALANCE_PERCENTAGE = 0.10  # 10% of account balance
MIN_BALANCE = 10  # Minimum balance to keep in USDT
PER_COIN_ALLOCATION = 0.05  # 5% per coin

# Coins to Monitor (Start with Top 5)
TOP_COINS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']

# Timeframes (1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 1w)
TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '1w']

# Indicator Weights (must sum to 100)
WEIGHT_PRICE = 70.0  # Price ROC weight
WEIGHT_VOLUME = 10.0  # Volume weight
WEIGHT_RSI = 10.0    # RSI weight
WEIGHT_VOLATILITY = 10.0  # Volatility weight

# Thresholds
BUY_THRESHOLD = 70.0   # Score > 70 = BUY signal
SELL_THRESHOLD = 30.0  # Score < 30 = SELL signal

# Normalization
LOOKBACK_PERIOD = 100
SIGMOID_K = 1.0
VOLATILITY_PERIOD = 20
RSI_PERIOD = 14

# Llama AI Configuration
LLAMA_MODEL = 'llama-3.1'  # Local model
LLAMA_HOST = 'http://localhost:11434'  # Ollama default

# Trading Parameters
MAX_CONCURRENT_POSITIONS = 5
POSITION_SIZE_USDT = 100  # Per position in USDT
RISK_PERCENTAGE_PER_TRADE = 2.0

# Backtest Configuration
BACKTEST_DAYS = 30  # Test on last 30 days of data
BACKTEST_INTERVAL = '1h'  # Backtest interval

# Learning Configuration
MIN_TRADES_FOR_LEARNING = 10
WIN_RATE_THRESHOLD = 0.55  # 55% win rate to enable strategy
MAX_STRATEGIES_PER_COIN = 3

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'trading_bot.log'

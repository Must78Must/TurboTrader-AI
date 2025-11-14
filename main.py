#!/usr/bin/env python3
# TurboTrader-AI Main Program
# Command-line interface for controlling the trading bot

import sys
import time
import logging
import argparse
from typing import Optional
from datetime import datetime

import config
from binance_connector import get_connector
from indicators import TechnicalIndicators, get_multi_timeframe_scores

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingBotController:
    """
    Main controller for TurboTrader-AI
    Handles commands: start, stop, status, backtest, etc.
    """
    
    def __init__(self):
        self.connector = get_connector()
        self.is_running = False
        self.active_coins = []
        self.positions = {}
        logger.info("TradingBotController initialized")
    
    def start_scanning(self, coins: list = None):
        """
        Start market scanning
        """
        if self.is_running:
            logger.warning("Bot is already running")
            return
        
        coins = coins or config.TOP_COINS
        self.active_coins = coins
        self.is_running = True
        
        logger.info(f"Starting trading bot with coins: {coins}")
        print(f"\n[START] Trading bot started at {datetime.now()}")
        print(f"Active coins: {coins}")
        print(f"Initial balance: {self.connector.get_usdt_balance()} USDT")
        print("\nBot is now scanning markets...")
    
    def stop_scanning(self):
        """
        Stop market scanning and close all positions
        """
        if not self.is_running:
            logger.warning("Bot is not running")
            return
        
        print("\n[STOP] Stopping trading bot...")
        print("Closing all positions...")
        
        # Close all positions logic would go here
        self.is_running = False
        logger.info("Trading bot stopped")
        print("[STOP] Bot stopped at", datetime.now())
    
    def get_status(self):
        """
        Get current bot status
        """
        status = {
            'running': self.is_running,
            'active_coins': self.active_coins,
            'usdt_balance': self.connector.get_usdt_balance(),
            'positions': self.positions,
            'timestamp': datetime.now().isoformat()
        }
        
        print("\n[STATUS] Trading Bot Status")
        print(f"Running: {status['running']}")
        print(f"Active Coins: {status['active_coins']}")
        print(f"USDT Balance: {status['usdt_balance']:.2f}")
        print(f"Open Positions: {len(status['positions'])}")
        
        return status
    
    def analyze_coin(self, symbol: str):
        """
        Analyze a specific coin across all timeframes
        """
        print(f"\n[ANALYZE] {symbol} - Multi-Timeframe Analysis")
        print("=" * 60)
        
        try:
            # Fetch OHLCV data for all timeframes
            ohlcv_dict = {}
            for tf in config.TIMEFRAMES:
                df = self.connector.get_ohlcv(symbol, tf, limit=100)
                if not df.empty:
                    ohlcv_dict[tf] = df
            
            if not ohlcv_dict:
                print(f"No data available for {symbol}")
                return
            
            # Calculate scores
            weights = {
                'price': config.WEIGHT_PRICE,
                'volume': config.WEIGHT_VOLUME,
                'rsi': config.WEIGHT_RSI,
                'volatility': config.WEIGHT_VOLATILITY
            }
            
            scores = get_multi_timeframe_scores(ohlcv_dict, weights)
            
            # Display results
            print(f"{'Timeframe':<12} {'Score':<8} {'Price':<8} {'Vol':<8} {'RSI':<8}")
            print("-" * 60)
            
            for tf in config.TIMEFRAMES:
                if tf in scores:
                    score, components = scores[tf]
                    print(f"{tf:<12} {score:>6.2f}   {components.get('price', 0):>6.2f}  "
                          f"{components.get('volume', 0):>6.2f}  {components.get('rsi', 0):>6.2f}")
            
            print("=" * 60)
        
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            print(f"Error: {e}")
    
    def backtest(self, coin: str, days: int = None):
        """
        Run backtest on historical data
        """
        days = days or config.BACKTEST_DAYS
        print(f"\n[BACKTEST] {coin} - Last {days} days")
        print("Backtest feature coming soon...")

def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(description='TurboTrader-AI Trading Bot')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'analyze', 'backtest'],
                       help='Command to execute')
    parser.add_argument('--coin', help='Coin symbol (e.g., BTCUSDT)')
    parser.add_argument('--coins', nargs='+', help='List of coins to trade')
    parser.add_argument('--days', type=int, help='Days for backtest')
    
    args = parser.parse_args()
    
    controller = TradingBotController()
    
    try:
        if args.command == 'start':
            coins = args.coins or config.TOP_COINS
            controller.start_scanning(coins)
            
            # Keep bot running
            while controller.is_running:
                time.sleep(10)
        
        elif args.command == 'stop':
            controller.stop_scanning()
        
        elif args.command == 'status':
            controller.get_status()
        
        elif args.command == 'analyze':
            if not args.coin:
                print("Error: --coin required for analyze command")
                sys.exit(1)
            controller.analyze_coin(args.coin)
        
        elif args.command == 'backtest':
            if not args.coin:
                print("Error: --coin required for backtest command")
                sys.exit(1)
            controller.backtest(args.coin, args.days)
    
    except KeyboardInterrupt:
        print("\n[STOP] Bot interrupted by user")
        controller.stop_scanning()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

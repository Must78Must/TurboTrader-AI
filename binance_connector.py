# TurboTrader-AI Binance Connector
# Handles API calls to Binance for market data and order execution

import ccxt
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import config

logger = logging.getLogger(__name__)

class BinanceConnector:
    """
    Binance API connector for market data and trading
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = None):
        """
        Initialize Binance connector
        """
        self.api_key = api_key or config.BINANCE_API_KEY
        self.api_secret = api_secret or config.BINANCE_API_SECRET
        self.testnet = testnet if testnet is not None else config.BINANCE_TESTNET
        
        # Initialize CCXT exchange
        self.exchange = ccxt.binance({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'sandbox': self.testnet
        })
        
        logger.info(f"Binance connector initialized (Testnet: {self.testnet})")
    
    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get OHLCV data from Binance
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_balance(self) -> Dict[str, float]:
        """
        Get account balance
        """
        try:
            balance = self.exchange.fetch_balance()
            return {
                'free': balance.get('free', {}),
                'used': balance.get('used', {}),
                'total': balance.get('total', {})
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}
    
    def get_usdt_balance(self) -> float:
        """
        Get USDT balance
        """
        try:
            balance = self.exchange.fetch_balance()
            return balance['USDT']['free']
        except Exception as e:
            logger.error(f"Error fetching USDT balance: {e}")
            return 0.0
    
    def place_buy_order(
        self,
        symbol: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Dict:
        """
        Place a buy order
        """
        try:
            if price:
                # Limit order
                order = self.exchange.create_limit_buy_order(symbol, quantity, price)
            else:
                # Market order
                order = self.exchange.create_market_buy_order(symbol, quantity)
            
            logger.info(f"Buy order placed: {symbol} {quantity} @ {price}")
            return order
        
        except Exception as e:
            logger.error(f"Error placing buy order: {e}")
            return {}
    
    def place_sell_order(
        self,
        symbol: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Dict:
        """
        Place a sell order
        """
        try:
            if price:
                # Limit order
                order = self.exchange.create_limit_sell_order(symbol, quantity, price)
            else:
                # Market order
                order = self.exchange.create_market_sell_order(symbol, quantity)
            
            logger.info(f"Sell order placed: {symbol} {quantity} @ {price}")
            return order
        
        except Exception as e:
            logger.error(f"Error placing sell order: {e}")
            return {}
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """
        Cancel an open order
        """
        try:
            cancelled = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order cancelled: {order_id}")
            return cancelled
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return {}
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get open orders
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []
    
    def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """
        Get order status
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            logger.error(f"Error fetching order status: {e}")
            return {}
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price of a symbol
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return 0.0
    
    def get_all_symbols(self) -> List[str]:
        """
        Get all trading pairs
        """
        try:
            return self.exchange.symbols
        except Exception as e:
            logger.error(f"Error fetching symbols: {e}")
            return []

# Global connector instance
_connector = None

def get_connector() -> BinanceConnector:
    """
    Get or create global connector instance
    """
    global _connector
    if _connector is None:
        _connector = BinanceConnector()
    return _connector

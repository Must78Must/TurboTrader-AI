# TurboTrader-AI Order Executor
# Handles order execution and position management

import logging
from typing import Dict, Optional
from datetime import datetime
from binance_connector import get_connector
import config

logger = logging.getLogger(__name__)

class OrderExecutor:
    """
    Manages order execution for trading positions
    """
    
    def __init__(self):
        self.connector = get_connector()
        self.positions = {}
        self.trades = []
    
    def execute_buy(
        self,
        symbol: str,
        quantity: float,
        reason: str = "AI Signal"
    ) -> Dict:
        """
        Execute a buy order
        """
        try:
            # Get current price
            price = self.connector.get_current_price(symbol)
            
            # Place order
            order = self.connector.place_buy_order(symbol, quantity)
            
            # Record trade
            trade = {
                'symbol': symbol,
                'type': 'BUY',
                'quantity': quantity,
                'entry_price': price,
                'timestamp': datetime.now(),
                'reason': reason
            }
            
            self.trades.append(trade)
            self.positions[symbol] = trade
            
            logger.info(f"Buy executed: {symbol} {quantity} @ {price}")
            return order
        
        except Exception as e:
            logger.error(f"Buy execution failed: {e}")
            return {}
    
    def execute_sell(
        self,
        symbol: str,
        quantity: float,
        reason: str = "AI Signal"
    ) -> Dict:
        """
        Execute a sell order
        """
        try:
            # Get current price
            price = self.connector.get_current_price(symbol)
            
            # Place order
            order = self.connector.place_sell_order(symbol, quantity)
            
            # Record trade
            trade = {
                'symbol': symbol,
                'type': 'SELL',
                'quantity': quantity,
                'exit_price': price,
                'timestamp': datetime.now(),
                'reason': reason
            }
            
            self.trades.append(trade)
            
            # Calculate P&L if position exists
            if symbol in self.positions:
                entry = self.positions[symbol]['entry_price']
                pnl = (price - entry) * quantity
                pnl_percent = ((price - entry) / entry) * 100
                
                logger.info(f"Sell executed: {symbol} {quantity} @ {price} | P&L: {pnl} ({pnl_percent:.2f}%)")
                del self.positions[symbol]
            
            return order
        
        except Exception as e:
            logger.error(f"Sell execution failed: {e}")
            return {}
    
    def get_positions(self) -> Dict:
        """
        Get current positions
        """
        return self.positions
    
    def close_all_positions(self) -> Dict:
        """
        Close all open positions
        """
        closed = {}
        for symbol in list(self.positions.keys()):
            try:
                entry = self.positions[symbol]['entry_price']
                quantity = self.positions[symbol]['quantity']
                price = self.connector.get_current_price(symbol)
                pnl = (price - entry) * quantity
                
                order = self.execute_sell(symbol, quantity, "Close All")
                closed[symbol] = {'pnl': pnl, 'order': order}
            
            except Exception as e:
                logger.error(f"Failed to close {symbol}: {e}")
        
        return closed

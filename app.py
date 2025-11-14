#!/usr/bin/env python3
# TurboTrader-AI Web Dashboard
# Flask-based GUI for trading bot control

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import threading
import json
import os
from pathlib import Path

import config
from indicators import TechnicalIndicators
from binance_connector import get_connector
from executor import OrderExecutor

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
bot_state = {
    'running': False,
    'active_coins': [],
    'positions': {},
    'trades': [],
    'status': 'IDLE',
    'last_update': None,
    'scores': {},
    'balance': 0.0,
    'total_pnl': 0.0
}

connector = get_connector()
executor = OrderExecutor()
indicator = TechnicalIndicators()

# ============= WEB ROUTES =============

@app.route('/')
def dashboard():
    """
    Main dashboard page
    """
    return render_template('dashboard.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Get current bot status
    """
    bot_state['balance'] = connector.get_usdt_balance()
    bot_state['last_update'] = datetime.now().isoformat()
    bot_state['positions'] = executor.get_positions()
    
    return jsonify(bot_state)

@app.route('/api/start', methods=['POST'])
def start_trading():
    """
    Start trading bot
    """
    data = request.json
    coins = data.get('coins', config.TOP_COINS)
    
    bot_state['running'] = True
    bot_state['active_coins'] = coins
    bot_state['status'] = 'RUNNING'
    
    logger.info(f"Bot started with coins: {coins}")
    
    # Start bot in background thread
    threading.Thread(target=run_bot_loop, args=(coins,), daemon=True).start()
    
    return jsonify({'status': 'started', 'coins': coins})

@app.route('/api/stop', methods=['POST'])
def stop_trading():
    """
    Stop trading and close positions
    """
    bot_state['running'] = False
    bot_state['status'] = 'STOPPING'
    
    # Close all positions
    closed = executor.close_all_positions()
    
    bot_state['status'] = 'STOPPED'
    logger.info(f"Bot stopped. Closed positions: {closed}")
    
    return jsonify({'status': 'stopped', 'closed_positions': len(closed)})

@app.route('/api/analyze/<coin>', methods=['GET'])
def analyze_coin(coin):
    """
    Analyze specific coin
    """
    try:
        symbol = f"{coin}USDT" if not coin.endswith('USDT') else coin
        
        # Fetch data for all timeframes
        scores = {}
        for tf in config.TIMEFRAMES:
            df = connector.get_ohlcv(symbol, tf, limit=100)
            if not df.empty:
                closes = df['close'].values
                volumes = df['volume'].values
                score, components = indicator.calculate_combined_score(
                    closes, volumes,
                    config.WEIGHT_PRICE, config.WEIGHT_VOLUME,
                    config.WEIGHT_RSI, config.WEIGHT_VOLATILITY
                )
                scores[tf] = {'score': float(score), 'components': components}
        
        bot_state['scores'][symbol] = scores
        
        return jsonify(scores)
    
    except Exception as e:
        logger.error(f"Error analyzing {coin}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/buy', methods=['POST'])
def manual_buy():
    """
    Manual buy order
    """
    data = request.json
    symbol = data.get('symbol')
    quantity = data.get('quantity', 0.01)
    
    try:
        order = executor.execute_buy(symbol, quantity, "Manual")
        logger.info(f"Manual buy: {symbol} {quantity}")
        return jsonify({'status': 'success', 'order': order})
    except Exception as e:
        logger.error(f"Buy error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sell', methods=['POST'])
def manual_sell():
    """
    Manual sell order
    """
    data = request.json
    symbol = data.get('symbol')
    quantity = data.get('quantity', 0.01)
    
    try:
        order = executor.execute_sell(symbol, quantity, "Manual")
        logger.info(f"Manual sell: {symbol} {quantity}")
        return jsonify({'status': 'success', 'order': order})
    except Exception as e:
        logger.error(f"Sell error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """
    Get trade history
    """
    return jsonify(executor.trades[-50:])  # Last 50 trades

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """
    Get account balance
    """
    balance = connector.get_usdt_balance()
    return jsonify({'usdt_balance': balance})

# ============= BOT LOOP =============

def run_bot_loop(coins):
    """
    Main bot trading loop (runs in background)
    """
    logger.info(f"Starting bot loop with coins: {coins}")
    
    while bot_state['running']:
        try:
            for coin in coins:
                symbol = f"{coin}USDT" if not coin.endswith('USDT') else coin
                
                # Analyze
                scores = analyze_coin(coin[:-5] if coin.endswith('USDT') else coin)
                data = scores.get_json()
                
                if data and '1h' in data:
                    score_1h = data['1h']['score']
                    
                    # BUY signal
                    if score_1h > config.BUY_THRESHOLD and symbol not in executor.positions:
                        quantity = 0.01  # Min quantity
                        executor.execute_buy(symbol, quantity, "AI Signal")
                    
                    # SELL signal
                    elif score_1h < config.SELL_THRESHOLD and symbol in executor.positions:
                        position = executor.positions[symbol]
                        quantity = position['quantity']
                        executor.execute_sell(symbol, quantity, "AI Signal")
        
        except Exception as e:
            logger.error(f"Bot loop error: {e}")
        
        # Sleep for 5 minutes
        import time
        time.sleep(300)

if __name__ == '__main__':
    logger.info("Starting TurboTrader-AI Web Dashboard")
    app.run(host='0.0.0.0', port=5000, debug=False)

# TurboTrader-AI Indicators Module
# Converts Pine Script logic to Python (Sigmoid Normalization)

import numpy as np
import pandas as pd
import math
from typing import Tuple, Dict, List

class TechnicalIndicators:
    """
    Multi-timeframe technical analysis based on Pine Script indicator
    Uses sigmoid normalization to convert all metrics to 0-100 scale
    """
    
    def __init__(self, lookback=100, sigmoid_k=1.0, vol_period=20, rsi_period=14):
        self.lookback = lookback
        self.sigmoid_k = sigmoid_k
        self.vol_period = vol_period
        self.rsi_period = rsi_period
    
    def sigmoid_normalize(self, data: np.ndarray) -> np.ndarray:
        """
        Normalize data using sigmoid function to 0-100 scale
        z-score -> sigmoid -> 0-100 mapping
        """
        if len(data) < 2:
            return data
        
        # Calculate z-score (standardization)
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return np.full_like(data, 50.0)  # Default to neutral
        
        z_score = (data - mean) / std
        
        # Apply sigmoid: 1 / (1 + e^(-k*z))
        sigmoid = 1.0 / (1.0 + np.exp(-self.sigmoid_k * z_score))
        
        # Scale to 0-100
        return sigmoid * 100.0
    
    def calculate_rsi(self, closes: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Calculate Relative Strength Index (RSI)
        """
        if len(closes) < period + 1:
            return np.full_like(closes, 50.0)
        
        # Calculate price changes
        deltas = np.diff(closes)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gains and losses
        avg_gains = np.zeros_like(closes)
        avg_losses = np.zeros_like(closes)
        
        avg_gains[period] = np.mean(gains[:period])
        avg_losses[period] = np.mean(losses[:period])
        
        # Calculate RSI for remaining values
        for i in range(period + 1, len(closes)):
            avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
            avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period
        
        # Calculate RSI
        rs = avg_gains / (avg_losses + 1e-10)  # Avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_price_score(self, closes: np.ndarray) -> float:
        """
        Calculate price momentum (ROC) score
        Price ROC (Rate of Change) normalized via sigmoid to 0-100
        """
        if len(closes) < 2:
            return 50.0
        
        # Calculate returns
        returns = (closes / np.roll(closes, 1))[1:] - 1.0
        
        # Normalize and convert to 0-100
        norm_returns = self.sigmoid_normalize(returns)
        
        return float(norm_returns[-1])
    
    def calculate_volume_score(self, volumes: np.ndarray) -> float:
        """
        Calculate volume score
        Volume normalized via sigmoid to 0-100
        """
        if len(volumes) < 2:
            return 50.0
        
        norm_volumes = self.sigmoid_normalize(volumes[-self.lookback:])
        return float(norm_volumes[-1])
    
    def calculate_volatility_score(self, closes: np.ndarray) -> float:
        """
        Calculate volatility score using log returns and standard deviation
        """
        if len(closes) < 2:
            return 50.0
        
        # Calculate log returns
        log_returns = np.log(closes / np.roll(closes, 1))[1:]
        
        # Standard deviation of log returns
        volatility = np.std(log_returns)
        
        # Normalize volatility array
        vol_array = np.full(len(log_returns), volatility)
        norm_vol = self.sigmoid_normalize(vol_array)
        
        return float(norm_vol[-1])
    
    def calculate_combined_score(
        self,
        closes: np.ndarray,
        volumes: np.ndarray,
        price_weight: float = 70.0,
        volume_weight: float = 10.0,
        rsi_weight: float = 10.0,
        volatility_weight: float = 10.0
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate weighted combined score (0-100)
        Returns (total_score, component_dict)
        """
        # Calculate individual components
        price_score = self.calculate_price_score(closes)
        volume_score = self.calculate_volume_score(volumes)
        rsi = self.calculate_rsi(closes, self.rsi_period)
        rsi_score = self.sigmoid_normalize(rsi[-self.lookback:])
        volatility_score = self.calculate_volatility_score(closes)
        
        # Normalize weights to sum to 100
        total_weight = price_weight + volume_weight + rsi_weight + volatility_weight
        if total_weight == 0:
            total_weight = 1.0
        
        # Calculate weighted average
        combined = (
            (price_weight * price_score +
             volume_weight * volume_score +
             rsi_weight * rsi_score[-1] +
             volatility_weight * volatility_score) / total_weight
        )
        
        components = {
            'price': float(price_score),
            'volume': float(volume_score),
            'rsi': float(rsi[-1]),
            'rsi_normalized': float(rsi_score[-1]),
            'volatility': float(volatility_score),
            'combined': float(combined)
        }
        
        return float(combined), components


def get_multi_timeframe_scores(
    ohlcv_dict: Dict[str, pd.DataFrame],
    weights: Dict[str, float]
) -> Dict[str, Tuple[float, Dict]]:
    """
    Calculate scores for multiple timeframes
    ohlcv_dict: {timeframe: DataFrame with 'close', 'volume'}
    Returns: {timeframe: (score, components)}
    """
    indicator = TechnicalIndicators()
    results = {}
    
    for timeframe, df in ohlcv_dict.items():
        if len(df) < 2:
            results[timeframe] = (50.0, {})
            continue
        
        closes = df['close'].values
        volumes = df['volume'].values
        
        score, components = indicator.calculate_combined_score(
            closes, volumes,
            price_weight=weights.get('price', 70.0),
            volume_weight=weights.get('volume', 10.0),
            rsi_weight=weights.get('rsi', 10.0),
            volatility_weight=weights.get('volatility', 10.0)
        )
        
        results[timeframe] = (score, components)
    
    return results

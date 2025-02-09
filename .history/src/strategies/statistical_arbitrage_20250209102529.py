# src/strategies/statistical_arbitrage.py

import numpy as np
import pandas as pd
from typing import Tuple, List
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.stattools import adfuller
from .base_strategy import BaseStrategy

class StatisticalArbitrageStrategy(BaseStrategy):
    def __init__(self,
                 lookback_period: int = 60,
                 entry_zscore: float = 2.0,
                 exit_zscore: float = 0.0,
                 max_position_hold: int = 20):
        self.lookback_period = lookback_period
        self.entry_zscore = entry_zscore
        self.exit_zscore = exit_zscore
        self.max_position_hold = max_position_hold
        
    def calculate_zscore(self, spread: pd.Series) -> pd.Series:
        """Calculate z-score of the spread."""
        mean = spread.rolling(window=self.lookback_period).mean()
        std = spread.rolling(window=self.lookback_period).std()
        return (spread - mean) / std
        
    def check_cointegration(self, series1: pd.Series, series2: pd.Series) -> bool:
        """Test for cointegration using Augmented Dickey-Fuller test."""
        spread = series1 - series2
        adf_result = adfuller(spread.dropna())
        return adf_result[1] < 0.05  # Return True if p-value < 0.05
        
    def calculate_hedge_ratio(self, series1: pd.Series, series2: pd.Series) -> float:
        """Calculate optimal hedge ratio using linear regression."""
        model = LinearRegression()
        X = series2.values.reshape(-1, 1)
        y = series1.values.reshape(-1, 1)
        model.fit(X, y)
        return model.coef_[0][0]
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trading signals based on statistical arbitrage."""
        if len(data) < self.lookback_period:
            return pd.Series(0, index=data.index)
            
        price1 = data['close']
        try:
            price2 = data['benchmark_close']
        except KeyError:
            return pd.Series(0, index=data.index)
            
        if not self.check_cointegration(price1, price2):
            return pd.Series(0, index=data.index)
            
        hedge_ratio = self.calculate_hedge_ratio(price1, price2)
        spread = price1 - hedge_ratio * price2
        zscore = self.calculate_zscore(spread)
        
        signals = pd.Series(0, index=data.index)
        signals[zscore > self.entry_zscore] = -1
        signals[zscore < -self.entry_zscore] = 1
        signals[(zscore > -self.exit_zscore) & (zscore < self.exit_zscore)] = 0
                
        return signals
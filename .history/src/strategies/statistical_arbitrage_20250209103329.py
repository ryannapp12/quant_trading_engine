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
                 exit_zscore: float = 0.5,  # Changed from 0.0 for more conservative exits
                 max_position_hold: int = 20,
                 min_half_life: int = 5,  # Added half-life check
                 confidence_level: float = 0.05):  # Added confidence level for cointegration
        self.lookback_period = lookback_period
        self.entry_zscore = entry_zscore
        self.exit_zscore = exit_zscore
        self.max_position_hold = max_position_hold
        self.min_half_life = min_half_life
        self.confidence_level = confidence_level
        
    def calculate_half_life(self, spread: pd.Series) -> float:
        """Calculate the half-life of mean reversion."""
        spread_lag = spread.shift(1)
        spread_diff = spread - spread_lag
        spread_lag = spread_lag[~spread_lag.isna()]
        spread_diff = spread_diff[~spread_diff.isna()]
        
        model = LinearRegression()
        model.fit(spread_lag.values.reshape(-1, 1), spread_diff.values.reshape(-1, 1))
        
        half_life = -np.log(2) / model.coef_[0][0] if model.coef_[0][0] < 0 else np.inf
        return half_life
        
    def calculate_zscore(self, spread: pd.Series) -> pd.Series:
        """Calculate z-score of the spread with additional validations."""
        mean = spread.rolling(window=self.lookback_period, min_periods=self.lookback_period//2).mean()
        std = spread.rolling(window=self.lookback_period, min_periods=self.lookback_period//2).std()
        
        # Avoid division by zero
        std = std.replace(0, np.nan)
        zscore = (spread - mean) / std
        
        return zscore.fillna(0)
        
    def check_cointegration(self, series1: pd.Series, series2: pd.Series) -> bool:
        """Test for cointegration with improved robustness."""
        if len(series1) != len(series2):
            return False
            
        # Remove any missing values
        valid_data = pd.concat([series1, series2], axis=1).dropna()
        if len(valid_data) < self.lookback_period:
            return False
            
        # Calculate spread
        model = LinearRegression()
        X = valid_data.iloc[:, 1].values.reshape(-1, 1)
        y = valid_data.iloc[:, 0].values.reshape(-1, 1)
        model.fit(X, y)
        spread = y.flatten() - model.coef_[0][0] * X.flatten() - model.intercept_[0]
        
        # Perform ADF test
        try:
            adf_result = adfuller(spread, maxlag=int(np.power(len(spread) - 1, 1/3)))
            return adf_result[1] < self.confidence_level
        except:
            return False
            
    def calculate_hedge_ratio(self, series1: pd.Series, series2: pd.Series) -> Tuple[float, float]:
        """Calculate optimal hedge ratio using rolling regression."""
        # Use rolling regression to calculate dynamic hedge ratio
        window = min(self.lookback_period, len(series1) - 1)
        hedge_ratios = []
        
        for i in range(window, len(series1)):
            X = series2.iloc[i-window:i].values.reshape(-1, 1)
            y = series1.iloc[i-window:i].values.reshape(-1, 1)
            model = LinearRegression()
            model.fit(X, y)
            hedge_ratios.append(model.coef_[0][0])
            
        # Use the median hedge ratio for stability
        return np.median(hedge_ratios), model.intercept_[0]
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trading signals based on statistical arbitrage."""
        if len(data) < self.lookback_period:
            return pd.Series(0, index=data.index)
            
        price1 = data['close']
        try:
            price2 = data['benchmark_close']
        except KeyError:
            return pd.Series(0, index=data.index)
            
        # Check for cointegration
        if not self.check_cointegration(price1, price2):
            return pd.Series(0, index=data.index)
            
        # Calculate hedge ratio and spread
        hedge_ratio, intercept = self.calculate_hedge_ratio(price1, price2)
        spread = price1 - hedge_ratio * price2 - intercept
        
        # Calculate half-life
        half_life = self.calculate_half_life(spread)
        if half_life < self.min_half_life or half_life == np.inf:
            return pd.Series(0, index=data.index)
            
        # Calculate z-score
        zscore = self.calculate_zscore(spread)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Entry signals
        signals[zscore > self.entry_zscore] = -1  # Short when spread is too high
        signals[zscore < -self.entry_zscore] = 1  # Long when spread is too low
        
        # Exit signals
        signals[(zscore > -self.exit_zscore) & (zscore < self.exit_zscore)] = 0
        
        # Add position holding limit
        entry_points = signals.shift(1).fillna(0) != signals
        last_entry = None
        for i in range(len(signals)):
            if entry_points.iloc[i]:
                last_entry = i
            elif last_entry is not None and i - last_entry >= self.max_position_hold:
                signals.iloc[i] = 0
                
        return signals
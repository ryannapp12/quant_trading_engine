# src/strategies/statistical_arbitrage.py

import numpy as np
import pandas as pd
from typing import Tuple
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.stattools import adfuller
from .base_strategy import BaseStrategy

class StatisticalArbitrageStrategy(BaseStrategy):
    def __init__(self,
                 lookback_period: int = 60,
                 entry_zscore: float = 2.0,
                 exit_zscore: float = 0.5,  # More conservative exits
                 max_position_hold: int = 20,
                 min_half_life: int = 5,     # Added half-life check
                 confidence_level: float = 0.05):  # Confidence level for cointegration
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
        spread_lag = spread_lag.dropna()
        spread_diff = spread_diff.dropna()
        
        model = LinearRegression()
        model.fit(spread_lag.values.reshape(-1, 1), spread_diff.values.reshape(-1, 1))
        
        coef = model.coef_[0][0]
        half_life = -np.log(2) / coef if coef < 0 else np.inf
        return half_life
        
    def calculate_zscore(self, spread: pd.Series) -> pd.Series:
        """Calculate z-score of the spread with rolling window."""
        mean = spread.rolling(window=self.lookback_period, min_periods=self.lookback_period // 2).mean()
        std = spread.rolling(window=self.lookback_period, min_periods=self.lookback_period // 2).std()
        std = std.replace(0, np.nan)  # Avoid division by zero
        zscore = (spread - mean) / std
        return zscore.fillna(0)
        
    def check_cointegration(self, series1: pd.Series, series2: pd.Series) -> bool:
        """Test for cointegration using the ADF test."""
        if len(series1) != len(series2):
            return False
            
        valid_data = pd.concat([series1, series2], axis=1).dropna()
        if len(valid_data) < self.lookback_period:
            return False
            
        model = LinearRegression()
        X = valid_data.iloc[:, 1].values.reshape(-1, 1)
        y = valid_data.iloc[:, 0].values.reshape(-1, 1)
        model.fit(X, y)
        spread = y.flatten() - model.coef_[0][0] * X.flatten() - model.intercept_[0]
        
        try:
            adf_result = adfuller(spread, maxlag=int(np.power(len(spread) - 1, 1/3)))
            p_value = adf_result[1]
            # Debug print: check p-value from the cointegration test
            print("ADF p-value:", p_value)
            return p_value < self.confidence_level
        except Exception as e:
            print("ADF test exception:", e)
            return False
            
    def calculate_hedge_ratio(self, series1: pd.Series, series2: pd.Series) -> Tuple[float, float]:
        """Calculate the optimal hedge ratio using rolling regression."""
        window = min(self.lookback_period, len(series1) - 1)
        hedge_ratios = []
        
        for i in range(window, len(series1)):
            X = series2.iloc[i-window:i].values.reshape(-1, 1)
            y = series1.iloc[i-window:i].values.reshape(-1, 1)
            model = LinearRegression()
            model.fit(X, y)
            hedge_ratios.append(model.coef_[0][0])
            
        # Use median hedge ratio for stability
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
            
        # Check for cointegration and log the result for debugging
        cointegration_result = self.check_cointegration(price1, price2)
        print("Cointegration Test Passed:", cointegration_result)
        if not cointegration_result:
            return pd.Series(0, index=data.index)
            
        hedge_ratio, intercept = self.calculate_hedge_ratio(price1, price2)
        spread = price1 - hedge_ratio * price2 - intercept
        
        # Calculate half-life and log the value
        half_life = self.calculate_half_life(spread)
        print("Calculated Half-life:", half_life)
        if half_life < self.min_half_life or half_life == np.inf:
            return pd.Series(0, index=data.index)
            
        # Calculate z-score of the spread
        zscore = self.calculate_zscore(spread)
        
        signals = pd.Series(0, index=data.index)
        signals[zscore > self.entry_zscore] = -1  # Short when spread is too high
        signals[zscore < -self.entry_zscore] = 1  # Long when spread is too low
        
        # Exit signals
        signals[(zscore > -self.exit_zscore) & (zscore < self.exit_zscore)] = 0
        
        # Enforce maximum holding period
        entry_points = signals.shift(1).fillna(0) != signals
        last_entry = None
        for i in range(len(signals)):
            if entry_points.iloc[i]:
                last_entry = i
            elif last_entry is not None and i - last_entry >= self.max_position_hold:
                signals.iloc[i] = 0
                
        return signals
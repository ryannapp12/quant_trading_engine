# src/strategies/mean_reversion_strategy.py

import pandas as pd
from .base_strategy import BaseStrategy

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, window: int = 20, threshold: float = 0.05):
        self.window = window
        self.threshold = threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        # Use the lower-case 'close' column
        price = data['close']
        rolling_mean = price.rolling(window=self.window).mean()
        # Signal: +1 when price is significantly below mean (buy), -1 when above (sell)
        buy_signal = (price < rolling_mean * (1 - self.threshold)).astype(int)
        sell_signal = (price > rolling_mean * (1 + self.threshold)).astype(int)
        # Combine signals: buy=+1, sell=-1, otherwise 0.
        signals = buy_signal - sell_signal
        return signals
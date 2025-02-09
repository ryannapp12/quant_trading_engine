# src/strategies/momentum_strategy.py

import pandas as pd
from .base_strategy import BaseStrategy

class MomentumStrategy(BaseStrategy):
    def __init__(self, window: int = 20):
        self.window = window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        data['rolling_mean'] = data['Close'].rolling(window=self.window).mean()
        signals = data['Close'] > data['rolling_mean']
        return signals.astype(int).replace(0, -1)
# src/strategies/momentum_strategy.py

import pandas as pd
from .base_strategy import BaseStrategy

class MomentumStrategy(BaseStrategy):
    def __init__(self, window: int = 20):
        self.window = window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        # Use the lower-case 'close' column (as ensured by the data provider)
        close_col = 'close'
        data['rolling_mean'] = data[close_col].rolling(window=self.window).mean()
        signals = data[close_col] > data['rolling_mean']
        return signals.astype(int).replace(0, -1)
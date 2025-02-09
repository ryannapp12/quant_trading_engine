# src/core/backtesting_engine.py

import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from src.strategies.base_strategy import BaseStrategy

class BacktestingEngine:
    def __init__(self, strategies: List[BaseStrategy], initial_capital: float = 100000.0):
        self.strategies = strategies
        self.initial_capital = initial_capital

    def _backtest_strategy(self, strategy: BaseStrategy, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['Signal'] = strategy.generate_signals(df)
        df['Returns'] = df['Close'].pct_change()
        df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
        df['Cumulative_Strategy'] = (1 + df['Strategy_Returns']).cumprod() * self.initial_capital
        df['Cumulative_Market'] = (1 + df['Returns']).cumprod() * self.initial_capital
        return df

    def run_all(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        results = {}
        with ThreadPoolExecutor() as executor:
            future_to_strategy = {
                executor.submit(self._backtest_strategy, strat, data): strat
                for strat in self.strategies
            }
            for future in as_completed(future_to_strategy):
                strat = future_to_strategy[future]
                results[str(type(strat).__name__)] = future.result()
        return results
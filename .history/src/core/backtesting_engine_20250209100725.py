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
        # Generate signals using the strategy (which already handles column names)
        df['signal'] = strategy.generate_signals(df)
        # Calculate daily returns using the 'close' column
        df['returns'] = df['close'].pct_change()
        # Compute strategy returns; shift the signal to avoid lookahead bias
        df['strategy_returns'] = df['signal'].shift(1) * df['returns']
        # Compute cumulative returns for the strategy and the market
        df['cumulative_strategy'] = (1 + df['strategy_returns']).cumprod() * self.initial_capital
        df['cumulative_market'] = (1 + df['returns']).cumprod() * self.initial_capital
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
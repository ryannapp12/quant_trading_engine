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
        # Generate signals using the strategy (which already handles the column name case)
        df['Signal'] = strategy.generate_signals(df)
        # Use the lower-case 'close' column (as data provider normalizes the columns)
        df['Returns'] = df['close'].pct_change()
        # Calculate strategy returns based on the signal
        df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
        # Compute cumulative returns for the strategy and market
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
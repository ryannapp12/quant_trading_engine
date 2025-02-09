# src/core/risk_engine.py

import numpy as np
import pandas as pd

class RiskEngine:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def sharpe_ratio(self) -> float:
        returns = self.data['Strategy_Returns'].dropna()
        return np.mean(returns) / np.std(returns) * np.sqrt(252) if returns.std() != 0 else 0.0

    def sortino_ratio(self, risk_free_rate: float = 0.0) -> float:
        returns = self.data['Strategy_Returns'].dropna()
        neg_returns = returns[returns < 0]
        downside_std = neg_returns.std()
        expected_return = np.mean(returns) - risk_free_rate / 252
        return expected_return / downside_std * np.sqrt(252) if downside_std != 0 else 0.0

    def max_drawdown(self) -> float:
        cumulative = self.data['Cumulative_Strategy']
        drawdown = (cumulative - cumulative.cummax()) / cumulative.cummax()
        return drawdown.min()

    def value_at_risk(self, confidence_level: float = 0.95) -> float:
        returns = self.data['Strategy_Returns'].dropna()
        return np.percentile(returns, (1 - confidence_level) * 100)
# src/core/risk_engine.py

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict
import warnings

class RiskEngine:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def calculate_tail_risk_metrics(self, confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Calculate tail risk metrics (VaR, CVaR, EVT VaR) with robust handling of edge cases.
        If strategy returns are constant (or nearly so), the metrics will naturally be near zero.
        """
        returns = self.data['strategy_returns'].dropna()

        # Not enough data points to compute risk metrics
        if len(returns) < 2:
            return {
                'historical_var': 0.0,
                'parametric_var': 0.0,
                'conditional_var': 0.0,
                'evt_var': 0.0
            }

        # Historical VaR based on empirical distribution
        hist_var = np.percentile(returns, (1 - confidence_level) * 100)

        # Calculate parametric VaR only if standard deviation is not near zero
        std = returns.std()
        if np.isclose(std, 0):
            param_var = hist_var
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                param_var = stats.norm.ppf(1 - confidence_level, loc=returns.mean(), scale=std)
                if np.isnan(param_var):
                    param_var = hist_var

        # Calculate Conditional VaR (Expected Shortfall)
        cvar_returns = returns[returns <= hist_var]
        cvar = cvar_returns.mean() if len(cvar_returns) > 0 else hist_var

        # Calculate EVT VaR if there are enough negative return observations
        negative_returns = -returns[returns < 0]
        if len(negative_returns) > 10:
            try:
                evt_params = stats.genpareto.fit(negative_returns)
                evt_var = -stats.genpareto.ppf(1 - confidence_level, *evt_params)
            except Exception:
                evt_var = hist_var
        else:
            evt_var = hist_var

        return {
            'historical_var': hist_var,
            'parametric_var': param_var,
            'conditional_var': cvar,
            'evt_var': evt_var
        }

    def calculate_factor_exposures(self, factor_returns: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate the strategy's exposure to given factors using a linear regression model.
        Returns the factor betas (including an intercept labeled as 'alpha') and R-squared.
        """
        strategy_returns = self.data['strategy_returns'].dropna()

        if len(strategy_returns) < 2 or factor_returns is None:
            return {'factor_betas': {}, 'r_squared': 0.0}

        # Align indices between strategy and factor returns
        common_idx = strategy_returns.index.intersection(factor_returns.index)
        if len(common_idx) < 2:
            return {'factor_betas': {}, 'r_squared': 0.0}

        y = strategy_returns.loc[common_idx]
        X = factor_returns.loc[common_idx]

        # Add an intercept term
        X = pd.concat([pd.Series(1, index=X.index, name='intercept'), X], axis=1)

        try:
            betas = np.linalg.pinv(X.T @ X) @ X.T @ y
            y_pred = X @ betas
            r_squared = max(0, 1 - np.sum((y - y_pred) ** 2) / np.sum((y - y.mean()) ** 2))
        except Exception:
            return {'factor_betas': {}, 'r_squared': 0.0}

        return {
            'factor_betas': dict(zip(['alpha'] + factor_returns.columns.tolist(), betas)),
            'r_squared': r_squared
        }

    def calculate_drawdown_metrics(self) -> Dict[str, float]:
        """
        Calculate drawdown metrics including maximum drawdown, average drawdown, average recovery time,
        and drawdown frequency.
        """
        equity_curve = self.data['cumulative_strategy']

        if len(equity_curve) < 2:
            return {
                'max_drawdown': 0.0,
                'average_drawdown': 0.0,
                'average_recovery_time': 0.0,
                'drawdown_frequency': 0.0
            }

        # Compute running maximum using cummax for robustness
        running_max = equity_curve.cummax()
        drawdowns = (equity_curve - running_max) / running_max

        max_drawdown = drawdowns.min()
        avg_drawdown = drawdowns[drawdowns < 0].mean() if (drawdowns < 0).any() else 0.0

        # Determine drawdown recovery times by detecting changes in drawdown state
        is_drawdown = drawdowns < 0
        drawdown_periods = is_drawdown.astype(int).diff()
        recovery_times = []
        current_drawdown_start = None

        for date, change in drawdown_periods.items():
            if change == 1:  # Start of a drawdown period
                current_drawdown_start = date
            elif change == -1 and current_drawdown_start is not None:  # End of a drawdown period
                recovery_times.append((date - current_drawdown_start).days)
                current_drawdown_start = None

        avg_recovery_time = np.mean(recovery_times) if recovery_times else 0.0
        drawdown_frequency = len(recovery_times) / len(equity_curve) if len(equity_curve) > 0 else 0.0

        return {
            'max_drawdown': max_drawdown,
            'average_drawdown': avg_drawdown,
            'average_recovery_time': avg_recovery_time,
            'drawdown_frequency': drawdown_frequency
        }
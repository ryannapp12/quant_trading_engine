# src/core/risk_engine.py

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Optional
import warnings

class RiskEngine:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        
    def calculate_tail_risk_metrics(self, confidence_level: float = 0.95) -> Dict[str, float]:
        """Calculate comprehensive tail risk metrics with better handling of edge cases."""
        returns = self.data['strategy_returns'].dropna()
        
        if len(returns) < 2:  # Not enough data
            return {
                'historical_var': 0.0,
                'parametric_var': 0.0,
                'conditional_var': 0.0,
                'evt_var': 0.0
            }
            
        # Calculate VaR using both historical and parametric methods
        hist_var = np.percentile(returns, (1 - confidence_level) * 100)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                param_var = stats.norm.ppf(1 - confidence_level, returns.mean(), returns.std())
            except:
                param_var = hist_var
                
        # Calculate CVaR (Expected Shortfall)
        cvar_returns = returns[returns <= hist_var]
        cvar = cvar_returns.mean() if len(cvar_returns) > 0 else hist_var
        
        # Calculate Extreme Value Theory VaR
        negative_returns = -returns[returns < 0]
        if len(negative_returns) > 10:  # Need enough data points for EVT
            try:
                evt_params = stats.genpareto.fit(negative_returns)
                evt_var = -stats.genpareto.ppf(1 - confidence_level, *evt_params)
            except:
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
        """Calculate strategy exposure to various factors with robust error handling."""
        strategy_returns = self.data['strategy_returns'].dropna()
        
        if len(strategy_returns) < 2 or factor_returns is None:
            return {'factor_betas': {}, 'r_squared': 0.0}
            
        common_idx = strategy_returns.index.intersection(factor_returns.index)
        if len(common_idx) < 2:
            return {'factor_betas': {}, 'r_squared': 0.0}
            
        y = strategy_returns.loc[common_idx]
        X = factor_returns.loc[common_idx]
        
        X = pd.concat([pd.Series(1, index=X.index), X], axis=1)
        
        try:
            betas = np.linalg.pinv(X.T @ X) @ X.T @ y
            y_pred = X @ betas
            r_squared = max(0, 1 - np.sum((y - y_pred)**2) / np.sum((y - y.mean())**2))
        except:
            return {'factor_betas': {}, 'r_squared': 0.0}
            
        return {
            'factor_betas': dict(zip(['alpha'] + factor_returns.columns.tolist(),
                                   betas)),
            'r_squared': r_squared
        }
        
    def calculate_drawdown_metrics(self) -> Dict[str, float]:
        """Calculate comprehensive drawdown metrics with better handling of edge cases."""
        equity_curve = self.data['cumulative_strategy']
        
        if len(equity_curve) < 2:
            return {
                'max_drawdown': 0.0,
                'average_drawdown': 0.0,
                'average_recovery_time': 0.0,
                'drawdown_frequency': 0.0
            }
            
        running_max = equity_curve.expanding().max()
        drawdowns = (equity_curve - running_max) / running_max
        
        max_drawdown = drawdowns.min()
        avg_drawdown = drawdowns[drawdowns < 0].mean() if len(drawdowns[drawdowns < 0]) > 0 else 0.0
        
        is_drawdown = drawdowns < 0
        drawdown_periods = is_drawdown.astype(int).diff()
        
        recovery_times = []
        current_drawdown_start = None
        
        for date, value in drawdown_periods.items():
            if value == 1:  # Start of drawdown
                current_drawdown_start = date
            elif value == -1 and current_drawdown_start:  # End of drawdown
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
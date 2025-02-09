# src/core/risk_engine.py

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Optional

class RiskEngine:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        
    def calculate_tail_risk_metrics(self, 
                                  confidence_level: float = 0.95) -> Dict[str, float]:
        """Calculate comprehensive tail risk metrics."""
        returns = self.data['strategy_returns'].dropna()
        
        # Calculate VaR using both historical and parametric methods
        hist_var = np.percentile(returns, (1 - confidence_level) * 100)
        param_var = stats.norm.ppf(1 - confidence_level, 
                                 returns.mean(),
                                 returns.std())
        
        # Calculate CVaR (Expected Shortfall)
        cvar = returns[returns <= hist_var].mean()
        
        # Calculate Extreme Value Theory VaR
        negative_returns = -returns[returns < 0]
        if len(negative_returns) > 0:
            evt_params = stats.genpareto.fit(negative_returns)
            evt_var = -stats.genpareto.ppf(1 - confidence_level, *evt_params)
        else:
            evt_var = np.nan
            
        return {
            'historical_var': hist_var,
            'parametric_var': param_var,
            'conditional_var': cvar,
            'evt_var': evt_var
        }
        
    def calculate_factor_exposures(self, 
                                 factor_returns: pd.DataFrame) -> Dict[str, float]:
        """Calculate strategy exposure to various factors."""
        strategy_returns = self.data['strategy_returns'].dropna()
        
        # Prepare data for regression
        common_idx = strategy_returns.index.intersection(factor_returns.index)
        y = strategy_returns.loc[common_idx]
        X = factor_returns.loc[common_idx]
        
        # Add constant for regression
        X = pd.concat([pd.Series(1, index=X.index), X], axis=1)
        
        # Calculate factor betas using OLS regression
        betas = np.linalg.pinv(X.T @ X) @ X.T @ y
        
        # Calculate R-squared
        y_pred = X @ betas
        r_squared = 1 - np.sum((y - y_pred)**2) / np.sum((y - y.mean())**2)
        
        return {
            'factor_betas': dict(zip(['alpha'] + factor_returns.columns.tolist(), 
                                   betas)),
            'r_squared': r_squared
        }
        
    def calculate_drawdown_metrics(self) -> Dict[str, float]:
        """Calculate comprehensive drawdown metrics."""
        equity_curve = self.data['cumulative_strategy']
        running_max = equity_curve.expanding().max()
        drawdowns = (equity_curve - running_max) / running_max
        
        # Calculate various drawdown metrics
        max_drawdown = drawdowns.min()
        
        # Calculate average drawdown
        avg_drawdown = drawdowns[drawdowns < 0].mean()
        
        # Calculate drawdown duration statistics
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
                
        avg_recovery_time = np.mean(recovery_times) if recovery_times else np.nan
        
        return {
            'max_drawdown': max_drawdown,
            'average_drawdown': avg_drawdown,
            'average_recovery_time': avg_recovery_time,
            'drawdown_frequency': len(recovery_times) / len(equity_curve)
        }
# src/core/portfolio_optimizer.py

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import List, Dict, Tuple

class PortfolioOptimizer:
    def __init__(self, 
                 returns: pd.DataFrame,
                 risk_free_rate: float = 0.02,
                 constraints: Dict = None):
        self.returns = returns
        self.risk_free_rate = risk_free_rate
        self.constraints = constraints or {}
        
    def calculate_portfolio_metrics(self, 
                                  weights: np.ndarray) -> Tuple[float, float, float]:
        """Calculate portfolio return, volatility, and Sharpe ratio."""
        portfolio_return = np.sum(self.returns.mean() * weights) * 252
        portfolio_vol = np.sqrt(
            np.dot(weights.T, np.dot(self.returns.cov() * 252, weights))
        )
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
        return portfolio_return, portfolio_vol, sharpe_ratio
        
    def optimize_sharpe(self) -> Dict:
        """Optimize portfolio weights for maximum Sharpe ratio."""
        num_assets = len(self.returns.columns)
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # weights sum to 1
        ]
        
        # Add custom constraints if provided
        if 'max_weight' in self.constraints:
            constraints.append({
                'type': 'ineq',
                'fun': lambda x: self.constraints['max_weight'] - x
            })
            
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        def objective(weights):
            return -self.calculate_portfolio_metrics(weights)[2]  # Negative Sharpe
            
        result = minimize(
            objective,
            num_assets * [1./num_assets],  # Equal weight initial guess
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = pd.Series(
            result.x,
            index=self.returns.columns
        )
        
        metrics = self.calculate_portfolio_metrics(result.x)
        return {
            'weights': optimal_weights,
            'metrics': {
                'return': metrics[0],
                'volatility': metrics[1],
                'sharpe_ratio': metrics[2]
            }
        }
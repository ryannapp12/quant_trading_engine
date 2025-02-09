# src/core/models.py

from dataclasses import dataclass

@dataclass
class Trade:
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    profit: float

@dataclass
class RiskMetrics:
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    value_at_risk: float
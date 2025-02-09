# main.py
from src.core.data_provider import YahooDataProvider
from src.core.csv_data_provider import CSVDataProvider
from src.strategies.momentum_strategy import MomentumStrategy
from src.strategies.mean_reversion_strategy import MeanReversionStrategy
from src.strategies.statistical_arbitrage import StatisticalArbitrageStrategy
from src.core.backtesting_engine import BacktestingEngine
from src.core.risk_engine import RiskEngine
from src.utils.logger import setup_logger
from config.settings import *
import matplotlib.pyplot as plt
from typing import Dict, Optional
import pandas as pd

logger = setup_logger(__name__)

def analyze_strategy_results(results_dict: Dict[str, pd.DataFrame],
                           factor_returns: Optional[pd.DataFrame] = None):
    """Analyze strategy results with enhanced metrics."""
    for strategy_name, results in results_dict.items():
        risk = RiskEngine(results)
        
        # Calculate enhanced risk metrics
        tail_metrics = risk.calculate_tail_risk_metrics()
        drawdown_metrics = risk.calculate_drawdown_metrics()
        
        # Calculate factor exposures if factor returns are provided
        if factor_returns is not None:
            factor_metrics = risk.calculate_factor_exposures(factor_returns)
            
        # Log enhanced metrics
        logger.info(f"\n{strategy_name} Analysis:")
        logger.info("Tail Risk Metrics:")
        for metric, value in tail_metrics.items():
            logger.info(f"- {metric}: {value:.2%}")
            
        logger.info("\nDrawdown Analysis:")
        for metric, value in drawdown_metrics.items():
            if 'time' in metric:
                logger.info(f"- {metric}: {value:.1f} days")
            else:
                logger.info(f"- {metric}: {value:.2%}")
                
        if factor_returns is not None:
            logger.info("\nFactor Analysis:")
            logger.info(f"- R-squared: {factor_metrics['r_squared']:.2%}")
            logger.info("Factor Betas:")
            for factor, beta in factor_metrics['factor_betas'].items():
                logger.info(f"- {factor}: {beta:.3f}")

def main():
    # Data provider setup
    provider = CSVDataProvider(CSV_FILE_PATH) if DATA_PROVIDER.lower() == 'csv' else \
              YahooDataProvider(DEFAULT_TICKER, DEFAULT_START_DATE, DEFAULT_END_DATE, db_path=DB_PATH)

    # Load primary asset data
    data = provider.load_data()
    logger.info(f"Data loaded for {DEFAULT_TICKER}")
    
    # Load benchmark data for statistical arbitrage (using S&P 500 as benchmark)
    benchmark_provider = YahooDataProvider("SPY", DEFAULT_START_DATE, DEFAULT_END_DATE, db_path=DB_PATH)
    benchmark_data = benchmark_provider.load_data()
    
    # Merge benchmark data
    data['benchmark_close'] = benchmark_data['close']

    # Initialize strategies
    momentum_strategy = MomentumStrategy(window=STRATEGY_CONFIG['momentum']['window'])
    mean_reversion_strategy = MeanReversionStrategy(
        window=STRATEGY_CONFIG['mean_reversion']['window'],
        threshold=STRATEGY_CONFIG['mean_reversion']['threshold']
    )
    stat_arb_strategy = StatisticalArbitrageStrategy(
        lookback_period=60,
        entry_zscore=2.0,
        exit_zscore=0.0
    )
    
    strategies = [momentum_strategy, mean_reversion_strategy, stat_arb_strategy]
    engine = BacktestingEngine(strategies=strategies, initial_capital=INITIAL_CAPITAL)

    # Run backtests
    results_dict = engine.run_all(data)
    logger.info("Backtesting completed.")

    # Analyze results
    analyze_strategy_results(results_dict)

if __name__ == "__main__":
    main()
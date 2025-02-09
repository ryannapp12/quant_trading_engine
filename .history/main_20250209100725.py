# main.py

from src.core.data_provider import YahooDataProvider
from src.core.csv_data_provider import CSVDataProvider
from src.strategies.momentum_strategy import MomentumStrategy
from src.strategies.mean_reversion_strategy import MeanReversionStrategy
from src.core.backtesting_engine import BacktestingEngine
from src.core.risk_engine import RiskEngine
from src.utils.logger import setup_logger
from config.settings import (
    DEFAULT_TICKER, DEFAULT_START_DATE, DEFAULT_END_DATE,
    INITIAL_CAPITAL, DB_PATH, DATA_PROVIDER, CSV_FILE_PATH, STRATEGY_CONFIG
)
import matplotlib.pyplot as plt

logger = setup_logger(__name__)

def main():
    # Choose the data provider based on configuration.
    if DATA_PROVIDER.lower() == 'csv':
        provider = CSVDataProvider(CSV_FILE_PATH)
    else:
        provider = YahooDataProvider(DEFAULT_TICKER, DEFAULT_START_DATE, DEFAULT_END_DATE, db_path=DB_PATH)

    data = provider.load_data()
    logger.info(f"Data loaded for {DEFAULT_TICKER}")

    # Initialize strategies.
    # For demonstration, we use both Momentum and Mean Reversion strategies.
    momentum_strategy = MomentumStrategy(window=STRATEGY_CONFIG['momentum']['window'])
    mean_reversion_strategy = MeanReversionStrategy(
        window=STRATEGY_CONFIG['mean_reversion']['window'],
        threshold=STRATEGY_CONFIG['mean_reversion']['threshold']
    )
    strategies = [momentum_strategy, mean_reversion_strategy]
    engine = BacktestingEngine(strategies=strategies, initial_capital=INITIAL_CAPITAL)

    # Run concurrent backtests for all strategies.
    results_dict = engine.run_all(data)
    logger.info("Backtesting completed.")

    # Analyze risk metrics and plot results for each strategy.
    for strategy_name, results in results_dict.items():
        risk = RiskEngine(results)
        logger.info(f"{strategy_name} - Sharpe Ratio: {risk.sharpe_ratio():.2f}")
        logger.info(f"{strategy_name} - Sortino Ratio: {risk.sortino_ratio():.2f}")
        logger.info(f"{strategy_name} - Max Drawdown: {risk.max_drawdown():.2%}")
        logger.info(f"{strategy_name} - VaR (95%): {risk.value_at_risk():.2%}")
        logger.info(f"{strategy_name} - CVaR (95%): {risk.cvar():.2%}")

        plt.figure(figsize=(12, 7))
        plt.plot(results.index, results['cumulative_strategy'], label='Strategy Equity')
        plt.plot(results.index, results['cumulative_market'], label='Market Equity', alpha=0.7)
        plt.title(f'Backtest Equity Curve - {strategy_name}')
        plt.xlabel('Date')
        plt.ylabel('Equity ($)')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    main()
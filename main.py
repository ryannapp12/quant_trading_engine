# main.py

from src.core.data_provider import YahooDataProvider
from src.strategies.momentum_strategy import MomentumStrategy
from src.core.backtesting_engine import BacktestingEngine
from src.core.risk_engine import RiskEngine
from src.utils.logger import setup_logger
from config.settings import DEFAULT_TICKER, DEFAULT_START_DATE, DEFAULT_END_DATE, INITIAL_CAPITAL, DB_PATH
import matplotlib.pyplot as plt

logger = setup_logger(__name__)

def main():
    # Configuration from settings
    ticker = DEFAULT_TICKER
    start_date = DEFAULT_START_DATE
    end_date = DEFAULT_END_DATE

    # Data loading with caching via YahooDataProvider
    provider = YahooDataProvider(ticker, start_date, end_date, db_path=DB_PATH)
    data = provider.load_data()
    logger.info(f"Data loaded for {ticker}")

    # Initialize the strategy (Momentum Strategy in this example)
    strategy = MomentumStrategy(window=20)
    engine = BacktestingEngine(strategies=[strategy], initial_capital=INITIAL_CAPITAL)

    # Run concurrent backtests for all strategies
    results_dict = engine.run_all(data)
    logger.info("Backtesting completed.")

    # Analyze risk metrics and plot results for each strategy
    for strategy_name, results in results_dict.items():
        risk = RiskEngine(results)
        logger.info(f"{strategy_name} - Sharpe Ratio: {risk.sharpe_ratio():.2f}")
        logger.info(f"{strategy_name} - Sortino Ratio: {risk.sortino_ratio():.2f}")
        logger.info(f"{strategy_name} - Max Drawdown: {risk.max_drawdown():.2%}")
        logger.info(f"{strategy_name} - VaR (95%): {risk.value_at_risk():.2%}")

        plt.figure(figsize=(12, 7))
        plt.plot(results.index, results['Cumulative_Strategy'], label='Strategy Equity')
        plt.plot(results.index, results['Cumulative_Market'], label='Market Equity', alpha=0.7)
        plt.title(f'Backtest Equity Curve - {strategy_name}')
        plt.xlabel('Date')
        plt.ylabel('Equity ($)')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    main()
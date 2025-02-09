import argparse
from src.core.data_provider import YahooDataProvider
from src.core.csv_data_provider import CSVDataProvider
from src.strategies.momentum_strategy import MomentumStrategy
from src.strategies.mean_reversion_strategy import MeanReversionStrategy
from src.strategies.statistical_arbitrage import StatisticalArbitrageStrategy
from src.core.backtesting_engine import BacktestingEngine
from src.core.risk_engine import RiskEngine
from src.utils.logger import setup_logger
from config.settings import (
    DEFAULT_TICKER,
    DEFAULT_BENCHMARK_TICKER,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    INITIAL_CAPITAL,
    DB_PATH,
    DATA_PROVIDER,
    CSV_FILE_PATH,
    STRATEGY_CONFIG
)
import matplotlib.pyplot as plt
from typing import Dict, Optional
import pandas as pd

logger = setup_logger(__name__)

def plot_pair_analysis(price_data: pd.DataFrame, pair_name: str):
    """Plot pair trading analysis charts."""
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Price Series
    plt.subplot(2, 2, 1)
    normalized_close = price_data['close'] / price_data['close'].iloc[0]
    normalized_benchmark = price_data['benchmark_close'] / price_data['benchmark_close'].iloc[0]
    plt.plot(normalized_close.index, normalized_close, label=DEFAULT_TICKER)
    plt.plot(normalized_benchmark.index, normalized_benchmark, label=DEFAULT_BENCHMARK_TICKER)
    plt.title('Normalized Price Series')
    plt.legend()
    plt.grid(True)
    
    # Plot 2: Spread
    plt.subplot(2, 2, 2)
    spread = price_data['close'] - price_data['benchmark_close']
    plt.plot(spread.index, spread)
    plt.title('Price Spread')
    plt.grid(True)
    
    # Plot 3: Rolling Correlation
    plt.subplot(2, 2, 3)
    rolling_corr = price_data['close'].rolling(window=60).corr(price_data['benchmark_close'])
    plt.plot(rolling_corr.index, rolling_corr)
    plt.title('60-Day Rolling Correlation')
    plt.grid(True)
    
    # Plot 4: Returns Scatter
    plt.subplot(2, 2, 4)
    returns1 = price_data['close'].pct_change()
    returns2 = price_data['benchmark_close'].pct_change()
    plt.scatter(returns1, returns2, alpha=0.5)
    plt.xlabel(f'{DEFAULT_TICKER} Returns')
    plt.ylabel(f'{DEFAULT_BENCHMARK_TICKER} Returns')
    plt.title('Daily Returns Scatter')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def create_enhanced_statistical_arbitrage() -> StatisticalArbitrageStrategy:
    """Create a statistical arbitrage strategy using configuration from settings.py."""
    config = STRATEGY_CONFIG['statistical_arbitrage']
    return StatisticalArbitrageStrategy(
        lookback_period=config['lookback_period'],
        entry_zscore=config['entry_zscore'],
        exit_zscore=config['exit_zscore'],
        max_position_hold=config['max_position_hold'],
        min_half_life=config['min_half_life'],
        confidence_level=config['confidence_level']
    )

def analyze_strategy_results(results_dict: Dict[str, pd.DataFrame],
                             factor_returns: Optional[pd.DataFrame] = None):
    """Analyze strategy results with enhanced metrics."""
    for strategy_name, results in results_dict.items():
        from src.core.risk_engine import RiskEngine
        risk = RiskEngine(results)
        tail_metrics = risk.calculate_tail_risk_metrics()
        drawdown_metrics = risk.calculate_drawdown_metrics()
        
        if factor_returns is not None:
            factor_metrics = risk.calculate_factor_exposures(factor_returns)
            
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

def run_ml_model():
    from config.settings import ML_CONFIG
    from src.ml.regime_detector import RegimeDetector
    from src.core.csv_data_provider import CSVDataProvider
    from src.core.data_provider import YahooDataProvider
    ml_params = ML_CONFIG['regime_detector']
    regime_detector = RegimeDetector(
        lookback_window=ml_params['lookback_window'],
        hidden_units=ml_params['hidden_units'],
        epochs=ml_params['epochs'],
        batch_size=ml_params['batch_size']
    )
    provider = CSVDataProvider(CSV_FILE_PATH) if DATA_PROVIDER.lower() == 'csv' else \
               YahooDataProvider(DEFAULT_TICKER, DEFAULT_START_DATE, DEFAULT_END_DATE, db_path=DB_PATH)
    data = provider.load_data()
    regime_detector.train(data['close'])
    predictions = regime_detector.predict(data['close'])
    plt.figure(figsize=(12, 6))
    plt.plot(data.index[ml_params['lookback_window']:], predictions, label='Predicted Regime')
    plt.plot(data.index, data['close'], label='Price')
    plt.legend()
    plt.title('Regime Detection using LSTM')
    plt.show()

def main_backtest():
    from src.core.csv_data_provider import CSVDataProvider
    from src.core.data_provider import YahooDataProvider
    # Choose the appropriate data provider
    provider = CSVDataProvider(CSV_FILE_PATH) if DATA_PROVIDER.lower() == 'csv' else \
               YahooDataProvider(DEFAULT_TICKER, DEFAULT_START_DATE, DEFAULT_END_DATE, db_path=DB_PATH)
    data = provider.load_data()
    logger.info(f"Data loaded for {DEFAULT_TICKER}")
    
    # Load benchmark data
    benchmark_provider = YahooDataProvider(DEFAULT_BENCHMARK_TICKER, DEFAULT_START_DATE, DEFAULT_END_DATE, db_path=DB_PATH)
    benchmark_data = benchmark_provider.load_data()
    data = data.join(benchmark_data[['close']].rename(columns={'close': 'benchmark_close'}), how='inner')
    data['benchmark_close'] = data['benchmark_close'].ffill()
    data = data.dropna(subset=['benchmark_close'])
    
    # Compute returns
    data['returns'] = data['close'].pct_change()
    data['benchmark_returns'] = data['benchmark_close'].pct_change()
    
    # Plot analysis charts
    plot_pair_analysis(data, f"{DEFAULT_TICKER}-{DEFAULT_BENCHMARK_TICKER}")
    
    # Initialize strategies using configuration
    momentum_strategy = MomentumStrategy(window=STRATEGY_CONFIG['momentum']['window'])
    mean_reversion_strategy = MeanReversionStrategy(
        window=STRATEGY_CONFIG['mean_reversion']['window'],
        threshold=STRATEGY_CONFIG['mean_reversion']['threshold']
    )
    stat_arb_strategy = create_enhanced_statistical_arbitrage()
    
    strategies = [momentum_strategy, mean_reversion_strategy, stat_arb_strategy]
    from src.core.backtesting_engine import BacktestingEngine
    engine = BacktestingEngine(strategies=strategies, initial_capital=INITIAL_CAPITAL)
    
    results_dict = engine.run_all(data)
    logger.info("Backtesting completed.")
    analyze_strategy_results(results_dict)
    
    # Plot cumulative returns
    plt.figure(figsize=(15, 7))
    for strategy_name, results in results_dict.items():
        plt.plot(results.index, results['cumulative_strategy'], 
                 label=f'{strategy_name} (Return: {(results["cumulative_strategy"].iloc[-1] / INITIAL_CAPITAL - 1) * 100:.1f}%)')
    plt.plot(results.index, results['cumulative_market'], label='Market', alpha=0.7)
    plt.title('Strategy Performance Comparison')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Quantitative Trading Engine")
    parser.add_argument("--mode", choices=["backtest", "ml"], default="backtest", help="Run backtesting or ML regime detection")
    args = parser.parse_args()

    if args.mode == "ml":
        run_ml_model()
    else:
        main_backtest()

if __name__ == "__main__":
    main()
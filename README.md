# Quantitative Trading Engine

A comprehensive Python-based trading engine that allows you to backtest multiple trading strategies using historical market data. The engine combines traditional technical analysis strategies like momentum and mean reversion with more sophisticated approaches like statistical arbitrage and portfolio optimization.

Key capabilities include:
- Backtesting multiple strategies simultaneously on any stock or ETF available through Yahoo Finance
- Analyzing risk metrics including Value at Risk (VaR), drawdown statistics, and factor exposures
- Visualizing strategy performance with detailed charts and statistical analysis
- Managing market data efficiently through local caching and multiple data provider options
- Implementing complex trading logic with built-in statistical tests and position sizing

This project is designed for:
- Quantitative researchers testing trading hypotheses
- Traders looking to evaluate strategy performance
- Developers interested in building robust financial software
- Students learning about quantitative finance and algorithmic trading

The engine supports three main trading strategies:
1. Momentum: Exploits trending behavior in price movements
2. Mean Reversion: Capitalizes on price deviations from historical averages
3. Statistical Arbitrage: Implements pairs trading using cointegration and statistical tests

All components are built with a focus on code quality, testing, and extensibility, making it easy to add new strategies or enhance existing functionality.

## Key Features

### Advanced Trading Strategies
- **Statistical Arbitrage:** Implements pairs trading with dynamic hedge ratios and cointegration testing
- **Mean Reversion:** Adaptive thresholds with position sizing
- **Momentum:** Trend-following with optimized lookback periods
- **Portfolio Optimization:** Modern portfolio theory implementation with custom constraints

### Sophisticated Analytics
- **Advanced Risk Metrics:** 
  - Value at Risk (VaR) with multiple calculation methods
  - Conditional VaR (Expected Shortfall)
  - Extreme Value Theory (EVT) for tail risk
  - Dynamic drawdown analysis with recovery metrics
- **Factor Analysis:**
  - Multi-factor exposure calculation
  - Dynamic beta estimation
  - R-squared analytics
- **Statistical Tests:**
  - Cointegration testing with ADF
  - Half-life calculation for mean reversion
  - Rolling correlation analysis

### Enhanced Visualization
- **Interactive Performance Dashboards:**
  - Strategy return comparisons
  - Risk metric visualization
  - Drawdown analysis
- **Pair Trading Analytics:**
  - Spread visualization
  - Rolling correlation plots
  - Returns scatter analysis
  - Normalized price series comparison

### Technical Architecture
- **Robust Data Management:**
  - SQLite-based market data caching
  - Multiple data provider support (Yahoo Finance, CSV)
  - Efficient data preprocessing and alignment
- **Concurrent Processing:**
  - Parallel strategy backtesting
  - Thread-safe data handling
  - Optimized computation engine
- **Production-Ready Features:**
  - Comprehensive logging system
  - Performance profiling decorators
  - Error handling and recovery
  - Modular, extensible design

## Project Structure

```
quant_trading_project/
├── config/
│   └── settings.py              # Configuration parameters
├── data/
│   └── market_data.db          # SQLite database (auto-generated)
├── src/
│   ├── core/
│   │   ├── backtesting_engine.py    # Parallel backtesting engine
│   │   ├── data_provider.py         # Abstract data provider interface
│   │   ├── csv_data_provider.py     # CSV data handler
│   │   ├── portfolio_optimizer.py    # Portfolio optimization engine
│   │   ├── risk_engine.py           # Enhanced risk analytics
│   │   └── models.py                # Data models and types
│   ├── strategies/
│   │   ├── base_strategy.py         # Strategy interface
│   │   ├── momentum_strategy.py     # Momentum implementation
│   │   ├── mean_reversion_strategy.py # Mean reversion logic
│   │   └── statistical_arbitrage.py  # Stat arb implementation
│   └── utils/
│       ├── logger.py                # Logging configuration
│       └── decorators.py            # Performance monitoring
├── main.py                     # Application entry point
├── requirements.txt            # Dependencies
└── README.md
```

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ryannapp12/quant_trading_project.git
cd quant_trading_project
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Engine

After installation, you can run the engine using:
```bash
python3 main.py
```

This will:
1. Load historical data for the configured stock (default: AAPL)
2. Run backtests for all three strategies
3. Generate performance analytics and visualizations
4. Display results in both console output and graphical format

### Pair Trading Analysis
![Pair Trading Analysis](assets/pairTradingAnalysis.png)

The above visualization shows:
- Normalized price series comparing the stock vs benchmark
- Price spread between the pairs
- 60-day rolling correlation
- Daily returns scatter analysis

### Strategy Performance
![Strategy Performance Comparison](assets/strategyPerformanceComparison.png)

The performance comparison shows:
- MeanReversionStrategy (Return: 14.5%)
- MomentumStrategy (Return: 160.4%)
- StatisticalArbitrageStrategy (Return: 0.0%)
- Market performance as benchmark

### Example Console Output

## Usage Examples

### Basic Backtesting
```python
from src.core.data_provider import YahooDataProvider
from src.strategies.momentum_strategy import MomentumStrategy

# Initialize data provider
provider = YahooDataProvider("AAPL", "2020-01-01", "2024-01-01")
data = provider.load_data()

# Create and run strategy
strategy = MomentumStrategy(window=20)
results = strategy.backtest(data)
```

### Statistical Arbitrage
```python
from src.strategies.statistical_arbitrage import StatisticalArbitrageStrategy

# Create pairs trading strategy
stat_arb = StatisticalArbitrageStrategy(
    lookback_period=20,
    entry_zscore=1.5,
    exit_zscore=0.5
)

# Add benchmark data
data['benchmark_close'] = benchmark_data['close']

# Run backtest
results = stat_arb.backtest(data)
```

## Performance Analysis

### Risk Metrics
```python
from src.core.risk_engine import RiskEngine

risk = RiskEngine(results)
tail_metrics = risk.calculate_tail_risk_metrics()
drawdown_metrics = risk.calculate_drawdown_metrics()
```

### Visualization
```python
# Plot performance comparison
plot_pair_analysis(data, "AAPL-QQQ")

# Display strategy results
plt.figure(figsize=(15, 7))
plt.plot(results.index, results['cumulative_strategy'])
plt.show()
```

### Example Output
```bash
[*********************100%***********************]  1 of 1 completed
2025-02-09 10:54:32,845 - __main__ - INFO - Data loaded for AAPL
[*********************100%***********************]  1 of 1 completed
2025-02-09 10:54:33.551 Python[72050:155795071] +[IMKClient subclass]: chose IMKClient_Modern
2025-02-09 10:54:33.551 Python[72050:155795071] +[IMKInputSession subclass]: chose IMKInputSession_Modern
2025-02-09 10:54:47,731 - __main__ - INFO - Backtesting completed.
2025-02-09 10:54:47,754 - __main__ - INFO - 
MeanReversionStrategy Analysis:
2025-02-09 10:54:47,755 - __main__ - INFO - Tail Risk Metrics:
2025-02-09 10:54:47,755 - __main__ - INFO - - historical_var: -1.77%
2025-02-09 10:54:47,755 - __main__ - INFO - - parametric_var: -2.15%
2025-02-09 10:54:47,755 - __main__ - INFO - - conditional_var: -3.27%
2025-02-09 10:54:47,755 - __main__ - INFO - - evt_var: -0.09%
2025-02-09 10:54:47,755 - __main__ - INFO - 
Drawdown Analysis:
2025-02-09 10:54:47,755 - __main__ - INFO - - max_drawdown: -30.62%
2025-02-09 10:54:47,755 - __main__ - INFO - - average_drawdown: -10.15%
2025-02-09 10:54:47,755 - __main__ - INFO - - average_recovery_time: 189.8 days
2025-02-09 10:54:47,755 - __main__ - INFO - - drawdown_frequency: 0.40%
2025-02-09 10:54:47,764 - __main__ - INFO - 
MomentumStrategy Analysis:
2025-02-09 10:54:47,764 - __main__ - INFO - Tail Risk Metrics:
2025-02-09 10:54:47,764 - __main__ - INFO - - historical_var: -2.98%
2025-02-09 10:54:47,764 - __main__ - INFO - - parametric_var: -3.19%
2025-02-09 10:54:47,764 - __main__ - INFO - - conditional_var: -4.48%
2025-02-09 10:54:47,764 - __main__ - INFO - - evt_var: -0.05%
2025-02-09 10:54:47,764 - __main__ - INFO - 
Drawdown Analysis:
2025-02-09 10:54:47,764 - __main__ - INFO - - max_drawdown: -36.67%
2025-02-09 10:54:47,764 - __main__ - INFO - - average_drawdown: -11.58%
2025-02-09 10:54:47,764 - __main__ - INFO - - average_recovery_time: 33.2 days
2025-02-09 10:54:47,764 - __main__ - INFO - - drawdown_frequency: 3.66%
2025-02-09 10:54:47,765 - __main__ - INFO - 
StatisticalArbitrageStrategy Analysis:
2025-02-09 10:54:47,765 - __main__ - INFO - Tail Risk Metrics:
2025-02-09 10:54:47,765 - __main__ - INFO - - historical_var: 0.00%
2025-02-09 10:54:47,765 - __main__ - INFO - - parametric_var: nan%
2025-02-09 10:54:47,765 - __main__ - INFO - - conditional_var: 0.00%
2025-02-09 10:54:47,765 - __main__ - INFO - - evt_var: 0.00%
2025-02-09 10:54:47,765 - __main__ - INFO - 
Drawdown Analysis:
2025-02-09 10:54:47,765 - __main__ - INFO - - max_drawdown: 0.00%
2025-02-09 10:54:47,765 - __main__ - INFO - - average_drawdown: 0.00%
2025-02-09 10:54:47,765 - __main__ - INFO - - average_recovery_time: 0.0 days
2025-02-09 10:54:47,765 - __main__ - INFO - - drawdown_frequency: 0.00%
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

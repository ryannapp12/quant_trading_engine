# config/settings.py

DEFAULT_TICKER = 'AAPL'
DEFAULT_START_DATE = '2020-01-01'
DEFAULT_END_DATE = '2025-02-08'
INITIAL_CAPITAL = 100000.0
DB_PATH = 'data/market_data.db'

# Data provider selection: 'yahoo' or 'csv'
DATA_PROVIDER = 'yahoo'
CSV_FILE_PATH = 'data/AAPL.csv'

# Strategy configuration
STRATEGY_CONFIG = {
    'momentum': {
        'window': 20
    },
    'mean_reversion': {
        'window': 20,
        'threshold': 0.05
    }
}
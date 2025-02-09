# config/settings.py

DEFAULT_TICKER = 'AAPL'
DEFAULT_START_DATE = '2020-01-01'
DEFAULT_END_DATE = '2021-01-01'
INITIAL_CAPITAL = 100000.0
DB_PATH = 'data/market_data.db'

# Configuration for strategies (example for the Momentum Strategy)
STRATEGY_CONFIG = {
    'momentum': {
        'window': 20
    }
}
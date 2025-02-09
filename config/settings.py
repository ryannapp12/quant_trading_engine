import os
from dotenv import load_dotenv

load_dotenv()  # This loads variables from .env into the environment

DEFAULT_TICKER = os.getenv("DEFAULT_TICKER", "XOM")
DEFAULT_BENCHMARK_TICKER = os.getenv("DEFAULT_BENCHMARK_TICKER", "CVX")
DEFAULT_START_DATE = os.getenv("DEFAULT_START_DATE", "2020-01-01")
DEFAULT_END_DATE = os.getenv("DEFAULT_END_DATE", "2025-01-01")
INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", "1000000.0"))
DB_PATH = os.getenv("DB_PATH", "data/market_data.db")
DATA_PROVIDER = os.getenv("DATA_PROVIDER", "yahoo")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "data/XOM.csv")
ALPACA_API_KEY_LIVE = os.getenv("ALPACA_API_KEY_LIVE")
ALPACA_API_SECRET_LIVE = os.getenv("ALPACA_API_SECRET_LIVE")
ALPACA_API_KEY_TEST = os.getenv("ALPACA_API_KEY_TEST")
ALPACA_API_SECRET_TEST = os.getenv("ALPACA_API_SECRET_TEST")
ALPACA_BASE_URL_TEST = os.getenv("ALPACA_BASE_URL_TEST", "https://paper-api.alpaca.markets/v2")
ALPACA_BASE_URL_LIVE = os.getenv("ALPACA_BASE_URL_LIVE", "https://api.alpaca.markets")

STRATEGY_CONFIG = {
    'momentum': {
        'window': 20
    },
    'mean_reversion': {
        'window': 20,
        'threshold': 0.05
    },
    'statistical_arbitrage': {
        'lookback_period': 60,
        'entry_zscore': 2.0,
        'exit_zscore': 0.5,
        'max_position_hold': 20,
        'min_half_life': 5,
        'confidence_level': 0.05
    }
}

ML_CONFIG = {
    'regime_detector': {
        'model_type': 'LSTM',
        'lookback_window': 30,
        'hidden_units': 50,
        'epochs': 10,
        'batch_size': 32
    }
}

DASHBOARD_CONFIG = {
    'update_interval_ms': int(os.getenv("DASHBOARD_UPDATE_INTERVAL_MS", "60000"))
}
import asyncio
import logging
from threading import Thread
from alpaca_trade_api.stream import Stream
import os
from dotenv import load_dotenv
import nest_asyncio
from config.settings import (
    DEFAULT_TICKER,
    ALPACA_API_KEY_LIVE,
    ALPACA_API_KEY_TEST,
    ALPACA_API_SECRET_LIVE,
    ALPACA_API_SECRET_TEST,
    ALPACA_BASE_URL_LIVE,
    ALPACA_BASE_URL_TEST,
)

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables (if not already loaded by config/settings.py)
load_dotenv()

logger = logging.getLogger(__name__)

class RealTimeDataIngestor:
    _instance = None

    def __new__(cls, symbols):
        if cls._instance is None:
            cls._instance = super(RealTimeDataIngestor, cls).__new__(cls)
        return cls._instance

    def __init__(self, symbols):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        self.api_key = ALPACA_API_KEY_TEST
        self.api_secret = ALPACA_API_SECRET_TEST
        self.base_url = ALPACA_BASE_URL_TEST
        self.symbols = symbols
        self.stream = Stream(self.api_key, self.api_secret, base_url=self.base_url)
        self.latest_data = {}

    async def on_minute_bar(self, bar):
        self.latest_data[bar.symbol] = {
            'timestamp': bar.timestamp,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        }
        logger.info(f"Received bar for {bar.symbol}: {bar.close}")

    async def subscribe_bars(self):
        for symbol in self.symbols:
            self.stream.subscribe_bars(self.on_minute_bar, symbol)
        while True:
            try:
                await self.stream.run()
                break
            except ValueError as e:
                if "connection limit exceeded" in str(e).lower():
                    logger.error("Connection limit exceeded. Waiting for 300 seconds before retrying...")
                    try:
                        self.stream.close()
                    except Exception as close_error:
                        logger.error(f"Error closing stream: {close_error}")
                    await asyncio.sleep(300)
                else:
                    logger.error(f"Unhandled error: {e}")
                    raise e

    def start(self):
        loop = asyncio.new_event_loop()
        t = Thread(target=loop.run_until_complete, args=(self.subscribe_bars(),))
        t.daemon = True
        t.start()
        logger.info("Real-time data ingestion started.")

    def get_latest(self, symbol):
        return self.latest_data.get(symbol, None)

# Standalone testing block
if __name__ == "__main__":
    symbols = [DEFAULT_TICKER]
    ingestor = RealTimeDataIngestor(symbols)
    ingestor.start()
    import time
    while True:
        data = ingestor.get_latest(DEFAULT_TICKER)
        if data:
            print("Latest bar for ${DEFAULT_TICKER}:", data)
        time.sleep(60)
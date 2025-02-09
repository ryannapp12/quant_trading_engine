# src/core/data_provider.py

import os
import sqlite3
import pandas as pd
import yfinance as yf
from abc import ABC, abstractmethod
from typing import Optional

class DataProvider(ABC):
    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        """Abstract method to load market data."""
        pass

class YahooDataProvider(DataProvider):
    def __init__(self, ticker: str, start_date: str, end_date: str, db_path: str = 'data/market_data.db'):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def _init_db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                ticker TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                PRIMARY KEY (ticker, date)
            )
        """)
        conn.commit()
        return conn

    def _save_to_db(self, data: pd.DataFrame, conn: sqlite3.Connection) -> None:
        df = data.copy()
        df = df.reset_index()

        # Convert all column names to lowercase strings
        df.columns = [str(col).lower() for col in df.columns]
        
        # Rename the date column if needed
        if 'datetime' in df.columns:
            df.rename(columns={'datetime': 'date'}, inplace=True)
        
        # Add ticker column
        df['ticker'] = self.ticker
        
        # Write to SQLite
        df.to_sql('market_data', conn, if_exists='replace', index=False)

    def _load_from_db(self, conn: sqlite3.Connection) -> Optional[pd.DataFrame]:
        query = f"""
            SELECT date, open, high, low, close, volume FROM market_data
            WHERE ticker = '{self.ticker}' AND date BETWEEN '{self.start_date}' AND '{self.end_date}'
            ORDER BY date ASC
        """
        df = pd.read_sql_query(query, conn, parse_dates=['date'], index_col='date')
        return df if not df.empty else None

    def load_data(self) -> pd.DataFrame:
        conn = self._init_db()
        cached = self._load_from_db(conn)
        
        if cached is not None:
            conn.close()
            return cached
            
        try:
            # Download data from Yahoo Finance
            data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
            
            # Convert column names to lowercase strings
            if isinstance(data.columns, pd.MultiIndex):
                # Handle MultiIndex columns
                data.columns = [str(col[0]).lower() for col in data.columns]
            else:
                # Handle regular Index columns
                data.columns = [str(col).lower() for col in data.columns]
            
            # Save to database
            self._save_to_db(data, conn)
            conn.close()
            return data
            
        except Exception as e:
            conn.close()
            raise Exception(f"Error downloading data for {self.ticker}: {str(e)}")
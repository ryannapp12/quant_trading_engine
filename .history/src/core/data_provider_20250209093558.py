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
        df = data.reset_index()
        # Flatten the columns if they are a MultiIndex
        new_columns = []
        for col in df.columns:
            if isinstance(col, tuple):
                # If the second element is empty, just take the first element.
                if len(col) == 2 and col[1] == '':
                    new_columns.append(col[0])
                else:
                    new_columns.append('_'.join([str(c) for c in col if c]))
            else:
                new_columns.append(col)
        df.columns = new_columns

        # Ensure that the first column is named 'date'
        first_col = df.columns[0]
        if first_col.lower() != 'date':
            df.rename(columns={first_col: 'date'}, inplace=True)

        df['ticker'] = self.ticker
        df.to_sql('market_data', conn, if_exists='append', index=False)
        
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
        data = yf.download(self.ticker, start=self.start_date, end=self.end_date)[['Open', 'High', 'Low', 'Close', 'Volume']]
        self._save_to_db(data, conn)
        conn.close()
        return data
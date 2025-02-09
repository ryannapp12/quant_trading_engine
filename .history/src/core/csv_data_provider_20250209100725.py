# src/core/csv_data_provider.py

import os
import pandas as pd
from src.core.data_provider import DataProvider

class CSVDataProvider(DataProvider):
    def __init__(self, csv_file: str):
        self.csv_file = csv_file

    def load_data(self) -> pd.DataFrame:
        if not os.path.exists(self.csv_file):
            raise FileNotFoundError(f"CSV file {self.csv_file} not found.")
        # Read CSV with a Date column as the index.
        data = pd.read_csv(self.csv_file, parse_dates=['Date'], index_col='Date')
        # Normalize column names to lowercase.
        data.columns = [col.lower() for col in data.columns]
        return data
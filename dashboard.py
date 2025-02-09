import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from config.settings import DASHBOARD_CONFIG
from src.core.real_time_data import RealTimeDataIngestor
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# No need to retrieve API keys here; they are loaded in RealTimeDataIngestor.
symbols = ['XOM']

# Initialize the real-time data ingestor (singleton ensures only one connection)
ingestor = RealTimeDataIngestor(symbols)
ingestor.start()

def get_live_data():
    # For simplicity, construct a DataFrame with the latest bar repeated over time.
    latest = ingestor.get_latest('XOM')
    if latest:
        # Build a DataFrame using the latest bar (in production, accumulate historical data)
        times = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='T')
        data = pd.DataFrame({
            'cumulative_strategy': [latest['close']] * 100,
            'cumulative_market': [latest['close']] * 100
        }, index=times)
        return data
    else:
        # Fallback: return simulated data if no real data is available.
        df = pd.DataFrame({
            'datetime': pd.date_range(start='2025-01-01', periods=100, freq='T'),
            'cumulative_strategy': (1 + pd.Series(0.001 * np.random.randn(100))).cumprod() * 1000000,
            'cumulative_market': (1 + pd.Series(0.001 * np.random.randn(100))).cumprod() * 1000000
        })
        df.set_index('datetime', inplace=True)
        return df

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Real-Time Trading Performance Dashboard"),
    dcc.Graph(id='performance-graph'),
    dcc.Interval(
        id='interval-component',
        interval=DASHBOARD_CONFIG['update_interval_ms'],
        n_intervals=0
    )
])

@app.callback(Output('performance-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    data = get_live_data()
    trace1 = go.Scatter(
        x=data.index,
        y=data['cumulative_strategy'],
        mode='lines',
        name='Strategy'
    )
    trace2 = go.Scatter(
        x=data.index,
        y=data['cumulative_market'],
        mode='lines',
        name='Market'
    )
    layout = go.Layout(
        title='Cumulative Returns',
        xaxis={'title': 'Time'},
        yaxis={'title': 'Portfolio Value ($)'},
        template='plotly_dark'
    )
    return {'data': [trace1, trace2], 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
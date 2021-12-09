
from pathlib import Path
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import yfinance as yf
import pandas as pd
import numpy as np


def ampm_to_24h(timestamp : str) -> str:
    date, time = timestamp.split(' ')
    
    if 'AM' in timestamp:
        hour = int(time.split('-')[0])
        new_ts = '{} {:02d}:00:00'.format(date, hour if hour != 12 else 0)
    elif 'PM' in timestamp:    
        hour = int(time.split('-')[0])
        new_ts = '{} {:02d}:00:00'.format(date, hour + 12 if hour != 12 else hour)
    else:
        new_ts = timestamp
    
    return new_ts

# data = pd.read_csv(Path(__file__).parent / 'data/Binance_BTCUSDT_1h.csv')
# data['date'] = pd.to_datetime(data['date'].map(ampm_to_24h))
# data = data.set_index('date')
# data = data.sort_index()


def update_data():
    hourly_data = yf.download("BTC-USD", period="1y", interval="1h")
    daily_data = yf.download("BTC-USD", period="max", interval="1d")

    return hourly_data, daily_data


def get_figures(hourly_data, daily_data, n_days=30):
    # Fig 0 is a candlestick plot of the daily data from the last 30 days
    subset = daily_data.iloc[-n_days:]
    candle_data = {"x": subset.index.tolist(), 
                   "open": subset['Open'].tolist(),
                   "close":subset['Close'].tolist(),
                   "high":subset['High'].tolist(),
                   "low":subset['Low'].tolist()}
    
    candle_layout = {"title": f'Market History <br> (Last {n_days} days)'}
    candle_graph = [go.Candlestick(**candle_data)]

    # Fig 1 is a MACD lines plot
    hourly_data['m7'] = hourly_data['Close'].rolling(7).mean()
    hourly_data['m25'] = hourly_data['Close'].rolling(25).mean()
    hourly_data['m99'] = hourly_data['Close'].rolling(99).mean()
    # data['macd'] = data['m7'] - data['m21']
    subset = hourly_data.iloc[-n_days * 24:]

    macd_graph = []
    for col in ['Close', 'm7', 'm25', 'm99']:
        macd_graph.append(go.Scatter(x=subset.index.tolist(), 
                                     y=subset[col].tolist(), 
                                     mode='lines',
                                     name=col))

    macd_layout = {'title': f'Moving Averages <br> (Last {n_days} days)'}

    # Fig 2 is a bar plot of BTC volume per month
    bar_graph = []
    resampled = daily_data.resample('M').mean()
    month_year = resampled.apply(lambda x: '{:02d}/{}'.format(x.name.month, x.name.year), axis=1)
    volume_per_month = resampled['Volume']
    
    bar_graph.append(go.Bar(x=month_year.tolist(), y=volume_per_month.tolist()))
    bar_layout = {'title': 'BTC Traded Volume in USDT'}

    # Fig 3 is a scatter plot of value per volume
    scatter_graph = []
    scatter_graph.append(go.Scatter(x=resampled['Volume'].tolist(), 
                                    y=resampled['Close'].tolist(),
                                    mode='markers',
                                    text=month_year.tolist(),
                                    textposition='top center',
                                    name='Data points'
                                    ))


    lr = LinearRegression(normalize=True)
    lr.fit(resampled['Volume'].to_numpy().reshape(-1, 1), resampled['Close'].to_numpy().reshape(-1, 1))
    xx = [resampled['Volume'].min(), resampled['Volume'].max()]
    yy = []
    for x in xx:
        yy.append(lr.predict(np.asarray(x).reshape(-1, 1))[0, 0])

    print(xx, yy)

    scatter_graph.append(go.Scatter(x=xx,
                                    y=yy,
                                    mode='lines',
                                    name='Trendline',
                                    line={'dash': 'dash'}
                                    ))

    scatter_layout = {'title': 'BTC Volume in USD vs. BTC Price in USD', 
                        'xaxis': {'title': 'Volume in USDT'}, 
                        'yaxis': {'title': 'BTC Value in USDT'}}

    figures = [{'data': candle_graph, 'layout': candle_layout, 'config': {'responsive': True}},
               {'data': macd_graph, 'layout': macd_layout, 'config': {'responsive': True}},
               {'data': bar_graph, 'layout': bar_layout, 'config': {'responsive': True}},
               {'data': scatter_graph, 'layout': scatter_layout, 'config': {'responsive': True}}]
    
    return figures
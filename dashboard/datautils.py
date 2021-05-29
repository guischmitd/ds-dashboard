
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd

data = pd.read_csv(Path(__file__).parent / 'data/Binance_BTCUSDT_1h.csv')

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

data['date'] = pd.to_datetime(data['date'].map(ampm_to_24h))
data = data.set_index('date')
data = data.sort_index()


def get_figures():
    # Fig 0 is a candlestick plot of the last n_days days
    n_days = 30
    subset = data[data.index[-n_days * 24]:]
    candle_data = {"x": subset.index.tolist(), 
                   "open": subset['open'].tolist(),
                   "close":subset['close'].tolist(),
                   "high":subset['high'].tolist(),
                   "low":subset['low'].tolist()}
    
    candle_layout = {"title": f'Market History <br> (Last {n_days} days)'}
    candle_graph = [go.Candlestick(**candle_data)]

    # Fig 1 is a MACD lines plot
    data['m7'] = data['close'].rolling(7).mean()
    data['m21'] = data['close'].rolling(21).mean()

    macd_graph = []
    for col in ['close', 'm7', 'm21']:
        macd_graph.append(go.Scatter(x=data.index.tolist(), 
                                     y=data[col].tolist(), 
                                     mode='lines',
                                     name=col))
    macd_layout = {'title': 'Moving Averages'}

    # Fig 2 is a bar plot of BTC volume per month
    bar_graph = []
    resampled = data.resample('M').mean()
    month_year = resampled.apply(lambda x: '{:02d}/{}'.format(x.name.month, x.name.year), axis=1)
    volume_per_month = resampled['Volume USDT']
    
    bar_graph.append(go.Bar(x=month_year.tolist(), y=volume_per_month.tolist()))
    bar_layout = {'title': 'BTC Traded Volume in USDT'}

    # Fig 3 is a scatter plot of value per volume
    scatter_graph = []
    scatter_graph.append(go.Scatter(x=resampled['Volume USDT'].tolist(), 
                                    y=resampled['close'].tolist(),
                                    mode='markers'))
    scatter_layout = {'title': 'BTC Volume in USDT vs. BTC Price in USDT', 
                        'xaxis': {'title': 'Volume in USDT'}, 
                        'yaxis': {'title': 'BTC Value in USDT'}}

    figures = [{'data': candle_graph, 'layout': candle_layout, 'config': {'responsive': True}},
               {'data': macd_graph, 'layout': macd_layout, 'config': {'responsive': True}},
               {'data': bar_graph, 'layout': bar_layout, 'config': {'responsive': True}},
               {'data': scatter_graph, 'layout': scatter_layout, 'config': {'responsive': True}}]
    
    return figures
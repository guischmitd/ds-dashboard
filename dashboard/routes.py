from dashboard import app
from flask import render_template, jsonify
from datetime import datetime
from .datautils import get_figures, update_data
import plotly
import yfinance as yf
import json


@app.route('/')
def main():
    last_updated_text = datetime.now().strftime("Last updated %Y-%m-%d @ %H:%M:%S")
    hourly, daily = update_data()
    print(hourly.shape, daily.shape)

    figures = get_figures(hourly, daily)

    # plot ids for the html id tag
    ids = [f'figure-{i}' for i in range(len(figures))]

    # Convert the plotly figures to JSON for javascript in html template
    figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)
    print(figuresJSON[0])

    

    return render_template('index.html', 
                            last_updated_text=last_updated_text, 
                            ids=ids,
                            figuresJSON=figuresJSON)
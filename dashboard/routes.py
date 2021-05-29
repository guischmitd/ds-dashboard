from dashboard import app
from flask import render_template, url_for, redirect, jsonify
from datetime import datetime
from .datautils import get_figures
import plotly
import json

last_updated_text = datetime.now().strftime("Last updated %Y-%m-%d @ %H:%M:%S")

@app.route('/')
def main():
    figures = get_figures()

    # plot ids for the html id tag
    ids = [f'figure-{i}' for i in range(len(figures))]

    # Convert the plotly figures to JSON for javascript in html template
    figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)
    print(figuresJSON[0])

    return render_template('index.html', 
                            last_updated_text=last_updated_text, 
                            ids=ids,
                            figuresJSON=figuresJSON)

@app.route('/refresh')
def refresh():
    print('Downloading new data!')

    return jsonify({'lastUpdated': last_updated_text})
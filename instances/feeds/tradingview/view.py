import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Sample DataFrame
df = pd.read_csv("data_file.csv")
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# Create Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    dcc.Graph(id='candlestick-chart'),
    html.Button('Minute', id='minute-button', n_clicks=0),
    html.Button('1 Day', id='day-button', n_clicks=0),
    html.Button('5 Days', id='5days-button', n_clicks=0),
    html.Button('1 Week', id='week-button', n_clicks=0)
])


# Callback to update the chart based on button clicks
@app.callback(
    Output('candlestick-chart', 'figure'),
    [Input('minute-button', 'n_clicks'),
     Input('day-button', 'n_clicks'),
     Input('5days-button', 'n_clicks'),
     Input('week-button', 'n_clicks')]
)
def update_chart(minute_clicks, day_clicks, five_days_clicks, week_clicks):
    ctx = dash.callback_context

    if not ctx.triggered_id:
        button_id = 'minute-button'
    else:
        button_id = ctx.triggered_id.split('.')[0]

    if button_id == 'minute-button':
        interval_df = df.resample('T').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        # show only 24 hours of data
        interval_df = interval_df.tail(24 * 60)
        # remove day from index
        interval_df.index = interval_df.index.strftime('%H:%M')
    elif button_id == 'day-button':
        interval_df = df.resample('D').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        interval_df.index = interval_df.index.strftime('%Y-%m-%d')
        # show only 30 days of data
        interval_df = interval_df.tail(30)
    elif button_id == '5days-button':
        interval_df = df.resample('5D').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        interval_df.index = interval_df.index.strftime('%Y-%m-%d')
    elif button_id == 'week-button':
        interval_df = df.resample('W').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        interval_df.index = interval_df.index.strftime('%Y-%m-%d')
    else:
        interval_df = df.resample('T').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})

    # remove index
    # interval_df.reset_index(inplace=True)
    interval_df = interval_df.dropna()

    # Hide seconds from x-axis

    trace = go.Candlestick(x=interval_df.index,
                           open=interval_df['open'],
                           high=interval_df['high'],
                           low=interval_df['low'],
                           close=interval_df['close'])

    # range breaks
    rangebreaks = [
        dict(bounds=["sat", "mon"]),  # hide weekends
    ]

    layout = go.Layout(title='Candlestick Chart',
                       xaxis=dict(title='Date', type='category', rangebreaks=rangebreaks),
                       yaxis=dict(title='Price'),
                       showlegend=False)

    return {'data': [trace], 'layout': layout}


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

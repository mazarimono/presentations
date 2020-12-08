import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

from dash.dependencies import Input, Output

app = dash.Dash(__name__)

hanpy_event = pd.read_csv("data/hanpy.csv", index_col=0)
hanpy_event.index = pd.to_datetime(hanpy_event.index)
hanpy_event_month = hanpy_event.resample("M").sum()

mem_data = pd.read_csv('data/hannari.csv', index_col=0, parse_dates=['registration'])
mem_data['one'] = 1 
mem_data = mem_data.set_index('registration')
mem_data = mem_data.sort_index()
mem_data['cumsum'] = mem_data['one'].cumsum()

len_month = len(hanpy_event_month) + 1
len_mem_data = len(mem_data) + 1

app.layout = html.Div([

    html.Div(
    [
        dcc.Interval(
            id="hanpy_interval",
            n_intervals=0,
            interval=100,
            disabled=False,
            max_intervals=len(hanpy_event_month) + 1,
        ),
        html.Button(id="hanpy_button", n_clicks=0, children="Button"),
        dcc.Graph(id="hanpy_graph"),
    ]
),
    html.Div([
        dcc.Interval(
            id='hanpy_mem_interval',
            n_intervals=len_mem_data,
            interval=100,
            disabled=False,
            max_intervals=len_mem_data/10
        ),
        html.Button(id="hanpy_mem_button", n_clicks=0, children="Button"),
        dcc.Graph(id="hanpy_mem_graph", style={'height': '600px'}),
    ])

])

@app.callback(
    Output("hanpy_interval", "n_intervals"), Input("hanpy_button", "n_clicks")
)
def interval_switch(n_clicks):
    if n_clicks > 0:
        return 0


@app.callback(Output("hanpy_graph", "figure"), Input("hanpy_interval", "n_intervals"))
def update_graph(n_counts):
    hanpy_event_graph = hanpy_event_month.iloc[:n_counts, :]
    return px.bar(hanpy_event_graph)


@app.callback(
    Output("hanpy_mem_interval", "n_intervals"), Input("hanpy_mem_button", "n_clicks")
)
def interval_switch(n_clicks):
    if n_clicks > 0:
        return 0


@app.callback(Output("hanpy_mem_graph", "figure"), Input("hanpy_mem_interval", "n_intervals"))
def update_graph(n_counts):
    mem_count = mem_data.iloc[:n_counts*10, :]
    return px.area(mem_count, x=mem_count.index, y='cumsum', title='はんなりPython登録者数')


app.run_server()

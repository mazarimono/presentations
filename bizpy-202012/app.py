import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH, ALLSMALLER


import plotly.express as px
import pandas as pd

# CSS

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

show_slides_css = {"height": "800px", "paddingTop": "2%"}

page_button_css = {"fontSize": "1.5rem", "display": "inline-block"}
page_num_css = {"display": "inline-block", "fontSize": "3rem", "paddingLeft": "80%"}

page_bottom_css = {"borderBottom": "inset 3px black"}

my_link_css = {"fontSize": "3rem", "paddingLeft": "4%"}

title_css = {
    "textAlign": "center",
    "fontSize": "6rem",
    "borderBottom": "inset 3px black",
    "width": "35%",
    "margin": "auto",
}

half_css = {
    "width": "50%",
    "display": "inline-block",
    "verticalAlign": "top",
    "margin": "auto",
}

bottom_css = {
    "display": "inline-block",
    "fontSize": "3rem",
    "paddingLeft": "80%",
    "position": "absolute",
    "bottom": "2%",
}

# application

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config.suppress_callback_exceptions = True

# pages あとからファイルにする

# page1

title = html.Div(
    [
        html.H1(
            "国内COVID-19データをDashを使って可視化する",
            style={"padding": "15%", "fontSize": "5rem", "textAlign": "center"},
        ),
        html.H3("BizPy 20201209", style={"textAlign": "right", "padding": "3% 10% 0"}),
        html.H3("合同会社長目　小川 英幸", style={"textAlign": "right", "padding": "0 10% 0"}),
    ]
)

# page2

intro = html.Div(
    [
        html.H1("自己紹介", style=title_css),
        html.Div(
            [
                html.Div(
                    [
                        html.P("小川 英幸"),
                        html.P("@ogawahideyuki"),
                        html.P("合同会社 長目"),
                        html.P("はんなりPython"),
                        html.P("最近黒豆にはまっている"),
                    ],
                    style={
                        "textAlign": "center",
                        "paddingTop": "14%",
                        "fontSize": "5rem",
                    },
                ),
            ],
            style=half_css,
        ),
        html.Div(
            [
                html.Img(
                    id="my_book",
                    src="assets/python.jpeg",
                    style={"width": "60%", "margin": "4% auto"},
                ),
            ],
            style=half_css,
            id="img_div",
            n_clicks=0,
        ),
    ]
)


@app.callback(Output("my_book", "src"), Input("img_div", "n_clicks"))
def update_image(n_clicks):
    if n_clicks % 2 == 1:
        return "assets/webdb.png"
    return "assets/python.jpeg"


# page3

hanpy_event = pd.read_csv("data/hanpy.csv", index_col=0)
hanpy_event.index = pd.to_datetime(hanpy_event.index)
hanpy_event_month = hanpy_event.resample("M").sum()
len_month = len(hanpy_event_month) + 1

mem_data = pd.read_csv('data/hannari.csv', index_col=0, parse_dates=['registration'])
mem_data['one'] = 1 
mem_data = mem_data.set_index('registration')
mem_data = mem_data.sort_index()
mem_data['cumsum'] = mem_data['one'].cumsum()

len_mem_data = len(mem_data) + 1

hanpy = html.Div(
    [
        html.H1("はんなりPython", style=title_css),
        html.Div(
            [
                html.Img(src="assets/hannari.png"),
                html.P("京都発のプログラミング勉強会"),
                html.P("2020年オンライン化し、その後イベントを多く開催"),
            ],
            style={
                "height": "800px",
                "width": "80%",
                "fontSize": "6rem",
                "textAlign": "center",
                "margin": "4% auto",
            },
        ),
        html.Div(
            [
                dcc.Interval(
                    id="hanpy_interval",
                    n_intervals=len_month,
                    interval=100,
                    disabled=False,
                    max_intervals=len_month,
                ),
                html.Button(id="hanpy_button", n_clicks=0, children="Button"),
                dcc.Graph(id="hanpy_graph", style={'height': '550px'}),
            ],
            style={'backgroudColor': 'yellow', 'height': '600px'},
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
    ]),
    ]
)


@app.callback(
    Output("hanpy_interval", "n_intervals"), Input("hanpy_button", "n_clicks")
)
def interval_switch(n_clicks):
    if n_clicks > 0:
        return 0


@app.callback(Output("hanpy_graph", "figure"), Input("hanpy_interval", "n_intervals"))
def update_graph(n_counts):
    hanpy_event_graph = hanpy_event_month.iloc[:n_counts, :]
    return px.bar(hanpy_event_graph, title='はんなりPython月間イベント数')


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

# page4
covid = html.Div([html.H1("国内COVID19可視化", style=title_css)])

# matome_chusen

final = html.Div([
    html.H1('まとめ & 抽選', style=title_css)
])


# circular

app.layout = html.Div(
    [
        dcc.Location(id="my_location"),
        html.Div(
            [
                html.Button(
                    id="back_button", children="Back", n_clicks=0, style=page_button_css
                ),
                html.Button(
                    id="next_button", children="Next", n_clicks=0, style=page_button_css
                ),
                dcc.Link(id="my_links", href="/1", style=my_link_css),
                html.P(id="show_page_num", children=1, style=page_num_css),
            ],
            style=page_bottom_css,
        ),
        html.Div(id="show_slides", style=show_slides_css),
        html.Div([dcc.Link(id="my_links2", href="/1", style=bottom_css)]),
    ],
    style={"margin": "3%", "borderRadius": "3%"},
)


@app.callback(
    Output("show_page_num", "children"),
    Input("back_button", "n_clicks"),
    Input("next_button", "n_clicks"),
    State("show_page_num", "children"),
)
def update_page_num(back_clicks, next_clicks, page_num):
    page_num = 1 - back_clicks + next_clicks
    if page_num < 1:
        page_num = 1

    return page_num


@app.callback(
    Output("back_button", "n_clicks"),
    Output("next_button", "n_clicks"),
    Input("show_page_num", "children"),
)
def change_button_num(page_num):
    if page_num == 1:
        return 0, 0


@app.callback(
    Output("my_links", "href"),
    Output("my_links2", "href"),
    Input("show_page_num", "children"),
)
def update_links(page_num):
    return f"/{page_num}", f"{page_num}"


@app.callback(Output("show_slides", "children"), Input("my_location", "pathname"))
def update_slides(pathname):
    if pathname == "/1":
        return title
    elif pathname == "/2":
        return intro
    elif pathname == "/3":
        return hanpy
    elif pathname == "/4":
        return covid


if __name__ == "__main__":
    app.run_server(debug=True)

from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
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
    "width": "46%",
    "display": "inline-block",
    "verticalAlign": "top",
    "margin": "auto",
    "padding": "2%",
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

mem_data = pd.read_csv("data/hannari.csv", index_col=0, parse_dates=["registration"])
mem_data["one"] = 1
mem_data = mem_data.set_index("registration")
mem_data = mem_data.sort_index()
mem_data["cumsum"] = mem_data["one"].cumsum()

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
                dcc.Graph(id="hanpy_graph", style={"height": "550px"}),
            ],
            style={"backgroudColor": "yellow", "height": "600px"},
        ),
        html.Div(
            [
                dcc.Interval(
                    id="hanpy_mem_interval",
                    n_intervals=len_mem_data,
                    interval=100,
                    disabled=False,
                    max_intervals=len_mem_data / 10,
                ),
                html.Button(id="hanpy_mem_button", n_clicks=0, children="Button"),
                dcc.Graph(id="hanpy_mem_graph", style={"height": "600px"}),
            ]
        ),
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
    return px.bar(hanpy_event_graph, title="はんなりPython月間イベント数")


@app.callback(
    Output("hanpy_mem_interval", "n_intervals"), Input("hanpy_mem_button", "n_clicks")
)
def interval_switch(n_clicks):
    if n_clicks > 0:
        return 0


@app.callback(
    Output("hanpy_mem_graph", "figure"), Input("hanpy_mem_interval", "n_intervals")
)
def update_graph(n_counts):
    mem_count = mem_data.iloc[: n_counts * 10, :]
    return px.area(mem_count, x=mem_count.index, y="cumsum", title="はんなりPython登録者数")


# page4

## データの日付から年、週数、曜日を加える
def add_weeknum_dayofweek(data):
    data["calendar"] = data.index.map(date.isocalendar)
    data["year"] = data["calendar"].map(lambda x: x[0])
    data["week_num"] = data["calendar"].map(lambda x: x[1])
    data["day_of_week"] = data["calendar"].map(lambda x: x[2])
    return data


# covid_csv from mhlw(厚生労働省)
## なぜか、退院、死亡者数だけが累計////

# データURL
covid_positive = "https://www.mhlw.go.jp/content/pcr_positive_daily.csv"
pcr_testing = "https://www.mhlw.go.jp/content/pcr_tested_daily.csv"
hospital_num = "https://www.mhlw.go.jp/content/cases_total.csv"
leaving_num = "https://www.mhlw.go.jp/content/recovery_total.csv"
death_num = "https://www.mhlw.go.jp/content/death_total.csv"

# データ読み込み
covid_positive_data = pd.read_csv(covid_positive, index_col=0, parse_dates=["日付"])
pcr_testing_data = pd.read_csv(pcr_testing, index_col=0, parse_dates=["日付"])
hospital_num_data = pd.read_csv(hospital_num, index_col=0, parse_dates=["日付"])
leaving_num_data = pd.read_csv(leaving_num, index_col=0, parse_dates=["日付"])
death_num_data = pd.read_csv(death_num, index_col=0, parse_dates=["日付"])


covid_positive_data = add_weeknum_dayofweek(covid_positive_data)
pcr_testing_data = add_weeknum_dayofweek(pcr_testing_data)

covid_table = covid_positive_data[-10:].reset_index()[["日付", "PCR 検査陽性者数(単日)"]]

# COVID-19 Data FROM
# JAG JAPAN https://gis.jag-japan.com/covid19jp/

jag_url = "https://dl.dropboxusercontent.com/s/6mztoeb6xf78g5w/COVID-19.csv"
jag = pd.read_csv(jag_url, low_memory=False, parse_dates=["確定日", "発症日"])

need_cols = ["年代", "性別", "確定日", "居住都道府県", "人数"]
jag_df = jag[need_cols].copy()

jag_df["年代"] = jag_df["年代"].map(lambda x: x.replace("\u3000", ""))
jag_df["年代"] = jag_df["年代"].map(lambda x: x.replace("\xa0", ""))
jag_df["年代"] = jag_df["年代"].map(lambda x: x.replace("0-10", "0"))
jag_df["年代"] = jag_df["年代"].map(lambda x: x.replace("不明", "50"))
jag_df["年代"] = jag_df["年代"].map(int)

jag_df["性別"] = jag_df["性別"].fillna("不明")
jag_df["性別"] = jag_df["性別"].map(lambda x: x.replace("\u3000", ""))
jag_df["性別"] = jag_df["性別"].map(lambda x: x.replace("\xa0", ""))
jag_df["性別"] = jag_df["性別"].map(lambda x: x.replace("⼥性", "女性"))

jag_df["居住都道府県"] = jag_df["居住都道府県"].fillna("不明")
jag_df["居住都道府県"] = jag_df["居住都道府県"].map(lambda x: x.replace("\xa0", ""))

jag_df_bar = jag_df.groupby(["確定日", "居住都道府県"], as_index=False).sum()
jag_df_table = jag_df[100000:100010]


covid = html.Div(
    [
        html.H1("国内COVID19可視化", style=title_css),
        html.Div(
            [
                html.H1(
                    html.A(
                        "データは厚生労働省より",
                        href="https://www.mhlw.go.jp/stf/covid-19/open-data.html",
                    )
                ),
                html.Div(
                    [
                        dcc.Graph(
                            figure=px.area(
                                covid_positive_data, y="PCR 検査陽性者数(単日)", title="陽性者数"
                            ),
                            style=half_css,
                        ),
                        dcc.Graph(
                            figure=px.area(
                                pcr_testing_data, y="PCR 検査実施件数(単日)", title="PCR検査実施人数"
                            ),
                            style=half_css,
                        ),
                    ]
                ),
                html.Div(
                    [
                        dcc.Graph(
                            figure=px.area(hospital_num_data, title="入院治療などを要する"),
                            style=half_css,
                        ),
                        dcc.Graph(
                            figure=px.area(death_num_data, title="死亡者数"), style=half_css
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.H3("気になる曜日ごとの推移(1 == 月曜日)"),
                        html.Div(
                            [
                                dcc.Graph(
                                    figure=px.line(
                                        pcr_testing_data["2020-9":],
                                        x="day_of_week",
                                        y="PCR 検査実施件数(単日)",
                                        color="week_num",
                                        title="曜日ごとのPCR検査の推移(2020年9月～)",
                                        height=800,
                                    )
                                )
                            ],
                            style=half_css,
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    figure=px.line(
                                        covid_positive_data["2020-9":],
                                        x="day_of_week",
                                        y="PCR 検査陽性者数(単日)",
                                        color="week_num",
                                        title="曜日ごとの感染者数の推移(2020年9月～)",
                                        height=800,
                                    )
                                )
                            ],
                            style=half_css,
                        ),
                    ],
                    style={"marginTop": "5%"},
                ),
                html.Div(
                    [
                        html.H1("より詳細にデータをみてみたい！！"),
                        html.H3(
                            html.A(
                                "ジャッグジャパンさんのデータを使う！！（11月30日まで）",
                                href="https://gis.jag-japan.com/covid19jp/",
                            ),
                            style={"paddingLeft": "5%"},
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    figure=px.bar(
                                        jag_df_bar,
                                        x="確定日",
                                        y="人数",
                                        color="居住都道府県",
                                        title="データの推移",
                                        height=800,
                                    )
                                ),
                                html.H2(
                                    "なぜJAG-JAPANさんのデータを使わせていただくか？",
                                    style={"paddingBottom": "5%"},
                                ),
                                html.Div(
                                    [
                                        html.H3("JAG-JAPANさんのデータ"),
                                        dash_table.DataTable(
                                            columns=[
                                                {"name": i, "id": i}
                                                for i in jag_df_table.columns
                                            ],
                                            data=jag_df_table.to_dict("records"),
                                            fill_width=False,
                                            style_cell={
                                                "textAlign": "center",
                                                "width": 140,
                                                "fontSize": 24,
                                            },
                                        ),
                                    ],
                                    style=half_css,
                                ),
                                html.Div(
                                    [
                                        html.H3("厚生労働省さんのデータ"),
                                        dash_table.DataTable(
                                            columns=[
                                                {"name": i, "id": i}
                                                for i in covid_table.columns
                                            ],
                                            data=covid_table.to_dict("records"),
                                            fill_width=False,
                                            style_cell={
                                                "textAlign": "center",
                                                "width": 140,
                                                "fontSize": 24,
                                            },
                                        ),
                                    ],
                                    style=half_css,
                                ),
                            ]
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.H1("年齢別の感染者数の対比"),
                        html.Button("PUSHME", id="pushme"),
                        html.Div(id="add_graph_div", children=[]),
                    ]
                ),
            ],
            style={"padding": "5%"},
        ),
    ]
)


@app.callback(
    Output("add_graph_div", "children"),
    Input("pushme", "n_clicks"),
    State("add_graph_div", "children"),
    prevent_initial_call=True,
)
def update_layout(n_clicks, append_child):
    new_layout = html.Div(
        [
            dcc.DatePickerRange(
                id={"type": "date_picker", "index": n_clicks},
                min_date_allowed=date(2020, 1, 15),
                max_date_allowed=date(2020, 12, 1),
                start_date=date(2020, 3, 1),
                end_date=date(2020, 4, 30),
            ),
            dcc.Graph(id={"type": "covid_graph", "index": n_clicks})
            # html.P(id={'type':'covid_graph', 'index': n_clicks})
        ],
        style=half_css,
    )
    append_child.append(new_layout)
    return append_child


@app.callback(
    Output({"type": "covid_graph", "index": MATCH}, "figure"),
    Input({"type": "date_picker", "index": MATCH}, "start_date"),
    Input({"type": "date_picker", "index": MATCH}, "end_date"),
)
def update_graph(start_date, end_date):
    jag_df_pm = jag_df.set_index("確定日").copy()
    jag_df_pm.index = pd.to_datetime(jag_df_pm.index)
    jag_df_pm = jag_df_pm.loc[f"{start_date}":f"{end_date}"]
    jag_df_pm = jag_df_pm.groupby(["年代", "性別"], as_index=False).sum()
    return px.treemap(jag_df_pm, path=["年代", "性別"], values="人数")
    # return f'{start_date} / {end_date}'


# matome

final = html.Div(
    [
        html.H1("まとめ", style=title_css),
        html.Div(
            [
                dcc.Markdown(
                    """
        - データをインタラテクィブに可視化すると注目される
        - データをインタラクティブに可視化すると詳細が分かる
        - それを簡単にできるとなお良い
        """,
                    style={
                        "textAlign": "center",
                        "marginTop": "5%",
                        "fontSize": "5rem",
                    },
                ),
                html.H1(
                    "本買ってね",
                    style={
                        "textAlign": "center",
                        "marginTop": "5%",
                        "fontSize": "10rem",
                        "color": "lime",
                    },
                    id="kattene",
                    hidden=True,
                ),
            ],
            id="mark_button",
            n_clicks=0,
        ),
    ]
)

# present

present = html.Div([html.H1("書籍プレゼント抽選", style=title_css),])


@app.callback(Output("kattene", "hidden"), Input("mark_button", "n_clicks"))
def update_h1(n_clicks):
    if n_clicks % 2 == 1:
        return False
    return True


# chusen

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
    elif pathname == "/5":
        return final
    elif pathname == "/6":
        return present


if __name__ == "__main__":
    app.run_server(debug=True)

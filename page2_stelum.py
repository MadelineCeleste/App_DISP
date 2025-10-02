from dash import register_page, html, callback, Input, Output, State, dcc, MATCH, ALL
import dash_bootstrap_components as dbc
import dash_latex as dl
from pathlib import Path
import plotly.express as px
import dash_mantine_components as dmc

page_url = "/STELUM"

df = px.data.iris()
fig1 = px.scatter(df, x="sepal_width",y="sepal_length")
fig2 = px.scatter(df, x="petal_length",y="petal_width")
fig3 = px.scatter(df, x="species",y="petal_width")

@callback(
    Output("stelum-selected-color", "children"),
    Input("stelum-color-picker", "value")
)
def pick(color):
    return f"Selected RGBA: {color}"

layout = html.Div(
    id="stelum-main",
    style={
        "display": "flex",
        "flexDirection": "column",
        "width": "100vw",
        "height": "100vh"
    },
    children=[
        html.Div(
            id="stelum-page",
            style={
                "width": "calc(100% - 5rem)",
                "height": "100%",
                "marginLeft": "auto",
                "display": "flex",
                "flexDirection": "row"
            },
            children=[
                html.Div(
                    id="stelum-left",
                    style={
                        "width": "45%",
                        "height": "100%",
                        "display": "flex",
                        "flexDirection": "column"
                    },
                    children=[
                        html.Div(
                            id="stelum-header-container",
                            style={
                                "width": "100%",
                                "height": "20%",
                                "display": "flex",
                                "flexDirection": "column",
                                "alignItems": "center",
                                "justifyContent": "center",
                            },
                            children=[
                                html.Span("STELUM Dashboard", className="subtitles-config", style={"fontSize": "4vh"}),
                                html.Hr(style={"width": "100%","marginBottom":"2vh"}),
                                dbc.Input(id="stelum-output-path", placeholder="Absolute path towards an output folder", type="text", style={"height": "5vh", "width": "80%", "marginBottom": "0.5vh"}),
                                dbc.Input(id="stelum-fig-name", placeholder="Figure name (not including .extension)", type="text", style={"height": "5vh", "width": "80%"})
                            ]
                        ),
                        html.Div(
                            id="stelum-add-remove-graph-container",
                            style={
                                "width": "100%",
                                "height": "20%",
                                "display": "flex",
                                "flexDirection": "row",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "marginTop":"2vh",
                                "marginBottom":"2vh"
                            },
                            children=[
                                html.Div(
                                    style={"width": "66.6%", "height": "100%", "display": "flex", "flexDirection": "row"},
                                    children=[
                                        dcc.Dropdown(id="stelum-dropdown-x", options=[{"label": "placeholder", 'value': "placeholder"}], style={"height": "100%", "width": "98%", "marginLeft": "1%", "marginRight": "1%"},value="placeholder",clearable=False),
                                        dcc.Dropdown(id="stelum-dropdown-y", options=[{"label": "placeholder", 'value': "placeholder"}], style={"height": "100%", "width": "98%", "marginRight": "2%"},value="placeholder",clearable=False)
                                    ]
                                ),
                                html.Div(
                                    style={"width": "33.3%", "height": "100%", "display": "flex", "flexDirection": "column"},
                                    children=[
                                        dbc.Button("Add", id="stelum-btn-add-graph", className="btn-add", style={"width": "98%", "height": "49%", "marginBottom": "2%", "marginRight": "2%"}),
                                        dbc.Button("Remove", id="stelum-btn-remove-graph", className="btn-remove", style={"width": "98%", "height": "49%", "marginRight": "2%"})
                                    ]
                                )
                            ]
                        ),
                        html.Hr(style={"width": "100%"}),
                        html.Div(
                            id="stelum-axes-range-container",
                            style={"height": "20%", "width": "100%", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center","marginBottom":"2vh","marginTop":"2vh","marginBottom":"2vh"},
                            children=[
                                html.Div(style={"height": "100%", "width": "20%", "display": "flex", "alignItems": "center", "justifyContent": "center", "marginRight":"1vw"}, 
                                        children=[html.Span("Axes ranges|scale: ", className="subtitles-config", style={"fontSize": "2vh"})]),
                                html.Div(
                                    style={"height": "100%", "width": "80%", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"},
                                    children=[
                                        html.Div(
                                            style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "flex-start", "marginBottom": "0.5vh"},
                                            children=[
                                                html.Span("x_range: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Input(id="stelum-x-range", placeholder="ex: [-1,15.6]", style={"height": "100%", "width": "22%", "marginRight": "5%"}),
                                                html.Span("x_scale: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dcc.RadioItems(
                                                        id="stelum-x-scale",
                                                        options=[
                                                            {"label": "Linear", "value": "linear"},
                                                            {"label": "Logarithmic", "value": "log"},
                                                        ],
                                                        value="linear",
                                                        labelStyle={"display": "block"},
                                                        style={"marginRight":"2vw","fontSize":"2vh"}
                                                    ),
                                                html.Span("reversed: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Checkbox(id="stelum-x-reversed", value=False),
                                            ]
                                        ),
                                        html.Div(
                                            style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "flex-start"},
                                            children=[
                                                html.Span("y_range: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Input(id="stelum-y-range", placeholder="ex: [2,1e6]", style={"height": "100%", "width": "22%", "marginRight": "5%"}),
                                                html.Span("y_scale: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dcc.RadioItems(
                                                        id="stelum-y-scale",
                                                        options=[
                                                            {"label": "Linear", "value": "linear"},
                                                            {"label": "Logarithmic", "value": "log"},
                                                        ],
                                                        value="linear",
                                                        labelStyle={"display": "block"},
                                                        style={"marginRight":"2vw","fontSize":"2vh"}
                                                    ),
                                                html.Span("reversed: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Checkbox(id="stelum-y-reversed", value=False),
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            id="stelum-axes-label-container",
                            style={"height": "20%", "width": "100%", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "center","marginTop":"2vh","marginBottom":"1vh"},
                            children=[
                                html.Div(style={"height": "100%", "width": "20%", "display": "flex", "alignItems": "center", "justifyContent": "center","marginRight":"1vw"}, 
                                        children=[html.Span("Axes labels: ", className="subtitles-config", style={"fontSize": "2vh"})]),
                                html.Div(
                                    style={"height": "100%", "width": "80%", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"},
                                    children=[
                                        html.Div(
                                            style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "flex-start", "marginBottom": "0.5vh"},
                                            children=[
                                                html.Span("x_label: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Input(id="stelum-x-label", placeholder="X(He)_{core}", style={"height": "100%", "width": "35%", "marginRight": "5%"}),
                                                html.Span("y_label: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Input(id="stelum-y-label", placeholder="latex works on SAVE", style={"height": "100%", "width": "35%", "marginRight": "5%"})
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Hr(style={"width": "100%"}),
                        html.Div(
                            id="stelum-graph-args",
                            style={"height":"20%","width":"100%","display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center","marginBottom":"1vh","marginTop":"1vh"},
                            children=[
                                 html.Span("Graph args: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                 dbc.Input(id="stelum-graph-label", placeholder="[name1:[args1],name2:[args2]..]", style={"height": "100%", "width": "85%"}),
                            ]
                        ),
                        html.Div(
                            id="stelum-graph-args-exemple",
                            style={"height":"20%","width":"100%","display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center","marginBottom":"1vh","marginTop":"1vh"},
                            children = [html.Span("Input example: [4G_R005-core_he_0.01:[label=X, color=rgba(255, 0, 0, 1), linestyle=dashed...]]", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"})]
                        ),
                        html.Div(
                            id="stelum-graph-color-picker",
                            style={
                                "height": "20%",
                                "width": "100%",
                                "display": "flex",
                                "flexDirection": "row",
                                "alignItems": "center",
                                "justifyContent": "center"
                            },
                            children = [
                                html.Div(
                                style={
                                "height": "100%",
                                "width": "100%",
                                "display": "flex",
                                "flexDirection": "column",
                                "alignItems": "center",
                                "justifyContent": "center"
                            },
                            children=[
                                dmc.Group(
                                    gap=40,
                                    children=[
                                        dmc.ColorPicker(
                                            id="stelum-color-picker",
                                            format="rgba",
                                            value="rgba(255, 0, 0, 1)",
                                            size="sm",
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id="stelum-selected-color",
                                    style={"marginTop": "1vh", "fontSize": "2vh", "fontWeight": "bold"}
                                )
                            ]
                            )]
                        )
                    ]
                ),
                html.Div(
                    id="stelum-right",
                    style={"width": "55%", "height": "100%", "display": "flex", "flexDirection": "column"},
                    children=[
                        html.Div(
                            id="stelum-graph-container",
                            style={"width": "100%", "height": "70vh", "display": "flex"}, #have to force the 70vh otherwise it bugs out sometimes, no clue why
                            children=[
                                dcc.Graph(id="stelum-right-side-graph", figure=fig1, style={"width": "100%", "height": "100%"}, responsive=True)
                            ]
                        ),
                        html.Div(
                            id="stelum-line-maker-container",
                            style={"width": "100%", "height": "30vh", "display": "flex","flexDirection":"row"},
                            children=[
                                html.Div(
                                    style={
                                        "width": "1px",
                                        "backgroundColor": "white",
                                        "height": "100%",
                                    }
                                ),
                                html.Div(
                                    style={"width":"10%","height":"100%","display":"flex","alignItems":"center","justifyContent":"center"},
                                    children=[html.Span("Lines: ", className="subtitles-config", style={"fontSize": "3vh"})]
                                ),
                                html.Div(
                                    style={"width":"30%","height":"100%","display":"flex","alignItems":"center","justifyContent":"center","flexDirection":"column"},
                                    children=[
                                        dbc.Input(id="stelum-line-value", placeholder="value || name:column", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="stelum-line-limits", placeholder="limits - [x1,x2] or [y1,y2]", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dcc.RadioItems(
                                                id="stelum-line-direction",
                                                options=[
                                                    {"label": "x-vertical", "value": "x"},
                                                    {"label": "y-horizontal", "value": "y"},
                                                ],
                                                value="x",
                                                labelStyle={"display": "block"},
                                                style={"marginRight":"2vw","fontSize":"2vh"}
                                            ),
                                    ]
                                ),
                                html.Div(
                                    style={"width":"30%","height":"100%","display":"flex","alignItems":"center","justifyContent":"center","flexDirection":"column"},
                                    children=[
                                        dbc.Input(id="stelum-line-width", placeholder="linewidth (plt)", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="stelum-line-style", placeholder="linestyle (plt)", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="stelum-line-label", placeholder="line label", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="stelum-line-color", placeholder="rgba color", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                    ]
                                ),
                                html.Div(
                                    style={"width":"30%","height":"100%","display":"flex","alignItems":"center","justifyContent":"center","flexDirection":"column"},
                                    children=[
                                        dbc.Button("Add", id="stelum-btn-add-line", className="btn-add", style={"width": "80%", "height": "30%","marginBottom":"1vh"}),
                                        dbc.Button("Remove", id="stelum-btn-remove-line", className="btn-remove", style={"width": "80%", "height": "30%"})
                                    ]
                                )   
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)
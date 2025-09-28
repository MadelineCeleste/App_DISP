from dash import register_page, html, callback, Input, Output, State, dcc, MATCH, ALL
import dash_bootstrap_components as dbc
import dash_latex as dl
from pathlib import Path
import plotly.express as px
import dash_mantine_components as dmc

page_url = "/PULSE"

df = px.data.iris()
fig1 = px.scatter(df, x="sepal_width",y="sepal_length")
fig2 = px.scatter(df, x="petal_length",y="petal_width")
fig3 = px.scatter(df, x="species",y="petal_width")

@callback(
    Output("pulse-selected-color", "children"),
    Input("pulse-color-picker", "value")
)
def pick(color):
    return f"Selected RGBA: {color}"

layout = html.Div(
    id="pulse-main",
    style={
        "display": "flex",
        "flexDirection": "column",
        "width": "100vw",
        "height": "100vh"
    },
    children=[
        html.Div(
            id="pulse-page",
            style={
                "width": "calc(100% - 5rem)",
                "height": "100%",
                "marginLeft": "auto",
                "display": "flex",
                "flexDirection": "row"
            },
            children=[
                html.Div(
                    id="pulse-left",
                    style={
                        "width": "45%",
                        "height": "100%",
                        "display": "flex",
                        "flexDirection": "column"
                    },
                    children=[
                        html.Div(
                            id="pulse-header-container",
                            style={
                                "width": "100%",
                                "height": "20%",
                                "display": "flex",
                                "flexDirection": "column",
                                "alignItems": "center",
                                "justifyContent": "center",
                            },
                            children=[
                                html.Span("PULSE Dashboard", className="subtitles-config", style={"fontSize": "4vh"}),
                                html.Hr(style={"width": "100%","marginBottom":"2vh"}),
                                dbc.Input(id="pulse-output-path", placeholder="Absolute path towards an output folder", type="text", style={"height": "5vh", "width": "80%", "marginBottom": "0.5vh"}),
                                dbc.Input(id="pulse-fig-name", placeholder="Figure name (not including .extension)", type="text", style={"height": "5vh", "width": "80%"})
                            ]
                        ),
                        html.Div(
                            id="pulse-add-remove-graph-container",
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
                                        dcc.Dropdown(id="pulse-dropdown-x", options=[{"label": "placeholder", 'value': "placeholder"}], style={"height": "100%", "width": "98%", "marginLeft": "1%", "marginRight": "1%"},value="placeholder",clearable=False),
                                        dcc.Dropdown(id="pulse-dropdown-y", options=[{"label": "placeholder", 'value': "placeholder"}], style={"height": "100%", "width": "98%", "marginRight": "2%"},value="placeholder",clearable=False)
                                    ]
                                ),
                                html.Div(
                                    style={"width": "33.3%", "height": "100%", "display": "flex", "flexDirection": "column"},
                                    children=[
                                        dbc.Button("Add", id="pulse-btn-add-graph", className="btn-add", style={"width": "98%", "height": "49%", "marginBottom": "2%", "marginRight": "2%"}),
                                        dbc.Button("Remove", id="pulse-btn-remove-graph", className="btn-remove", style={"width": "98%", "height": "49%", "marginRight": "2%"})
                                    ]
                                )
                            ]
                        ),
                        html.Hr(style={"width": "100%"}),
                        html.Div(
                            id="pulse-axes-range-container",
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
                                                dbc.Input(id="pulse-x-range", placeholder="ex: [-1,15.6]", style={"height": "100%", "width": "22%", "marginRight": "5%"}),
                                                html.Span("x_scale: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dcc.RadioItems(
                                                        id="pulse-x-scale",
                                                        options=[
                                                            {"label": "Linear", "value": "linear"},
                                                            {"label": "Logarithmic", "value": "log"},
                                                        ],
                                                        value="linear",
                                                        labelStyle={"display": "block"},
                                                        style={"marginRight":"2vw","fontSize":"2vh"}
                                                    ),
                                                html.Span("reversed: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Checkbox(id="pulse-x-reversed", value=False),
                                            ]
                                        ),
                                        html.Div(
                                            style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "flex-start"},
                                            children=[
                                                html.Span("y_range: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Input(id="pulse-y-range", placeholder="ex: [2,1e6]", style={"height": "100%", "width": "22%", "marginRight": "5%"}),
                                                html.Span("y_scale: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dcc.RadioItems(
                                                        id="pulse-y-scale",
                                                        options=[
                                                            {"label": "Linear", "value": "linear"},
                                                            {"label": "Logarithmic", "value": "log"},
                                                        ],
                                                        value="linear",
                                                        labelStyle={"display": "block"},
                                                        style={"marginRight":"2vw","fontSize":"2vh"}
                                                    ),
                                                html.Span("reversed: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Checkbox(id="pulse-y-reversed", value=False),
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            id="pulse-axes-label-container",
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
                                                dbc.Input(id="pulse-x-label", placeholder="X(He)_{core}", style={"height": "100%", "width": "35%", "marginRight": "5%"}),
                                                html.Span("y_label: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Input(id="pulse-y-label", placeholder="latex works on SAVE", style={"height": "100%", "width": "35%", "marginRight": "5%"})
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Hr(style={"width": "100%"}),
                        html.Div(
                            id="pulse-graph-label-container",
                            style={"height":"20%","width":"100%","display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center","marginBottom":"1vh","marginTop":"1vh"},
                            children=[
                                 html.Span("Graph label: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                 dbc.Input(id="pulse-graph-label", placeholder="[name1:label1,name2:label2..] <--> [4G_R0005-core_he_0.01:X(He)_{core}=0.01,...]", style={"height": "100%", "width": "85%"}),
                            ]
                        ),
                        html.Div(
                            id="pulse-graph-color-container",
                            style={"height":"20%","width":"100%","display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center","marginBottom":"2vh"},
                            children=[
                                 html.Span("Graph color: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                 dbc.Input(id="pulse-graph-color", placeholder="[name1:color1,name2:color2..] <--> [4G_R0005-core_he_0.01:rgba(123,3,54,1),...]", style={"height": "100%", "width": "85%"}),
                            ]
                        ),
                        html.Div(
                            id="pulse-graph-color-picker",
                            style={
                                "height": "20%",
                                "width": "100%",
                                "display": "flex",
                                "flexDirection": "row",
                                "alignItems": "center",
                                "justifyContent": "center"
                            },
                            children = [
                                html.Div(style={"height":"100%","width":"50%","display":"flex","justifyContent":"center","alignItems":"center"},
                                children = [html.Span("RGBA Color picker: ", className="subtitles-config", style={"fontSize": "3vh", "marginRight": "1%"})]),
                                html.Div(
                                style={
                                "height": "100%",
                                "width": "50%",
                                "display": "flex",
                                "flexDirection": "column",
                                "alignItems": "flex-start",
                                "justifyContent": "center"
                            },
                            children=[
                                dmc.Group(
                                    gap=40,
                                    children=[
                                        dmc.ColorPicker(
                                            id="pulse-color-picker",
                                            format="rgba",
                                            value="rgba(255, 0, 0, 1)",
                                            size="sm",
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id="pulse-selected-color",
                                    style={"marginTop": "1vh", "fontSize": "2vh", "fontWeight": "bold"}
                                )
                            ]
                            )]
                        )
                    ]
                ),
                html.Div(
                    id="pulse-right",
                    style={"width": "55%", "height": "100%", "display": "flex", "flexDirection": "column"},
                    children=[
                        html.Div(
                            id="pulse-graph-container",
                            style={"width": "100%", "height": "70vh", "display": "flex"}, #have to force the 70vh otherwise it bugs out sometimes, no clue why
                            children=[
                                dcc.Graph(id="pulse-right-side-graph", figure=fig2, style={"width": "100%", "height": "100%"}, responsive=True)
                            ]
                        ),
                        html.Div(
                            id="pulse-line-maker-container",
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
                                        dbc.Input(id="pulse-line-value", placeholder="value || name:k || name:pi0", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="pulse-line-limits", placeholder="limits - [x1,x2] or [y1,y2]", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dcc.RadioItems(
                                                id="pulse-line-direction",
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
                                        dbc.Input(id="pulse-line-width", placeholder="linewidth (plt)", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="pulse-line-style", placeholder="linestyle (plt)", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="pulse-line-label", placeholder="line label", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="pulse-line-color", placeholder="rgba color", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                    ]
                                ),
                                html.Div(
                                    style={"width":"30%","height":"100%","display":"flex","alignItems":"center","justifyContent":"center","flexDirection":"column"},
                                    children=[
                                        dbc.Button("Add", id="pulse-btn-add-line", className="btn-add", style={"width": "80%", "height": "30%","marginBottom":"1vh"}),
                                        dbc.Button("Remove", id="pulse-btn-remove-line", className="btn-remove", style={"width": "80%", "height": "30%"})
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
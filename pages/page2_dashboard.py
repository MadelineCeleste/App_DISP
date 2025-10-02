from dash import register_page, html, callback, Input, Output, State, dcc, MATCH, ALL, ctx
import dash
import dash_bootstrap_components as dbc
import dash_latex as dl
from pathlib import Path
import plotly.express as px
import dash_mantine_components as dmc
import numpy as np
from DISP import data_reading
import time
import copy

page_url = "/dashboard"

df = px.data.iris()
fig1 = px.scatter(df, x="sepal_width",y="sepal_length")
fig2 = px.scatter(df, x="petal_length",y="petal_width")
fig3 = px.scatter(df, x="species",y="petal_width")


stelum_dropdown_options = ['n','r','mr','rho','p','t','chir','chit','grad','grad_ad','Y','b','lq','mode','fl','fx',
                'lum','eta','etar','kappa','kappar','kappat','grad_rad','zeta','eps','epsr','epst',
                'log10_tau','w','wtau','delr','delp','delt','deltau','dellum','dp','dt','dadmd',
                'ui','duidp','duidt','cp','cv','eta_e','zmoy','gamma',
                'H','He','C','O','rhog']

pulse_dropdown_options = ["Reduced_Pad","Reduced_Pspacing","Pad","Pspacing","L","K","Ekin", "Ckl","Kp","Kg","Kp+Kg"]

@callback(
    Output("selected-color", "children"),
    Input("color-picker", "value")
)
def pick(color):
    return f"Selected RGBA: {color}"

@callback(
    Output("tab-container","children"), #actually need to change dropdowns and stuff too no ? Or we leave that to display:yes ?
    #maybe just change the placeholder then it's fine :)
    Output("line-value","placeholder"),
    Output("store-active-tab","data"),
    Input({"type":"tab-choosing", "group":1, "name":ALL}, "n_clicks"),
    State("tab-container","children"),
    State("store-active-tab","data")
)
def header_value(clicks, children, store_active_tab):

    placeholder = "value || name:column"

    if store_active_tab is None:
        store_active_tab = {"active_tab":"stelum", "previous_tab":"pulse"} #either stelum, pulse or eig

    try:
        for props in children:
            prop = props["props"]
            if prop["id"]["name"] == ctx.triggered_id["name"]:
                prop["className"] = "btn-choosen"
                store_active_tab["previous_tab"] = store_active_tab["active_tab"]
                store_active_tab["active_tab"] = ctx.triggered_id["name"].split("-")[1]
            else:
                prop["className"] = "btn-tab"

            if ctx.triggered_id["name"] == "btn-pulse":
                placeholder = "value || name:k || name:pi0"
    except:
        children[0]["props"]["className"] = "btn-choosen"

    return(children, placeholder, store_active_tab)

@callback(
    Output("store-displayed","data"),
    Input("store-datatable-data","data"),#triggers on adding new models or changing display to "yes"
    State("store-displayed","data")
)
def store_file_data(store_datatable_data, store_displayed):

    datatable = copy.deepcopy(store_datatable_data) #this is ABSOLUTELY NECESSARY
    #but you know the fun thing ? I HAVE NO CLUE WHY
    #otherwise it triggers a callback loop between page1 and 2 on display edit, and I'm way too tired to understand why imma be honest
    #that's an #onlyDashthings if I've ever seen one holy smokes

    if store_displayed is None:
        store_displayed = {}

    try: #so, dash convert numpy arrays to list when they are parsed in to a dcc.Store
        #because it serializes in JSON, so, yeah that's happening...
        display = np.array(datatable["table_data"]["display"])

        display_indexes = np.where(display != "no")[0] #in case of misstypes I guess ?

        names = np.array(datatable["names"])[display_indexes]
        spes = np.array(datatable["spe"])[display_indexes]
        path_stelums = np.array(datatable["stelum_paths"])[display_indexes]
        path_pulses = np.array(datatable["pulse_paths"])[display_indexes]

        for name, spe, path_stelum, path_pulse in zip(names, spes, path_stelums, path_pulses):
            store_displayed[f"{name}"] = data_reading.data_parsing(spe, path_stelum, path_pulse) #returns {"stelum":{},"pulse":{}} dict of dict
            #might be some huge overhead but we'll see, with the lenght of the files
            #I'm concerned about the .eig in particular...


    except Exception as e: ##just for me during debugging
        import traceback
        print("Error:", e)
        traceback.print_exc()
        raise(dash.exceptions.PreventUpdate)


@callback(
    Output("dropdown-x","options"),
    Output("dropdown-y","options"),
    Output("dropdown-x","value"),
    Output("dropdown-y","value"),
    Output("store-dropdown-values","data"),
    Input("store-displayed","data"),
    Input("store-active-tab","data"),
    State("dropdown-x","value"),
    State("dropdown-y","value"),
    State("dropdown-x","options"),
    State("dropdown-y","options"),
    State("store-dropdown-values","data"),
)
def main_update_func(store_displayed, store_active_tab, value_x, value_y, options_x, options_y, store_dropdown_values):

    tab = store_active_tab["active_tab"]
    prev_tab = store_active_tab["previous_tab"]

    if store_dropdown_values is None:
        store_dropdown_values = {"stelum": ["lq","n"], "pulse": ["Reduced_Pad","Reduced_Pspacing"]}

    if ctx.triggered_id == "store-active-tab": #this changes the dropdown only on tab change + allows keeping the values of dropdown in between tab changes

        if tab == "stelum":
            store_dropdown_values[prev_tab] = [value_x, value_y] #store the values for next time
            options_x = [{"label": f"{value}", 'value': f"{value}"} for value in stelum_dropdown_options]
            options_y = options_x
            value_x = store_dropdown_values[tab][0] #update the tab values with the previous ones
            value_y = store_dropdown_values[tab][1] #basically this allows a type of persistence

        elif tab == "pulse":
            store_dropdown_values[prev_tab] = [value_x, value_y]
            options_x = [{"label": f"{value}", 'value': f"{value}"} for value in pulse_dropdown_options]
            options_y = options_x
            value_x = store_dropdown_values[tab][0]
            value_y = store_dropdown_values[tab][1]

    return(options_x, options_y, value_x, value_y, store_dropdown_values)


layout = html.Div(
    id="dashboard",
    style={
        "display": "flex",
        "flexDirection": "column",
        "width": "100vw",
        "height": "100vh"
    },
    children=[
        html.Div(
            id="page",
            style={
                "width": "calc(100% - 5rem)",
                "height": "100%",
                "marginLeft": "auto",
                "display": "flex",
                "flexDirection": "row"
            },
            children=[
                html.Div(
                    id="left",
                    style={
                        "width": "45%",
                        "height": "100%",
                        "display": "flex",
                        "flexDirection": "column"
                    },
                    children=[
                        html.Div(
                            id="header-container",
                            style={
                                "width": "100%",
                                "height": "20%",
                                "display": "flex",
                                "flexDirection": "column",
                                "alignItems": "center",
                                "justifyContent": "center",
                            },
                            children=[
                                html.Div(
                                    id="tab-container",
                                    style={"height":"6.5vh","width":"100%","display":"flex","flexDirection":"row","marginTop":"0.5vh"},
                                    children=[
                                        dbc.Button("STELUM", id={"type":"tab-choosing", "group": 1, "name":"btn-stelum"}, className="btn-tab", style={"height":"100%","width":"33.3%"}),
                                        dbc.Button("PULSE", id={"type":"tab-choosing", "group": 1, "name":"btn-pulse"}, className="btn-tab", style={"height":"100%","width":"33.3%"}),
                                        dbc.Button("EIG", id={"type":"tab-choosing", "group": 1, "name":"btn-eig"}, className="btn-tab", style={"height":"100%","width":"33.3%"}),
                                    ],
                                ),
                                html.Hr(style={"width": "100%","marginBottom":"2vh","marginTop":"0"}),
                                dbc.Input(id="output-path", placeholder="Absolute path towards an output folder", type="text", style={"height": "5vh", "width": "80%", "marginBottom": "0.5vh"}),
                                dbc.Input(id="fig-name", placeholder="Figure name (not including .extension)", type="text", style={"height": "5vh", "width": "80%"})
                            ]
                        ),
                        html.Div(
                            id="add-remove-graph-container",
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
                                        dcc.Dropdown(id="dropdown-x", options=[{"label": "placeholder", 'value': "placeholder"}], style={"height": "100%", "width": "98%", "marginLeft": "1%", "marginRight": "1%"},value="placeholder",clearable=False,persistence=True,persistence_type="session"),
                                        dcc.Dropdown(id="dropdown-y", options=[{"label": "placeholder", 'value': "placeholder"}], style={"height": "100%", "width": "98%", "marginRight": "2%"},value="placeholder",clearable=False,persistence=True,persistence_type="session")
                                    ]
                                ),
                                html.Div(
                                    style={"width": "33.3%", "height": "100%", "display": "flex", "flexDirection": "column"},
                                    children=[
                                        dbc.Button("Add", id="btn-add-graph", className="btn-add", style={"width": "98%", "height": "49%", "marginBottom": "2%", "marginRight": "2%"}),
                                        dbc.Button("Remove", id="btn-remove-graph", className="btn-remove", style={"width": "98%", "height": "49%", "marginRight": "2%"})
                                    ]
                                )
                            ]
                        ),
                        html.Hr(style={"width": "100%"}),
                        html.Div(
                            id="axes-range-container",
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
                                                dbc.Input(id="x-range", placeholder="ex: [-1,15.6]", style={"height": "100%", "width": "22%", "marginRight": "5%"}),
                                                html.Span("x_scale: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dcc.RadioItems(
                                                        id="x-scale",
                                                        options=[
                                                            {"label": "Linear", "value": "linear"},
                                                            {"label": "Logarithmic", "value": "log"},
                                                        ],
                                                        value="linear",
                                                        labelStyle={"display": "block"},
                                                        style={"marginRight":"2vw","fontSize":"2vh"}
                                                    ),
                                                html.Span("reversed: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Checkbox(id="x-reversed", value=False),
                                            ]
                                        ),
                                        html.Div(
                                            style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "flex-start"},
                                            children=[
                                                html.Span("y_range: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Input(id="y-range", placeholder="ex: [2,1e6]", style={"height": "100%", "width": "22%", "marginRight": "5%"}),
                                                html.Span("y_scale: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dcc.RadioItems(
                                                        id="y-scale",
                                                        options=[
                                                            {"label": "Linear", "value": "linear"},
                                                            {"label": "Logarithmic", "value": "log"},
                                                        ],
                                                        value="linear",
                                                        labelStyle={"display": "block"},
                                                        style={"marginRight":"2vw","fontSize":"2vh"}
                                                    ),
                                                html.Span("reversed: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Checkbox(id="y-reversed", value=False),
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            id="axes-label-container",
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
                                                dbc.Input(id="x-label", placeholder="X(He)_{core}", style={"height": "100%", "width": "35%", "marginRight": "5%"}),
                                                html.Span("y_label: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                                dbc.Input(id="y-label", placeholder="latex works on SAVE", style={"height": "100%", "width": "35%", "marginRight": "5%"})
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Hr(style={"width": "100%"}),
                        html.Div(
                            id="graph-args",
                            style={"height":"20%","width":"100%","display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center","marginBottom":"1vh","marginTop":"1vh"},
                            children=[
                                 html.Span("Graph args: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                                 dbc.Input(id="graph-label", placeholder="[name1:[args1],name2:[args2]..]", style={"height": "100%", "width": "85%"}),
                            ]
                        ),
                        html.Div(
                            id="graph-args-exemple",
                            style={"height":"20%","width":"100%","display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center","marginBottom":"1vh","marginTop":"1vh"},
                            children = [html.Span("Input example: [4G_R005-core_he_0.01:[label=X, color=rgba(255, 0, 0, 1), linestyle=dashed...]]", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"})]
                        ),
                        html.Div(
                            id="graph-color-picker",
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
                                            id="color-picker",
                                            format="rgba",
                                            value="rgba(255, 0, 0, 1)",
                                            size="sm",
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id="selected-color",
                                    style={"marginTop": "1vh", "fontSize": "2vh", "fontWeight": "bold"}
                                )
                            ]
                            )]
                        )
                    ]
                ),
                html.Div(
                    id="right",
                    style={"width": "55%", "height": "100%", "display": "flex", "flexDirection": "column"},
                    children=[
                        html.Div(
                            id="graph-container",
                            style={"width": "100%", "height": "70vh", "display": "flex"}, #have to force the 70vh otherwise it bugs out sometimes, no clue why
                            children=[
                                dcc.Graph(id="right-side-graph", figure=fig1, style={"width": "100%", "height": "100%"}, responsive=True)
                            ]
                        ),
                        html.Div(
                            id="line-maker-container",
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
                                        dbc.Input(id="line-value", placeholder="value || name:column", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="line-limits", placeholder="limits - [x1,x2] or [y1,y2]", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dcc.RadioItems(
                                                id="line-direction",
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
                                        dbc.Input(id="line-width", placeholder="linewidth (plt)", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="line-style", placeholder="linestyle (plt)", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="line-label", placeholder="line label", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="line-color", placeholder="rgba color", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                    ]
                                ),
                                html.Div(
                                    style={"width":"30%","height":"100%","display":"flex","alignItems":"center","justifyContent":"center","flexDirection":"column"},
                                    children=[
                                        dbc.Button("Add", id="btn-add-line", className="btn-add", style={"width": "80%", "height": "30%","marginBottom":"1vh"}),
                                        dbc.Button("Remove", id="btn-remove-line", className="btn-remove", style={"width": "80%", "height": "30%"})
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
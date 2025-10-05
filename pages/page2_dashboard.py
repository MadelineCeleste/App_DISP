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
import plotly.graph_objects as go

import logging
logging.basicConfig(level=logging.DEBUG)

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

name_options = ["names"]

@callback(
    Output("selected-color", "children"),
    Input("color-picker", "value"),
)
def pick(color):
    color = color.lstrip("#")
    r, g, b = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
    rgba = f"rgba({r}, {g}, {b}, 1)"
    return html.Span(rgba, className="subtitles-config", style={"fontSize": "2vh"})

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
    Output("dropdown-graph-container", "children"),
    Input("store-datatable-data","data"),#triggers on adding new models or changing display to "yes"
)
def store_file_data(store_datatable_data):

    datatable = copy.deepcopy(store_datatable_data) #this is ABSOLUTELY NECESSARY
    #but you know the fun thing ? I HAVE NO CLUE WHY
    #otherwise it triggers a callback loop between page1 and 2 on display edit, and I'm way too tired to understand why imma be honest
    #that's an #onlyDashthings if I've ever seen one holy smokes

    dict_structure = {key:[] for key in (name_options + stelum_dropdown_options + pulse_dropdown_options)}

    try: #so, dash convert numpy arrays to list when they are parsed in to a dcc.Store
        #because it serializes in JSON, so, yeah that's happening...
        display = np.array(datatable["table_data"]["display"])

        display_indexes = np.where(display != "no")[0] #in case of misstypes I guess ?

        names = np.array(datatable["names"])[display_indexes]
        spes = np.array(datatable["spe"])[display_indexes]
        path_stelums = np.array(datatable["stelum_paths"])[display_indexes]
        path_pulses = np.array(datatable["pulse_paths"])[display_indexes]

        for name, spe, path_stelum, path_pulse in zip(names, spes, path_stelums, path_pulses):

            data_dict = data_reading.data_parsing(spe, path_stelum, path_pulse) #returns {"stelum":{},"pulse":{}} dict of dict
            dict_structure["names"].append(name)
            stelum_keys, pulse_keys = list(data_dict["stelum"].keys()), list(data_dict["pulse"].keys())
            #might be some huge overhead but we'll see, with the lenght of the files
            #I'm concerned about the .eig in particular...

            for key in stelum_keys:
                dict_structure[key].append(data_dict["stelum"][key])

            pulse_data = {key:[] for key in pulse_dropdown_options} 
            #so, I should just change how the data_parsing work, but I ain't gonna lie, I don't have this type of time right now
            #This will do, even though it hurts me in some harsh type of ways
            for key in pulse_keys:
                sub_keys = list(data_dict["pulse"][key])
                for sub_key in sub_keys:
                    if sub_key in pulse_dropdown_options:
                        pulse_data[sub_key].append(data_dict["pulse"][key][sub_key])

            for key in pulse_dropdown_options:
                dict_structure[key].append(pulse_data[key])

        dropdown_children = [dcc.Dropdown(id="dropdown-graph", options=[{"label": name, 'value': name} for name in names], style={"height": "75%", "width": "80%"},value=names[0],clearable=False,persistence=True,persistence_type="session")]

        return(copy.deepcopy(dict_structure), dropdown_children)

    except Exception as e: ##just for me during debugging
        import traceback
        print("Error:", e)
        traceback.print_exc()
        raise(dash.exceptions.PreventUpdate)


@callback( #changes children on page-change (well, tab change, but you get it)
    Output("dropdown-div","children"),
    Output("store-dropdown-values","data"),
    Input("store-active-tab","data"),
    State("dropdown-x","value"),
    State("dropdown-y","value"),
    State("store-dropdown-values","data"),
    prevent_initial_call=True
)
def updates_on_tab_change(store_active_tab, value_x, value_y, store_dropdown_values):

    tab = store_active_tab["active_tab"]
    prev_tab = store_active_tab["previous_tab"]
    
    if store_dropdown_values is None:
        store_dropdown_values = {"stelum": ["lq","n"], "pulse": ["Reduced_Pad","Reduced_Pspacing"]}
    
    store_dropdown_values[prev_tab] = [value_x, value_y]
    
    ### memory of graph dropdown are kept here
    if tab == "stelum":
        dropdown_children = html.Div(children=[
            dcc.Dropdown(id="dropdown-x", options=[{"label": f"{value}", 'value': f"{value}"} for value in stelum_dropdown_options], 
                        style={"height": "100%", "width": "98%", "marginLeft": "1%", "marginRight": "1%"},
                        value=store_dropdown_values[tab][0], clearable=False),
            dcc.Dropdown(id="dropdown-y", options=[{"label": f"{value}", 'value': f"{value}"} for value in stelum_dropdown_options], 
                        style={"height": "100%", "width": "98%", "marginRight": "2%"},
                        value=store_dropdown_values[tab][1], clearable=False)
        ], id=f"dropdown-wrapper-{tab}", style={"width": "100%", "height": "100%", "display": "flex", "flexDirection": "row"})
    elif tab == "pulse":
        dropdown_children = html.Div(children=[
            dcc.Dropdown(id="dropdown-x", options=[{"label": f"{value}", 'value': f"{value}"} for value in pulse_dropdown_options], 
                        style={"height": "100%", "width": "98%", "marginLeft": "1%", "marginRight": "1%"},
                        value=store_dropdown_values[tab][0], clearable=False),
            dcc.Dropdown(id="dropdown-y", options=[{"label": f"{value}", 'value': f"{value}"} for value in pulse_dropdown_options], 
                        style={"height": "100%", "width": "98%", "marginRight": "2%"},
                        value=store_dropdown_values[tab][1], clearable=False)
        ], id=f"dropdown-wrapper-{tab}", style={"width": "100%", "height": "100%", "display": "flex", "flexDirection": "row"})

    return dropdown_children, store_dropdown_values

def update_children_graph(x_range, y_range, x_scale, y_scale, x_reversed, y_reversed, x_label, y_label):

    if x_reversed == True:
        x_range = x_range[::-1]
    if y_reversed == True:
        y_range = y_range[::-1]

    #yes this can be done in comprehension
    #yes I'm just trying my hand at lambda functions, which turns out, is simple
    if x_scale == "log":
        x_range = list(map(lambda x: np.round(10**x,2), x_range))
    else:
        x_range = list(map(lambda x: np.round(x,2), x_range))

    if y_scale == "log":
        y_range = list(map(lambda x: np.round(10**x,2), y_range))
    else:
        y_range = list(map(lambda x: np.round(x,2), y_range))

    label_container = [html.Div(style={"height": "100%", "width": "20%", "display": "flex", "alignItems": "center", "justifyContent": "center","marginRight":"1vw"}, 
                    children=[html.Span("Axes labels: ", className="subtitles-config", style={"fontSize": "2vh"})]),
            html.Div(
                style={"height": "100%", "width": "80%", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"},
                children=[
                    html.Div(
                        style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "flex-start", "marginBottom": "0.5vh"},
                        children=[
                            html.Span("x_label: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                            dbc.Input(id="x-label", placeholder="X(He)_{core}", value=x_label, style={"height": "100%", "width": "35%", "marginRight": "5%"}),
                            html.Span("y_label: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                            dbc.Input(id="y-label", placeholder="latex for save graph", value=y_label, style={"height": "100%", "width": "35%", "marginRight": "5%"})
                        ]
                    )
                ]
            )]

    range_container = [html.Div(style={"height": "100%", "width": "20%", "display": "flex", "alignItems": "center", "justifyContent": "center", "marginRight":"1vw"}, 
        children=[html.Span("Axes ranges|scale: ", className="subtitles-config", style={"fontSize": "2vh"})]),
        html.Div(
            style={"height": "100%", "width": "80%", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"},
            children=[
                html.Div(
                    style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "flex-start", "marginBottom": "0.5vh"},
                    children=[
                        html.Span("x_range: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                        dbc.Input(id="x-range", placeholder="-1,15.6", value = ",".join(map(str, x_range)), style={"height": "100%", "width": "22%", "marginRight": "5%"}),
                        html.Span("x_scale: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                        dcc.RadioItems(
                                id="x-scale",
                                options=[
                                    {"label": "Linear", "value": "linear"},
                                    {"label": "Logarithmic", "value": "log"},
                                ],
                                value=x_scale,
                                labelStyle={"display": "block"},
                                style={"marginRight":"2vw","fontSize":"2vh"}
                            ),
                        html.Span("reversed: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                        dbc.Checkbox(id="x-reversed", value=x_reversed),
                    ]
                ),
                html.Div(
                    style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "row", "alignItems": "center", "justifyContent": "flex-start"},
                    children=[
                        html.Span("y_range: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                        dbc.Input(id="y-range", placeholder="2,1e6", value= ",".join(map(str, y_range)), style={"height": "100%", "width": "22%", "marginRight": "5%"}),
                        html.Span("y_scale: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                        dcc.RadioItems(
                                id="y-scale",
                                options=[
                                    {"label": "Linear", "value": "linear"},
                                    {"label": "Logarithmic", "value": "log"},
                                ],
                                value=y_scale,
                                labelStyle={"display": "block"},
                                style={"marginRight":"2vw","fontSize":"2vh"}
                            ),
                        html.Span("reversed: ", className="subtitles-config", style={"fontSize": "2vh", "marginRight": "1%"}),
                        dbc.Checkbox(id="y-reversed", value=y_reversed),
                    ]
                )
            ]
        )]
    
    return(label_container, range_container)

@callback(
    Output("axes-label-container","children"),
    Output("axes-range-container","children"),
    Input("dropdown-x","value"),
    Input("dropdown-y", "value"),
    State("store-graph-options","data")
)
def memory_dropdown_key_state(value_x, value_y, store_graph_options):

    try:
        sub_store_graph_options = store_graph_options[f"{value_x}_{value_y}"]
        label_container, range_container = update_children_graph(*sub_store_graph_options)
    except Exception as e: ##just for me during debugging
        import traceback
        print("Error:", e)
        traceback.print_exc()

        sub_store_graph_options = ['', '', 'linear', 'linear', False, False, '', '']
        label_container, range_container = update_children_graph(*sub_store_graph_options)

    return(label_container, range_container)

def update_children_left_footer(linewidth, linestyle, model_label, color, markers, marker_size, marker_style, marker_color, model_name):
    
    left_footer_children = [
        html.Div(
            id="graph-option-container",
            key=f"graph-option-container-{model_name}",
            style={"height":"100%","width":"33.3%","display":"flex","flexDirection":"column","alignItems":"center","justifyContent":"center"},
            children=[
                dbc.Input(id="graph-width", key=f"graph-width-{model_name}", placeholder="linewidth", value=linewidth, persistence=False, style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                dbc.Input(id="graph-style", key=f"graph-style-{model_name}", placeholder="linestyle", value=linestyle, persistence=False, style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                dbc.Input(id="graph-label", key=f"graph-label-{model_name}", placeholder="label", value=model_label, persistence=False, style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                dbc.Input(id="graph-color", key=f"graph-color-{model_name}", placeholder="rgba color (or preset)", value=color, persistence=False, style={"height": "15%", "width": "80%"}),
            ]
        ),
        html.Div(
            id="markers-options-container",
            key=f"markers-options-container-{model_name}",
            style={"height":"100%","width":"33.3%","display":"flex","flexDirection":"column","alignItems":"center","justifyContent":"center"},
            children=[
                html.Div(style={"display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center", "height":"15%"},
                    children=[
                        html.Span("markers: ", className="subtitles-config", style={"fontSize": "2vh","marginRight": "10%", "marginBottom":"0.5vh"}),
                        dbc.Checkbox(id="markers", value=markers, persistence=False)
                    ]),
                dbc.Input(id="marker-size", key=f"marker-size-{model_name}", placeholder="marker size", value=marker_size, persistence=False, style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                dbc.Input(id="marker-style", key=f"marker-style-{model_name}", placeholder="marker style", value=marker_style, persistence=False, style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                dbc.Input(id="marker-color", key=f"marker-color-{model_name}", placeholder="rgba color (or preset)", value=marker_color, persistence=False, style={"height": "15%", "width": "80%"}),
            ]
        ),
        html.Div(
            id="color-picker-container",
            style={"height":"100%","width":"33.3%","display":"flex","flexDirection":"column","alignItems":"center","justifyContent":"center"},
            children=[
                dbc.InputGroup(style={"width":"80%"},
                    children = [
                        dbc.InputGroupText("Click to pick a color", style={
                                                                        "textAlign": "center",
                                                                        "display": "flex",
                                                                        "alignItems": "center",
                                                                        "justifyContent": "center",
                                                                        "width": "100%",
                                                                        "color":"white",
                                                                        "marginBottom":"1vh",
                                                                        "fontSize":"2vh"
                                                                    },),
                        dbc.Input(type="color", id="color-picker", value="#ff0000",style={"height":"5vh"}),
                    ]
                ),
                html.Div(
                    id="selected-color",
                    style={"marginTop": "1vh", "fontSize": "2vh", "fontWeight": "bold"}
                )
            ]
        )
    ]
    
    return left_footer_children


@callback(
    Output("left-footer-container", "children"),
    Input("dropdown-graph", "value"),
    State("store-graph-options", "data"),
    State("store-active-tab", "data"),
)
def memory_dropdown_name_model(name, store_graph_options, store_active_tab):
    sub_store_graph_options = store_graph_options[f"{name}_{store_active_tab['active_tab']}"]
    left_footer_children = update_children_left_footer(*sub_store_graph_options, model_name=name)
    
    #here you might say "hey wait, why's that guy building the WHOLE left footer children ?"
    #well, it's because otherwise the dbc.Input menu flickers du to the not amazing way Reacts handle those components
    #so I trade a flicker on the color picker for an annoying flicker on the whole footer
    #not mentionning the fact that it retained previous input value if I didn't rebuild the whole thing
    #anyways, only Dash things I guess

    return left_footer_children


@callback(
    Output("right-side-graph","figure"),
    Output("store-graph-options","data"),
    Input("store-displayed","data"),
    Input("x-range","value"),
    Input("y-range","value"),
    Input('x-scale',"value"),
    Input("y-scale","value"),
    Input("x-reversed","value"),
    Input("y-reversed","value"),
    Input("x-label","value"),
    Input("y-label","value"),
    Input("graph-width","value"),
    Input("graph-style","value"),
    Input("graph-label","value"),
    Input("graph-color","value"),
    Input("markers","value"),
    Input("marker-size","value"),
    Input("marker-style","value"),
    Input("marker-color","value"),
    State("store-active-tab","data"),
    State("store-graph-options","data"),
    State("dropdown-x","value"),
    State("dropdown-y","value"),
    State("dropdown-graph","value"),
    prevent_initial_call=True,
)
def update_graph(store_displayed, x_range, y_range, x_scale, y_scale, x_reversed, y_reversed, x_label, y_label, linewidth, linestyle, model_label, color, markers, marker_size, marker_style,  marker_color, store_active_tab, store_graph_options, value_x, value_y, dropdown_model_name):

    n_names = len(store_displayed["names"])
    active_tab = store_active_tab["active_tab"]
    
    if n_names > 0:

        names = store_displayed["names"]

        if store_graph_options is None:
            store_graph_options = {}

        if not store_graph_options.get(f"{value_x}_{value_y}"): #first time the specific key pair is used

            store_graph_options.update({f"{value_x}_{value_y}":[""]*8})
            #0:x_range, 1:y_range, 2:x_scale, 3:y_scale, 4:x_reversed, 5:y_reversed, 6:x_label, 7:y_label
            #associated to each given pair of dropdown values across stelum, pulse, eig
            #of course this supposes no pair are dupes, which should completely be the case

            #You might want to say "why is this absolute idiot not using a dictionnary", well, it's because you can't
            #it's not JSON serializable apparently, and so only the top most layer of dcc.Store can be a dictionnary
            #so I have to painfully suffer through lists of lists of lists

        parameters = [x_range, y_range, x_scale, y_scale, x_reversed, y_reversed, x_label, y_label]
        
        for i, parameter in enumerate(parameters):
            if (parameter is not None) and (parameter != ""):
                store_graph_options[f'{value_x}_{value_y}'][i] = parameter
            else:
                store_graph_options[f'{value_x}_{value_y}'][i] = ""

        x_values, y_values = [], []

        for i in range(n_names):
            x_values.append(store_displayed[value_x][i])
            y_values.append(store_displayed[value_y][i])

        store_graph_options[f'{value_x}_{value_y}'] = formatting_graph_options(store_graph_options[f'{value_x}_{value_y}'], x_values, y_values, value_x, value_y, active_tab)

        #This is deactivated for now but I'm terrified of a potential MEGA overhead
        #if someone leaves the apply open and does like 500 different combination of graphs, that thing is going to get real slow real quick...
        #And I don't really want to put a "cleanup" button in there do I ?
        #I guess it comes down to design choices all in all
        
        # keys = list(store_graph_options.keys())

        # for key in keys: #lil cleanups so that we don't get too much overhead if someone leave the program open for god knows how long
        #     #the thing is I'm not sure it's the best of ideas yet. It might be worth to keep the configs
        #     #because then we could quickly switch between what is displayed without config loss...
        #     #to think about honestly.
        #     splitted = key.split("_")
        #     if (splitted[0] not in stelum_dropdown_options) and ((splitted[0] not in pulse_dropdown_options)): #aka, one name, one key, another key
        #         name = "_".join(splitted[0:-2])
        #         if name not in names:
        #             del store_graph_options[key]

        for name in names: 
            #so, I initialize all the name in display, but of course, the parameters are only choosen for one name at a time
            #otherwise this is complete chaos obviously (it already is, do not look the callbacks graph in debug mode...)

            if not store_graph_options.get(f"{name}_{active_tab}"): #first time the specific trio name_key1_key2 is used

                store_graph_options.update({f"{name}_{active_tab}":['']*8})
                store_graph_options[f"{name}_{active_tab}"][4] = False #by default, no markers
                #0:linewidth, 1:linestyle, 2:model_label, 3:color, 4:markers, 5:marker_size, 6:marker_style, 7:marker_color

        parameters = [linewidth, linestyle, model_label, color, markers, marker_size, marker_style,  marker_color]

        for i, parameter in enumerate(parameters):

            if (parameter is not None) and (parameter != ""):
                store_graph_options[f"{dropdown_model_name}_{active_tab}"][i] = parameter
            else:
                store_graph_options[f"{dropdown_model_name}_{active_tab}"][i] = ''

        #just some light conversions so that we don't get errors update the graphs on the sizes
        if store_graph_options[f"{dropdown_model_name}_{active_tab}"][0] != '':
            store_graph_options[f"{dropdown_model_name}_{active_tab}"][0] = float(store_graph_options[f"{dropdown_model_name}_{active_tab}"][0])

        if store_graph_options[f"{dropdown_model_name}_{active_tab}"][5] != '':
            store_graph_options[f"{dropdown_model_name}_{active_tab}"][5] = float(store_graph_options[f"{dropdown_model_name}_{active_tab}"][5])

        if active_tab == "stelum":

            figure = updated_graph_stelum(store_graph_options, names, x_values, y_values, value_x, value_y)
            return(figure, store_graph_options)

    raise(dash.exceptions.PreventUpdate)

def formatting_graph_options(sub_store_graph_options, x_values, y_values, value_x, value_y, tab):

    x_range, y_range, x_scale, y_scale, x_reversed, y_reversed, x_label, y_label = sub_store_graph_options

    if x_label == "":
        sub_store_graph_options[6] = value_x
    if y_label == "":
        sub_store_graph_options[7] = value_y

    if tab == "stelum": #needed because not the same structure for pulse and stelum values

        if (x_range == "") or (y_range == ""): #avoid double iterations if both are ""

            min_x, max_x = np.min(x_values[0]), np.max(x_values[0])
            min_y, max_y = np.min(y_values[0]), np.max(y_values[0])

            range_x = [min_x,max_x]
            range_y = [min_y,max_y]

            for (x_value, y_value) in zip(x_values,y_values):

                min_x, max_x = np.min(x_value), np.max(x_value)
                min_y, max_y = np.min(y_value), np.max(y_value)

                #ew :(
                if min_x < range_x[0]:
                    range_x[0] = min_x
                if min_y < range_y[0]:
                    range_y[0] = min_y
                if max_x > range_x[1]:
                    range_x[1] = max_x
                if max_y < range_y[1]:
                    range_y[1] = min_y

        if (x_range != ""):

            ranges = x_range.split(",")
            range_x = [float(ranges[0]), float(ranges[1])]

        if (y_range != ""):

            ranges = y_range.split(",")
            range_y = [float(ranges[0]), float(ranges[1])]

        sub_store_graph_options[0] = range_x
        sub_store_graph_options[1] = range_y

        if x_reversed:
            sub_store_graph_options[0] = sub_store_graph_options[0][::-1]
        if y_reversed:
            sub_store_graph_options[1] = sub_store_graph_options[1][::-1]

        if x_scale == "log":
            sub_store_graph_options[0] = np.log10(np.array(sub_store_graph_options[0]))
        if y_scale == "log":
            sub_store_graph_options[1] = np.log10(np.array(sub_store_graph_options[1]))

    return(sub_store_graph_options)

def updated_graph_stelum(store_graph_options, names, x_values, y_values, value_x, value_y):

    sub_store_graph_options = store_graph_options[f"{value_x}_{value_y}"]

    fig = go.Figure()

    colors = ["blue","red","green","black","orange","purple"]

    #0:x_range, 1:y_range, 2:x_scale, 3:y_scale, 4:x_reversed, 5:y_reversed, 6:x_label, 7:y_label

    for i, name in enumerate(names):

        name_graph_options = store_graph_options[f"{name}_stelum"] #obligatory stelum, it's the func for it after all
        #0:linewidth, 1:linestyle, 2:model_label, 3:color, 4:markers, 5:marker_size, 6:marker_style, 7:marker_color

        #it's time to set all the defaults yiho
        params = [2,"solid",name,colors[i],"void",4,"circle",colors[i]]

        for j,param in enumerate(name_graph_options):
            if param != "":
                params[j] = name_graph_options[j]

        if (name_graph_options[7] == "") and (name_graph_options[3] != ""):
            #just a little something to ensure markers are of the same color of the graph if no color is specified :)
            params[7] = params[3]

        if name_graph_options[4] == False: #no markers

            fig.add_trace(go.Scatter(
            x=x_values[i],
            y=y_values[i],
            mode="lines",
            name=params[2],
            #ok but what are those parameters names ?
            #who calls the linestyle "dash" ????
            line=dict(color=params[3],
                      width=params[0],
                      dash=params[1])))
            
        else: #markers
            fig.add_trace(go.Scatter(
            x=x_values[i],
            y=y_values[i],
            mode="lines+markers",
            name=params[2],
            #ok but what are those parameters names ?
            #who calls the linestyle "dash" ????
            line=dict(color=params[3],
                      width=params[0],
                      dash=params[1]),
            marker=dict(
                symbol=params[6],
                size=params[5],
                color = params[7]
            )))

    fig.update_layout(
        font=dict(color="black"),
        legend=dict(
            xref='paper', yref='paper',  # default
            x=0.99, y=0.99,
            xanchor='right', yanchor='top',
            traceorder='normal'
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True, #force the legend to be displayed even with one trace here
        #I'd call plotly stupid for this not being default but oh well...
        xaxis=dict(
            showgrid=False,
            title=sub_store_graph_options[6],
            type=sub_store_graph_options[2],
            range=sub_store_graph_options[0]
        ),
        yaxis=dict(
            showgrid=False,
            title=sub_store_graph_options[7],
            type=sub_store_graph_options[3],
            range=sub_store_graph_options[1]
        )
        )

    return(fig)


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
                                html.Div(id="dropdown-div",
                                    style={"width": "66.6%", "height": "100%", "display": "flex", "flexDirection": "row"},
                                    children=[
                                        html.Div(children=[
                                        dcc.Dropdown(id="dropdown-x", options=[{"label": "Reduced_Pad", 'value': "Reduced_Pad"}], style={"height": "100%", "width": "98%", "marginLeft": "1%", "marginRight": "1%"},value="Reduced_Pad",clearable=False,persistence=True,persistence_type="session"),
                                        dcc.Dropdown(id="dropdown-y", options=[{"label": "Reduced_Pspacing", 'value': "Reduced_Pspacing"}], style={"height": "100%", "width": "98%", "marginRight": "2%"},value="Reduced_Pspacing",clearable=False,persistence=True,persistence_type="session")],style={"width": "100%", "height": "100%", "display": "flex", "flexDirection": "row"},)
                                    ]
                                ),
                                html.Div(
                                    style={"width": "33.3%", "height": "100%", "display": "flex", "flexDirection": "column"},
                                    children=[
                                        dbc.Button("Save Graph", id="btn-add-graph", className="btn-add", style={"width": "98%", "height": "49%", "marginRight": "2%"}),
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
                                                dbc.Input(id="x-range", placeholder="-1,15.6", style={"height": "100%", "width": "22%", "marginRight": "5%"}),
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
                                                dbc.Input(id="y-range", placeholder="2,1e6", style={"height": "100%", "width": "22%", "marginRight": "5%"}),
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
                                                dbc.Input(id="y-label", placeholder="latex for save graph", style={"height": "100%", "width": "35%", "marginRight": "5%"})
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Hr(style={"width": "100%"}),
                        html.Div(
                            id="dropdown-graph-container",
                            style={"height":"4vh","width":"100%","display":"flex","alignItems":"center","justifyContent":"center"},
                            children=[dcc.Dropdown(id="dropdown-graph", options=[{"label": "name", 'value': "name"}], style={"height": "75%", "width": "80%"},value="name",clearable=False,persistence=True,persistence_type="session"),]
                        ),
                        html.Div(
                            id="left-footer-container",
                            style={"height":"30vh","width":"100%", "display":"flex", "flexDirection":"row", "alignItems":"center","justifyContent":"center"},
                            children = [
                                html.Div(
                                    id="graph-option-container",
                                    style={"height":"100%","width":"33.3%","display":"flex","flexDirection":"column","alignItems":"center","justifyContent":"center"},
                                    children=[
                                        dbc.Input(id="graph-width", placeholder="linewidth", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="graph-style", placeholder="linestyle", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="graph-label", placeholder="label", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="graph-color", placeholder="rgba color (or preset)", style={"height": "15%", "width": "80%"}),
                                    ]
                                ),
                                html.Div(
                                    id="markers-options-container",
                                    style={"height":"100%","width":"33.3%","display":"flex","flexDirection":"column","alignItems":"center","justifyContent":"center"},
                                    children=[
                                        html.Div(style={"display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center", "height":"15%"},
                                            children=[
                                                html.Span("markers: ", className="subtitles-config", style={"fontSize": "2vh","marginRight": "10%", "marginBottom":"0.5vh"}),
                                                dbc.Checkbox(id="markers", value=False)]),
                                        dbc.Input(id="marker-size", placeholder="marker size", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="marker-style", placeholder="marker style", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="marker-color", placeholder="rgba color (or preset)", style={"height": "15%", "width": "80%"}),
                                    ]
                                ),
                                html.Div(
                                    id="color-picker-container",
                                    style={"height":"100%","width":"33.3%","display":"flex","flexDirection":"column","alignItems":"center","justifyContent":"center"},
                                    children=[
                                        dbc.InputGroup(style={"width":"80%"},
                                            children = [
                                                dbc.InputGroupText("Click to pick a color", style={
                                                                                                "textAlign": "center",
                                                                                                "display": "flex",
                                                                                                "alignItems": "center",
                                                                                                "justifyContent": "center",
                                                                                                "width": "100%",
                                                                                                "color":"white",
                                                                                                "marginBottom":"1vh",
                                                                                                "fontSize":"2vh"
                                                                                            },),
                                                dbc.Input(type="color", id="color-picker", value="#ff0000",style={"height":"5vh"}),
                                            ]
                                        ),
                                        html.Div(
                                            id="selected-color",
                                            style={"marginTop": "1vh", "fontSize": "2vh", "fontWeight": "bold"}
                                        )
                                    ]
                                )
                            ]
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
                                dcc.Graph(id="right-side-graph", figure=fig1, style={"width": "100%", "height": "100%"}, responsive=True, config={'scrollZoom':True})
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
                                        dbc.Input(id="line-limits", placeholder="limits - x1,x2 or y1,y2", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
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
                                        dbc.Input(id="line-width", placeholder="linewidth", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="line-style", placeholder="linestyle", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
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
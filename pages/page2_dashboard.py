from dash import html, callback, Input, Output, State, dcc, ALL, ctx
import dash
import dash_bootstrap_components as dbc
import dash_latex as dl
from pathlib import Path
import plotly.express as px
import dash_mantine_components as dmc
import numpy as np
from DISP import data_reading, custom_calc
from DISP.global_vars import data, graph_options
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
                'H','He','C','O','rhog',"L_1^2","L_2^2","L_3^2","L_4^2","N^2"]

custom_stelum_key = ["L_1^2","L_2^2","L_3^2","L_4^2","N^2"]

pulse_dropdown_options = ["Reduced_Pad","Reduced_Pspacing","Pad","Pspacing","L","K","Ekin", "Ckl","Kp","Kg","Kp+Kg"]

name_options = ["names"]

## for dropdown later ##
stelum_options = [{"label": f"{value}", 'value': f"{value}"} for value in stelum_dropdown_options]
pulse_options = [{"label": f"{value}", 'value': f"{value}"} for value in pulse_dropdown_options]

base_colors = {"colors":["#0000FF","#FF0000","#00FF00","#000000"]}
#init at -1 to account for the init "None" model going through
#AND for the init from the store-update-graph..
#I should change this system tbh, it's not good
mode_colors = ["#0000FF","#FF0000","#00FF00","#000000"]

@callback(
    Output({"type": "tab-choosing", "group": 1, "name": ALL}, "className"),
    Output("store-active-tab","data"),
    Input({"type": "tab-choosing", "group": 1, "name": ALL}, "n_clicks"),
    State("store-active-tab","data")
)
def header_value(n_clicks, store_active_tab):
    triggered = ctx.triggered_id #id of the button we clicked on

    if not triggered: #init at stelum
        triggered = {'group': 1, 'name': 'btn-stelum', 'type': 'tab-choosing'}

    if store_active_tab is None:
            store_active_tab = {"active_tab":"pulse", "previous_tab":"stelum"} #either stelum, pulse or eig

    clicked_name = triggered["name"]
    classnames = []
    for btn in ctx.outputs_list[0]:
        if btn["id"]["name"] == clicked_name:
            classnames.append("btn-choosen")
            store_active_tab["previous_tab"] = store_active_tab["active_tab"]
            store_active_tab["active_tab"] = clicked_name.split("-")[-1]
        else:
            classnames.append("btn-tab")

    return classnames, store_active_tab

@callback(
    Output("dropdown-graph","options"),
    Output("dropdown-graph-container","children"),
    Input("store-datatable-data","data") #triggers on adding new models or changing display to "yes"
)
def store_file_data(store_datatable_data):

    global data #only because dcc.Store is limited in storage :)
    #this is also because dcc.Store doesn't allow nested dicts, and that makes me a sad person
    #An actual good general rule is :
    # - If the dcc.Store isn't used as an Input anywhere, then turn it into a global instead !

    display = np.array(store_datatable_data["table_data"]["display"])
    display_indexes = np.where(display != "no")[0]
    #yeah, technically anything but "no" works, in case of misstypes ?

    names = np.array(store_datatable_data["names"])[display_indexes]
    spes = np.array(store_datatable_data["spe"])[display_indexes]
    path_stelums = np.array(store_datatable_data["stelum_paths"])[display_indexes]
    path_pulses = np.array(store_datatable_data["pulse_paths"])[display_indexes]

    for name, spe, path_stelum, path_pulse in zip(names, spes, path_stelums, path_pulses):

        name = str(name) #this is just for prints for myself, don't mind it

        if name not in list(data.keys()):
            data[name] = data_reading.data_parsing(spe, path_stelum, path_pulse)
            #str(name) to avoid the np.str, it's just cleaner on prints really...
            #SHOULD BE IN A POPEN ? or only disjoint the .eig I guess, which are the bottleneck here
            #there is now a dict of keys "stelum","pulse","eig" and key in data["names"][name]
            #so to access a quantity: data["names"][name]["stelum"][quantity]
            #which looks convoluted but I mean, it's the most handy I can get there

        stelum_keys, pulse_keys = list(data[name]["stelum"].keys()), list(data[name]["pulse"].keys())

        for key in custom_stelum_key:
            if key not in stelum_keys:
                if key == "N^2":
                    data[name]["stelum"].update({key:custom_calc.brunt_vaisala_freq(data[name]["stelum"])})
                #yes yes I know, I'm just lazy here
                elif key == "L_1^2":
                    data[name]["stelum"].update({key:custom_calc.lamb_freq(data[name]["stelum"],1)})
                elif key == "L_2^2":
                    data[name]["stelum"].update({key:custom_calc.lamb_freq(data[name]["stelum"],2)})
                elif key == "L_3^2":
                    data[name]["stelum"].update({key:custom_calc.lamb_freq(data[name]["stelum"],3)})
                elif key == "L_4^2":
                    data[name]["stelum"].update({key:custom_calc.lamb_freq(data[name]["stelum"],4)})

    dropdown_options = [{"label": name, 'value': name} for name in names]

    if len(names) == 1:#init

        dropdown_children = [dcc.Dropdown(id="dropdown-graph", options=dropdown_options, style={"height": "75%", "width": "80%"},value=names[0],clearable=False,persistence=True,persistence_type="session")]

        return(dash.no_update, dropdown_children)

    return(dropdown_options, dash.no_update)

@callback(
    Output("store-line-data","data"),
    Input("btn-add-line","n_clicks"),
    Input("btn-remove-line","n_clicks"),
    State("line-value","value"),
    State("line-limits","value"),
    State("line-direction","value"),
    State("line-width","value"),
    State("line-style","value"),
    State("line-label","value"),
    State("line-color","value"),
    State("dropdown-x","value"),
    State("dropdown-y","value"),
    State("store-line-data","data"),
    State("store-datatable-data","data")
)
def update_line_information(click_add, click_remove, line_value, line_limits, line_direction, line_width, line_style, line_label, line_color, value_x, value_y, store_line_data, store_datatable_data):

    if store_line_data is None:
        store_line_data = {"line_value":[],"line_limits":[],"line_direction":[],"line_style":[], "line_width":[], "line_label":[],"line_color":[], "line_number":0,"line_key":[],"line_dropdown":[]}

    if ctx.triggered_id == "btn-add-line":

        if (line_label is None) or (line_label == ""):
                #so, this is not optimal because it's shared between all graphs
                #but I mean the line_label should never be empty anyways, that's just bad practise to not label those by default
                #hmm, I'd like to have a way to just change the lines even after they're added, but I'm not sure how to do all that
                #I'll think about it later, first, do the easy things...
                line_label = f"line_{store_line_data["line_number"]}"
                store_line_data["line_number"] += 1

        if line_direction == "x":
            line_key = f"{line_direction}_{value_x}_{line_label}"
            store_line_data["line_dropdown"].append(value_x)
        else:
            line_key = f"{line_direction}_{value_y}_{line_label}"
            store_line_data["line_dropdown"].append(value_y)

        line_keys = np.array(store_line_data["line_key"])
        key_index = np.where(line_keys == line_key)[0]

        if len(key_index) == 0:

            if (line_value is None) or (line_value == ""):
                line_value = 0
            else:
                try:
                    line_value = float(line_value)
                except:
                    string_value = line_value.split(":")
                    names = np.array(store_datatable_data["names"])
                    index = np.where(names == string_value[0])[0][0]
                    line_value = float(store_datatable_data["table_data"][string_value[1]][index])

            if (line_style is None) or (line_style == ""):
                line_style = "dash"
            if (line_color is None) or (line_color == ""):
                line_color = "red"
            if (line_width is None) or (line_width == ""):
                line_width = 2
            else:
                line_width = float(line_width)

            if (line_limits is not None) and line_limits != "":
                line_limits = list(map(float, line_limits.split(",")))
            else:
                line_limits = "auto"

            store_line_data["line_value"].append(line_value)
            store_line_data["line_limits"].append(line_limits)
            store_line_data["line_direction"].append(line_direction)
            store_line_data["line_style"].append(line_style)
            store_line_data["line_width"].append(line_width)
            store_line_data["line_color"].append(line_color)
            store_line_data["line_label"].append(line_label)
            store_line_data["line_key"].append(line_key)

        else:
            raise dash.exceptions.PreventUpdate

    if ctx.triggered_id == "btn-remove-line":

        if line_direction == "x":
            line_key = f"{line_direction}_{value_x}_{line_label}"
        else:
            line_key = f"{line_direction}_{value_y}_{line_label}"

        line_keys = np.array(store_line_data["line_key"])
        key_index = np.where(line_keys == line_key)[0]

        if len(key_index) == 1:#there should only be ONE of each keys anyways, otherwise it's weird
            for key in list(store_line_data.keys()):
                if key != "line_number":#this feels stupid; maybe line_number should be a local variable in the file, not in the dcc.Store ?
                    del(store_line_data[key][key_index[0]])
        else:
            raise dash.exceptions.PreventUpdate

    return(store_line_data)

@callback(
    Output("x-range","value"),
    Output("y-range","value"),
    Output('x-scale',"value"),
    Output("y-scale","value"),
    Output("x-reversed","value"),
    Output("y-reversed","value"),
    Output("x-label","value"),
    Output("y-label","value"),
    Input("dropdown-x","value"),
    Input("dropdown-y","value"),
    Input("store-active-tab-graph","data"), #this is because this callback needs to trigger AFTER the tab change, not before
)
def memory_imprint_graph(dropdown_x_value, dropdown_y_value, store_active_tab):

    global graph_options

    keys = ["ranges","scale","reversed_axis"]

    default = [None,"linear",False] #not filled Inputs, linear scale and not reversed

    if graph_options.get(f"{dropdown_x_value}_x"):
        x_range, x_scale, x_reversed = [graph_options[f"{dropdown_x_value}_x"][key] for key in keys]
        x_label = graph_options[f"{dropdown_x_value}_x"]["label"]
    else:
        graph_options[f"{dropdown_x_value}_x"] = {}
        graph_options[f"{dropdown_x_value}_x"].update({key:default_value for key, default_value in zip(keys, default)})
        graph_options[f"{dropdown_x_value}_x"].update({"label":dropdown_x_value})
        x_range, x_scale, x_reversed = default
        x_label = dropdown_x_value

    if graph_options.get(f"{dropdown_y_value}_y"):
        y_range, y_scale, y_reversed = [graph_options[f"{dropdown_y_value}_y"][key] for key in keys]
        y_label = graph_options[f"{dropdown_y_value}_y"]["label"]
    else:
        graph_options[f"{dropdown_y_value}_y"] = {}
        graph_options[f"{dropdown_y_value}_y"].update({key:default_value for key, default_value in zip(keys, default)})
        graph_options[f"{dropdown_y_value}_y"].update({"label":dropdown_y_value})
        y_range, y_scale, y_reversed = default
        y_label = dropdown_y_value

    return(x_range, y_range, x_scale, y_scale, x_reversed, y_reversed, x_label, y_label)

@callback(
    Output("graph-width","value"),
    Output("graph-style","value"),
    Output("graph-label","value"),
    Output("graph-color","value"),
    Output("marker-bind","value"),
    Output("markers","value"),
    Output("marker-size","value"),
    Output("marker-style","value"),
    Output("marker-color","value"),
    Output("displayed-modes","value"),
    Output("modes-color","value"),
    Input("dropdown-graph","value"),
    Input("store-active-tab-graph","data"), #this is because this callback needs to trigger AFTER the tab change, not before
    Input("dropdown-graph","options")
)
def memory_imprint_model(dropdown_graph_value, store_active_tab, dropdown_graph_options):

    #this function really ought to be shorter, lots of things are repeated I feel like...

    global graph_options

    active_tab = store_active_tab["active_tab"]
    common_keys = ["line_width","line_style","line_label","line_color","marker_bind"]
    self_keys = ["marker_enabled","marker_size","marker_style","marker_color"]
    mode_keys = ["mode_displayed","mode_color"]
    count_color = -1

    for option in dropdown_graph_options:
        name = option["label"]
        count_color += 1
        if name == dropdown_graph_value:
            if graph_options.get(name) and graph_options.get("active_tab"): #aka, if the tab has just been changed
                if graph_options["active_tab"] != active_tab:
                    if graph_options[name].get(active_tab): #if the active_tab dict is already there
                        #then we return the values associated to it directly
                        #overwise, we'll overwrite pulse values with stelum values, and so on
                        graph_options["active_tab"] = active_tab
                        marker_enabled, marker_size, marker_style, marker_color = [graph_options[name][active_tab][key] for key in self_keys]

                        return(dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, marker_enabled, marker_size, marker_style, marker_color, dash.no_update, dash.no_update)

            if graph_options.get(name):
                if graph_options[name].get("common"):
                    line_width, line_style, line_label, line_color, marker_bind = [graph_options[name]["common"][key] for key in common_keys]
                if graph_options[name].get(active_tab):
                    marker_enabled, marker_size, marker_style, marker_color = [graph_options[name][active_tab][key] for key in self_keys]
                else: #this is in case we change tabs, we need to init the dict according to it
                    graph_options[name][active_tab] = {"marker_enabled":False,
                                                    "marker_size":4,
                                                    "marker_style":"circle",
                                                    "marker_color":line_color}

                    if active_tab == "pulse":
                        graph_options[name][active_tab]["marker_enabled"] = True
                        graph_options[name][active_tab]["marker_size"] = 8

                marker_enabled, marker_size, marker_style, marker_color = [graph_options[name][active_tab][key] for key in self_keys]

                if graph_options[name].get("mode"):
                    mode_displayed, mode_colors = [graph_options[name]["mode"][key] for key in mode_keys]
            else:
                graph_options[name] = {"common":{}, active_tab:{}, "mode":{}}
                color = base_colors["colors"][count_color%len(base_colors["colors"])]
                graph_options[name]["common"] = {"line_width":2,
                                                "line_style":"solid",
                                                "line_label":name,
                                                "line_color":color,
                                                "marker_bind":True}
                line_width, line_style, line_label, line_color, marker_bind = [graph_options[name]["common"][key] for key in common_keys]
                
                graph_options[name][active_tab] = {"marker_enabled":False,
                                                "marker_size":4,
                                                "marker_style":"circle",
                                                "marker_color":graph_options[name]["common"]["line_color"]}
                marker_enabled, marker_size, marker_style, marker_color = [graph_options[name][active_tab][key] for key in self_keys]

                if graph_options[name]["mode"]:
                    mode_displayed, mode_colors = [graph_options[name]["mode"][key] for key in mode_keys]
                else:
                    graph_options[name]["mode"]["mode_displayed"] = '1,2'
                    graph_options[name]["mode"]["mode_color"] = 'blue;red'
                    mode_displayed, mode_colors = [graph_options[name]["mode"][key] for key in mode_keys]

                if active_tab == "pulse":
                    graph_options[name][active_tab]["marker_enabled"] = True
                    graph_options[name][active_tab]["marker_size"] = 8

            if marker_bind == True:
                graph_options[name][active_tab]["marker_color"] = graph_options[name]["common"]["line_color"]
                marker_color = line_color

            graph_options["active_tab"] = active_tab
        else:
            #here we HAVE to init the other graphs
            #otherwise it won't display correctly for multiple models from the get go
            #I'll look into making the func more readable later on
            if graph_options.get(name): #init if name exists
                for tab in ["stelum","pulse"]:
                    if not graph_options[name].get(tab):
                        graph_options[name][tab] = {"marker_enabled":False,
                                                            "marker_size":4,
                                                            "marker_style":"circle",
                                                            "marker_color":graph_options[name]["common"]["line_color"]}
                        if tab == "pulse":
                            graph_options[name][tab]["marker_enabled"] = True
                            graph_options[name][tab]["marker_size"] = 8

            else: #init if nothing exists
                graph_options[name] = {"common":{}, "stelum":{}, "pulse":{}, "mode":{}}
                color = base_colors["colors"][count_color%len(base_colors["colors"])]
                graph_options[name]["common"] = {"line_width":2,
                                                "line_style":"solid",
                                                "line_label":name,
                                                "line_color":color,
                                                "marker_bind":True}

                for tab in ["stelum","pulse"]:
                    graph_options[name][tab] = {"marker_enabled":False,
                                                    "marker_size":4,
                                                    "marker_style":"circle",
                                                    "marker_color":graph_options[name]["common"]["line_color"]}
                    if tab == "pulse":
                        graph_options[name][tab]["marker_enabled"] = True
                        graph_options[name][tab]["marker_size"] = 8

                graph_options[name]["mode"]["mode_displayed"] = '1,2'
                graph_options[name]["mode"]["mode_color"] = 'blue;red'

    if graph_options.get(None):#very first iterations cleanup, not very clean though
        del graph_options[None]
    if graph_options.get("name"):
        del graph_options["name"]

    return(line_width, line_style, line_label, line_color, marker_bind, marker_enabled, marker_size, marker_style, marker_color, mode_displayed, mode_colors)

def dropdown_creation(set_id, options, value):

    return(dcc.Dropdown(id=set_id, options=options,
                        style={"height": "100%", "width": "98%", "marginLeft": "1%", "marginRight": "1%"},
                        value=value, clearable=False))

@callback( #changes children on tab-change
           #this is just for the dropdown options !
    Output("dropdown-div","children"),
    Output("store-dropdown-values","data"),
    Output("displayed-modes","style"),
    Output("modes-color","style"),
    Output("graph-color-container","style"),
    Output("marker-color-container","style"),
    Output("marker-span-bind","style"),
    Output("marker-bind","style"),
    Output("store-active-tab-graph","data"),
    Input("store-active-tab","data"),
    Input("dropdown-graph","options"), #here to trigger on display change
    #otherwise if we're on pulse tab already, it won't remove the color thing
    State("dropdown-x","value"),
    State("dropdown-y","value"),
    State("store-dropdown-values","data"),
    
    prevent_initial_call=True
)
def updates_on_tab_change(store_active_tab, dropdown_graph_options, dropdown_x_value, dropdown_y_value, store_dropdown_values):

    n_models = len(dropdown_graph_options)

    active_tab = store_active_tab["active_tab"]
    previous_tab = store_active_tab["previous_tab"]

    #this store is our memory for tabs values
    if store_dropdown_values is None:
        store_dropdown_values = {"stelum":["lq","n"], "pulse":["Reduced_Pad","Reduced_Pspacing"]}

    if ctx.triggered_id == "store-active-tab": #this avoid accidentally switching tab if we're here because of dropdown-graph-options
        store_dropdown_values[previous_tab] = [dropdown_x_value, dropdown_y_value]

    x_id, y_id = "dropdown-x", "dropdown-y"

    style_modes = {"height": "15%", "width": "80%","marginBottom":"1vh","marginTop":"2vh","display":"none"}
    style_color = {"height": "15%", "width": "80%","marginBottom":"1vh","display":"none"}
    style_color_graph_maker = {"height":"5vh","width":"100%","display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center"}
    style_span = {"fontSize": "2vh","marginRight": "3%"}
    style_checkbox = {}

    if active_tab == "stelum":
        dropdown_x = dropdown_creation(x_id, stelum_options, store_dropdown_values[active_tab][0])
        dropdown_y = dropdown_creation(y_id, stelum_options, store_dropdown_values[active_tab][1])

    if active_tab == "pulse":
        dropdown_x = dropdown_creation(x_id, pulse_options, store_dropdown_values[active_tab][0])
        dropdown_y = dropdown_creation(y_id, pulse_options, store_dropdown_values[active_tab][1])
        
        style_modes["display"] = "block"
        if n_models < 2:
            style_color["display"] = "block"
            style_color_graph_maker["display"] = "none" #disabled colors else than mode colors
            style_span["display"] = "none"
            style_checkbox["display"] = "none"

    dropdown_children = html.Div(children=[
        dropdown_x,
        dropdown_y],
        id=f"dropdown-wrapper-{active_tab}", style={"width": "100%", "height": "100%", "display": "flex", "flexDirection": "row"})

    store_active_tab_graph = copy.deepcopy(store_active_tab)#used to order the callbacks
    #In reality this could be anything really, as long as it trigger the memory_imprint callbacks

    return(dropdown_children, store_dropdown_values, style_modes, style_color, style_color_graph_maker, style_color_graph_maker, style_span, style_checkbox, store_active_tab_graph)

def graph_update():

    global data, graph_options


def draw_graph(active_tab, dropdown_graph_options, store_line_data, dropdown_x_value, dropdown_y_value):

    global graph_options, data

    n_models = len(dropdown_graph_options)

    if n_models == 0:
        return(dash.no_update)

    #here we don't really have a choice, gotta use ifs to disjoint cases

    fig = go.Figure()

    def draw_func(data_x, data_y, *, line_label, line_color, line_width, line_style, marker_enabled, marker_color, marker_size, marker_style, marker_bind, **kwargs): #I'm learning so much about those unpacking operators :D

        if kwargs.get("mode_color"):
            line_color = kwargs["mode_color"]
            marker_color = kwargs["mode_color"]

        if kwargs.get("mode_displayed"):
            line_label = f"l{kwargs["mode_displayed"]} {line_label}"

        if marker_bind == True:
            marker_color = line_color

        trace_args = dict(
                x = data_x,
                y = data_y,
                mode = "lines",
                name = line_label,
                line = dict(
                    color = line_color,
                    width = line_width,
                    dash = line_style
                )
            )

        if marker_enabled == True:

            trace_args["mode"] = "lines+markers"
            trace_args["marker"] = dict(
                color = marker_color,
                size = marker_size,
                symbol = marker_style
            )

        return(trace_args)

    if active_tab == "stelum":
        #for stelum graph, it's simple, just parse in all the arguments really

        for option in dropdown_graph_options:

            name = option["label"]
            
            common_opt = graph_options[name]["common"]
            self_opt = graph_options[name][active_tab]

            data_x = data[name][active_tab][f"{dropdown_x_value}"]
            data_y = data[name][active_tab][f"{dropdown_y_value}"]

            trace_args = draw_func(data_x, data_y, **common_opt, **self_opt)
            fig.add_trace(go.Scatter(**trace_args))
            #I love those unpacking operators, it's so elegant :p

    if active_tab == "pulse":

        if n_models == 1:

            name = dropdown_graph_options[0]["label"]
            common_opt = graph_options[name]["common"]
            self_opt = graph_options[name][active_tab]

            mode_opt = graph_options[name]["mode"]
            mode_displayed = list(map(int,mode_opt["mode_displayed"].split(",")))
            mode_color = mode_opt["mode_color"].split(";")

            for i,mode in enumerate(mode_displayed):

                data_x = data[name][active_tab][mode][f"{dropdown_x_value}"]
                data_y = data[name][active_tab][mode][f"{dropdown_y_value}"]

                trace_args = draw_func(data_x, data_y, **common_opt, **self_opt, **{"mode_displayed":mode_displayed[i], "mode_color":mode_color[i]})
                fig.add_trace(go.Scatter(**trace_args))

        elif n_models > 1:

            for option in dropdown_graph_options:

                name = option["label"]
                
                common_opt = graph_options[name]["common"]
                self_opt = graph_options[name][active_tab]

                mode_opt = graph_options[name]["mode"]
                mode_displayed = int(mode_opt["mode_displayed"].split(",")[0])
                #by default always only show the first of mode_displayed

                data_x = data[name][active_tab][mode_displayed][f"{dropdown_x_value}"]
                data_y = data[name][active_tab][mode_displayed][f"{dropdown_y_value}"]

                trace_args = draw_func(data_x, data_y, **common_opt, **self_opt, mode_displayed=mode_displayed)
                fig.add_trace(go.Scatter(**trace_args))

    x_opt = graph_options[f"{dropdown_x_value}_x"]
    y_opt = graph_options[f"{dropdown_y_value}_y"]

    def build_axis(*, label, ranges, scale, reversed_axis):

        axis_dict = dict(
            showgrid = False,
            title = label,
            type = scale,
            showexponent = 'all',
            exponentformat = 'e',
            ticks = 'outside',
            ticklen = 6,
            tickwidth = 2,
        )

        if ranges == None or ranges == "":
            if reversed_axis == True:
                axis_dict["autorange"] = "reversed"
            else:
                axis_dict["autorange"] = True
        else:
            range_list = list(map(float,ranges.split(",")))
            if reversed_axis == True:
                range_list = axis_dict["range"][::-1]
            if scale == "log":
                range_list = list(map(np.log10,range_list))

            axis_dict["range"] = range_list
        
        return(axis_dict)

    fig.update_layout(
        font=dict(color="black"),
        legend=dict(
            xref="paper", yref="paper",
            x=0.99, y=0.99,
            xanchor="right", yanchor="top",
            traceorder="normal"
        ),
        margin = dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        xaxis = build_axis(**x_opt),
        yaxis = build_axis(**y_opt))

    return(fig)

@callback(
    Output("marker-color-container","children"),
    Input("store-graph-color","data"),
    State("dropdown-graph","value"),
    #so this is nitpicking, but if binding == True I want the marker color to match the line color indicator...
)
def matching_colors(store_graph_color, dropdown_graph_value):

    global graph_options

    if graph_options[dropdown_graph_value]["common"]["marker_bind"] == True:
        return([dbc.Input(type="color", id="marker-color", value=store_graph_color["color"],style={"height":"100%","width":"80%"}, debounce=True)])
    else:
        return(dash.no_update)


@callback(
    Output("right-side-graph","figure"),
    Output("store-graph-color","data"),
    ### Input from dcc.Inputs ###
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
    Input("marker-bind","value"),
    Input("displayed-modes","value"),
    Input("modes-color","value"),

    ### If Lines are added or removed ###
    Input("store-line-data","data"),

    # Those are necessary "State"
    # Because they are used as Input for memory imprints
    State("store-active-tab","data"),
    State("dropdown-x","value"),
    State("dropdown-y","value"),
    State("dropdown-graph","value"),
    State("dropdown-graph","options"),
)
def update_graph(x_range, y_range, x_scale, y_scale, x_reversed, y_reversed, x_label, y_label, line_width, line_style, line_label, line_color, marker_enabled, marker_size, marker_style, marker_color, marker_bind, mode_displayed, mode_color, store_line_data, store_active_tab, dropdown_x_value, dropdown_y_value, dropdown_graph_value,dropdown_graph_options):

    global data, graph_options
    #again here, better to use those than dcc.Store
    #Trust me, I've tried both :)
    #dcc.Store only leads to spaghetti code if not needed as Input trigger
    #also, those global variable are not "None" at init, which is very welcome

    line_width, marker_size = float(line_width), float(marker_size)

    names = list(data.keys())
    n_display = len(names)
    active_tab = store_active_tab["active_tab"]
    #checks if we're looking at stelum / pulse / eig

    if n_display > 0:
        #if there is at least one model to display

        #Below is not the init, the init is in the memory imprints
        #Instead, this is an update to the graph_options global var
        #Which triggers everytime an Input field changes

        #the way we do things for graph options, aka general graph parameters, is by keys for dropdown_menus
        #keys are of value "dropdown_value" + "x", and so are axes dependant
        graph_options.update({f"{dropdown_x_value}_x":{"ranges":x_range,"scale":x_scale,"reversed_axis":x_reversed,"label":x_label}})
        graph_options.update({f"{dropdown_y_value}_y":{"ranges":y_range,"scale":y_scale,"reversed_axis":y_reversed,"label":y_label}})
        #defaults are not set here yet, another good point for using globals is not caring that we have "None" values if they are there :)
        #(This really only concern x_range and y_range)

        #stores the parameters conserved between stelum, pulse and eig for a given name
        graph_options[dropdown_graph_value]["common"].update({"line_width": line_width,
                                                              "line_style": line_style,
                                                              "line_label": line_label,
                                                              "line_color": line_color,
                                                              "marker_bind": marker_bind})

        #And then, we update by tab, in which we set markers by default for PULSE:
        if (active_tab == "pulse") and not graph_options[f"{dropdown_graph_value}"].get(active_tab):
            marker_enabled = True

        graph_options[dropdown_graph_value][active_tab].update({"marker_enabled": marker_enabled,
                                                                  "marker_size": marker_size,
                                                                  "marker_style": marker_style,
                                                                  "marker_color": marker_color})
        
        if marker_bind == True:
            marker_color = line_color

        store_graph_color = {"color":line_color}#so... yeah
        #I just want the graph color of markers and line to be synched if marker_bind is true...

        graph_options[dropdown_graph_value]["mode"].update({"mode_displayed": mode_displayed,
                                                             "mode_color": mode_color})

        figure = draw_graph(active_tab, dropdown_graph_options, store_line_data, dropdown_x_value, dropdown_y_value)

        return(figure, store_graph_color)

    else:
        return(dash.no_update)


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
                                # html.Div(style={"height": "100%", "width": "20%", "display": "flex", "alignItems": "center", "justifyContent": "center", "marginRight":"1vw"},
                                #         children=[html.Span("Axes ranges|scale: ", className="subtitles-config", style={"fontSize": "2vh"})]),
                                html.Div(
                                    style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"},
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
                                # html.Div(style={"height": "100%", "width": "20%", "display": "flex", "alignItems": "center", "justifyContent": "center","marginRight":"1vw"},
                                #         children=[html.Span("Axes labels: ", className="subtitles-config", style={"fontSize": "2vh"})]),
                                html.Div(
                                    style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"},
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
                                        html.Div(id="graph-color-container",children=[dbc.Input(type="color", id="graph-color", value="#0000FF",style={"height":"100%","width":"80%"}, debounce=True)], style={"height":"5vh","width":"100%","display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center"})
                                    ]
                                ),
                                html.Div(
                                    id="markers-options-container",
                                    style={"height":"100%","width":"33.3%","display":"flex","flexDirection":"column","alignItems":"center","justifyContent":"center"},
                                    children=[
                                        html.Div(style={"display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center", "height":"15%"},
                                            children=[
                                                html.Div(style={"display":"flex", "flexDirection":"row","alignItems":"center","justifyContent":"center","width":"100%"},
                                                         children = [
                                                             html.Span("markers: ", className="subtitles-config", style={"fontSize": "2vh","marginRight": "3%"}),
                                                            dbc.Checkbox(id="markers", value=False,style={"marginRight":"10%"}),
                                                            html.Span("bind: ", id="marker-span-bind", className="subtitles-config", style={"fontSize": "2vh","marginRight": "3%"}),
                                                            dbc.Checkbox(id="marker-bind", value=True)
                                                            ]),
                                                         ]),
                                        dbc.Input(id="marker-size", placeholder="marker size", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        dbc.Input(id="marker-style", placeholder="marker style", style={"height": "15%", "width": "80%","marginBottom":"1vh"}),
                                        html.Div(id="marker-color-container",children=[dbc.Input(type="color", id="marker-color", value="#0000FF",style={"height":"100%","width":"80%"}, debounce=True)], style={"height":"5vh","width":"100%","display":"flex","flexDirection":"row","alignItems":"center","justifyContent":"center"})
                                    ]
                                ),
                                html.Div(
                                    id="color-picker-container",
                                    style={"height":"100%","width":"33.3%","display":"flex","flexDirection":"column","alignItems":"center","justifyContent":"center"},
                                    children=[
                                        dbc.Input(id="displayed-modes", placeholder="degrees - 1,2,3,4", style={"height": "15%", "width": "80%","marginBottom":"1vh","marginTop":"1vh","display":"none"}),
                                        dbc.Input(id="modes-color", placeholder="color - blue;red;rgca()..", style={"height": "15%", "width": "80%","marginBottom":"1vh","display":"none"}),
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
                                        dbc.Input(type="color", id="line-color", value="#ff0000",style={"height":"15%","width":"80%"}, debounce=True),
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
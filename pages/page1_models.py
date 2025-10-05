from dash import register_page, html, callback, Input, Output, State, dcc, MATCH, ALL, dash_table, ctx
import dash
import dash_bootstrap_components as dbc
import dash_latex as dl
import pathlib
import pandas as pd
import plotly.express as px
from DISP import data_reading
from collections import OrderedDict
import platform
import copy
import numpy as np

page_url = "/files"

df = px.data.iris()
table_columns = ["P (s)","Reduced P (s)", "Mode degree"]
periods = df["sepal_width"]
reduced_period = df["sepal_length"]
modes = ["void"]*len(periods)
degree_labels = ["l1","l2","void"]

df_freq = pd.DataFrame(OrderedDict([
    ('period', periods),
    ('reduced-period',reduced_period),
    ('degree',modes)]))

system_os = platform.system()

def dataTable_creation(store_datatable_data, table_data, names, spe, model_type, model_paths):


    spe_str = [f"{int(spe_list[0])}, {int(spe_list[1])}, {int(spe_list[2])}" for spe_list in spe]
    keys = list(table_data.keys())

    #['mass', 'lq_envl', 'lq_core', 'core_he', 'core_o', 'core_z', 'pf_envl', 'delta_core', 'lq_diff', 'diff_h', 'pf_diff', 'lq_flash', 'flash_c', 'pf_flash', 'conv_alpha', 'opc_metal', 'use_filters', 'lmin', 'lmax', 'period_scan', 'pmin', 'pmax', 'dp', 'frequency_scan', 'fmin', 'fmax', 'nf', 'nelems', 'compute_nad', 'mode_output', 'ad_filter', 'ad_highres']
    ## THIS IS ALL POSSIBLE KEYS
    kept_columns = ["mass","lq_envl","lq_core","core_he","pf_envl","delta_core","lq_diff","diff_h","pf_diff","lq_flash","flash_c","pf_flash","lmin","lmax"]
    retained_keys = []
    for key in keys:
        if key in kept_columns:
            retained_keys.append(key)

    types = [model_type]*len(table_data[retained_keys[0]])
    display = ["no"]*len(table_data[retained_keys[0]])

    if store_datatable_data["init"] == True:

        df_data = pd.DataFrame(OrderedDict({
        'name': names,
        'display': display,
        'spe': spe_str,
        'model-type': types,
        **{f'{key}': table_data[key] for key in retained_keys}
        }))

        store_datatable_data["table_data"] = {col: df_data[col] for col in df_data.columns}
        store_datatable_data["names"] = names
        store_datatable_data["stelum_paths"] = [str(p) for p in model_paths["STELUM"]]
        store_datatable_data["pulse_paths"] = [str(p) for p in model_paths["PULSE"]]
        store_datatable_data["eig_paths"] = [str(p) for p in model_paths["EIG"]]
        store_datatable_data["spe"] = spe
        store_datatable_data["model_type"] = types
        store_datatable_data["init"] = False

        # try: #useful debugging trick if we get the non-serializable error !
        #     json.dumps(store_datatable_data)
        #     print("Store data is JSON-serializable")
        # except Exception as e:
        #     print("Non-serializable detected:", e)

    else:

        df_new = pd.DataFrame(OrderedDict({
        'name': names,
        'display': display,
        'spe': spe_str,
        'model-type': types,
        **{f'{key}': table_data[key] for key in retained_keys}}))

        df_old = pd.DataFrame(store_datatable_data["table_data"])

        df_data = pd.concat([df_old, df_new], ignore_index=True)

        store_datatable_data["table_data"] = {col: df_data[col] for col in df_data.columns}
        store_datatable_data["names"].extend(names)
        store_datatable_data["stelum_paths"].extend([str(p) for p in model_paths["STELUM"]])
        store_datatable_data["pulse_paths"].extend([str(p) for p in model_paths["PULSE"]])
        store_datatable_data["eig_paths"].extend([str(p) for p in model_paths["EIG"]])
        store_datatable_data["spe"].extend(spe)
        store_datatable_data["model_type"].extend(types)

    children=[
        html.Div(
                id="datatable-wrapper-container",
                className="datatable-wrapper",
                children=[
                    dash_table.DataTable(
                    id='freq-table',
                    data=df_data.to_dict("records"),
                    filter_action="native",
                    sort_action="native",
                    style_table={
                        "overflowY": "hidden",
                        "height":"100%",
                        "width":"100%",
                        "backgroundColor": "rgba(0,0,0,0.25)",
                        "minHeight":"100%"
                    }, 
                    style_cell={
                        "backgroundColor": "rgba(0,0,0,0.25)",
                        "color": "white",
                        "fontFamily": "Arial, sans-serif",
                        "fontSize": "2vh",
                        "textAlign": "center",
                        "border": "1px solid rgba(255,255,255,0.1)",
                        "width":"10vw",
                        "maxwidth":"10vw",
                        "minwdith":"10vw",
                        "height":"3vh",
                    },
                    style_header={
                        "backgroundColor": "rgba(0,0,0,0.5)",
                        "fontWeight": "bold",
                        "color": "white",
                        "borderBottom": "2px solid rgba(255,255,255,0.3)",
                    },
                    style_data={
                        "backgroundColor": "rgba(0,0,0,0.25)",
                        "color": "white",
                    },
                    style_cell_conditional=[
                        {"if": {"column_id": "name"}, "width": "15vw"}],
                    fixed_rows={'headers': True},
                    page_action='none', #otherwise it puts pagination not scrolling :(
                    columns = [
                        {'id':'name', 'name':'Name','type': 'text','editable':False},
                        {'id':'display', 'name':'Display ?','type':'text','editable':True},
                        {'id':'spe', 'name':'S,P,E', 'type':'text','editable':False},
                        {'id':'model-type', 'name':'Model_type', 'type':'text','editable':False},
                        *[{'id': name, 'name': name, 'type': 'numeric', 'editable':False} for name in retained_keys]
                        #I really need to learn how to use that unpacking operator better, it's great
                    ]
                        )
        ]
        )
    ]

    return(children, store_datatable_data)

@callback(
    Output("datatable-wrapper-container","children"),
    Output("store-inputs","data"),
    Output("store-datatable-data","data"),
    Input("input-path-btn","n_clicks"),
    Input("freq-table","data"),
    State("input-path-files","value"),
    State("store-inputs","data"),
    State("store-datatable-data","data"),
    prevent_initial_call=True,
)
def add_datatable_data(clicks_add, table_data, input_path, store_inputs, store_datatable_data):

    if input_path is None:
        raise dash.exceptions.PreventUpdate
    else: #Because Windows is as bad as always smiley face
        if system_os == "Windows":
            input_path = pathlib.WindowsPath(f"{input_path}")
        else:
            input_path = pathlib.PosixPath(f"{input_path}")

    if store_inputs is None:
        store_inputs = {"inputs":[]}

    if store_datatable_data is None:
        store_datatable_data = {"table_data":[], "names":[], "stelum_paths":[], "pulse_paths":[], "eig_paths":[], "spe":[], "model_type":[], "init":True}

    if ctx.triggered_id == "input-path-btn":
        try:
            table_data, names, model_paths, spe, model_type = data_reading.datatable_mainframe(input_path)
        except Exception as e: ##just for me during debugging
            import traceback
            print("Error:", e)
            traceback.print_exc()
            raise dash.exceptions.PreventUpdate

        if str(input_path) in store_inputs["inputs"]:
            raise dash.exceptions.PreventUpdate
        else:
            store_inputs["inputs"].append(str(input_path))
            data_table, store_datatable_data = dataTable_creation(store_datatable_data, table_data, names, spe, model_type, model_paths)
            #table_data is data parsed from gbuilder or (?) (?) --> not coded yet
            #names - model names, either from gbuilder or (?)
            #model_paths are the paths or all models from gbuilder or (?)
            return(data_table, store_inputs, store_datatable_data)
    else:
        display = [value["display"] for value in table_data]
        store_datatable_data["table_data"]["display"] = display

        return(dash.no_update, dash.no_update, store_datatable_data)

layout = html.Div(
    id="files",
    style={
        "display":"flex",
        "width":"100vw",
        "height":"100vh"
    },
    children=[
        html.Div(id = "files_page",
                 style={"width":"calc(100% - 5rem)", "height":"100vh", "marginLeft":"auto"}, #to account for the sidebar
                 children=[
                    html.Div(id="DISP-header",
                             style={"display":"flex","flexDirection":"column","height":"12vh"},
                             children= [
                                html.Div(id = "title-files",
                                        style={"display":"flex","height":"4vh","width":"100%", "marginBottom":"1vh","marginTop":"1vh", "flexDirection":"column", "alignItems":"center","justifyContent":"center"},
                                        children = [html.Span("Models informations", className="subtitles-config", style={"fontSize":"4vh"})]),
                                html.Div(id = "input-div",
                                        style= {"height":"6vh","display":"flex","flexDirection":"row","width":"100%","alignItems":"center","justifyContent":"center"},
                                        children=[
                                            dbc.Input("input-path-files", placeholder="Absolute path for model files", type="text", style={"height":"5vh","width":"40%","marginRight":"2vw"}),
                                            dbc.Button(dl.DashLatex("Add model from path"), id="input-path-btn", className="btn-add", style={"height":"6vh","width":"20%", "fontSize":"3vh"})]),
                                html.Hr(style={"width":"98%"}),
                             ]),
                                html.Div(className= "datatable-container",
                                        children=[
                                            html.Div(
                                                    id="datatable-wrapper-container",
                                                    className="datatable-wrapper",
                                                    children=[
                                            dash_table.DataTable(
                                                        id='freq-table',
                                                        data=df_freq.to_dict('records'),
                                                        style_table={
                                                            "overflowY": "hidden",
                                                            "height":"100%",
                                                            "width":"100%",
                                                            "backgroundColor": "rgba(0,0,0,0.25)",
                                                            "minHeight":"100%"
                                                        }, 
                                                        style_cell={
                                                            "backgroundColor": "rgba(0,0,0,0.25)",
                                                            "color": "white",
                                                            "fontFamily": "Arial, sans-serif",
                                                            "fontSize": "2vh",
                                                            "textAlign": "center",
                                                            "border": "1px solid rgba(255,255,255,0.1)",
                                                            "width":"10%",
                                                            "maxwidth":"10%",
                                                            "minwdith":"10%",
                                                            "height":"3vh",
                                                        },
                                                        style_header={
                                                            "backgroundColor": "rgba(0,0,0,0.5)",
                                                            "fontWeight": "bold",
                                                            "color": "white",
                                                            "borderBottom": "2px solid rgba(255,255,255,0.3)",
                                                        },
                                                        style_data={
                                                            "backgroundColor": "rgba(0,0,0,0.25)",
                                                            "color": "white",
                                                        },
                                                        fixed_rows={'headers': True},
                                                        page_action='none', #otherwise it puts pagination not scrolling :(
                                                        columns=[
                                                            {'id':'degree', 'name':'Placeholder','type': 'text','editable':True},
                                                            {'id':'period', 'name':'Placeholder','type':'numeric','editable':False},
                                                            {'id':'reduced-period', 'name':'Placeholder', 'type':'numeric','editable':False}],
                                                            )
                                            ]
                                            )
                                        ])
                 ],
                 ) 
    ]
)

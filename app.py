import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import webbrowser, os, pkgutil, importlib, pages
from threading import Timer
import dash_latex as dl
import dash_mantine_components as dmc

meta_tags = [{"name":"viewport","content":"width=device-width, initial-scale=1.0"}]

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.icons.FONT_AWESOME],
    use_pages=True,
)

#to have dark theme on, even though I didn't design a light theme
#because I have respect for people's eyes (looking at you Stackoverflow)
app.index_string = """  
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

page_modules = {}
layouts = []

for _, module_name, _ in pkgutil.iter_modules(pages.__path__):
    module = importlib.import_module(f"pages.{module_name}")
    if hasattr(module, "layout") and hasattr(module, "page_url"):
        page_modules[module.page_url] = module
        layouts.append(module.layout)

page_urls = list(page_modules.keys())

icons = ["F","DB"]
names = ["Files","Dashboard"]

default_url = "/files"

store_inputs = dcc.Store(id="store-inputs",storage_type="session")
store_datatable_data = dcc.Store(id="store-datatable-data",storage_type="session")
store_paths = dcc.Store(id="store-path", storage_type="session")
store_stelum = dcc.Store(id="store-stelum", storage_type="session")
store_pulse = dcc.Store(id="store-pulse", storage_type="session")
store_eig = dcc.Store(id="store-eig", storage_type="session")
store_active_tab = dcc.Store(id="store-active-tab", storage_type="session")
store_displayed = dcc.Store(id="store-displayed", storage_type="session")
store_dropdown_values = dcc.Store(id="store-dropdown-values",storage_type="session")
store_graph_options = dcc.Store(id="store-graph-options", storage_type="session")
#need one for each this way it's easy to keep track of everything in between tabs !

sidebar = html.Div(
        [
        html.Div(
            [
                html.Img(src="/assets/PEGASuS_logo_black.png", style={"height":"100%","width":"100%"}),
                html.Span(dl.DashLatex("DISP"),style={"fontSize":"3vh","lineHeight":"100%","font-weight":"bold","padding-top":"1rem"}),
            ], style={"display":"flex","flexDirection":"column"},
            className="sidebar-header",
        ),
        html.Hr(),
        dbc.Nav([
            dbc.NavLink([html.Span(icon, className="icon", style={"marginRight": "1rem"}), html.Span(name, className="non_icon")],
                        href=page_url,
                        active="exact",)
                        for (icon, name, page_url) in zip(icons,names,page_urls)
        ],
        vertical=True,
        pills=True,
        ),
    ],
    className="sidebar",
)

@app.callback(
    [Output(layout.id, "style") for layout in layouts],
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname not in page_modules:
        pathname = default_url

    return [
        {"display": "block"} if pathname == page_modules[page_url].page_url else {"display": "none"}
        for page_url in page_modules
    ]

app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    children=html.Div(
        id="main-app",
        children=[
            dcc.Location(id="url", refresh=False),
            sidebar,
            store_inputs,
            store_datatable_data,
            store_paths,
            store_stelum,
            store_pulse,
            store_eig,
            store_active_tab,
            store_displayed,
            store_dropdown_values,
            store_graph_options,
            *layouts
        ],
        style={"display": "block"}
    )
)

def open_browser(): ##That's to open the browser window on start
    if not os.environ.get("WERKZEUG_RUN_MAIN"): #prevent double window opening
	    webbrowser.open_new("http://localhost:{}".format(port))

if __name__ == '__main__':
    port = 8050 #offline port

    Timer(1, open_browser).start()
    app.run(debug=True, port=port)
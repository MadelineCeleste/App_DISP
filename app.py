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
for _, module_name, _ in pkgutil.iter_modules(pages.__path__):
    module = importlib.import_module(f"pages.{module_name}") #careful about structure here, needs to be Dash.pages
    if hasattr(module, "layout") and hasattr(module, "page_url"):
        page_modules[module.page_url] = module.layout

page_urls = list(page_modules.keys())
layouts = list(page_modules.values())

icons = ["F","S","P","E"]
names = ["Files","STELUM","PULSE","EIG"]

default_url = "/files"

store_inputs = dcc.Store(id="store-inputs",storage_type="session")
store_datatable_data = dcc.Store(id="store-datatable-data",storage_type="session")

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
    
    outputs = []
    for page_url in page_urls:
        if pathname == page_url:
            outputs.append({"display": "block"})
        else:
            outputs.append({"display": "none"})
    return outputs

app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},  # or "dark"
    children=html.Div(
        id="main-app",
        children=[
            dcc.Location(id="url", refresh=False),
            sidebar,               # your dbc sidebar
            store_inputs,          # dcc.Store
            store_datatable_data,  # dcc.Store
            *page_modules.values() # your pages
        ],
        style={"display": "block"}
    )
)

def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"): #prevent double window opening
	    webbrowser.open_new("http://localhost:{}".format(port))

if __name__ == '__main__':
    port = 8050 #offline port

    Timer(1, open_browser).start()
    app.run(debug=True, port=port)
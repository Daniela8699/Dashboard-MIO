import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from src.bus import busModel
app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN, dbc.themes.GRID])

MIO_LOGO = "./assets/mio.png"
CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


nav = dbc.Nav(
    [
        html.Div(dbc.NavItem(dbc.NavLink("Reporte", href="/")),
                 style={"color": "white"}),


        dbc.DropdownMenu(
            [dbc.DropdownMenuItem("Bus ID", header=True), dbc.DropdownMenuItem(
                "571", href="/bus-571"), dbc.DropdownMenuItem("132", href="/bus-132"), dbc.DropdownMenuItem("306",  href="/bus-306")],
            label="Buses",
            nav=True,
        ),
    ]
)

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=MIO_LOGO, height="20px")),
                    dbc.Col(dbc.NavbarBrand(
                        "Dash MetroCali", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="http://www.mio.com.co/",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(nav, id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
)
content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dbc.Row(dbc.Col(html.Div(navbar))),
        dbc.Row(dbc.Col(html.Div(content))),
    ])

# add callback for toggling the collapse on small screens


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/bus-571":
        return busModel("571")
    elif pathname == "/bus-132":
        return busModel("132")
    elif pathname == "/bus-306":
        return busModel("306")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(debug=True)

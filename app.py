import dash
import dash_bootstrap_components as dbc

app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN, dbc.themes.GRID])
server = app.server

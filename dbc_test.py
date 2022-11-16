# Demonstration app for issue with left-justifying items
# Related question: https://community.plotly.com/t/using-justify-start-within-dash-bootstrap-doesnt-move-all-items-to-the-left/69928
# See also: https://github.com/facultyai/dash-bootstrap-components/issues/904

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = html.Div(
    children=[

        dbc.Row([

            dbc.Col(html.H5(children="Color bars based on:"), width=2),
            dbc.Col(dcc.Dropdown(['Airport', 'Airline', 'Route Type',
                                  'None'], 'Airport', id='color_value_input', multi=False), width=1),

            dbc.Col(html.H5(children="Compare by:"), width=2),
            dbc.Col(dcc.Dropdown(['Airport', 'Airline', 'Route Type'],
                                 ['Airport'], id='pivot_value_input', multi=True), width=2),
        ], justify="start"),

        dbc.Row([

            dbc.Col(html.H5(children="Number of airports to show:"), width=2),

            dbc.Col(dcc.Input(id="interactive_air_traffic_airports_limit",
                              type="number", value=5, min=1, size='5'), width=1),


            dbc.Col(html.H5(children="Route Types To Show:"), width=2),
            dbc.Col(dcc.Dropdown(['Domestic', 'International'],
                                 ['Domestic', 'International'],
                id='interactive_air_traffic_route_types', multi=True), width=2),


        ], justify="start")

    ])

if __name__ == '__main__':
    app.run_server(debug=True)

import pandas as pd
import dash
from dash.dependencies import Input, Output
# from dash import html
import dash_html_components as html
import dash_pivottable

df_airline_airport_pairs = pd.read_csv('airport_airline_pairs_2018.csv')
airline_list = ['DL', 'AA', 'UA', 'WN']
airport_list = ['ATL', 'LAX', 'ORD', 'DFW', 'JFK']
df_airline_airport_pairs = df_airline_airport_pairs.query("Airline in @airline_list & Airport in @airport_list").copy()

print(len(df_airline_airport_pairs))

print(df_airline_airport_pairs)

app = dash.Dash(__name__)
app.title = 'My Dash example'

app.layout = html.Div([
    dash_pivottable.PivotTable(
        id='table',
        data=df_airline_airport_pairs,
        cols=['Airline'],
        colOrder="key_a_to_z",
        rows=['Airport'],
        rowOrder="key_a_to_z",
        rendererName="Grouped Column Chart",
        aggregatorName="Average",
        vals="Passengers"
    ),
    html.Div(
        id='output'
    )
])

print("Here!")

@app.callback(Output('output', 'children'),
              [Input('table', 'cols'),
               Input('table', 'rows'),
               Input('table', 'rowOrder'),
               Input('table', 'colOrder'),
               Input('table', 'aggregatorName'),
               Input('table', 'rendererName')])
def display_props(cols, rows, row_order, col_order, aggregator, renderer):
    return [
        html.P(str(cols), id='columns'),
        html.P(str(rows), id='rows'),
        html.P(str(row_order), id='row_order'),
        html.P(str(col_order), id='col_order'),
        html.P(str(aggregator), id='aggregator'),
        html.P(str(renderer), id='renderer'),
    ]

print("Here!")

if __name__ == '__main__':
    app.run_server(debug=True)
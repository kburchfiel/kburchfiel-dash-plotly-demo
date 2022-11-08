# A workspace for testing out different charts that I can then incorporate into my main Dash app. Also ideal for offline situations (since I can connect directly to .csv files)

# Based on code found in the following links:
# https://dash.plotly.com/dash-core-components/dropdown
# https://dash.plotly.com/basic-callbacks#dash-app-with-multiple-inputs
# Jinnyzor's response to my question at
# https://community.plotly.com/t/how-can-i-allow-users-to-select-which-comparison-variables-to-display-on-a-chart/69124

from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

all_data_value = 'All_Traffic'
df_airline_airport_pairs = pd.read_csv('airport_airline_pairs_2018.csv')
df_airline_airport_pairs[all_data_value] = all_data_value # This column will allow
# the code to show all values when no pivot value is selected.


app = Dash(__name__)
app.layout = html.Div([
    html.H2(children = "Interactive Airline Traffic Graph"),
    html.H4(children = "Compare by:"),
    dcc.Dropdown(['Airport', 'Airline', 'Route Type'], ['Airport'], id='pivot_value_input', multi = True),
    html.H4(children = "Color bars based on: (Note: this item must be one \
of the selected comparisons)"),
    dcc.Dropdown(['Airport', 'Airline', 'Route Type', 'None'], 'None', id='color_value_input', multi = False),
    html.H4(children = "Airports Limit: (Clear entry to include all airports)"),
    dcc.Input(id="airports_limit", type="number", value=5, min = 1),
    html.H4(children = "Airlines Limit: (Clear entry to include all airports)"),
    dcc.Input(id="airlines_limit", type="number", value=4, min = 1),
    # See https://dash.plotly.com/dash-core-components/input

    # html.Div(id='dd-output-container'),
    # # multi = True will cause all outputs to be returned
    # # as a list.
    dcc.Graph(id='pivot_chart')

])


@app.callback(
    Output('pivot_chart', 'figure'),
    Input('pivot_value_input', 'value'),
    Input('color_value_input', 'value'),
    Input('airports_limit', 'value'),
    Input('airlines_limit', 'value')
)

def update_chart(pivot_values, color_value, airports_limit, airlines_limit):
    # These arguments correspond to the input values
    # listed (in the same order).
    # return f'You have selected {pivot_values}'

    # The following code creates a pivot table version of the DataFrame that 
    # can be used for creating bar charts. It takes the specified pivot values
    # and color values as inputs, and then uses those values to group the
    # data accordingly. The code works with different numbers of pivot values,
    # including zero pivot values.
    # In order to represent all of the specified values, the code creates a 
    # column describing all (or almost all) of the pivot index variables
    # in the other columns, which then gets fed 
    # into the x axis parameter of the bar chart. However, if a color value is
    # also specified, this item does not get added into this column, since this
    # data will already get represented in the bar chart (by means of the color
    # legend). Removing this value helps
    # simplify the final chart output.


    airlines_to_keep = list(df_airline_airport_pairs.pivot_table(index = 'Airline', values = 'Passengers', aggfunc = 'sum').sort_values('Passengers', ascending = False).index[0:airlines_limit])
    print(airlines_to_keep)
    df_airline_airport_pairs_filtered = df_airline_airport_pairs.query("Airline in @airlines_to_keep").copy()

    airports_to_keep = list(df_airline_airport_pairs.pivot_table(index = 'Airport', values = 'Passengers', aggfunc = 'sum').sort_values('Passengers', ascending = False).index[0:airports_limit])
    df_airline_airport_pairs_filtered = df_airline_airport_pairs_filtered.query("Airport in @airports_to_keep").copy()
    print(airports_to_keep)



    # The following lines convert dropdown text to 
    # DataFrame column variables where discrepancies
    # exist between the two.
    pivot_values = ['Route_Type' if entry == 'Route Type' else entry for entry in pivot_values]

    if color_value == 'Route Type':
        color_value = 'Route_Type'
    
    color_value = color_value # This color value must also be present
    # within the pivot_values table.
    # group_value = 'Airline'
    if len(pivot_values) == 0:
        df_airline_airport_pairs_pivot = df_airline_airport_pairs_filtered.pivot_table(index = 'All_Traffic', values = 'Passengers', aggfunc = 'sum').reset_index()
    else:
        df_airline_airport_pairs_pivot = df_airline_airport_pairs_filtered.pivot_table(index = pivot_values, values = 'Passengers', aggfunc = 'sum').reset_index()

    # The following lines create a column containing the values of each of the
    # columns (other than the 'Passengers') column present in the bar chart. A
    # for loop is used so that this column can adapt to different variable
    # choices and different numbers of columns.
    if len(pivot_values) == 0:
        data_descriptor = all_data_value
    else:
        data_descriptor_values = pivot_values.copy()
        if color_value != 'None':
            data_descriptor_values.remove(color_value) # If a value will be assigned a
            # color component in the graph, it doesn't need to be assigned a 
            # group component, since it will show up in the graph regardless. Removing 
            # it here helps simplify the graph.
        print(data_descriptor_values)   
        data_descriptor = df_airline_airport_pairs_pivot[data_descriptor_values[0]].copy() # This copy() statement
        # is needed in order to avoid  modifying this column when the group column
        # gets chosen.
        for i in range(1, len(data_descriptor_values)):
            data_descriptor += ' ' + df_airline_airport_pairs_pivot[data_descriptor_values[i]]

    df_airline_airport_pairs_pivot['Group'] = data_descriptor

    df_airline_airport_pairs_pivot.head(5)

    output_histogram = px.histogram(df_airline_airport_pairs_pivot, x = 'Group', y = 'Passengers', color = None if color_value == 'None' else color_value, barmode = 'group')

    return output_histogram






if __name__ == '__main__':
    app.run_server(debug=True)
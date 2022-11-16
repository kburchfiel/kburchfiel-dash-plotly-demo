# Web dashboard (work in progress)
# Kenneth Burchfiel
# Released under the MIT license


# For local debugging/deployment: with online_deployment set to False, 
# run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# Note: running this program within Visual Studio Code by pressing F5 doesn't appear to work.
# Instead, you need to launch it from Command Prompt or a similar program.

# For web debugging/deployment: with online_deployment set to True,
# run this app by entering
# gcloud run deploy --source . Press enter to choose the default project
# name and 27 to choose the us-central1 data center.


from dash import Dash, html, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
# from google.cloud import secretmanager
# from google.oauth2 import service_account
import json
import sqlalchemy
# import os
import numpy as np


online_deployment = False # Set to False for local development and debugging
# Make sure this is set to True before you deploy a new version of the app
# to Cloud Run!

app = Dash(__name__)
server = app.server # From https://medium.com/kunder/deploying-dash-to-cloud-run-5-minutes-c026eeea46d4
# Also found on https://dash.plotly.com/deployment (within the Heroku section)


if online_deployment == True: # The URL for the ElephantSQL database will
    # be accessed through a Secret Manager volume stored online
    with open('/projsecrets/elephantsql_db_url') as file:
        elephantsql_url_from_gcp = file.read()
# Based on https://stackoverflow.com/questions/68533094/how-do-i-access-mounted-secrets-when-using-google-cloud-run
# In order for this step to work, I needed to go to 
# https://console.cloud.google.com/run , select 'Edit & Deploy New Revision,'
# and then mount my secret (which I had created earlier) as a volume. (I chose 'projsecrets' as my volume
# name.
# Note that the Secret Manager Secret Accessor role must be enabled for your service account for your code to work, as noted here:
# https://cloud.google.com/run/docs/configuring/secrets#access-secret


else: # This URL will be accessed through a file stored on my computer
    with open (r"C:\Users\kburc\D1V1\Documents\!Dell64docs\Programming\py\kjb3_programs\key_paths\path_to_keys_folder.txt") as file:
        key_path = file.read()
    with open(key_path+"\\elephantsql_kjb3webchartapp_db_url.txt") as file:
        db_url = file.read()
        # This code reads in my database's URL. This URL is listed on the home page for my database within elephantsql.com. As shown below, SQLAlchemy can use this URL to connect to the database. 
    elephantsql_url_from_gcp = db_url.replace('postgres://', 'postgresql://')
    # This change, which is required for SQLAlchemy to work correctly, is based on the code suggested at:
    # # https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres


elephantsql_engine = sqlalchemy.create_engine(elephantsql_url_from_gcp)

airline_color_map = {
    "DL":"purple", # One of Delta's color schemes (shown at the link below)
    # is at least somewhat purplish, and I wanted to make AA red, so
    # I assigned Delta a generic purple color. (The pre-existing purplish
    # DL color is a bit too close to that for AA.)
    "UA":"#005DAA",
    "AA":"#B53126",
    "WN":"#F9B612",
    "AS":"green",
    "B6":"#003876",
    "Other":"#804000"
}
# See https://plotly.com/python/discrete-color/

# RGB color sources:
# Delta: Schemecolor at https://www.schemecolor.com/delta-airlines-logo-colors.php
# United: Keshav Naidu at https://www.schemecolor.com/united-airlines-logo-blue-color.php
# JetBlue: Schemecolor at https://www.schemecolor.com/jetblue-airways-logo-color.php
# AA: I had initially used the gray color provided at 
# https://coloropedia.com/american-airlines-group-colors-logo-codes/ ,
# but that proved to be too light, so I chose a generic gray instead.
# Southwest (WN): https://www.schemecolor.com/southwest-airlines-logo-colors.php
# Color for 'other': https://en.wikipedia.org/wiki/Brown 





# df_aaa = pd.read_sql("select * from airports_airlines_aircraft_2018", con = elephantsql_engine)

# df_aaa_len = len(df_aaa)

# print(len(df_aaa))

# Note: this code was based on: https://dash.plotly.com/layout#more-about-html-components

# https://plotly.com/python/px-arguments/ for more options

# Graphs:
# Top 20 Airports:

# Top 20 Airlines:
df_top_20_airlines = pd.read_sql("top_20_airlines_by_passengers_2018", con = elephantsql_engine)
fig_top_20_airlines_2018 = px.bar(df_top_20_airlines, x="Airline", y="Passengers", color = "Route_Type", barmode = 'group', title = "Top 20 Airlines by Passenger Traffic Involving at Least 1 US Airport in 2018")
## https://plotly.com/python/bar-charts/

# Top 20 US Airports by Airline Share:

all_data_value = 'All_Traffic'
df_airline_airport_pairs = pd.read_sql('airline_airport_pairs_2018', con = elephantsql_engine)
df_airline_airport_pairs[all_data_value] = all_data_value # This column will allow
# the code to show all values when no pivot value is selected.

# Top Domestic Hubs:


df_top_hubs = df_airline_airport_pairs.pivot_table(index = ['Airline', 'Airport'], values = 'Passengers', aggfunc = 'sum').reset_index().sort_values('Passengers', ascending = False)
df_top_hubs['Hub'] = df_top_hubs['Airline'] + ' ' + df_top_hubs['Airport']
fig_top_hubs = px.bar(df_top_hubs.iloc[0:20, :], x = 'Hub', y = 'Passengers', color = 'Airline', color_discrete_map=airline_color_map, title = "Top 20 US Airport Hubs in 2018 by Arriving Passengers")
fig_top_hubs.update_xaxes(categoryorder = 'total descending') # See https://plotly.com/python/categorical-axes/


# Top International Hubs:

df_top_intl_hubs = df_airline_airport_pairs.query("Route_Type == 'International' & Destination_Region == 'Domestic'").pivot_table(index = ['Airline', 'Airport'], values = 'Passengers', aggfunc = 'sum').reset_index().sort_values('Passengers', ascending = False)
# I'd only like to show US airports within this chart, so I chose to filter it to include only domestic airports.
df_top_intl_hubs['Hub'] = df_top_intl_hubs['Airline'] + ' ' + df_top_intl_hubs['Airport']
fig_top_intl_hubs = px.bar(df_top_intl_hubs.iloc[0:20, :], x = 'Hub', y = 'Passengers', color = 'Airline', color_discrete_map=airline_color_map, title = "Top 20 US Airport Hubs in 2018 by Arriving International Passengers")
fig_top_intl_hubs.update_xaxes(categoryorder = 'total descending') # See https://plotly.com/python/categorical-axes/

# It seems that the above charts need to be created before initializing the
# app.layout set below, since otherwise the figure values won't be found.
# However, for the graph and table created by create_departures_table(),
# this isn't an issue, since those items do not have an explicit 


app.layout = html.Div(style = {'font-family':'sans-serif'},
# See https://community.plotly.com/t/list-of-all-dash-fonts-accessible-through-style/50089
 children=[
    html.H1(children='Sample Dash/Plotly Data Visualization App'),

    html.H3(children='By Kenneth Burchfiel'),

    html.Div(children='''
        This page, which is still a work in progress, shows how Plotly and Dash can be used to visualize data retrieved from a database.
    '''),

    # Top Airports Interactive Graph:
    html.H2(children = "Top US Airports by Arrival Traffic in 2018"),
    dcc.Checklist(
            id = 'top_airports_graph_options_input',
    options={
            'show_airline_comparison': 'Show Airline Comparison',
            'show_route_type': 'Show Route Type',
    },
    value=['show_airline_comparison']),
    # Note: if both are selected, the output will appear as:
    # ['show_airline_comparison', 'show_route_type']
    html.H4(children = "Route Types To Show"),
    dcc.Dropdown(['Domestic', 'International'], ['Domestic','International'], id='top_airports_graph_route_types', multi = True),
    html.H4(children = "Number of Airports to Show (Up to 100)"),
    dcc.Input(id="airports_graph_airports_limit_input", type="number", value=20, min = 1),
    html.H4(children = "Airports to Include"),
    dcc.Dropdown(id = "airports_to_graph", multi = True), # The initial value
    # will be set through a callback, so no list is specified here.
    dcc.Graph("top_airports_interactive_graph"),


    # Interactive Airline Traffic Graph
    html.H2(children = "Interactive Airline Traffic Graph"),

    # Filters/Limits:
    html.H4(children = "Route Types To Show"),
    dcc.Dropdown(['Domestic', 'International'], ['Domestic','International'], id='interactive_airline_traffic_route_types', multi = True),

    html.H4(children = "Number of airports to show (up to 20)"),
    dcc.Input(id="airports_limit", type="number", value=5, min = 1),
    html.H4(children = "Number of airlines to show (up to 10)"),
    dcc.Input(id="airlines_limit", type="number", value=4, min = 1),
    # See https://dash.plotly.com/dash-core-components/input

    html.H4(children = "Airports to Include"),
    dcc.Dropdown(id = "interactive_airline_traffic_airports_filter", multi = True),
    html.H4(children = "Airlines to Include"),
    dcc.Dropdown(id = "interactive_airline_traffic_airlines_filter", multi = True),

    # Comparisons:
    html.H4(children = "Compare by:"),
    dcc.Dropdown(['Airport', 'Airline', 'Route Type'], ['Airport'], id='pivot_value_input', multi = True),
    html.H4(children = "Color bars based on: (Note: this item must be one \
    of the selected comparisons)"),
    dcc.Dropdown(['Airport', 'Airline', 'Route Type', 'None'], 'None', id='color_value_input', multi = False),

    # html.Div(id='dd-output-container'),
    # # multi = True will cause all outputs to be returned
    # # as a list.
    dcc.Graph(id='pivot_chart'),

    dcc.Graph(
        id='top_20_airlines_graph',
        figure=fig_top_20_airlines_2018
    ),

    dcc.Graph(
        id = 'top_20_hubs',
        figure = fig_top_hubs),

    dcc.Graph(
            id = 'top_20_intl_hubs',
            figure = fig_top_intl_hubs),

        html.H3(children = "Top origin airports for a given destination airport:"),

        dcc.Input(
            id="airport-text",
            style={"width": "100%"},
            value="ABQ",
        ),
        # Source: https://dash-example-index.herokuapp.com/creating-and-updating-figures


        dcc.Graph(id = 'top_origins_for_airport_table'),
            # Based on https://dash-example-index.herokuapp.com/circular-callback-app

        dcc.Graph(
            id = 'top_origins_for_airport_graph')
])

# Top airports graph:

# Note: The airports shown on the graph are selected through multiple stages.
# First, the user selects which route types to view (domestic, international,
# or both) and the number of airports to show. Next, the create_top_airports_list
# function (shown below) retrieves a list of the top n airports to show
# based on this criteria. This list is then shown as a multiselect dropdown
# window so that the user can manually remove certain airports. The 
# create_interactive_top_airports_graph then uses this list to determine
# which airports will actually appear on the graph.

# Callback/function that populate an interactive airports filter for the 
# top airports graph.
# Note that the same data gets returned under both the 'options' and 
# the 'value' category. This way, the default value(s) for the airports
# filter will consist of all the potential options. (Otherwise, the 
# default values list will be blank and there won't be any data to display.)
# Thank you to Eduardo at 
# https://community.plotly.com/t/how-to-dynamically-set-a-default-value-in-a-dcc-dropdown-when-options-come-from-a-callback/48463/4
# for explaining this.
@app.callback(
    Output("airports_to_graph", "options"),
    Output("airports_to_graph", "value"),
    Input("top_airports_graph_route_types", "value"),
    Input("airports_graph_airports_limit_input", "value")
)

def create_top_airports_list(route_types_to_show, airports_graph_airports_limit):
    data_source = df_airline_airport_pairs.query("Destination_Region == 'Domestic'").copy()
    data_source = data_source.query("Route_Type in @route_types_to_show").copy()

    if airports_graph_airports_limit == None:
        airports_graph_airports_limit = 100
    if ((1 <= airports_graph_airports_limit <= 100) == False):
        airports_graph_airports_limit = 100

    df_airline_airport_pivot = data_source.pivot_table(index = 'Airport', values = 'Passengers', aggfunc = 'sum').sort_values('Passengers', ascending = False).reset_index()
    airports_to_keep = list(df_airline_airport_pivot['Airport'][0:airports_graph_airports_limit].copy())
    return airports_to_keep, airports_to_keep



# Callback and function for creating top 20 airports graph:
@app.callback(
    # Output("graph_options_output", "children"),
    Output("top_airports_interactive_graph", "figure"),
    Input("top_airports_graph_options_input", "value"),
    Input("airports_to_graph", "value"),
    Input("top_airports_graph_route_types", "value"),
)

def create_interactive_top_airports_graph(top_airports_graph_options, airports_to_graph, route_types_to_show):
    '''This function creates a graph of the top airports specified by 
    the parameters provided.
    '''
    data_source = df_airline_airport_pairs.query("Destination_Region == 'Domestic'").copy() # Using a copy
    # of this DataFrame ensures that changes to the DataFrame won't
    # affect the original DataFrame (which could distort other graphs
    # or later versions of this graph).
    # The data source is also limited to US airports since that is the
    # region of interest for this chart.

    # The following query statement filters data_source to only include
    # the rows specified in the 'Route Types to Show' menu.
    print("Filtering data source to only include the following route types:", route_types_to_show)
    data_source = data_source.query("Route_Type in @route_types_to_show").copy()


    print(f"Calling create_interactive_top_airports_graph with the following graph options: {top_airports_graph_options} and the following airports limit: {airports_to_graph}")

    top_airlines = list(data_source.pivot_table(index = 'Airline', values = 'Passengers', aggfunc = 'sum').sort_values('Passengers', ascending = False).index[0:4])

    # The following code groups all airlines outside the top 4 in the 
    # dataset into an 'other' category. I switched from Series.isin()
    # to str.contains() because an airline named 'AAT' was found 
    # in the results for SJU, and this airline code would still appear
    # using str.contains (since AAT contains 'AA', one of the top 4
    # airlines in the dataset).
    data_source['Airline'] = np.where(data_source['Airline'].isin(top_airlines) == False, 'Other', data_source['Airline'])
    # See https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.isin.html

    data_source


    df_airline_airport_pivot = data_source.pivot_table(index = 'Airport', values = 'Passengers', aggfunc = 'sum').sort_values('Passengers', ascending = False).reset_index()
    df_airline_airport_pivot['airport_rank'] = df_airline_airport_pivot['Passengers'].rank(ascending=False)
    df_airline_airport_pivot

    data_source_filtered = data_source.query("Airport in @airports_to_graph").copy()
    data_source_filtered = data_source_filtered.merge(df_airline_airport_pivot[['Airport', 'airport_rank']], on = 'Airport')
    data_source_filtered


    # The following code creates a pivot table based on the parameters specified above.

    pivot_values = ['Airport', 'airport_rank']

    if 'show_airline_comparison' in top_airports_graph_options:
        pivot_values.append('Airline')

    if 'show_route_type' in top_airports_graph_options:
        pivot_values.append('Route_Type')

    data_source_filtered_pivot = data_source_filtered.pivot_table(index = pivot_values,
    values = 'Passengers', aggfunc = 'sum').reset_index()
    data_source_filtered_pivot

    if ('show_airline_comparison' in top_airports_graph_options) and ('show_route_type' in top_airports_graph_options):
        data_source_filtered_pivot['Airport_Route_Pair'] = data_source_filtered_pivot['Airport'] + ' ' + data_source_filtered_pivot['Route_Type']

    if 'show_route_type' in top_airports_graph_options:
        print("Sorting airports.")
        data_source_filtered_pivot.sort_values(by = ['airport_rank', 'Airport', 'Route_Type'], inplace = True, ascending = [True, True, True]) # Sorting 'Airport' in ascending order ensures that 
        # domestic traffic will precede international traffic.
    # See https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html 
    # regarding the list passed to the 'ascending' option here.

    else:
        data_source_filtered_pivot.sort_values(by = ['airport_rank', 'Airport'], inplace = True, ascending = [True, True])
        # The 'Airport' filter will sort airports alphabetically in the 
        # very unlikely event of a tie (at least for the top 100 airports
        # in the US).

    # Since there are two different top_airports_graph_options items that
    # can be chosen, there are in turn four possible graphs that can be created. 
    # Thus, the following code creates four separate bar charts.

    if ('show_airline_comparison' in top_airports_graph_options) and ('show_route_type' in top_airports_graph_options):

        x_val = 'Airport_Route_Pair'
        color_val = 'Airline'

    if top_airports_graph_options == ['show_airline_comparison']:
        x_val = 'Airport'
        color_val = 'Airline'

    if top_airports_graph_options == ['show_route_type']:
        x_val = 'Airport'
        color_val = 'Route_Type'
        

    if top_airports_graph_options == []:
        x_val = 'Airport'
        color_val = 'Airport'
        

    top_airports_graph = px.histogram(data_source_filtered_pivot, x = x_val, y = 'Passengers', color = color_val, color_discrete_map=airline_color_map)
    top_airports_graph.update_xaxes(categoryorder = 'array', 
    categoryarray = data_source_filtered_pivot[x_val])
    # Adding in a color value can change the order of the bars; therefore,
    # the above line resets the bars to their original order.
    # # See https://plotly.com/python/categorical-axes/#automatically-sorting-categories-by-name-or-total-value

    return top_airports_graph

# def print_graph_options(graph_options):
#     print(graph_options)
#     return(graph_options)



@app.callback(
    Output("top_origins_for_airport_table", "figure"),
    Output("top_origins_for_airport_graph", "figure"),
    Input("airport-text","value"),
)

# Top origin airports for a given airport (displayed as both a graph 
# and as a table):
# Note: the callback component of the code was based on 
# the examples shown at 
# https://dash-example-index.herokuapp.com/circular-callback-app
# and at https://dash-example-index.herokuapp.com/creating-and-updating-figures .
# See also: https://dash.plotly.com/basic-callbacks

def create_departures_table(dest_airport):
    '''Creates a list of the top 20 departure airports (along with an 'Other' 
    category if more than 20 origin airports exist) for the given airport.'''
    df_airport_by_origin = df_dest_by_origin.query("Airport == @dest_airport").sort_values('Passengers', ascending = False).reset_index(drop=True)
    if len(df_airport_by_origin) > 20:
        other_row = [dest_airport, 'Other', sum(df_airport_by_origin.iloc[20:,]['Passengers'])]
        df_airport_by_origin = df_airport_by_origin.iloc[0:20]
        df_airport_by_origin.loc[len(df_airport_by_origin)] = other_row
    pax_sum = sum(df_airport_by_origin['Passengers'])    
    df_airport_by_origin['Share'] = 100*df_airport_by_origin['Passengers'] / pax_sum  

    fig_origins_for_airport_table = go.Figure(data=go.Table(
        header = dict(
            values = list(df_airport_by_origin.columns)
            ), 
        cells = dict(
            values = [df_airport_by_origin['Airport'], df_airport_by_origin['Origin'], df_airport_by_origin['Passengers'], df_airport_by_origin['Share']] )))

    fig_origins_for_airport_graph = px.bar(df_airport_by_origin, x = 'Origin', y = 'Passengers')
    fig_origins_for_airport_graph


    return fig_origins_for_airport_table, fig_origins_for_airport_graph
    # These correspond to top_origins_for_airport_table and 
    # top_origins_for_airport_graph in the callbacks list.
    # I imagine that the callback links these items to the Output items by
    # looking for the items returned by the function immediately proceeding
    # the callback.
    # Meanwhile, perhaps it links dest_airport (the function parameter)
    # to airport_text (the Input item and the DCC item) by examining the
    # input parameter(s) in this same function.


df_dest_by_origin = pd.read_sql('select * from dest_to_origin', con = elephantsql_engine)


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

    if airports_limit == None:
        airports_limit = 20
    if ((1 <= airports_limit <= 20) == False):
        airports_limit = 20

    if airlines_limit == None:
        airlines_limit = 10
    if ((1 <= airlines_limit <= 10) == False):
        airlines_limit = 10

    data_source = df_airline_airport_pairs.copy()
    airlines_to_keep = list(data_source.pivot_table(index = 'Airline', values = 'Passengers', aggfunc = 'sum').sort_values('Passengers', ascending = False).index[0:airlines_limit])
    print(airlines_to_keep)
    data_source_filtered = data_source.query("Airline in @airlines_to_keep").copy()

    airports_to_keep = list(data_source.pivot_table(index = 'Airport', values = 'Passengers', aggfunc = 'sum').sort_values('Passengers', ascending = False).index[0:airports_limit])
    data_source_filtered = data_source_filtered.query("Airport in @airports_to_keep").copy()
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
        data_source_pivot = data_source_filtered.pivot_table(index = 'All_Traffic', values = 'Passengers', aggfunc = 'sum').reset_index()
    else:
        data_source_pivot = data_source_filtered.pivot_table(index = pivot_values, values = 'Passengers', aggfunc = 'sum').reset_index()

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
        data_descriptor = data_source_pivot[data_descriptor_values[0]].copy() # This copy() statement
        # is needed in order to avoid  modifying this column when the group column
        # gets chosen.
        for i in range(1, len(data_descriptor_values)):
            data_descriptor += ' ' + data_source_pivot[data_descriptor_values[i]]

    data_source_pivot['Group'] = data_descriptor

    data_source_pivot.head(5)

    output_histogram = px.histogram(data_source_pivot, x = 'Group', y = 'Passengers', color = None if color_value == 'None' else color_value, barmode = 'group', color_discrete_map=airline_color_map)

    return output_histogram






if __name__ == '__main__':
    app.run_server(debug=True)
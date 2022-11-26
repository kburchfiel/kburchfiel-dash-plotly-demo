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
import dash_bootstrap_components as dbc
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
read_from_csv = True # If set to True, data will be loaded from
# local .csv copies of the database tables (but only if 
# online_deployment is also set to False. This is useful for 
# working on the app when internet access is limited or unavailable.)

if (read_from_csv == False) or (online_deployment == True):
    read_from_sql = True
else:
    read_from_sql = False


app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
# See https://dash-bootstrap-components.opensource.faculty.ai/docs/quickstart/
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

if (read_from_csv == False) or (online_deployment == True):
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

# Top 20 US Airports by Airline Share:

all_data_value = 'All_Traffic'

if read_from_sql == True:
    df_airline_airport_pairs = pd.read_sql('airline_airport_pairs_2018', con = elephantsql_engine)
else:
    df_airline_airport_pairs = pd.read_csv(r'..\airport_airline_pairs_2018.csv')

df_airline_airport_pairs[all_data_value] = all_data_value # This column will allow
# the code to show all values when no pivot value is selected.

# It seems that the above charts need to be created before initializing the
# app.layout set below, since otherwise the figure values won't be found.
# However, for the graph and table created by create_departures_table(),
# this isn't an issue, since those items do not have an explicit 


# Functions that can be called for multiple charts:

def create_airlines_list(airlines_limit, route_types_to_show = ['Domestic', 'International'], max_airlines_limit = 10):
    '''This function creates a list of airlines that should be included
    in a graph.
    max_airlines_limit determines what the maximum number of airlines to show
    should be in the event that airlines_limit (the user-selected value) falls
    outside a reasonable range or is otherwise invalid.
    '''
    data_source = df_airline_airport_pairs.query("Destination_Region == 'Domestic'").copy()
    data_source = data_source.query("Route_Type in @route_types_to_show").copy()

    if airlines_limit == None:
        airlines_limit = max_airlines_limit
    if ((1 <= airlines_limit <= max_airlines_limit) == False):
        airlines_limit = max_airlines_limit

    df_airline_airport_pivot = data_source.pivot_table(index = 'Airline', values = 'Passengers', aggfunc = 'sum').sort_values('Passengers', ascending = False).reset_index()
    airlines_to_keep = list(df_airline_airport_pivot['Airline'][0:airlines_limit].copy())
    return airlines_to_keep, airlines_to_keep
    # This returns two instances of the airlines list: one for the 'options'
    # section of the Dropdown and the other for the default 'value' section.





# Application layout:

app.layout = html.Div(
style = {"margin": "2%"}, # See 
# https://developer.mozilla.org/en-US/docs/Web/CSS/margin
# This applies a percentage-based margin to all four sides of this block.
# To make all of the font sans serif without using Dash Bootstrap, 
# you can choose style = {'font-family':'sans-serif'}. See 
# https://community.plotly.com/t/list-of-all-dash-fonts-accessible-through-style/50089
 children=[
    # Intro
    html.H1(children='Sample Dash/Plotly Data Visualization App'),

    html.H3(children='By Kenneth Burchfiel'),

    html.Div(children='''
        This page, which is still a work in progress, shows how Plotly and Dash can be used to visualize data retrieved from a database.
    ''', style = {"margin-top": "1%", "margin-bottom": "3%"}),
    # This style parameter adds some extra space in between lines.

    # Top Airports Interactive Graph:
    html.H2(children = "Top US Airports by Arrival Traffic in 2018", style = {"margin-top": "1%"}),
    # See https://developer.mozilla.org/en-US/docs/Web/CSS/margin
    # and https://dash.plotly.com/dash-html-components/h2
    # for the 'style' argument (note that Dash expects a dict to be passed 
    # as the parameter for 'style')
    html.H5(children = "Comparisons to Show:", style = {"margin-top": "1%"}),
    dcc.Dropdown(
            id = 'top_airports_graph_options_input',
    options={
            'show_airline_comparison': 'Airline Comparison',
            'show_route_type': 'Route Type'
    },
    value=['show_airline_comparison', 'show_route_type'], style = {"margin-top": "1%"}, multi = True),
    # I added in width = 3 to force the checklist items to appear vertically.
    # I'm not sure why they didn't do so beforehand, since the documentation
    # states that checklist items appear vertically by default.
    # (See https://dash.plotly.com/dash-core-components/checklist)
    # Note: if both are selected, the output will appear as:
    # ['show_airline_comparison', 'show_route_type']
    html.H5(children = "Route Types To Show:", style = {"margin-top": "1%"}),
    dcc.Dropdown(['Domestic', 'International'], ['Domestic','International'], id='top_airports_graph_route_types', multi = True),
    html.H5(children = "Airport Count (Max 100):", style = {"margin-top": "1%"}),
    dcc.Input(id="airports_graph_airports_limit_input", type="number", value=20, min = 1),
    html.H5(children = "Airports to Include:", style = {"margin-top": "1%"}),
    dcc.Dropdown(id = "airports_to_graph", multi = True), # The initial value
    # will be set through a callback, so no list is specified here.
    dcc.Graph("top_airports_interactive_graph"),

    # Interactive Air Traffic Graph:
    html.H2(children = "Interactive Air Traffic Graph"),
    # Filters/Limits:
    # I'm using Dash Bootstrap to place certain items on the same line, saving
    # vertical space. See https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
    dbc.Row([
    dbc.Col(html.H5(children = "Route Types To Show:"), xl = 2, ),
    # Note: 'xl' is used here instead of 'width' so that Dash will only apply
    # a width of 1 when the screen size is 'xl' or larger. That way, the column
    # elements will still wrap down for smaller screens (preventing overlap)
    dbc.Col(dcc.Dropdown(['Domestic', 'International'], ['Domestic','International'], id='interactive_air_traffic_route_types', multi = True), xl = 2), 
    # I added in widths because doing so allowed me to use 'justify = start'
    # to left-justify these text and entry boxes.
    # See https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
    
    dbc.Col(html.H5(children = "Airport Count (Max 20):"), xl = 2),

    dbc.Col(dcc.Input(id="interactive_air_traffic_airports_limit", type="number", value=5, min = 1, size = '5'), xl = 1),
    # See https://dash.plotly.com/dash-core-components/input
    # regarding the 'size' argument.

    dbc.Col(html.H5(children = "Airline Count (Max 10):"), xl = 2),

    dbc.Col(dcc.Input(id="interactive_air_traffic_airlines_limit", type="number", value=4, min = 1, size = '5'), xl = 1)
    # See https://dash.plotly.com/dash-core-components/input


    ], justify = "start", style = {"margin-top": "1%"}),


    dbc.Row([
    dbc.Col(html.H5(children = "Airports to Include:"), xl = 2),
    dbc.Col(dcc.Dropdown(id = "interactive_air_traffic_airports_filter", multi = True), xl = 6)
    ], justify = "start", style = {"margin-top": "1%"}),

    dbc.Row([
    dbc.Col(html.H5(children = "Airlines to Include:"), xl = 2),
    dbc.Col(dcc.Dropdown(id = "interactive_air_traffic_airlines_filter", multi = True), xl = 6),
    ], justify = "start", style = {"margin-top": "1%"}),
    
    # Comparisons:

    dbc.Row([
    dbc.Col(html.H5(children = "Compare by:"), xl = 2),
    dbc.Col(dcc.Dropdown(['Airport', 'Airline', 'Route Type'], ['Airport'], id='pivot_value_input', multi = True), xl = 2),
    dbc.Col(html.H5(children = "Color bars based on: (Note: this item must be one \
    of the selected comparisons)"), xl = 2),
    dbc.Col(dcc.Dropdown(['Airport', 'Airline', 'Route Type', 'None'], 'Airport', id='color_value_input', multi = False), xl = 2)
    ], justify = "start", style = {"margin-top": "1%"}),
    # html.Div(id='dd-output-container'),
    # # multi = True will cause all outputs to be returned
    # # as a list.
    dcc.Graph(id='pivot_chart'),



    # Top Airlines Graph:
    html.H2(children = "Top Airlines by Traffic Involving at Least 1 US Airport in 2018"),
    dcc.Checklist(
            id = 'top_airlines_graph_show_route_types',
    options={
            'show_route_type': 'Compare by Route Type'
    },
    value=['show_route_type'], style = {"margin-top": "1%"}),

    html.H5(children = "Route Types To Show:", style = {"margin-top": "1%"}),
    dcc.Dropdown(['Domestic', 'International'], ['Domestic','International'], id='top_airlines_graph_route_types', multi = True),

    dbc.Row([dbc.Col(html.H5(children = "Airline Count (Max 100):"), xl = 2),

    dbc.Col(dcc.Input(id="top_airlines_graph_airlines_limit", type="number", value=20, min = 1, size = '5'), xl = 1)
    # See https://dash.plotly.com/dash-core-components/input
    ], justify = "start", style = {"margin-top": "1%"}),



    dbc.Row([
    dbc.Col(html.H5(children = "Airlines to Include:"), xl = 2),
    dbc.Col(dcc.Dropdown(id = "top_airlines_graph_airlines_filter", multi = True), xl = 6),
    ], justify = "start", style = {"margin-top": "1%"}),

    dcc.Graph(
        id='top_airlines_graph',
    ),

    # Top US Hubs:
    html.H2(children = "Top US Airport Hubs:"),
    dbc.Row([
    dbc.Col(html.H5(children = "Hubs to Show (Max 100):"), xl = 2),

    dbc.Col(dcc.Input(id="top_hubs_graph_hubs_limit", type="number", value=20, min = 1, size = '5'), xl = 1),
    # See https://dash.plotly.com/dash-core-components/input
    # regarding the 'size' argument.

    dbc.Col(html.H5(children = "Route Types To Show:"), xl = 2),
    # Note: 'xl' is used here instead of 'width' so that Dash will only apply
    # a width of 1 when the screen size is 'xl' or larger. That way, the column
    # elements will still wrap down for smaller screens (preventing overlap)
    dbc.Col(dcc.Dropdown(['Domestic', 'International'], ['Domestic','International'], id='top_hubs_graph_route_types', multi = True), xl = 3)

    ], justify = 'start', style = {"margin-top": "1%"}), 

    dcc.Graph(
        id = 'top_hubs_graph'),


    # Top Origin Airports for a Selected Airport:
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


# Functions for creating interactive graphs:

# Top airports graph:

# Note: The airports shown on the graph are selected through multiple stages.
# First, the user selects which route types to view (domestic, international,
# or both) and the number of airports to show. Next, the create_top_airports_list
# function (shown below) retrieves a list of the top n airports to show
# based on this criteria. This list is then shown as a multiselect dropdown
# window so that the user can manually remove certain airports. The 
# create_interactive_top_airports_graph then uses this list to determine
# which airports will actually appear on the graph.

# Callback and function that populate an interactive airports filter for the 
# top airports graph:
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
    dest_airport = dest_airport.upper()
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

if read_from_sql == True:
    df_dest_by_origin = pd.read_sql('select * from dest_to_origin', con = elephantsql_engine)
else:
    df_dest_by_origin = pd.read_csv(r'..\dest_to_origin_2018.csv')

# Functions for interactive air traffic graph:

# Determining airports to include:
@app.callback(
    Output("interactive_air_traffic_airports_filter", "options"),
    Output("interactive_air_traffic_airports_filter", "value"),
    Input("interactive_air_traffic_route_types", "value"),
    Input("interactive_air_traffic_airports_limit", "value")
)

def create_airports_list_for_interactive_air_traffic_graph(route_types_to_show, airports_limit):
    data_source = df_airline_airport_pairs.query("Destination_Region == 'Domestic'").copy()
    data_source = data_source.query("Route_Type in @route_types_to_show").copy()

    if airports_limit == None:
        airports_limit = 20
    if ((1 <= airports_limit <= 20) == False):
        airports_limit = 20

    df_airline_airport_pivot = data_source.pivot_table(index = 'Airport', values = 'Passengers', aggfunc = 'sum').sort_values('Passengers', ascending = False).reset_index()
    airports_to_keep = list(df_airline_airport_pivot['Airport'][0:airports_limit].copy())
    return airports_to_keep, airports_to_keep

# Determining airlines to include:
@app.callback(
    Output("interactive_air_traffic_airlines_filter", "options"),
    Output("interactive_air_traffic_airlines_filter", "value"),
    Input("interactive_air_traffic_airlines_limit", "value"),
    Input("interactive_air_traffic_route_types", "value")
)

def create_airlines_list_for_interactive_air_traffic_graph(airlines_limit, route_types_to_show):
    return create_airlines_list(airlines_limit = airlines_limit, route_types_to_show=route_types_to_show, max_airlines_limit=10)


@app.callback(
    Output('pivot_chart', 'figure'),
    Input('pivot_value_input', 'value'),
    Input('color_value_input', 'value'),
    Input('interactive_air_traffic_route_types', 'value'),
    Input('interactive_air_traffic_airlines_filter', 'value'),
    Input('interactive_air_traffic_airports_filter', 'value')
)

def update_chart(pivot_values, color_value, route_types_to_show, airlines_to_graph, airports_to_graph):
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


    # print("Route_Type values to show:", route_types_to_show)
    # print("Airlines to graph:", airlines_to_graph)
    # print("Airports to graph:", airports_to_graph)
    data_source = df_airline_airport_pairs.copy()
    data_source_filtered = data_source.query("Route_Type in @route_types_to_show & Airport in @airports_to_graph & Airline in @airlines_to_graph").copy()
    # print("data_source_filtered:")
    # print(data_source_filtered)



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
        if (color_value != 'None') & (len(data_descriptor_values) > 1):
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

    # There is no need to perform bar grouping if only one pivot variable exists,
    # so the following if/else statement sets barmode to 'relative' in that 
    # case. Otherwise, barmode is set to 'group' in order to simplify 
    # the x axis variables.
    if len(pivot_values) == 1:
        barmode = 'relative'
    
    else:
        barmode = 'group'

    output_histogram = px.histogram(data_source_pivot, x = 'Group', y = 'Passengers', color = None if color_value == 'None' else color_value, barmode = barmode, color_discrete_map=airline_color_map)

    return output_histogram

# Functions for creating top airlines graph:


# Determining airlines to include:
@app.callback(
    Output("top_airlines_graph_airlines_filter", "options"),
    Output("top_airlines_graph_airlines_filter", "value"),
    Input("top_airlines_graph_airlines_limit", "value"),
    Input("top_airlines_graph_route_types", "value")
)

def create_airlines_list_for_top_airlines_graph(airlines_limit, route_types_to_show):
    return create_airlines_list(airlines_limit = airlines_limit, route_types_to_show=route_types_to_show, max_airlines_limit=100)

# Creating the top airlines chart:
@app.callback(
    Output('top_airlines_graph', 'figure'),
    Input('top_airlines_graph_show_route_types', 'value'),
    Input('top_airlines_graph_airlines_filter', 'value'),
    Input('top_airlines_graph_route_types', 'value'),
    )

def create_top_airlines_chart(show_route_types, airline_filter, route_types):
    data_source = df_airline_airport_pairs.copy()
    data_source = data_source.query("Airline in @airline_filter & Route_Type in @route_types")

    # Determining airline ranks (which will be useful for sorting bars after
    # creating a pivot table):
    # Note that these airline ranks are based on passenger traffic within
    # the filtered copy of the pivot table rather than on all passenger traffic.

    df_airline_pivot = data_source.pivot_table(index = 'Airline', values = 'Passengers', aggfunc = 'sum').sort_values('Passengers', ascending = False).reset_index()
    df_airline_pivot['Airline_Rank'] = df_airline_pivot['Passengers'].rank(ascending=False) 
    df_airline_pivot.drop('Passengers', axis = 1, inplace = True) # This 
    # column will get in the way when merging the table with the pivot table 
    # on which the graph will be based.
    # print(df_airline_pivot)

    if 'show_route_type' in show_route_types:
        pivot_index = ['Airline', 'Route_Type']
    else:
        pivot_index = ['Airline'] 
    data_pivot = data_source.pivot_table(index = pivot_index, values = 'Passengers', aggfunc = 'sum').reset_index()
    data_pivot = data_pivot.merge(df_airline_pivot, on = 'Airline')
    
    if 'show_route_type' in show_route_types:
        data_pivot.sort_values(['Airline_Rank', 'Route_Type'], inplace = True)
    else:
        data_pivot.sort_values('Airline_Rank', inplace = True)

    if 'show_route_type' in show_route_types:
        data_pivot['Airline_Route_Pair'] = data_pivot['Airline'] + ' ' + data_pivot['Route_Type']
        x_val = 'Airline_Route_Pair'
    else:
        x_val = 'Airline'

    # print(data_pivot)

    fig_top_airlines = px.histogram(data_pivot, x = x_val, y = 'Passengers', color = 'Airline', color_discrete_map=airline_color_map)
    if 'show_route_type' in show_route_types:
        fig_top_airlines.update_xaxes(categoryorder = 'array', 
    categoryarray = data_pivot['Airline_Route_Pair']) # Reorders bars so that
    # domestic ones will always precede international ones

    return fig_top_airlines

# Top hubs graph:

@app.callback(
    Output('top_hubs_graph', 'figure'),
    Input('top_hubs_graph_hubs_limit', 'value'),
    Input('top_hubs_graph_route_types', 'value')
    )

def generate_top_hubs_graph(hubs_limit, route_types):
    max_hubs_limit = 100
    # print("hubs_limit:",hubs_limit,"route_types:",route_types)

    if hubs_limit == None:
        hubs_limit = max_hubs_limit
    if ((1 <= hubs_limit <= max_hubs_limit) == False):
        hubs_limit = max_hubs_limit
    
    # print("hubs_limit:",hubs_limit)

    data_source = df_airline_airport_pairs.query("Destination_Region == 'Domestic' & Route_Type in @route_types").copy()
    df_top_hubs = data_source.pivot_table(index = ['Airline', 'Airport'], values = 'Passengers', aggfunc = 'sum').reset_index().sort_values('Passengers', ascending = False)
    df_top_hubs['Hub'] = df_top_hubs['Airline'] + ' ' + df_top_hubs['Airport']
    # print(df_top_hubs.iloc[0:hubs_limit, :])
    
    # For some reason, I was receiving an 'Invalid value' error at times
    # when this graph first loaded. LeoWY on the Plotly forums suggested
    # wrapping functions within a try/except block when this occurs,
    # which I did here. (See his/her response
    # at https://community.plotly.com/t/inconsistent-callback-error-updating-scatter-plot/46754/8)

    try: 
        fig_top_hubs = px.histogram(df_top_hubs.iloc[0:hubs_limit, :], x = 'Hub', y = 'Passengers', color = 'Airline', color_discrete_map=airline_color_map)
    except:
        fig_top_hubs = px.histogram(df_top_hubs.iloc[0:hubs_limit, :], x = 'Hub', y = 'Passengers', color = 'Airline', color_discrete_map=airline_color_map)
    fig_top_hubs.update_xaxes(categoryorder = 'total descending') # See https://plotly.com/python/categorical-axes/

    return fig_top_hubs


    # Creating the top airline hubs chart:





if __name__ == '__main__':
    app.run_server(debug=True)
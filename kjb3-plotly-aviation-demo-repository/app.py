# Web dashboard (work in progress)
# Kenneth Burchfiel
# Released under the MIT license


# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# Note: running this program within Visual Studio Code by pressing F5 doesn't appear to work.
# Instead, you need to launch it from Command Prompt or a similar program.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
# from google.cloud import secretmanager
# from google.oauth2 import service_account
import json
import sqlalchemy
# import os
import numpy as np


online_deployment = True # Set to False for local development and debugging
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
df_aaa = pd.read_sql("select * from airports_airlines_aircraft_2018", con = elephantsql_engine)

df_aaa_len = len(df_aaa)

print(len(df_aaa))

# Note: this code was based on: https://dash.plotly.com/layout#more-about-html-components

# https://plotly.com/python/px-arguments/ for more options

# Graphs:
# Top 20 Airports:

df_top_20_airports = pd.read_sql("top_20_airports_by_pax_arrivals_2018", con = elephantsql_engine)

fig_top_20_airports_2018 = px.bar(df_top_20_airports, x="Airport", y="2018_Passenger_Arrivals", title = "Top 20 Airports by Arriving Passengers in 2018")

# Top 20 Airlines:
df_top_20_airlines = pd.read_sql("top_20_airlines_by_passengers_2018", con = elephantsql_engine)
fig_top_20_airlines_2018 = px.bar(df_top_20_airlines, x="Airline", y="Passengers", title = "Top 20 US Airlines in 2018")

# Top 20 US Airports by Airline Share

top_airlines_list = list(df_top_20_airlines['Airline'][0:5])
top_airline_list_as_string = ("|".join(top_airlines_list)) # Converts the airlines in the list to a string value that the following np.where statement can use to create an 'Other' category of airlines

top_20_airports_list = list(df_top_20_airports['Airport'])

df_airline_airport_pairs = pd.read_sql("airline_airport_pairs_2018", con = elephantsql_engine)


df_top_airlines_and_airports = df_airline_airport_pairs.query("Dest_Airport in @top_20_airports_list").copy().reset_index(drop=True)
df_top_airlines_and_airports['Airline'] = np.where(df_top_airlines_and_airports['Airline'].str.contains(top_airline_list_as_string) == False, 'Other', df_top_airlines_and_airports['Airline'])

df_top_airlines_and_airports = df_top_airlines_and_airports.pivot_table(index = ["Airline", "Dest_Airport"], values = "Passengers", aggfunc = "sum").reset_index()

airport_ranks = df_top_20_airports[['Airport', 'Rank']]

df_top_airlines_and_airports = df_top_airlines_and_airports.merge(airport_ranks, left_on = "Dest_Airport", right_on = "Airport")


df_top_airlines_and_airports.sort_values("Rank", inplace = True)

fig_t4_airline_presence_at_t20_airports = px.bar(df_top_airlines_and_airports, x="Dest_Airport", y="Passengers", color="Airline", title="Top 20 US Airports by Airline Share in 2018")






app.layout = html.Div(children=[
    html.H1(children='Sample Dash/Plotly Data Visualization App'),

    html.H3(children='By Kenneth Burchfiel'),

    html.Div(children='''
        This page, which is still a work in progress, shows how Plotly and Dash can be used to visualize data retrieved from a database.
    '''),

    dcc.Graph(id='fig_t4_airline_presence_at_t20_airports',
    figure = fig_t4_airline_presence_at_t20_airports),

    dcc.Graph(
        id='top_20_airports_graph',
        figure=fig_top_20_airports_2018
    ),

    dcc.Graph(
        id='top_20_airlines_graph',
        figure=fig_top_20_airlines_2018
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
## Plotly Demo Program Notes

Kenneth Burchfiel

## Steps I took:

1. I created a new Google Cloud project called 'kjb3-plotly-avdemo' and set up the Google Cloud CLI interface on my computer. (See ['Initializing the gcloud CLI'](https://cloud.google.com/sdk/docs/initializing) for more information.) As instructed by the [Cloud Run setup guide](https://cloud.google.com/run/docs/setup), I enabled the Cloud Run API for this new project. 

2. I then completed the Installation and Layout sections of the [Dash Tutorial](https://dash.plotly.com/installation) in order to familiarize myself with Plotly. As part of this process, I created a folder on my computer called 'kjb3-plotly-aviation-demo-repository' and entered a python file called 'app.py' within that folder. I'll discuss what I entered into app.py below.

3. I also created a new Python environment called 'kbdashdemo.' Using Miniforge and conda, I installed pandas, dash, and jupyter-dash, as recommended in the Dash tutorial. (I also ended up using pip to install gunicorn, as noted below.)

4. I followed the steps shown in Google's [Deploy a Python service to Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service) article, but made a couple changes along the way based on the [Dash Heroku deployment guide](https://dash.plotly.com/deployment#heroku-for-sharing-public-dash-apps-for-free) and on Arturo Tagle Correa's [Deploying Dash to Google Cloud Run in 5 minutes](https://medium.com/kunder/deploying-dash-to-cloud-run-5-minutes-c026eeea46d4) guide. These changes were necessary because the Deploy a Python Service to Cloud Run guide uses a Flask app as its example rather than Dash (which also happens to be based on Flask, I believe).

First, instead of using the main.py file shown in the Google article, I used the app.py example found [within the Layout section of the Plotly tutorial](https://dash.plotly.com/layout#more-about-html-components). I then added  "server = app.server" under "app = Dash(\_\_name\_\_)," as shown in Arturo's guide and Dash's Heroku deployment tutorial. 

Second, I used pip to install gunicorn into my virtual environment as shown in the Heroku deployment guide (although I'm not sure this was necessary, since I also added it to my requirements.txt file.)

Third, to create my requirements.txt file, I simply typed in:

dash

pandas

gunicorn


Fourth, I changed the final part of the Dockerfile example in the Google guide from "main:app" to "app:server", since (1) I was receiving error messages relating to gunicorn's inability to find 'main,' and (2) Arturo's guide showed app:server here as well (See https://medium.com/kunder/deploying-dash-to-cloud-run-5-minutes-c026eeea46d4 ). Note that the Heroku Procfile shown in the Heroku deployment guide also ends in app:server.

5. Once I made these changes, I was able to successfully deploy my app to Cloud Run. I did so by opening my command prompt, navigating to the folder containing my app.py file, and entering:

gcloud run deploy --source .

(Note that the space and period after 'source' are part of the command and must be included.)


When errors arose, I could debug them using my project's log at https://console.cloud.google.com/logs/ .

(Note: I didn't simply follow Arturo's guide because his method involves installing Docker desktop. However, Docker is not free for certain commercial use cases. The above steps did not require that I install Docker desktop.)

6. Next, I connected my Dash app to a small ElephantSQL database. (See elephantsql_database_builder.ipynb for the steps I took to create this database.) Since this process requires both sqlalchemy and psycopg2-binary, I added both of these to my requirements.txt file. (I used psycopg2-binary instead of psycopg to avoid an error message.)

In order to enable Google to access my ElephantSQL database's URL while keeping the value of the URL secure, I enabled the Google Cloud Secret Manager API (see Google Cloud's ["Use secrets"](https://cloud.google.com/run/docs/configuring/secrets) guide for more details) and then entered my ElephantSQL database URL as a new secret. (I did change the 'postgres:' component to 'postgresql:'--see [this link](https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres) for an explanation.

However, simply creating the secret was not sufficient: I also needed to add it to my Cloud Run service. I did so by visiting https://console.cloud.google.com/run for my project; selecting 'Edit & Deploy New Revision'; and then mounting my secret as a volume. (I chose 'projsecrets' as my volume name.) More information about this step can be found in the "Use secrets" guide linked to above.
Note that the Secret Manager Secret Accessor role must be enabled for your service account for your code to work. This is also mentioned in the "Use secrets" guide.
https://cloud.google.com/run/docs/configuring/secrets#access-secret

In order for my Python script to access this secret, I simply needed to open it as I would with any other file. See the code in app.py for an example. (https://stackoverflow.com/questions/68533094/how-do-i-access-mounted-secrets-when-using-google-cloud-run was a helpful resource for this step.)

One limitation with this approach is that the steps would only work when the app was running online. (This is because the file with the secret that the code accesses can only be found online.) However, I got around this limitation by creating an online_deployment Boolean variable within app.py. When set to True (for online deployment), the code would load the variable within its volume on Google; when set to False, the code would instead load this variable from a local file on my computer. There's probably a more elegant way to resolve this discrepancy, but it worked for my use cases.


(Note: As recommended in the use secrets guide, I clicked on my new secret in order to connect it to my project's service account, but it appeared to already be connected.)

As instructed by the ['Using Secret Manager With Python'](https://codelabs.developers.google.com/codelabs/secret-manager-python#3) guide, I then installed the google-cloud-secret-manager library into my kbdashdemo Python environment using pip. I also added google-cloud-secret-manager to my requirements.txt file.

At this point, I had a pretty good foundation for my app: I had a database with statistics; I had means of connecting to the database online and offline; and I had some sample Plotly code that I could adjust to display the items shown within the app.

I'm now working on adding in additional Plotly charts. I hope to introduce more interactive charts in the future (e.g. that allow users to select different values to compare).

Some chart ideas I have in mind include:

* Average flight distance by airplane (this may involve grouping similar airplanes into bins and also creating a widebody/narrowbody category)

* Top 10-20 airlines for a user-selected airport (similar to the graph and table I've included
that show the top origin airports for a user-selected airport)

* Adding at least one corresponding data table for each chart

* Average distance by plane

* A chart in which the user can choose at least 3 comparison variables in order to 
understand a given dataset (e.g. domestic/international traffic for the top 4 airlines
at the top 5 airports. In this case, the comparison variables would be (1) destination 
airport, (2) airline, and (3) domestic/international traffic)

* More filter options for each graph

* A chart showing traffic by airport by year (would be an interesting way to infer
which airports cater to tourists vs. business/VFR traffic)


**Implementing more advanced graphs**

Now that I had created some basic graphs using Plotly, I wanted to incorporate more advanced features (such as interactive filters and comparison choices). However, I knew that I would need to learn more about Plotly and Dash in order to implement these additions.

The [Basic Callbacks](https://dash.plotly.com/basic-callbacks) component of the Dash walkthrough provided a very useful overview of how to implement callbacks.

Next, I reviewed dropdown options on Plotly's [dcc.Dropdown](https://dash.plotly.com/dash-core-components/dropdown) page. 

Using these tools and other resources that I found along the way, I was able to revise my graphs to incorporate more interactive features. However, this revision process is still a work in progress.


## Notes to self:
Next: add in airport, airline, and route type filters for the Interactive Airline Traffic Graph using the methods that you applied for adding route type and airport filters to the Top US Airports by Arrival Traffic in 2018 graph.


1. On Part 5 of the Dash tutorial: https://dash.plotly.com/sharing-data-between-callbacks 

2. To make a graph with selected groupings: you can feed the results of a multi-select dropdown box into pd.pivot_table's index parameter. 

Note that the results of choosing 'NYC', 'MTL', and 'SF' in a multi-value dropdown box equal ['NYC', 'MTL', 'SF']. This could be the argument passed to index = when creating a pivot table.

And then, once the pivot table has been created, you can create a grouped bar chart by just graphing each of the bars individually. (You could also choose some color/stack options for some of them.)

Actually, you could add in additional dropdown menus to choose which variables (if any) to group (as different colors) using the color px.bar parameter, and which (if any) to stack!

So when you have some free time, try drafting a chart like this, perhaps as a separate Dash app first (this could involve reading a .csv file) and then as part of your new app.

Alternatively, you could simply use the dash-pivottable code, which looks very robust. (See https://dash.gallery/dash-pivottable/)

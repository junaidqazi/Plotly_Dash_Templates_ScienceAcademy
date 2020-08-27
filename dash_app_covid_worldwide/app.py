#!/usr/bin/env python
# coding: utf-8

# # Global CoVID19 Statistics.
# Author: __Dr. Junaid Qazi, PhD__

# #### Let's read the data directly from the website/source
# [Website link to the datasets](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide)<br>
# As of, August 19, 2020, the data files (`.csv` and `.xlsx`) are also available on [this link in my personal git repository](https://raw.githubusercontent.com/junaidqazi/datasets-practice-qazi/master/COVID-19-geographic-disbtribution-worldwide-2020-08-19.csv)

# In[1]:


import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
#import dash_table
import dash_bootstrap_components as dbc


# In[2]:


################################################################################################################
# initializing dash app
external_stylesheets = [dbc.themes.SKETCHY]#YETI]#CYBORG]#CERULEAN]#LUMEN]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
# More Style Sheets from Dash Bootstrap Components:
#https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/


# In[3]:


# The utility function given below can be saved as .py file and we can import for use
def get_data_in_df():#url):
    """
    This utility function returns the inputs for our dashboard.
    Output is: (dataFrame, data start date, data last updated data)
    The function tries to read the most updated data from
    https://opendata.ecdc.europa.eu/covid19/casedistribution/csv. In case, the server is down, the data will
    be read from the csv file on git, this data may not be the latest version.
    git url is given below:
    https://raw.githubusercontent.com/junaidqazi/DataSets_Practice_ScienceAcademy/master/COVID-19-geographic-disbtribution-worldwide-2020-08-19.csv
    """
    try:
        print("Reading data from the original source 'opendata.europa.eu'..... !")
        df = pd.read_csv("https://opendata.ecdc.europa.eu/covid19/casedistribution/csv")
        print("Data read from the source 'opendata.europa.eu'")
    except:
        print("The original data source is either down and not responding, or, the provided url is not correct.")
        print("Reading data file stored in the git account and it may not be the latest updated version.")
        git_url="https://raw.githubusercontent.com/junaidqazi/DataSets_Practice_ScienceAcademy/master/COVID-19-geographic-disbtribution-worldwide-2020-08-19.csv"
        #git_url=url
        df=pd.read_csv(git_url)
        print("Data read from the git, this may not be the updated version.")
    print("Done reading.....!")
    print("Dateframe 'df' is available for work....!")

    ##########################
    #Data Preparation
    # Dropping the column with more than 5% missing data.
    # missing_data_pct_values_above_threshold = [x for x in missing_data_info.values.tolist() if x > 5.0 ]
    try:
        df = df.drop("Cumulative_number_for_14_days_of_COVID-19_cases_per_100000", axis=1)#, inplace = True)
        #print("the requested column is dropped.")
    except:
        pass

    # Excluding all the observations from Japan Cruise Ship.
    df = df[df.continentExp != "Other"]

    #Now the only column which has missing data is geoId.
    #Let's check their country territory id and code for these observations.
    df.fillna(value = 'NMB', inplace = True)

    # This might be a good idea to set data as index column
    # let's first change the name from dateRep to date and then set it as index
    try:
        df.rename(columns={"dateRep": "date"}, inplace=True)
        # setting date as index
        df.set_index(["date"], inplace=True)
    except:
        pass

    #print("Converting date index to datetime...!")
    df.index = pd.to_datetime(df.index)#
    df.index = pd.to_datetime(df.index, format="%d/%m/%y")
    df = df.sort_index()

    # For easier comparisions, cases and deaths per million
    df["Cases Per Million"] = df["cases"]/df["popData2019"]*1000000
    df["Deaths Per Million"] = df["deaths"]/df["popData2019"]*1000000

    # Need to put this date on dashboard
    start_date_data = df.index.min().date() #df.head(1).index[0].date()
    last_date_data = df.index.max().date()  #df.tail(1).index[0].date()

    # Getting list of all the countries in the data
    available_countries = df["countriesAndTerritories"].unique()
    return (df, start_date_data, last_date_data, available_countries)


# In[4]:


data = get_data_in_df()
df=data[0]
start_date_data=data[1]
last_date_data=data[2]
available_countries=data[3]


# **********
# **********
# *************
# *************
# #  `html` components and required callbacks for our dashboard.
# **https://www.w3schools.com/ is a wonderful resource for `html` and `css`.**

# *************
# ## BLOCK 1
# * Dashboard name and company logo
# * Data collection dates
# * Dropdown for selection reported cases and/or reported deaths
#
# **Dashboard name and company logo**

# In[5]:


# 1: Adding a row with logo and title for the dashboard
comp_1_title_logo = dbc.Row([
    dbc.Col(html.H1(children='CoVID19 Trends Worldwide'),
            className=["mt-4","mb-2"]), #margin top/bottom/left/right-# size (0->5 & auto)
    dbc.Col(html.A([html.Img(src='/assets/Logo_SA.png',
                             style={'width' : '40%',
                                    'float' : 'right',
                                    'position' : 'relative',
                                    'padding-top' : 10,
                                    'padding-right' : 10})],
                   href='http://www.scienceacademy.ca',
                   target="_blank", # target to open new browser
                   className=["mt-4","mb-2"]))])


# **Data collection dates**

# In[6]:


# 2: Adding a row with start data
comp_2_start_date = dbc.Row([
    dbc.Col(html.H4(children='Data Collection Start Date: {}'.format(start_date_data)),
            className=["mt-2","mb-2"])])
# 3: Adding a row with latest update date
comp_3_latest_data_updated_on = dbc.Row([
    dbc.Col(html.H4(children='Latest Update: {}'.format(last_date_data)),
            className=["mt-2","mb-2"])]) #margin-bottom-4
# more on bootstram 4 utilities ==> https://www.w3schools.com/bootstrap4/bootstrap_utilities.asp


# **`Dropdown` for selection reported cases and/or reported deaths.**

# In[7]:


# 4: Adding dropdown to choose between cases or deaths
comp_4_dropdown_for_cases_or_deaths = dcc.Dropdown(
    id='choice_top_dropdown_cases_deaths_column',
    #Selection between 'Cases Per Million' and 'Cases Per Million' columns
    options=[{'label': 'Cases Per Million Individuals', 'value': 'Cases Per Million'},
             {'label': 'Deaths Per Million Individuals', 'value': 'Deaths Per Million'}],
    # Default column that will appear in the dropdown with respective label in the options
    value='Cases Per Million',
    style={'width': '50%'})
    #,multi=True) # parameter to get multiple selections in dropdown


# *************
# ### BLOCK 2
# * Pie charts by continents and related components

# **Some data manipulation for the plots.**

# **Task 1:** <br>
# *Get the daily reported numbers by continent*
#
# * To get the daily reported number by continent, we need to perform following steps:
#
#     * 1: group by continent and date ==> `grooupby(["continentExp", "date"])`
#     * 2: compute sum on grouped data ==> `.sum()`
#     * 3: good to reorder by ascending dates ==> `.sort_values(["date"], ascending = True)`
#
#

# In[8]:


# Creating a function to get the daily reported numbers by continent
def daily_reported_nums_continent(data):
    """
    data = the dataframe df we have after some cleaning
    Output will be after following steps:
        1: group by continent and date ==> grooupby(["continentExp", "date"])
        2: compute sum on grouped data ==> .sum()
        3: good to reorder by ascending dates ==> .sort_values(["date"], ascending = True)
    """
    daily_sum_continent = data.groupby(["continentExp","date"]).sum()
    daily_sum_continent = daily_sum_continent.sort_values(["date"], ascending = True)
    return daily_sum_continent
df_daily_reported_sum = daily_reported_nums_continent(df)


# In[9]:


# daily sum of reported numbers by continent in sorted order by date
#df2 = df.groupby(['continentExp','date']).sum().sort_values(['date'], ascending = True)
#daily_sum_continent = df.groupby(['continentExp','date']).sum().sort_values(['date'], ascending = True)


# **Task:** <br>
# *Get the total reported numbers on the last updated day with respect to continents.*
# * We have the daily reported number from `daily_reported_nums_continent()` by continent in sorted by `date`. Grab the `tail(5)` --  as we have 5 continents in the data --  and `reset_index()` to get `continentExp` and `date` columns.

# In[10]:


# last day sum of reported numbers by continent
#df3 = df.groupby(['continentExp','date']).sum().sort_values(['date'], ascending = True).tail(5).reset_index()
def last_day_total_nums_continent(data):
    last_day_sum_continent = daily_reported_nums_continent(data) # function call with in the function
    last_day_sum_continent = last_day_sum_continent.tail(5).reset_index()
    return last_day_sum_continent

df_last_day_sum_continent = last_day_total_nums_continent(df)


# **Task:** *Total reported numbers by continent since last update*
# * simply group the data by continent and get the sum ==> `df.groupby(['continentExp']).sum()`

# In[11]:


# total number reported by continent till last update
#df4 = df.groupby(['continentExp']).sum() # total number since the start date of data
def total_nums_reported_by_continent(data):
    """
    Simply group the data by continent and get the sum
    """
    return data.groupby(["continentExp"]).sum()

df_total_reported_by_continent = total_nums_reported_by_continent(df)


# **`Main header` and the titles for pie charts by continent**

# In[12]:


# 5: Adding a row for main header for the Pie charts -- Continents
comp_5_main_header_pie_charts = dbc.Row([
    dbc.Col(dbc.Card(html.H3(
        children='Pie Charts Showing Distribution By Continent (Per Million Individuals)',
        className="text-center text-light bg-dark"),
                     body=True,
                     color="dark"),
            className=["mt-2","mb-2"])])
# 6: Adding a row for the sub-titles for Pie charts  -- Continents
comp_6_sub_titles_pie_charts = dbc.Row([
    dbc.Col(html.H5(
        children='Total Reported Number (Per Million) on {} Only'.format(last_date_data),
        className="text-center"),
            width=6,
            className=["mt-2","mb-2"]),
    dbc.Col(html.H5(
        children='Total Reported Numbers (Per Million) Since {}'.format(start_date_data),
        className="text-center"),
            width=6,
            className=["mt-2","mb-2"])])


# **`Pie charts by continents` and the callbacks**

# In[13]:


# 7: Adding a row for the Pie charts  -- Continents
comp_7_pie_charts = dbc.Row([
    dbc.Col(dcc.Graph(
        id='pie_last_day_numbers_only'),
            width=6,
            className=["mt-2","mb-2"]), # <shift+tab> to know more about id
    dbc.Col(dcc.Graph(
        id='pie_total_numbers_since_start_data'),
            width=6,
            className=["mt-2","mb-2"])])

# Callback for the pie charts
@app.callback(
    [Output(component_id='pie_last_day_numbers_only', component_property='figure'),
     Output(component_id='pie_total_numbers_since_start_data', component_property='figure')],
    [Input(component_id='choice_top_dropdown_cases_deaths_column', component_property='value')])
def pie_charts_by_continents(choice_top_dropdown_cases_deaths_column):

    # 1st Output
    fig1 = go.Figure(data=[go.Pie(labels=df_last_day_sum_continent['continentExp'],
                                 values=df_last_day_sum_continent[choice_top_dropdown_cases_deaths_column])])
    # Updating Figure Layout
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0.05)',#'white' #rgba => rgb colors, with alpha/opacity (0-1)
                       plot_bgcolor='rgba(0,0,0,0.05)',
                       template = "seaborn",
                       margin=dict(l=30,r=30,t=30,b=30))#,pad=10))

    # 2nd Output
    fig2 = go.Figure(data=[go.Pie(labels=df_total_reported_by_continent.index,
                                  values=df_total_reported_by_continent[choice_top_dropdown_cases_deaths_column])])
    # Updating Figure Layout
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0.05)',
                       plot_bgcolor='rgba(0,0,0,0.05)',
                       template = "seaborn",
                       margin=dict(l=30,r=30,t=30,b=30))#,pad=10))
    return fig1, fig2
######################################################################
# More on layout: https://plotly.com/python/setting-graph-size/


# *************
# ### BLOCK 3
# * Line plots (reported numbers and cumulative sum) by continents
#
# **`Header and the titles` for the line plots by continent**

# In[14]:


# 8: Adding a row for main header for the line plots -- Continents
comp_8_main_header_line_plots_continents = dbc.Row([
    dbc.Col(dbc.Card(html.H3(
        children='Statistics By Continent (Per Million Individuals)',
        className="text-center text-light bg-dark"),
                     body=True,
                     color="dark"),
            className=["mt-2","mb-2"])])

# 9: Adding a row for the sub-titles for line plots  -- Continents
comp_9_sub_titles_for_line_plots_continents = dbc.Row([
    dbc.Col(html.H5(
        children='Daily Reported Numbers {}'.format(start_date_data),
        className="text-center"),
            width=6,
            className=["mt-2","mb-2"]),
    dbc.Col(html.H5(
        children='Cumulative Sum (CUMSUM) Since {}'.format(start_date_data),
        className="text-center"),
            width=6,
            className=["mt-2","mb-2"])])


# **`Line plots by continent` along with the callbacks**
#
# **Need to do some data manipulation**

# In[15]:


# Cumulative sum of cases and/or deaths
def cum_sum_continent(data):
    """
    function returns the dataframe with cumulative sum by continent
    steps:
        group by continent & date then sum
        reset the index to get continent and date column
        group the data again on continent and get cumulative sum on cases and deaths
        """
    continent_cumsum = data.groupby(["continentExp","date"]).sum()
    continent_cumsum = continent_cumsum.reset_index()
    continent_cumsum["Cases Per Million"] = continent_cumsum.groupby(["continentExp"]
                                                                    )["Cases Per Million"].apply(
        lambda x: x.cumsum())
    continent_cumsum["Deaths Per Million"] = continent_cumsum.groupby(["continentExp"]
                                                                     )["Deaths Per Million"].apply(
        lambda x: x.cumsum())
    return continent_cumsum

df_cumsum_continent = cum_sum_continent(df)


# In[16]:


# 10: Adding a row for the line plots  -- Continents
comp_10_line_plots_continents = dbc.Row([
    dbc.Col(dcc.Graph(
        id='line_continent_daily_reported_numbers'),
            width=6,
            className=["mt-2","mb-2"]),
    dbc.Col(dcc.Graph(
        id='line_continent_daily_cumsum'),
            width=6,
            className=["mt-2","mb-2"])])

@app.callback(
    [Output('line_continent_daily_reported_numbers', 'figure'),
     Output('line_continent_daily_cumsum', 'figure')],
    [Input('choice_top_dropdown_cases_deaths_column', 'value')])
def line_plots_by_continents(choice_top_dropdown_cases_deaths_column):
    df_daily_reported_sum_pivoted = pd.pivot_table(df_daily_reported_sum,#dff,
                         values=choice_top_dropdown_cases_deaths_column,
                         index=['date'],
                         columns='continentExp')

    ##############################--Pie plot for daily reported numbers by continent--###########################
    fig1 = go.Figure()
    for col in df_daily_reported_sum_pivoted.columns:
        fig1.add_trace(go.Scatter(x=df_daily_reported_sum_pivoted.index,
                                  y=df_daily_reported_sum_pivoted[col].values,
                                  name=col,
                                  mode='markers+lines'))
    # Updating Figure Layout
    fig1.update_layout(yaxis_title="Reported Numbers (Per Million)",
                       paper_bgcolor='rgba(0,0,0,0.05)',
                       plot_bgcolor='rgba(0,0,0,0.05)',
                       template = "seaborn",
                       margin=dict(l=30,r=30,t=30,b=30))

    ##############################--Pie plot:CUMSUM of reported numbers by continent--###########################
    df_cumsum_pivoted = pd.pivot_table(df_cumsum_continent,#dff2,
                          values=choice_top_dropdown_cases_deaths_column,
                          index=['date'],
                          columns='continentExp')

    fig2 = go.Figure()
    for col in df_cumsum_pivoted.columns:
        fig2.add_trace(go.Scatter(x=df_cumsum_pivoted.index,
                                  y=df_cumsum_pivoted[col].values,
                                  name=col,
                                  mode='markers+lines'))
    # Updating Figure Layout
    fig2.update_layout(yaxis_title="Reported Numbers (Per Million)",
                       paper_bgcolor='rgba(0,0,0,0.05)',
                       plot_bgcolor='rgba(0,0,0,0.05)',
                       template = "seaborn",
                       margin=dict(l=30,r=30,t=30,b=30))
    return fig1, fig2


# *************
# ### BLOCK 4
# * Line plots by selected countries (reported number and cumulative sum) and related components
#
# **`Main header for line plots by countries` for comparisons.**

# In[17]:


# 11: Adding a row for the main header for Country comparisions line plots
comp_11_main_header_line_plots_country = dbc.Row([
    dbc.Col(dbc.Card(html.H3(
        children='Statistics by Country (Per Million Individuals)',
        className="text-center text-light bg-dark"),
                     body=True,
                     color="dark"),
            className=["mt-2","mb-2"])])


# **Dropdown for country selection**

# In[18]:


# 12: Adding Dropdown For Country selection to get Line Plots for comparisions
comp_12_dropdown_country_selection = dcc.Dropdown(
    id='countries',
    options=[{'label': i, 'value': i} for i in available_countries],
    value=['Qatar', 'Kuwait', 'Bahrain', 'Saudi_Arabia', 'United_Arab_Emirates'],
    multi=True,
    style={'width': '70%', 'margin-left': '5px'})


# **`Titles and line plots` comparing selected countries.**

# In[19]:


# 13: Title daily plot -- Adding a Row for countries seleted in the dropdown in no 12 (above) -- Daily
comp_13_line_plots_countries = dbc.Row([
    dbc.Col(html.H5(
        children="Daily Reported Numbers by Countries Since {}".format(start_date_data),
        className="text-center"),
            className=["mt-2","mb-2"])])

# 14: Daily plot -- Adding a row with country comparision line plot
comp_14_county_line_plots = dcc.Graph(
    id="line_country_daily_reported_numbers",
    className=["mt-2","mb-2"])

# 15: Title CUMSUM -- Adding a Row for the line plots of countries seleted in dropdown (# 12 above)
comp_15_sub_title_country_cumsum_line_plot = dbc.Row([
    dbc.Col(html.H5(
        children="Cumulative Sum (CUMSUM) of Reported Numbers by Countries Since {}".format(start_date_data),
        className="text-center"),
            className=["mt-2","mb-2"])])

# 16: Plot CUMSUM -- Adding a row with CUMSUM plot countries
comp_16_country_cumsum_line_plot = dcc.Graph(
    id="line_country_daily_cumsum",
    className=["mt-2","mb-2"])

# Cases and/or Deaths Comparisions Between Countries
@app.callback(
    [Output("line_country_daily_reported_numbers", "figure"),
     Output("line_country_daily_cumsum", "figure")],
    [Input("choice_top_dropdown_cases_deaths_column", "value"),
     Input("countries", "value")])
def line_plots_by_countries(choice_top_dropdown_cases_deaths_column, countries_name):
    # data selection based on the country selection in dropdown comp_12*
    df_country_select = df[df.countriesAndTerritories.isin(countries_name)]

    ##############################--line plot of daily numbers by country--###########################
    # Creating a pivot table
    df_country_select_pivoted = pd.pivot_table(df_country_select,
                                               values=choice_top_dropdown_cases_deaths_column,
                                               index=["date"],
                                               columns="countriesAndTerritories")
    # Figure daily reported line plot by country
    fig1 = go.Figure()
    for county_name in df_country_select_pivoted.columns:
        fig1.add_trace(go.Scatter(x=df_country_select_pivoted.index,
                                  y=df_country_select_pivoted[county_name].values,
                                  name=county_name,
                                  mode="markers+lines"))

    # In case, you want to update the layout
    fig1.update_layout(yaxis_title="Reported Numbers (Per Million)",
                       paper_bgcolor="rgba(0,0,0,0.05)",
                       plot_bgcolor="rgba(0,0,0,0.05)",
                       template = "seaborn",
                       margin=dict(l=30,r=30,t=30,b=30))

    #####################################--cumsum line plot by country--###########################
    # Preparing data for cumsum plot by country
    df_country_cumsum = df_country_select.groupby(["countriesAndTerritories", "date"]).sum()
    df_country_cumsum = df_country_cumsum.reset_index()
    df_country_cumsum["Cases Per Million"] = df_country_cumsum.groupby(["countriesAndTerritories"]
                                                                      )["Cases Per Million"].apply(
        lambda x: x.cumsum())
    df_country_cumsum["Deaths Per Million"] = df_country_cumsum.groupby(["countriesAndTerritories"]
                                                                       )["Deaths Per Million"].apply(
        lambda x: x.cumsum())

    df_country_cumsum_pivoted = pd.pivot_table(df_country_cumsum,
                                               values=choice_top_dropdown_cases_deaths_column,
                                               index=["date"],
                                               columns="countriesAndTerritories")

    # Figure cumsum plot by country
    fig2 = go.Figure()
    for country_name in df_country_cumsum_pivoted.columns:
        fig2.add_trace(go.Scatter(x=df_country_cumsum_pivoted.index,
                                  y=df_country_cumsum_pivoted[country_name].values,
                                  name=country_name,
                                  mode="markers+lines"))

        # Updating layout of the figure
        fig2.update_layout(yaxis_title="Reported Numbers (Per Million)",
                           paper_bgcolor="rgba(0,0,0,0.05)",
                           plot_bgcolor="rgba(0,0,0,0.05)",
                           template = "seaborn",
                           margin=dict(l=30,r=30,t=30,b=30))
    return fig1, fig2


# *************
# ### BLOCK 5
# * Thanks, acknowledgements, reference request, contact etc....!
#
# **`Thanks` and acknowledgements.**

# In[20]:


# 17: Adding special thanks, contact etc along with the link to open in new browser window
comp_17_thanks_Acknowledgements = html.A("Thank you for using this template, interested to get one for your data? contact us...!",
                                         href="http://www.scienceacademy.ca",
                                         target="_blank", # to open in the new webpage
                                         style={"float": "right"},
                                         className=["mt-5","mb-2"])


# *************
# *************
# *************
# *************
# # `html` component container and `app` Layout

# In[21]:


# Layout along with all html components for the dashboard
html_comp_container = dbc.Container([comp_1_title_logo,
                                     comp_2_start_date,
                                     comp_3_latest_data_updated_on,
                                     comp_4_dropdown_for_cases_or_deaths,
                                     comp_5_main_header_pie_charts,
                                     comp_6_sub_titles_pie_charts,
                                     comp_7_pie_charts,
                                     comp_8_main_header_line_plots_continents,
                                     comp_9_sub_titles_for_line_plots_continents,
                                     comp_10_line_plots_continents,
                                     comp_11_main_header_line_plots_country,
                                     comp_12_dropdown_country_selection,
                                     comp_13_line_plots_countries,
                                     comp_14_county_line_plots,
                                     comp_15_sub_title_country_cumsum_line_plot,
                                     comp_16_country_cumsum_line_plot,
                                     comp_17_thanks_Acknowledgements])
layout = html.Div([html_comp_container])
app.layout = layout


# # The main

# In[22]:


if __name__ == '__main__':
    app.run_server()#True)
    #app.run_server(debug=True) # good to set True when running on terminal and/or deploying


# In[23]:


# Deploy on cloud -- heroku is the free option


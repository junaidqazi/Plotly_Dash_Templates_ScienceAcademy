#!/usr/bin/env python
# coding: utf-8

# ## Part 2: Building a dashboard using Python` (Plotly & Dash)` and deploying on local server
# ***Created for learning by Junaid Qazi, PhD for Ministry of Health, Saudi Arabia.***
# Well, the dashboard is good and running on the local server (default is `localhost at port 8050`).
#
# ### Putting the code from Part 1 in a single cell to export as `"app.py"` and run on command line/terminal.
# Let's put all the code above in a single cell save as `app.py` file. We can then run this python file using `cmd` or `terminal` and it will bring up the dashboard on localhost, command is: (`terminal$ python3 file_name.py`).

# In[ ]:

#Deployed on heroku: https://iris-sci-acd-01.herokuapp.com/

import numpy as np
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html

#############################################################################################################
# I am reading iris dataset from my git repo of datasets
url = "https://raw.githubusercontent.com/junaidqazi/DataSets_Practice_ScienceAcademy/master/Iris.csv"
iris_df = pd.read_csv(url)
iris_df[["NoNeed", "FlowerName"]] =  iris_df.Species.str.split('-', expand = True)
iris_df.drop(['Species', 'NoNeed'], axis=1, inplace = True)#.head(2)

#############################################################################################################
# Style sheet and app initilization
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Activate the line below for cloud deployment
server = app.server

#############################################################################################################
# Plotly plots for the dashboard
scatter_1 = px.scatter(
    data_frame=iris_df, # <shift+tab> for the docstring
    x="SepalLengthCm",
    y="PetalLengthCm",
    color="FlowerName",
    size="PetalWidthCm", #[.03]*150,

    # I want to change the names on the labels, need to pass a dictionary
    labels={
        "SepalLengthCm": "Sepal Length (cm)",
        "PetalLengthCm": "Petal Width (cm)",
        "FlowerName": "Species of Iris:",
        "PetalWidthCm":"Petal Width"},
    #title="Sepal Length Vs Petal Length. Size reflects the Petel Width. (All in cm)" #default position
                   )
# If you want to put title in the center.
scatter_1.update_layout(
    title={
        'text': "Sepal Length Vs Petal Length. Size reflects the Petel Width. (All in cm)",
        'y':.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

#********************************
scatter_2 = px.scatter(data_frame=iris_df,
           x="SepalWidthCm",
           y="PetalWidthCm",
           color="FlowerName",
           size="PetalLengthCm", #[1.0]*150,

           title="sepal width (cm) vs petal width (cm) color-encoded by flower type")

#********************************
hist_1 = px.histogram(data_frame=iris_df,
             x="SepalLengthCm",
             color="FlowerName",
             title="Distributions of sepal length (cm) color-encoded by flower name")

#********************************
box_1 = px.box(data_frame=iris_df,
           x="FlowerName",
           y="SepalWidthCm",
           color="FlowerName",
           title="concentration of sepal width (cm) by flower types")

#********************************
pie_1 = px.pie(
    iris_df, names='FlowerName',
    title="concentration of sepal width (cm) by flower types")

#*******************************
# For correlation heatmap, we need to do some extra stuf....!
import re # regular expression
# Let's get corr dataframe and yes, we don't need Id column, leave it for the moment..!
df_corr = iris_df.drop(['Id'], axis = 1).corr()
#df_corr = iris_df.corr()
x=[]; y=[]
for num in range(len(df_corr)):
    #x.append(" ".join(re.findall('[A-Z][^A-Z]*', list(iris_df.corr().index)[num])[0:-1]))
    #y.append(" ".join(re.findall('[A-Z][^A-Z]*', list(iris_df.corr().columns)[num])[0:-1]))
    x.append(" ".join(re.findall('[A-Z][^A-Z]*', df_corr.index[num])[0:-1]))
    y.append(" ".join(re.findall('[A-Z][^A-Z]*', df_corr.columns[num])[0:-1]))
# The above block of the code was required here to

heatmap_corr = px.imshow(df_corr,
         labels={'x': 'Features', 'y': 'Features', 'color': 'Correlation'},
         #labels=dict(x="Features", y="Features", color="Correlation"), # same as above line
                   x=x,
                   y=y,
                   title = "Correlation Heatmap, this is just an example to show how to get such plots......!  "
                  )
#heatmap_corr.update_xaxes(side="top") # To change the x-axes label position
heatmap_corr.update_layout(
    title={
        'text': 'Example Correlation Heatmap to show how to get such plots......! ',
        'y':.90,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

#############################################################################################################
# Embedding plots into dcc components
graph1 = dcc.Graph(
    id='graph1',
    figure=scatter_1,
    className="six columns")
#
graph2 = dcc.Graph(id='graph2', figure=scatter_2, className="six columns")
graph3 = dcc.Graph(id='graph3', figure=hist_1, className="six columns")
graph4 = dcc.Graph(id='graph4', figure=box_1, className="six columns")
graph5 = dcc.Graph(id='graph5', figure=pie_1, className="six columns")
graph6 = dcc.Graph(id='graph6', figure=heatmap_corr, className="six columns")#"nine columns")

#############################################################################################################
# Creating html components/layout for our dashboard
# Adding Company Logo
comp_logo = html.A([html.Img(
    src='/assets/Logo_SA.png',
    style={
        'height' : '15%',
        'width' : '15%',
        'float' : 'right',
        'position' : 'relative',
        'padding-top' : 10,
        'padding-right' : 10
    })
                   ], href='http://www.scienceacademy.ca', target="_blank") # To open in the new page
# Try this one as well ==> Adding company logo
#comp_logo = html.Img(src="/assets/Logo_SA.png", #srcSet='www.scienceacademy.ca',#height="30px",
#                     style={'width':'15%', 'margin':30, 'float':'right'})#'vertical-align': 'text-top'})
# more on: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img

# Notice the size "H1" for the title, the main header
dashboard_title = html.H1(
    children="IRIS Dataset Analysis - Public Dataset")

# Now the size is "H3" for the header header
overview = html.H3(
    children="This dashboard providee overview on the benchmark IRIS dataset. \
    We can add project background or something interesting here. \
    This dashboard providee overview on the benchmark IRIS dataset.\
    Just some random text.................!")

# Now the size is "H4" for our captions
caption_1 = html.H4(
    children="Caption 1: Explain your figure, copmare plots and write some related text. \
    Figure caption......??? \
    This is just some random text.................!")

caption_2 = html.H4(
    children="Caption 2: Explain your figure, copmare plots and write some related text. \
    Figure caption......??? \
    This is just some random text.................!")

caption_3 = html.H4(
    children="Caption 3: Explain your figure, copmare plots and write some related text. \
    Figure caption......??? \
    This is just some random text.................!")

# Conclusions, we can go for size "H3"
conclusions = html.H3(
    children="Conclusions: Some conclusions for the executives........!!\
    This is just some random text.................!")

# The "A" below is a wrapper for the tag <a> HTML5 element which is used to define hyperlink.
thanks = html.A("Special thanks and Acknowledgements.",
                href="http://www.scienceacademy.ca",
                target="_blank", # to open in the new webpage
                style={'float': 'right'})

# We are planning to add six graphs in our dashboard, two graphs in each row.
# For this purpose, we need to create three rows of `html.Div` components.
row1 = html.Div(children=[graph1, graph3, caption_1])
row2 = html.Div(children=[graph2, graph4, caption_2])
row3 = html.Div(children=[graph5, graph6, caption_3])

#############################################################################################################
# Defining our dashboard app layout
layout = html.Div(
    children=[comp_logo, dashboard_title, overview,
              row1, row2, row3,
              conclusions,thanks])#,
#style={"text-align": "center"}) # to center align everything

# Setting layout of the dDashboard
# We need to set layout as the layout of the dashboard app, already initialized above in the beginning.
app.layout = layout

#############################################################################################################
# Our main function for python .py file
if __name__ == "__main__":
    app.run_server(debug=True)#False) # True giving error for notebook deployment
#    app.run_server(port=3003)# incase, you need to change the port

# more on deploying Dash app
# https://dash.plotly.com/deployment


# ***Next is deployment on the server, it is sometime not trivial because of installations....!***

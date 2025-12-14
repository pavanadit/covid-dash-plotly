import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output

import plotly.graph_objects as go

import requests 
from bs4 import BeautifulSoup 
import os 
import numpy as np 
#import matplotlib.pyplot as plt
import pandas as pd

import json  
import datetime



app = dash.Dash(__name__, external_stylesheets =[dbc.themes.BOOTSTRAP])
app.title = 'COVID APP'
server = app.server

BLUE = 'rgb(100,110,251)'
GREEN = 'rgb(2,204,151)'
RED = 'rgb(240,85,59)'


STATE = ['Kerala', 'Delhi', 'Telangana', 'Rajasthan', 'Haryana','Uttar Pradesh', 'Ladakh', 'Tamil Nadu', 'Jammu and Kashmir',
       'Karnataka', 'Maharashtra', 'Punjab', 'Andhra Pradesh','Uttarakhand', 'Odisha', 'Puducherry', 'West Bengal', 'Chandigarh',
       'Chhattisgarh', 'Gujarat', 'Himachal Pradesh', 'Madhya Pradesh','Bihar', 'Manipur', 'Mizoram', 'Goa',
       'Andaman and Nicobar Islands', 'Jharkhand', 'Assam','Arunachal Pradesh', 'Dadra and Nagar Haveli', 'Tripura']

print("Sau************")

'''
 IN THIS CODE WE EXPLORE:
 1] USE NEW DASH daq COMPONENT                      ==> Directly updating value without callback
 2] df and dd DATAFRAME IS GLOBALLY CALLED         
 3] getDistrictLevelData() FUNCTION IS BLOCKING PREPROCESSING       ==> Hence decalred outside function  
 4] DYNAMICALLY PARSED STATE's INTO DROPDOWN
 5] HANDLED LINE CHART WITH CALLBACK
 6] Added config={"displaylogo": False} to rmv dash logo
 7] added app title
 8] Added Navbar and Footer, hovermode='x'(on axis by default)
 9] Flag image and card like styling
'''
def init():
    
    #df3 =  requests.get("https://api.covid19india.org/data.json").json()
    x = datetime.datetime.now()

    print(x.year)
    
    
    return x.year


def getdata():
    
    State = []
    Active = []
    Recovered = []
    Confirmed = []
    Deaths = []
    stats = []
    
    XX= requests.get("https://covid-19india-api.herokuapp.com/v2.0/state_data").json()
    
    for x in XX[1].get('state_data'):
        State.append(x.get("state"))
        Active.append(x.get("active"))
        Recovered.append(x.get("recovered"))
        Confirmed.append(x.get("confirmed"))
        Deaths.append(x.get("deaths"))
    
    data = {'State': State,'Active': Active, 'Cured/Discharge': Recovered, 'Deaths': Deaths, 'Total_Confirmed_cases' : Confirmed }
    df = pd.DataFrame(data)  
    print("x")
    return df

############### Data ###################################
#df = getdata()

#dd
#Inside of function it was workinf in BLOCKING FASHION.. 
data = requests.get("https://api.covid19india.org/v2/state_district_wise.json").json()

states = []
districts = []
confirmed = []
for state in data:
    
    XXX = state.get('state')
    
    for dist in state.get('districtData'):
        #print(dist)
        states.append(XXX)
        YYY = dist.get('district')
        ZZZ = dist.get('confirmed')
        districts.append(YYY)
        confirmed.append(ZZZ)
    

d = {'states': states, 'districts': districts, 'Confirmed':confirmed}

dd = pd.DataFrame(data=d)

## has 2 network call
#df3 =  requests.get("https://api.covid19india.org/data.json").json()

############### function df###################################



def piePlotStats():

    df = getdata()
    
    colors = [BLUE, GREEN, RED]
    #df = getdata()
    labels = ['Active','Recovered','Deaths']
    #values = [df['Active'].iloc[-1],df['Cured/Discharge'].iloc[-1],df['Deaths'].iloc[-1]]
    values = [df['Active'].sum(axis = 0),df['Cured/Discharge'].sum(axis = 0),df['Deaths'].sum(axis = 0)]
    layout = go.Layout(title='<b>Total Cases</b>')
    # pull is given as a fraction of the pie radius
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0, 0.2, 0],marker=dict(colors=colors),sort=False)],layout=layout) 

    return fig

def rateofGrowthLinePlot():

    df3 =  requests.get("https://api.covid19india.org/data.json").json()

    date = []
    totConf = []
    totRecovered= []
    totDeath= []
    for x in df3:
        cases = df3.get("cases_time_series")
    for c in cases[-62:]:#21
        date.append(c.get("date"))#x
        totConf.append(c.get("totalconfirmed"))#y Conf
        totRecovered.append(c.get("totalrecovered"))
        totDeath.append(c.get("totaldeceased"))
    
    fig = go.Figure()
    #set color throuout
    fig.add_trace(go.Scatter(x=date, y=totConf,mode='lines+markers',name="Confirmed",connectgaps=True,marker=dict(color='rgb(231,107,243)'))),
    fig.add_trace(go.Scatter(x=date,y=totRecovered,mode='lines+markers', name="Recovered",connectgaps=True,marker=dict(color='rgb(2,204,151)')))
    fig.add_trace(go.Scatter(x=date,y=totDeath,mode='lines+markers', name="Deaths",connectgaps=True,marker=dict(color='rgb(240,85,59)')))

    fig.update_layout(xaxis_tickangle=-45,hovermode='x',title="<b>All cases [2 Months]</b>")
    
    return fig


def dailyConfirmedCase():

    df3 =  requests.get("https://api.covid19india.org/data.json").json()

    #weekly
    date = []
    dailyC = []
    for x in df3:
        cases = df3.get("cases_time_series")
    for c in cases[-21:]:
        date.append(c.get("date"))#x
        dailyC.append(c.get("dailyconfirmed"))#y
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=date,
        y=dailyC,
        name='wWekly Cases',
        marker_color='LightSeaGreen' #'rgb(231,107,243)'
    ))
    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(barmode='group', xaxis_tickangle=-45,title="<b>New Cases [3 Weeks]</b>")
    return fig

def countStackPlot():

    df = getdata()
    x=  df["State"]#[:-2]
    #colors = ['rgb(2,204,151)', 'light blue', 'lred']

    #######################print("C", df["Active"] )
    fig = go.Figure(go.Bar(x=x, y=df["Active"], name='Active', marker_color='rgb(100,110,251)'))
    fig.add_trace(go.Bar(x=x, y=df["Cured/Discharge"], name='Cured/Discharge', marker_color='rgb(2,204,151)'))
    fig.add_trace(go.Bar(x=x, y=df["Deaths"], name='Deaths', marker_color='rgb(240,85,59)'))
    fig.update_layout(barmode='stack',hovermode='x', xaxis_tickangle=-25,xaxis={'categoryorder':'total descending'},title="<b>Statewise Cases</b>")

    return fig

############### function df3###################################

############################################

footer = dbc.Row(dbc.Col(html.P("Data from MOHFW website & other credible Sources",style={ "text-align" : "right","color":"black"}))
            ,style={"background-color": "#108DE4","border":"0px black solid","padding": "10px",  "box-shadow": "5px 5px 5px  #888888"}
)

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [   #dbc.Col(dbc.NavbarBrand("COVID-19 Analytic Dashboard", className="ml-2")),
                    #dbc.Col(html.Img(src="https://drive.google.com/file/d/1yskVaZ0lk5p8aRc5bvLMnfjpaHggfcUM/view?usp=sharing", height="40px")),
                    dbc.Col(    html.H2(" COVID-19 Analytic Dashboard"))
                ],
                align="center",
                no_gutters=True,
            )
        )
    ],
    color="primary",
    dark=True,
    style={ "text-align" : "left","color":"white","background-color": "#108DE4","border":"0px black solid","padding": "10px",  "box-shadow": "5px 5px 5px  #888888"}
)

def get_layout():
    return html.Div([
        navbar,
      
        # DIRECT updating value here without call back
        dbc.Row([ #MAIN ROW
            
            dbc.Col([
                    html.H5("Confirmed"),
                    daq.LEDDisplay(#init()
                            value= getdata()['Total_Confirmed_cases'].sum(axis = 0),#getdata()['Total_Confirmed_cases'].iloc[-1], #dataMeter()[0],#pd.to_numeric(df["Confirmed"]).sum(),
                            color= "rgb(231,107,243)" #"#0000ff"
                        )  
            ],width=3, lg=3, md=4,sm=6,xs=12 ),

            dbc.Col([
                    html.H5("Active"),
                    daq.LEDDisplay(
                            value=  getdata()['Active'].sum(axis = 0), #getdata()['Active'].iloc[-1], #dataMeter()[0],#pd.to_numeric(df["Confirmed"]).sum(),
                            color= "rgb(100,110,251)" #"#0000ff"
                        )  
            ],width=3, lg=3, md=4,sm=6,xs=12),

            dbc.Col([
                    html.H5("Recovered"),
                    daq.LEDDisplay(
                            value= getdata()['Cured/Discharge'].sum(axis = 0), #getdata()['Cured/Discharge'].iloc[-1], #dataMeter()[2],#pd.to_numeric(df["Death"]).sum(),
                            color= 'rgb(2,204,151)' #"#00ff00"
                        )  
            ],width=3, lg=3, md=4,sm=6,xs=12),

            dbc.Col([
                    html.H5("Deaths"),
                    daq.LEDDisplay(
                            value= getdata()['Deaths'].sum(axis = 0),  #getdata()['Deaths'].iloc[-1],  #dataMeter()[1],#pd.to_numeric(df["Cured"]).sum(),
                            color= 'rgb(240,85,59)' #"#ff0000",
                        )  
            ],width=3, lg=3, md=4, sm=6, xs=12)


        ],no_gutters = True,justify="center",style={"border":"0px black solid","padding": "10px",  "box-shadow": "5px 5px 5px #888888"}),

        # 1st div
         dbc.Row([

            dbc.Col([
                #html.H5("Total Cases ",style={ "text-align" : "center" } ),             
                # GRAPH
                dcc.Graph(id="my-pie-plot",figure=piePlotStats(),config={"displaylogo": False})
            ],width=4, lg=4, md=12, sm=12, xs=12),

            dbc.Col([
                                                                    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #html.H5("All cases [2 Months] ",style={ "text-align" : "center" } ),             
                # GRAPH
                dcc.Graph(id="my-rateofGrowthLinePlot",figure=rateofGrowthLinePlot(),config={"displaylogo": False} )
            ],width=8,lg=8, md=12, sm=12,  xs=12)

        ],no_gutters = False, style={"border":"0px black solid","padding": "10px",  "box-shadow": "5px 5px 5px #888888"}),    

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        dbc.Row([

           dbc.Col([
                #html.H5("New Cases [3 Weeks] ",style={ "text-align" : "center" } ),             
                # GRAPH
                dcc.Graph(id="my-dailyConfirmedCase",figure=dailyConfirmedCase(),config={"displaylogo": False})
            ], width=4, lg=4, md=12, sm=12,  xs=12),

            dbc.Col([
                                                                 # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #html.H5("Statewise Cases",style={ "text-align" : "center" } ),             
                # GRAPH
                dcc.Graph(id="my-count-plot",figure=countStackPlot(),config={"displaylogo": False} )
            ],width=8,lg=8, md=12, sm=12,  xs=12)

        ],no_gutters = False, style={"border":"0px black solid","padding": "10px",  "box-shadow": "5px 5px 5px #888888"} ),  
        
        # 2nd Div
                
        dbc.Row(
            dbc.Col([

                html.H5("Districtwise Confirm cases",style={ "text-align" : "center" } ),
                dcc.Dropdown(id='my-dropdown-state',
                        options=[{'label': i, 'value': i} for i in STATE],
                        value= 'Kerala'),
                #Graph
                dcc.Graph(id='my-distlevel-plot',config={"displaylogo": False} )
            ]
        ), no_gutters=False,style={"border":"0px black solid","padding": "10px",  "box-shadow": "5px 5px 5px  #888888"}),       

        dbc.Row(
            dbc.Col(
                    footer
            ),no_gutters=False,style={"border":"0px black solid","padding": "10px",  "box-shadow": "5px 5px 5px  #888888"})
    ])

app.layout =  get_layout


#GRAPH
@app.callback(
    Output(component_id='my-distlevel-plot', component_property='figure'),
    [Input(component_id='my-dropdown-state', component_property='value')]
)
def update_districtLevelPlot(input_value):
    

    X = dd[dd['states']== input_value]["districts"]
    Y= dd[dd['states']== input_value]["Confirmed"]

    fig = go.Figure()
      #fig.add_trace(go.Scatter(x=X, y=Y,mode='lines+markers',name='Kerala',line=dict(color='firebrick', width=4, dash='dash')))
    fig.add_trace(go.Scatter(x=X, y=Y,mode='lines+markers',line_color='rgb(231,107,243)',fillcolor='rgba(231,107,243,0.2)',name='Kerala'))
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False,)  # Turn off reloader if inside Jupyter

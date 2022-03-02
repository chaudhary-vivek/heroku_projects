import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from mc4 import return_unique1
from mc4 import pie
from mc4 import return_finalfig
from mc4 import run_simulation
from dash.dependencies import Input, Output
from flask import Flask
from dash_utils import make_card
from statistics import mean
import plotly.express as px
import plotly.graph_objects as go

server = Flask(__name__)

app = dash.Dash(__name__,server = server ,meta_tags=[{ "content": "width=device-width"}], external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = 'Robust Supply Chain Network Design Using Monte Carlo Simulation'

# Importing manufacturing variable costs
manvar_costs = pd.read_excel('data/variable costs.xlsx', index_col = 0)
# Importing freight costs
freight_costs = pd.read_excel('data/freight costs.xlsx', index_col = 0)
fc = freight_costs.reset_index(level=0)
# Calculating total cost by adding manufacturing cost and freight cost
var_cost = freight_costs/1000 + manvar_costs 
# Factory Fixed Costs
fixed_costs = pd.read_excel('data/fixed cost.xlsx', index_col = 0)
fxc = fixed_costs.reset_index(level=0)
# Importing geographical data for summary
geo_df = pd.read_excel('data/geo-data.xlsx', index_col = 0)
# Two types of plants: Low Capacity and High Capacity Plant
cap = pd.read_excel('data/capacity.xlsx', index_col = 0)
# Demand by Market
demand = pd.read_excel('data/demand.xlsx', index_col = 0)
# Importing latituds and longitude
location = pd.read_excel('data/location_df.xlsx', index_col = 0)
location = location.reset_index(level=0)
# Importing cost matrix as a linear table
cmatrix = pd.read_excel('data/matrix.xlsx', index_col = 0)
cmatrix = cmatrix.reset_index(level=0)

#  Summary choropleth plot
summary_choropleth = px.choropleth(geo_df, locations='country',
                    color="demand", 
                    #hover_name="country", # column to add to hover information
                    hover_data=["high production capacity", "low production capacity", "high production fixed cost", "low production fixed cost"],
                    color_continuous_scale=px.colors.sequential.Plasma)

# Transport choropleth cost
cost_choropleth = go.Figure()
cost_choropleth.add_trace(go.Scattergeo(
    showlegend = False,
    locationmode = 'ISO-3',
    lon = location['long'],
    lat = location['lat'],
    text = location['loc'],
    mode = 'markers',
    marker = dict(
        size = 9,
        color = 'rgb(255, 0, 0)',
        line = dict(
            width = 3,
            color = 'rgba(68, 68, 68, 0)'
        )
    )))
paths = []
for i in range(len(cmatrix)):
    cost_choropleth.add_trace(
        go.Scattergeo(
            showlegend = True,
            lon = [cmatrix['fromlong'][i], cmatrix['tolong'][i]],
            lat = [cmatrix['fromlat'][i], cmatrix['tolat'][i]],
            mode = 'lines',            
            line = dict(width = 1,color = 'red'),
            #hover_data=["from", "to", "freight cost", "variable cost"]
            name=cmatrix['hover'][i]           
        )
    )
cost_choropleth.update_layout(
    hoverlabel_align = 'right')
                

app.layout = html.Div([
    html.Div([
        html.H4('Robust Supply Chain Network Design Using Monte Carlo Simulation'),
    ], style={'width': '100%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),   
    dbc.Row(        
        [dbc.Col(make_card('Case details', 'primary', 
                           html.P([
        '1. Company X has production facilites in Brazil, Germany, India, Japan, and USA', html.Br(),'2. Each production facility can produce at either 500 units/week or 1500 units/week', html.Br(),
                                                                    '3. Fixed cost of production at each location is given in table below', html.Br(),
                                                                    '4. Each plant produces a different family of products', html.Br(),
                                                                    '5. Company X has customers in Brazil, Germany, India, Japan, and USA ', html.Br(),
                                                                    '6.The forecast demand for all five customer locations is given in adjoining chart', html.Br(),
                                                                    '7. The cost of transportation from each production facility location to customer location is given in chart below', html.Br(),
                                                                    '8.  However, the demand is uncertain', html.Br(),
                                                                    '9. Company X wants to know which plants are to be operated and at what capacity? ', html.Br(),
                                                                    
                                                                    ]),           
                      )),
         dbc.Col(make_card('Hover of shaded countries for more details for Demand, Production Cost, and Production Capacity', 'primary',dcc.Graph(id = 'summary-choropleth', figure = summary_choropleth)))                
             ]),
    dbc.Row(
            make_card('Freight and variable cost details','primary',dcc.Graph(id = 'line-choropleth', figure = cost_choropleth))          
               ),   
    dbc.Row([dbc.Col(make_card('Enter desired CV of demand to run simulation: (try 0.3, 0.4, 0.5 etc)', 'primary', dcc.Input(id="input1", type="text", placeholder="", value=0.4) )), 
             dbc.Col(html.Div(id='card1'))]),
    dbc.Row(make_card('Robustness of top 20 supply chain networks in 50 simulaitons','primary',dcc.Graph(id = 'pie'))),  
    dbc.Row(make_card('Production facilities in most robust supply chain network (hover for details) ','primary',dcc.Graph(id = 'Final_figure'))),
    
    html.Div(html.H6('Vivek Chaudhary'), style={'display': 'inline-block', 'width': '100%', 'textAlign': 'center', "float": 'center'}),
    html.Div([
        html.A([
            html.Img(
                #src='http://pngimg.com/uploads/github/github_PNG84.png',
                src=app.get_asset_url('m.png'),
                style={
                    'height': '8%',
                    'width': '8%',
                    'float': 'center',
                    'position': 'relative',
                    'padding-top': 0,
                    'padding-right': 0
                })
        ], href='https://medium.com/@vivek-v-chaudhary',  style={'display': 'inline-block', 'width': '50%', 'textAlign': 'right'}),
        html.A([
            html.Img(
                src=app.get_asset_url('lin.png'),
                style={
                    'height': '7%',
                    'width': '7%',
                    'float': 'center',
                    'position': 'relative',
                    'padding-top': 0,
                    'padding-right': 0
                })
        ], href='https://www.linkedin.com/in/vivek-chaudhary-b2b6b416a/',
            style={'display': 'inline-block', 'width': '50%', 'textAlign': 'left'}),
    ])
    ])


@app.callback(Output('card1', 'children'),
              Input('input1', 'value'))
def refresh_casrds(input1):
    input1 = int(input1)
    objective  = run_simulation(input1)[0]
    objective = mean(objective)
    objective = round(objective, 2)
    objective = objective/1000000
    objective = round(objective, 2)
    #objective = str(objective)
    card1 = make_card('Average total cost in 50 simulations in Million USD ', 'primary', objective)
    return card1

@app.callback(Output('pie', 'figure'),
              Input('input1', 'value'))
def refresh_cards(input1):    
    fig = pie(input1)   
    return fig
    
@app.callback(Output('Final_figure', 'figure'),
              Input('input1', 'value'))
def refresh_cards(input1):    
    fig = return_finalfig(input1)   
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)



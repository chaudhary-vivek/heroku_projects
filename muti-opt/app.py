import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from flask import Flask
from sc import optim
from sc_graph import plot
from output_graph import output_plot
from output_graph_2 import output_plot_2
from dash_utils import make_card
from jade_slevel import distance_bands

server = Flask(__name__)

app = dash.Dash(__name__,server = server ,meta_tags=[{ "content": "width=device-width"}], external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = 'Supply chain optimization dashboard'
app.layout = html.Div([

    html.Div([
        html.H4('Multi echelon network optimization'),
    ], style={'width': '100%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
    html.Hr(),
    dbc.Row([dbc.Col(make_card('Case details', 'primary', html.P([
        'Complete case can be found in "Supply chain network design" by Watson & Hoormann', html.Br(),'"JADE paint and covering inc." has a three echelon supply chain', html.Br(),
                                                                    'The company has plants in 4 locations in the USA', html.Br(),
                                                                    'Each plant produces a different family of products', html.Br(),
                                                                    'The production capacity of each plant is fixed and given', html.Br(),
                                                                    'There are 25 possible locations for warehouses in the country', html.Br(),
                                                                    'Their customers are located in 100 locations across US', html.Br(),
                                                                    'The demand at each customer node is fixed on basis of historical data', html.Br(),
                                                                    'Minimum transportation charge per tonne is $10', html.Br(),
                                                                    'Cost of transportation from plant to warehouse is TL at $0.07 per tonne per mile ', html.Br(),
                                                                    'Cost of transportation from warehouse to customer is LTL at $0.12 per tonne per mile ', html.Br(),
                                                                    'In interest of computation time, fixed costs are considered to be $0', html.Br(),
                                                                    "Scroll down to Linear programming details for details of the linear programming model", html.Br(),
                                                                    ]),
                      )), dbc.Col(dcc.Graph(id = 'graph'))]),
    dbc.Row([dbc.Col(make_card('Enter no. of warehouses below: (try 2, 3, 4 etc. Because of limitations of the free platform, runtime of higher number of warehouses may be long)', 'primary', dcc.Input(id="input1", type="text", placeholder="", value=1) ))]),
    dbc.Row([dbc.Col(html.Div(id="card")),dbc.Col(html.Div(id="card1")), dbc.Col(html.Div(id="card2")), dbc.Col(html.Div(id="card3")),dbc.Col(html.Div(id="card4"))]),
    dbc.Row([dbc.Col(dcc.Graph(id='output_graph_2'))]),
    dbc.Row([dbc.Col(dcc.Graph(id='output_graph'))]),
    dbc.Row([ dbc.Col(make_card("Linear programming details", 'primary', html.P(
        ['The objective function is : Total cost = ΣTransportation cost from plant to warehouse + ΣTransportation cost from warehouse to customers + ΣFixed costs', html.Br(),
         'Constraint 1 : Every customer should be served by a warehouse', html.Br(),
'Constraint 2 : Plants cannot ship more than their capacity', html.Br(),
'Constraint 3 : Warehouses cant inventory more than their capacity', html.Br(),
'Constraint 4 : No warehouse can ship more than its inventory', html.Br(),
'Constraint 5 : One customer cannot be served by two warehouses', html.Br(),
'Constraint 6 : Every warehouse should serve at least one customer', html.Br(),
'Constraint 7 : The customer demand cannot be negative', html.Br(),
'Constraint 8 : The production in plants cannot be negative', html.Br(),
'Constraint 9 : The inventory at each warehouse should be greater than 0', html.Br(),

         ]),
                                                               ))]),

    html.Div(html.H6('Vivek Chaudhary, SIBM Pune'), style={'display': 'inline-block', 'width': '100%', 'textAlign': 'center', "float": 'center'}),
    html.Div([
        html.A([
            html.Img(
                #src='http://pngimg.com/uploads/github/github_PNG84.png',
                src=app.get_asset_url('git.png'),
                style={
                    'height': '7%',
                    'width': '7%',
                    'float': 'center',
                    'position': 'relative',
                    'padding-top': 0,
                    'padding-right': 0
                })
        ], href='https://github.com/chaudhary-vivek',  style={'display': 'inline-block', 'width': '49%', 'textAlign': 'right'}),

        html.A([
            html.Img(
                #src='https://cdn3.iconfinder.com/data/icons/2018-social-media-logotypes/1000/2018_social_media_popular_app_logo_linkedin-512.png',
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
            style={'display': 'inline-block', 'width': '49%', 'textAlign': 'left'}),
    ]),
])

@app.callback([Output('card1', 'children'), Output('card2', 'children'), Output('card3', 'children'), Output('card4', 'children')],
              [Input('input1', 'value')])
def refresh_cards(input1):
    input1 = int(input1)
    b1, b2, b3, b4 = distance_bands(input1)


    card1 = make_card('Demand in 200 miles', 'secondary', b1)
    card2 = make_card('Demand in 400 miles', 'secondary', b2)
    card3 = make_card('Demand in 800 miles', 'secondary', b3)
    card4 = make_card('Demand in 1600 miles', 'secondary', b4)
    return card1, card2, card3, card4

@app.callback(Output('card', 'children'),
              [Input('input1', 'value')])
def refresh_cards(input1):
    input1 = int(input1)
    df = optim(input1)[3]
    df = round((df/1000000),0)
    card = make_card('Total cost (million USD)', 'secondary', df)
    return card



@app.callback(Output('output_graph', 'figure'),
              [Input('input1', 'value')])
def refresh_cards(input1):
    input1 = int(input1)
    fig = output_plot(input1)
    return fig

@app.callback(Output('graph', 'figure'),
              [Input('input1', 'value')])
def refresh_cards(input1):
    input1 = int(input1)
    fig = plot(input1)
    return fig

@app.callback(Output('output_graph_2', 'figure'),
              [Input('input1', 'value')])
def refresh_cards(input1):
    input1 = int(input1)
    fig = output_plot_2(input1)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)



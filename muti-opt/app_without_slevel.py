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

server = Flask(__name__)

app = dash.Dash(__name__,server = server ,meta_tags=[{ "content": "width=device-width"}], external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = 'Supply chain optimization dashboard'
app.layout = html.Div([

    html.Div([
        html.H4('Multi echelon network optimization'),
    ], style={'width': '100%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
    html.Hr(),
    dbc.Row([dbc.Col(make_card('Case brief', 'primary', html.P(['JADE paint and covering has a three echelon supply chain', html.Br(),
                                                                    'The company has plants in 4 locations in the USA', html.Br(),
                                                                    'Each plant produces a different family of products', html.Br(),
                                                                    'There are 25 possible locations for warehouses in the country', html.Br(),
                                                                    'Their customers are located in 100 locations across US', html.Br(),
                                                                    'Cost of transportation from plant to warehouse is TL at $0.07 per tonne per mile ', html.Br(),
                                                                    'Cost of transportation from warehouse to customer is LTL at $0.12 per tonne per mile ', html.Br(),
                                                                    'The management has to reduce the transportation cost ', html.Br(),
                                                                    ]),
                      )), dbc.Col(dcc.Graph(id = 'graph'))]),
    dbc.Row([dbc.Col(make_card('Enter no. of warehouses (try 2, 3, 4 etc.)', 'primary', dcc.Input(id="input1", type="text", placeholder="", value=1) )), dbc.Col(html.Div(id="card"))]),
    dbc.Row([dbc.Col(dcc.Graph(id='output_graph_2'))]),
    dbc.Row([dbc.Col(dcc.Graph(id='output_graph'))]),
    dbc.Row([ dbc.Col(make_card("Author's notes", 'primary', html.P(
        ['The complete case can be found in "Supply chain network design" by Watson, Hoormann, Caccioppi and Jayaraman', html.Br(),
         'The cost of transportation should be compared with total cost of setting up warehouses for decision making', html.Br(),
          'The linear programming problem was solved using "pulp" library in Python', html.Br(),
            'The linear programming problem was solved using "pulp" library in Python', html.Br(),
         'Because of limitations of the platform, calculations with higher no. of warehouses may take longer', html.Br(),

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

@app.callback(Output('card', 'children'),
              [Input('input1', 'value')])
def refresh_cards(input1):
    input1 = int(input1)
    df = optim(input1)[3]
    df = round((df/1000000),0)
    card = make_card('Total cost of supply chain (fixed + variable) in million USD', 'secondary', df)
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
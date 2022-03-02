import dash
import dash_core_components as dcc
import dash_html_components as html
from tickers import dropitems
from dash.dependencies import Output, Input
import plotly.express as px
from flask import Flask
import dash_bootstrap_components as dbc
from weights import weights
from monte_carlo import mote_carlo
from risk_return import risk_return
from dash_utils import make_card
from percentiles import percentile


server = Flask(__name__)

app = dash.Dash(__name__,server = server ,meta_tags=[{ "content": "width=device-width"}], external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = 'Portfolio optimization and VaR dashboard'

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H4('Portfolio optimization and VaR Dashboard'),
            # First let users choose stocks
        ], style={'width': '100%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),

        # First let users choose stocks
    ], style={'width': '100%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
    dbc.Row([dbc.Col(html.P('Choose stock tickers from the drop-down or start typing ticker for suggestions')), dbc.Col( dcc.Dropdown(
                        id='ticker_dropdown',
                        options=dropitems,
                        multi=True,
                        value=['AAPL','AMZN', 'TSLA', 'MSFT'],
                        placeholder="Select four stocks"
                    ))]),
    html.Hr(),
    html.Div([
             dcc.Graph(id='pie')
        ], style={'width': '48%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
        html.Div([
            dcc.Graph(id='hist')
        ], style={'width': '49%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),

    dbc.Row([dbc.Col(html.Div(id="Annual_Risk")), dbc.Col(html.Div(id="Annual_Return")), dbc.Col(html.Div(id="Sharpe_ratio")),dbc.Col(html.Div(id="var"))]),
    html.Hr(),
    html.Div(make_card("Author's notes ", "secondary", html.P(['500 simulations were run for next 365 days, higher number of simulations can be run depending on hardware constraints',html.Br(), 'All figures are for portfolio with maximum Sharpe ratio',html.Br(), 'This optimization of portfolio was carried out using Markowitz efficient frontier theorem']))),
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

## Callback for pie chart
@app.callback(
    Output('pie', 'figure'),
    Input('ticker_dropdown', 'value'))
def update_output(value):
    x = weights(value)
    piechart=px.pie(
            values= x,
            names= value,
            hole=.3, title= 'Portfolio optimized for maximum Sharpe ratio'
            )
    return piechart

@app.callback(
    Output('hist', 'figure'),
    Input('ticker_dropdown', 'value'))
def update_hist(ticker_dropdown):
    data = mote_carlo(ticker_dropdown)
    fig = px.histogram(data, nbins=60, title=  'Frequency distribution of average returns per day in year')
    fig.update_layout(showlegend=False)
    return fig

@app.callback([
    Output('Annual_Risk', 'children'), Output('Annual_Return', 'children'), Output('Sharpe_ratio', 'children')],
    Input('ticker_dropdown', 'value'))
def update_hist(ticker_dropdown):
    outputs = risk_return(ticker_dropdown)
    risk = outputs[1]
    returns = outputs[0]
    sharpe = outputs[2]
    card = make_card("Expected annual volatility ", "primary", risk)
    card2= make_card("Expected annual returns ", "primary", returns)
    card3 = make_card("Sharpe ratio ", "primary", sharpe)
    return card, card2, card3

@app.callback(
    Output('var', 'children'),
    Input('ticker_dropdown', 'value'))
def update_hist(ticker_dropdown):
    var = percentile(ticker_dropdown)
    card = make_card("VaR ", "primary", var)
    return card

if __name__ == '__main__':
    app.run_server(debug=True)
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from flask import Flask
from financial_table import get_financial_table
from tickers import dropitems
from warning_table import get_warnings
import plotly_express as px
from bounds import  get_bounds
from pandas_datareader import data as web
from datetime import datetime as dt
from dash_utils import make_card
from bounds_limits import get_bound_limits

server = Flask(__name__)

app = dash.Dash(__name__,server = server ,meta_tags=[{ "content": "width=device-width"}], external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = 'Ratio analysis and valuation dashboard'
app.layout = html.Div([
    html.Div([
        html.H4('Company valuation and ratio analysis Dashboard'),
        # First let users choose stocks
    ], style={'width': '100%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
    html.Hr(),
    dbc.Row([dbc.Col(html.P('Choose a stock ticker from the drop-down or start typing ticker for suggestions')), dbc.Col( dcc.Dropdown(
                    id='ticker_dropdown',
                    options=dropitems,
                    multi=False,
                    value='AAPL',
                    placeholder="Select four stocks"
                ))]),
    dbc.Row([dbc.Col(html.Div(id="fin-table"))]),
    dbc.Row([
        dbc.Col(html.Div(id="fin-warning"))
    ]),
    html.Div([
         dcc.Graph(id='my-graph')
    ], style={'width': '48%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
    html.Div([
        dcc.Graph(id='hist_graph')
    ], style={'width': '49%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
    html.Div(id = 'cards'),
    html.Hr(),
    dbc.Row([dbc.Col(make_card("Warning criteria ", "secondary", html.P(['The EPS should have grown in last FY', html.Br(),'ROE should be gerater than 15%',  html.Br(),'ROA should be greater than 7%', html.Br(),'Long term debt should be less than 5 times assets', html.Br(),'Equity should be more than debt', html.Br(),'Interest coverage ratio should be greater than 3'])))
        , dbc.Col(make_card("Assumptions", "secondary", html.P(['Market risk premium is 0.059',html.Br(),'Tax rate is 0.3',html.Br(),'Risk free return rate is equal to 10 year treasury yields'])))
        ]),

    html.Hr(),
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

## Callback for ratio table
@app.callback(Output('cards', 'children'),
              [Input('ticker_dropdown', 'value')])
def refresh_cards(ticker_dropdown):
    lower, upper = get_bound_limits(ticker_dropdown)
    cards = dbc.Row([dbc.Col(make_card("Minimum valuation ", "secondary", lower))
        , dbc.Col(make_card("Maximum valuation", "secondary", upper))
        , dbc.Col(make_card("Level of Confidence", "secondary", '95%'))
             ])  # end cards list
    return cards

@app.callback(
    Output('fin-table', 'children'),
        Input('ticker_dropdown', 'value'))
def update_output(ticker_dropdown):
    df = get_financial_table(ticker_dropdown)
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    return table

@app.callback(
    Output('fin-warning', 'children'),
        Input('ticker_dropdown', 'value'))
def update_output(ticker_dropdown):
    df = get_warnings(ticker_dropdown)
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    return table
# For the stocks graph
@app.callback(Output('my-graph', 'figure'), [Input('ticker_dropdown', 'value')])
def update_graph(selected_dropdown_value):
    global stockpricedf # Needed to modify global copy of stockpricedf
    stockpricedf = web.DataReader(
        selected_dropdown_value.strip(), data_source='yahoo',
        start=dt(2013, 1, 1), end=dt.now())
    return {
        'data': [{
            'x': stockpricedf.index,
            'y': stockpricedf.Close
        }], 'layout': {'title': 'Closing prices since 2013 in USD'}
    }
@app.callback(
    Output('hist_graph', 'figure'),
         Input('ticker_dropdown', 'value')
         )
def update_output(ticker_dropdown):
    data = get_bounds(ticker_dropdown)
    fig = px.histogram(data, nbins=30, title= ''
                                              'valuation of company using Monte-Carlo simulation of DCF')
    fig.update_layout(showlegend=False)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pickle
import bnlearn as bn
from flask import Flask

#%%

# Defining function which returns the quartiles of input variables
def return_quartiles(r0,r1,r2,r3,r4,r5,r6,r7,r8,r9):
    # Loading the pickled quartile_df
    dffile = open('quartile_df_pickle', 'rb')
    quartile_df = pickle.load(dffile)
    dffile.close()
    # Checking v0
    if r0 <= quartile_df.iloc[0,0]:
        v0 = 1
    elif r0 <= quartile_df.iloc[0,1]:
        v0 =2
    elif r0 <= quartile_df.iloc[0,2]:
        v0 =3
    else:
        v0 = 4
    # Checking v1
    if r1 <= quartile_df.iloc[1,0]:
        v1 = 1
    elif r1 <= quartile_df.iloc[1,1]:
        v1 =2
    elif r1 <= quartile_df.iloc[1,2]:
        v1 =3
    else:
        v1 = 4
    # Checking v2
    if r2 <= quartile_df.iloc[2,0]:
        v2 = 1
    elif r2 <= quartile_df.iloc[2,1]:
        v2 =2
    elif r2 <= quartile_df.iloc[2,2]:
        v2 =3
    else:
        v2 = 4
    # Checking v3
    if r3 <= quartile_df.iloc[3,0]:
        v3 = 1
    elif r3 <= quartile_df.iloc[3,1]:
        v3 =2
    elif r3 <= quartile_df.iloc[3,2]:
        v3 =3
    else:
        v3 = 4
    # Checking v4
    if r4 <= quartile_df.iloc[4,0]:
        v4 = 1
    elif r4 <= quartile_df.iloc[4,1]:
        v4 =2
    elif r4 <= quartile_df.iloc[4,2]:
        v4 =3
    else:
        v4 = 4
    # Checking v5
    if r5 <= quartile_df.iloc[5,0]:
        v5 = 1
    elif r5 <= quartile_df.iloc[5,1]:
        v5 =2
    elif r5 <= quartile_df.iloc[5,2]:
        v5 =3
    else:
        v5 = 4
    # Checking v6
    if r6 <= quartile_df.iloc[6,0]:
        v6 = 1
    elif r6 <= quartile_df.iloc[6,1]:
        v6 =2
    elif r6 <= quartile_df.iloc[6,2]:
        v6 =3
    else:
        v6 = 4
    # Checking v7
    if r7 <= quartile_df.iloc[7,0]:
        v7 = 1
    elif r7 <= quartile_df.iloc[7,1]:
        v7 =2
    elif r7 <= quartile_df.iloc[7,2]:
        v7 =3
    else:
        v7 = 4
    # Checking v8
    if r8 <= quartile_df.iloc[8,0]:
        v8 = 1
    elif r8 <= quartile_df.iloc[8,1]:
        v8 =2
    elif r8 <= quartile_df.iloc[8,2]:
        v8 =3
    else:
        v8 = 4
    # Checking v9
    if r9 <= quartile_df.iloc[9,0]:
        v9 = 1
    elif r9 <= quartile_df.iloc[9,1]:
        v9 =2
    elif r9 <= quartile_df.iloc[9,2]:
        v9 =3
    else:
        v9 = 4
    return v0,v1,v2,v3,v4,v5,v6,v7,v8,v9



# Defining the function which returns the probability of fault
def get_probab(r0,r1,r2,r3,r4,r5,r6,r7,r8,r9):
# Getting values of quartiles of input variables
    v0,v1,v2,v3,v4,v5,v6,v7,v8,v9 = return_quartiles(r0,r1,r2,r3,r4,r5,r6,r7,r8,r9)
    # Loading the pickled model
    mlefile = open('mle_pickle', 'rb')
    model_mle = pickle.load(mlefile)
    mlefile.close()
    # Creating the probability of fault
    query = bn.inference.fit(model_mle, variables=['Fault'], evidence={'Reactor cooling water flow valve': v0,
                                                                       'Reactor cooling water outlet temp':v2,
                                                                       'Total feed flow stripper valve':v2,
                                                                       'Stripper steam valve':v3,
                                                                       'A feed stream':v4,
                                                                       'A feed flow valve':v5,
                                                                       'Stripper steam flow':v6,
                                                                       'Condenser cooling water outlet temp':v7,
                                                                       'Reactor temp':v8,
                                                                       'Stripper temperature':v9 })
    probab_of_fault = query.df.iloc[1,1]
    probab_of_fault = round(probab_of_fault*100,2)
    return(probab_of_fault)



server = Flask(__name__)

app = dash.Dash(__name__,server = server ,meta_tags=[{ "content": "width=device-width"}], external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = 'Fault Prediction - TEP'
          

app.layout = html.Div([
    html.Div([html.H4('Predicting fault in a chemical manufacturing process with Random Forests and Bayesian Networks'),], style={'width': '100%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
    html.Hr(),
    dbc.Row([dbc.Col(html.P('Reactor cooling water flow valve : ')),dbc.Col( dcc.Input(id="input0", type="text", placeholder="", value=41)), dbc.Col(html.P('Reactor cooling water outlet temp : ')),dbc.Col( dcc.Input(id="input1", type="text", placeholder="", value=94.6))]),
    dbc.Row([dbc.Col(html.P('Total feed flow stripper valve : ')),dbc.Col( dcc.Input(id="input2", type="text", placeholder="", value=59)), dbc.Col(html.P('Stripper steam valve : ')),dbc.Col( dcc.Input(id="input3", type="text", placeholder="", value=120.932))]),
    dbc.Row([dbc.Col(html.P('A feed stream : ')),dbc.Col( dcc.Input(id="input4", type="text", placeholder="", value=0.3)), dbc.Col(html.P('A feed flow valve : ')),dbc.Col( dcc.Input(id="input5", type="text", placeholder="", value=29))]),
    dbc.Row([dbc.Col(html.P('Stripper steam flow : ')),dbc.Col( dcc.Input(id="input6", type="text", placeholder="", value=242)), dbc.Col(html.P('Condenser cooling water outlet temp : ')),dbc.Col( dcc.Input(id="input7", type="text", placeholder="", value=77.2))]),
    dbc.Row([dbc.Col(html.P('Reactor temp : ')),dbc.Col( dcc.Input(id="input8", type="text", placeholder="", value=50)), dbc.Col(html.P('Stripper temperature : ')),dbc.Col( dcc.Input(id="input9", type="text", placeholder="", value=66))]),

    html.Hr(),
    html.Div(html.P('The probability % of fault is :'), style={'width': '100%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
    html.Div(html.P(id='risk_fault'), style={'width': '100%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
    html.A([html.P('Click here for full article')], href='https://vivek-v-chaudhary.medium.com/draft-c0e8b9c1ef37', style={'width': '100%', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto'}),
    html.Div(html.H6('Vivek Chaudhary'), style={'display': 'inline-block', 'width': '100%', 'textAlign': 'center', "float": 'center'}),
    html.Div([
        html.A([
            html.Img(
                src=app.get_asset_url('m.png'),
                style={
                    'height': '8%',
                    'width': '8%',
                    'float': 'center',
                    'position': 'relative',
                    'padding-top': 0,
                    'padding-right': 0
                })
        ], href='https://vivek-v-chaudhary.medium.com/draft-c0e8b9c1ef37',  style={'display': 'inline-block', 'width': '50%', 'textAlign': 'right'}),
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


@app.callback(Output('risk_fault', 'children'),
              [Input('input0', 'value'),
               Input('input1', 'value'),])
def refresh_risk(input0, input1):
    r0 = float(input0)
    r1 = float(input1)
    risk_fault = get_probab(r0, r1, 59, 120.932, 0.3, 29, 242, 77.2, 50, 66)
    return risk_fault


if __name__ == '__main__':
    app.run_server(debug=True)
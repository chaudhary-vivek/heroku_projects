from pandas_datareader import data as web
from datetime import datetime as dt
import pandas as pd
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import EfficientFrontier

def weights(stocklist):
    df = pd.DataFrame()
    for stock in stocklist:
        df1 = web.DataReader(stock, data_source='yahoo',start=dt(2013, 1, 1), end=dt.now())
        df1 = df1['Close']
        df[stock] = df1
    mu = expected_returns.mean_historical_return(df)
    Sigma = risk_models.sample_cov(df)
    ef = EfficientFrontier(mu, Sigma, weight_bounds=(0,1)) 
    sharpe_pfolio=ef.max_sharpe()
    weights= list(sharpe_pfolio.values())
    return weights

    

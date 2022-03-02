from pandas_datareader import data as web
from datetime import datetime as dt
import pandas as pd
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import EfficientFrontier

def risk_return(stocklist):
    df = pd.DataFrame()
    for stock in stocklist:
        df1 = web.DataReader(stock, data_source='yahoo',start=dt(2013, 1, 1), end=dt.now())
        df1 = df1['Close']
        df[stock] = df1
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    ef = EfficientFrontier(mu, S, weight_bounds=(0,1))
    weights =ef.max_sharpe()
    results = ef.portfolio_performance(verbose=True)
    returns = results[0]
    returns = str(round(returns*100, 2)) + '%'
    risk = results[1]
    risk = str(round(risk * 100, 2)) + '%'
    sharpe = results[2]
    sharpe = round(sharpe, 2)
    return returns, risk, sharpe



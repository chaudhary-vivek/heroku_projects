from datetime import date
from pandas.tseries.offsets import DateOffset
import numpy as np
import pandas as pd
import pandas_datareader as web
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
import math
from datetime import datetime as dt

tickerlist = ['MSFT','AMZN','AAPL','GOOG']

def mote_carlo(tickerlist):
    df_stocks = pd.DataFrame()
    for stock in tickerlist:
        df1 = web.DataReader(stock, data_source='yahoo',start=dt(2013, 1, 1), end=dt.now())
        df1 = df1['Close']
        df_stocks[stock] = df1
    mu = expected_returns.mean_historical_return(df_stocks)
    #Sample Variance of Portfolio
    Sigma = risk_models.sample_cov(df_stocks)
    #Max Sharpe Ratio - Tangent to the EF
    ef = EfficientFrontier(mu, Sigma, weight_bounds=(0,1)) #weight bounds in negative allows shorting of stocks
    sharpe_pfolio=ef.max_sharpe()
    #May use add objective to ensure minimum zero weighting to individual stocks
    sharpe_pwt=ef.clean_weights()
    sh_wt = list(sharpe_pwt.values())
    sh_wt=np.array(sh_wt)
    # gives dataframe of daily returns on all 4 stocks
    thelen = len(tickerlist)
    ticker_rx2 = []
    for a in range(thelen):
      ticker_rx = df_stocks[[tickerlist[a]]].pct_change()
      ticker_rx = (ticker_rx+1).cumprod()
      ticker_rx2.append(ticker_rx[[tickerlist[a]]])
    ticker_final = pd.concat(ticker_rx2,axis=1)
    ticker_final = ticker_final.dropna()
    # this will be plot
    # Gives array of two elements : risk and return on the entire portfolio
    pret = []
    price =[]
    for x in range(thelen):
      pret.append(ticker_final.iloc[[-1],[x]])
      price.append((df_stocks.iloc[[-1],[x]]))
    pre1 = pd.concat(pret,axis=1)
    pre1 = np.array(pre1)
    varsigma = pre1.std()
    ex_rtn = pre1.dot(sh_wt)[0]
    # Returns a list of all returns possible in 1000 simulations
    Time= 365 #No of days(steps or trading days in this case)
    daily_return = []
    for i in range(500): #runs of simulation
      daily_return=(np.random.normal(ex_rtn/Time,varsigma/math.sqrt(Time),Time))
    # this will be made into a plot and a frequency histogram
    # Returns the maximum loss and profit with 95 % level of confidence

    return daily_return


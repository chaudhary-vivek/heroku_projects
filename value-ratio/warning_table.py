import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import date

def get_element(list,element):
    try:
        return list[element]
    except:
        return 'NA'


def get_warnings(ticker):

    # try:
    urlfinancials = 'https://www.marketwatch.com/investing/stock/'+ticker+'/financials'
    urlbalancesheet = 'https://www.marketwatch.com/investing/stock/'+ticker+'/financials/balance-sheet'

    text_soup_financials = BeautifulSoup(requests.get(urlfinancials).text,"html") #read in
    text_soup_balancesheet = BeautifulSoup(requests.get(urlbalancesheet).text,"html") #read in


    # build lists for Income statement
    titlesfinancials = text_soup_financials.findAll('td', {'class': 'rowTitle'})
    epslist=[]
    netincomelist = []
    longtermdebtlist = [] 
    interestexpenselist = []
    ebitdalist= []

    for title in titlesfinancials:
        if 'EPS (Basic)' in title.text:
            epslist.append ([td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text])
        if 'Net Income' in title.text:
            netincomelist.append ([td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text])
        if 'Interest Expense' in title.text:
            interestexpenselist.append ([td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text])
        if 'EBITDA' in title.text:
            ebitdalist.append ([td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text])


    # find the table headers for the Balance sheet
    titlesbalancesheet = text_soup_balancesheet.findAll('td', {'class': 'rowTitle'})
    equitylist=[]
    for title in titlesbalancesheet:
        if 'Total Shareholders\' Equity' in title.text:
            equitylist.append( [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text])
        if 'Long-Term Debt' in title.text:
            longtermdebtlist.append( [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text])

    #get the data from the income statement lists 
    #use helper function get_element
    print(equitylist)
    eps = get_element(epslist,0)
    
    netIncome = get_element(netincomelist,0)
    shareholderEquity = get_element(equitylist,0)
    roa = get_element(equitylist,1)

    longtermDebt = get_element(longtermdebtlist,0)
    interestExpense =  get_element(interestexpenselist,0)
    ebitda = get_element(ebitdalist,0)

    # load all the data into dataframe 
    df= pd.DataFrame({'eps (USD)': eps,'net Income (Bn USD)': netIncome,'shareholder Equity (Bn USD)': shareholderEquity,'longterm Debt (Bn USD)': longtermDebt,'interest Expense (Bn USD)': interestExpense,'ebitda (Bn USD)': ebitda, 'roa (%)': roa,},index=range(date.today().year-5,date.today().year))
    
    df.reset_index(inplace=True)
    df = df.set_index('index')
    columns = list(df)    
    for i in columns:
        df[i] = df[i].str.replace('B', '')
        df[i] = df[i].str.replace('M', '')
        df[i] = df[i].str.replace('%', '')
        df[i] = df[i].str.replace('NA', '')
        df[i] = df[i].astype(float)    
    df['roe (%)'] = round((df['net Income (Bn USD)']/df['shareholder Equity (Bn USD)'])*100,2)
    df['Interest coverage ratio'] = round(df['ebitda (Bn USD)']/df['interest Expense (Bn USD)'], 2)
    df['Debt to equity'] = round(df['longterm Debt (Bn USD)']/df['shareholder Equity (Bn USD)'],2)
    
    eps = df.iloc[4,0]/df.iloc[3,0] #1 or more
    roe = df.iloc[4,7] # 15 more
    roa = df.iloc[4,6] # 7 ore more
    debt_equity = df.iloc[4,9] # 1 or less
    interest_cov = df.iloc[4, 8] # 5 or more
    
    warninglist = []
    if eps<1:
        warninglist.append('Earning per share has decreased in last FY')
    if roe<15:
        warninglist.append('Return on equity is less than 15%')
    if roa<7:
        warninglist.append('Return on assets is less than 7%')
    if debt_equity >1:
        warninglist.append('Debt to equity ratio is {}. There is more debt than equity'.format(debt_equity))
    if interest_cov <5:
        warninglist.append('Interest coverage ratio is less than 5')
    if len(warninglist) == 0:
        warninglist.append("The company has sound ratios.")
    df = pd.DataFrame(warninglist, columns = ["Warnings (Scroll down to warning criteria for details)"])
        
    return df






 

    

    

    



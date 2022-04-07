from sqlite3 import Timestamp
from tkinter import E
from tkinter.font import names
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import json


# obtain list of stock
nasdaqStockList = 'https://en.wikipedia.org/wiki/Nasdaq-100'
sp500StockList = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

print('********************Querying stock list********************')
NasdaqResponse = pd.read_html(nasdaqStockList)
Sp500Response = pd.read_html(sp500StockList)

SP500JsonFileName = 'sp500'
SP500responseDf = Sp500Response[0]
SP500Tag = ['Symbol', 'Security', 'GICS Sector']
SP500responseDf = SP500responseDf[SP500Tag]

NasdaqJsonFileName = 'nasdaq'
NasdaqResponseDf = NasdaqResponse[3]
NasdaqTag = ['Ticker', 'Company', 'GICS Sector']
NasdaqResponseDf = NasdaqResponseDf[NasdaqTag]

tickers = []

stockDict = {}

responseDf = SP500responseDf.reset_index()
for index, row in responseDf.iterrows():
    tickers.append(row[SP500Tag[0]])
    stockDict[row[SP500Tag[0]]] = [row[SP500Tag[1]], row[SP500Tag[2]]]

responseDf = NasdaqResponseDf.reset_index()
for index, row in responseDf.iterrows():
    if row[NasdaqTag[0]] in tickers:
        continue
    tickers.append(row[NasdaqTag[0]])
    stockDict[row[NasdaqTag[0]]] = [row[NasdaqTag[1]], row[NasdaqTag[2]]]

pkDict = {}

# print(pkDict)

# tickers = ['AAPL','TSLA']

print('********************Downloading stock data*****************')
stockPriceDf = yf.download(tickers, group_by = 'ticker', start="2011-01-01", end="2018-01-01", threads = True, interval = '1d',prepost = False,proxy = None)


print('********************Trimming stock data*********************')
trimmedStockPriceDf = stockPriceDf.dropna(axis=0, how='all')
trimmedStockPriceDf = trimmedStockPriceDf.dropna(axis=1)

rowNum = len(trimmedStockPriceDf)
colNum = len(trimmedStockPriceDf.columns)

for ticker in tickers:
    try:
        trimmedStockPriceDf = trimmedStockPriceDf.drop([(ticker,'Open'),(ticker,'High'),(ticker,'Low'),(ticker,'Close'),(ticker,'Volume')], axis = 1)
    except:
        continue

trimmedStockPriceDf.columns = trimmedStockPriceDf.columns.droplevel(1)
trimmedStockPriceDf.reset_index(drop=True, inplace=True)
# tdict = trimmedStockPriceDf.to_dict()
# print(tdict)


print('********************Saving stock data***********************')
# trimmedStockPriceDf.to_csv('trimmedStockdata.csv')

# indexNamesArr = trimmedStockPriceDf.index.values
# for i in range(len(indexNamesArr)):
#     print(str(indexNamesArr[i]), i)

data = []
for col in trimmedStockPriceDf:
    # print(col)
    try:
        dataInstance = {}
        field = {}
        dataInstance['model'] = 'aifund.Stock'
        field['symbol'] = col[0]
        field['name'] = stockDict[col[0]][0]
        field['sector'] = stockDict[col[0]][1]
        stockPrice = trimmedStockPriceDf[col].tolist()
        daily_return = [0]

        for i in range(1, len(stockPrice)):
            returnValue = (stockPrice[i] - stockPrice[i-1])/stockPrice[i-1]*100
            daily_return.append(returnValue)

        field['dailyReturn'] = daily_return
        dataInstance['fields'] = field
        data.append(dataInstance)
    except Exception as E:
        print(E)


with open(f'newStock.json', 'w') as f:
    json.dump(data, f)



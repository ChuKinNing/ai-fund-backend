import yfinance as yf
import pandas as pd
import json

with open('newStock.json') as json_file:
    stocks = json.load(json_file)

    # Print the type of data variable
    # print("Type:", type(stocks))
    # print(stocks[0]['model'])
    # print(stocks[0]['fields']['symbol'])
    # "fields": {"symbol": "NEE", "name": "NextEra Energy", "sector": "Utilities", "dailyReturn": [], "start2018":0,'end2018','start2019','end2019','start2020','end2020','start2021','end2021'

tickers = []

for stock in stocks:
    tickers.append(stock['fields']['symbol'])

print('********************Downloading stock data*****************')
stockPriceDf18 = yf.download(tickers, group_by='Ticker', start="2018-01-02", end="2018-01-03")
stockPriceDf19 = yf.download(tickers, group_by='Ticker', start="2019-01-02", end="2019-01-03")
stockPriceDf20 = yf.download(tickers, group_by='Ticker', start="2020-01-02", end="2020-01-03")
stockPriceDf21 = yf.download(tickers, group_by='Ticker', start="2021-01-04", end="2021-01-05")
stockPriceDf18end = yf.download(tickers, group_by='Ticker', start="2018-12-29", end="2018-12-30")
stockPriceDf19end = yf.download(tickers, group_by='Ticker', start="2020-01-01", end="2020-01-01")
stockPriceDf20end = yf.download(tickers, group_by='Ticker', start="2021-01-01", end="2021-01-01")
stockPriceDf21end = yf.download(tickers, group_by='Ticker', start="2022-01-01", end="2022-01-01")
stockPriceDf = pd.concat([stockPriceDf18, stockPriceDf18end, stockPriceDf19, stockPriceDf19end, stockPriceDf20, stockPriceDf20end, stockPriceDf21, stockPriceDf21end])


print('********************Trimming stock data*********************')
trimmedStockPriceDf = stockPriceDf.dropna(axis=0, how='all')
trimmedStockPriceDf = trimmedStockPriceDf.dropna(axis=1)

for ticker in tickers:
    try:
        trimmedStockPriceDf = trimmedStockPriceDf.drop([(ticker,'Open'),(ticker,'High'),(ticker,'Low'),(ticker,'Close'),(ticker,'Volume')], axis = 1)
    except:
        continue

trimmedStockPriceDf.columns = trimmedStockPriceDf.columns.droplevel(1)
trimmedStockPriceDf.reset_index(drop=True, inplace=True)
tdict = trimmedStockPriceDf.to_dict()

print('********************Saving in dict*********************')
for stock in stocks:
    stock['fields']['start2018'] = tdict[stock['fields']['symbol']][0]
    stock['fields']['end2018'] = tdict[stock['fields']['symbol']][1]
    stock['fields']['start2019'] = tdict[stock['fields']['symbol']][2]
    stock['fields']['end2019'] = tdict[stock['fields']['symbol']][3]
    stock['fields']['start2020'] = tdict[stock['fields']['symbol']][4]
    stock['fields']['end2020'] = tdict[stock['fields']['symbol']][5]
    stock['fields']['start2021'] = tdict[stock['fields']['symbol']][6]
    stock['fields']['end2021'] = tdict[stock['fields']['symbol']][7]

print('********************Saving in JSON*********************')
with open(f'updateNewStock.json', 'w') as f:
    json.dump(stocks, f)
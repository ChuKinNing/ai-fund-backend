from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from aifund.api.serializers import PortfolioSerializer, WeightedStockSerializer, StockSerializer, SocialLoginSerializer
from aifund.models import Portfolio, WeightedStock, Stock, SocialAccount
from django.http import JsonResponse
from .services.portfolioOptimization import Optimizer
from django.contrib.auth.models import User

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

import yfinance as yf
import pandas as pd

@api_view(['POST'])
def createPortfolio(request):
    if request.method == 'POST':
        data = request.data
        socialAccount = SocialAccount.objects.get(unique_id=data['unique_id'])
        portfolio = Portfolio(name=data['portfolioName'], 
                                owner=socialAccount.user, 
                                allowShort=bool(data['allowShort']))
        portfolio.save()
        addStockToPortfolio(data['stocks'], portfolio)
        portfolios = Portfolio.objects.filter(owner=socialAccount.user.id)
        serializer = PortfolioSerializer(portfolios, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def deletePortfolio(request):
    if request.method == 'POST':
        try:
            data = request.data
            socialAccount = SocialAccount.objects.get(unique_id=data['unique_id'])
            portfolio = Portfolio(id=data['delete_portfolio_id'], 
                                    owner=socialAccount.user)
            portfolio.delete()
        except Exception as e:
            print(e)
        finally:
            portfolios = Portfolio.objects.filter(owner=socialAccount.user.id)
            serializer = PortfolioSerializer(portfolios, many=True)
            return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def updatePortfolio(request):
    if request.method == 'POST':
        try:
            data = request.data
            Portfolio.objects.filter(id=data['update_portfolio_id']).update(name=data['portfolioName'], allowShort=bool(data['allowShort']), hasOpitimized = False)
            portfolio = Portfolio.objects.get(id=data['update_portfolio_id'])
            WeightedStock.objects.filter(portfolio=portfolio).delete()
            addStockToPortfolio(data['stocks'], portfolio)
            portfolio.save()
        except Exception as e:
            print(e)
        finally:
            portfolios = Portfolio.objects.filter(id=data['update_portfolio_id'])
            serializer = PortfolioSerializer(portfolios, many=True)
            return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def getAllPortfolio(request):
    if request.method == 'POST':
        data = request.data
        # print(data)
        socialAccount = SocialAccount.objects.get(unique_id=data['unique_id'])
        portfolios = Portfolio.objects.filter(owner=socialAccount.user.id)
        serializer = PortfolioSerializer(portfolios, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def getOnePortfolio(request):
    if request.method == 'POST':
        data = request.data
        stocks = WeightedStock.objects.filter(portfolio=data['portfolio_id'])
        serializer = WeightedStockSerializer(stocks, many=True)
        # print(serializer.data)
        return JsonResponse(serializer.data, safe=False)

# add stock to portfolio
def addStockToPortfolio(stocks, portfolio):
    for stock in stocks:
        if WeightedStock.objects.filter(stock=stock, portfolio=portfolio).exists():
            pass
        else:
            targetedStock = Stock.objects.get(id=str(stock))
            weightedStockObj = WeightedStock(stock=targetedStock, portfolio=portfolio)
            weightedStockObj.save()

@api_view(['POST'])
def getSpecificStocks(request):
    if request.method == 'POST':
        data = request.data
        wantedStocks = data['stocks']
        stocks = Stock.objects.filter(id__in=wantedStocks)
        serializer = StockSerializer(stocks, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def getStockData(request):
    if request.method == 'POST':
        data = request.data
        stock = data['stock_name']
        stockData = yf.download(stock, period = "3mo",)
        stockData = stockData['Adj Close']
        temp = stockData.index.tolist()
        dates = []
        res = {}
        for date in temp:
            dates.append(date.strftime("%Y-%m-%d"))
        stockData = stockData.set_axis(dates)
        stockData = stockData.to_dict()

        ticker = yf.Ticker(stock)
        try:
            res['stockInfo'] = ticker.info
        except:
            res['stockInfo'] = 'NA'
        try:
            res['stockNews'] = ticker.news
        except:
            res['stockNews'] = 'NA'
        res['stockPriceData'] = stockData
        return Response(res)

@api_view(['POST'])
def portfolioOverview(request):
    if request.method == 'POST':
        data = request.data
        portfolio_id = data['portfolio_id']
        portfolio = Portfolio.objects.get(id=portfolio_id)
        portfolioSerializer = PortfolioSerializer(portfolio)

        stocks = WeightedStock.objects.filter(portfolio=portfolio)
        stockSerializer = WeightedStockSerializer(stocks, many=True)

        res = {}
        res['portfolio'] = portfolioSerializer.data
        res['stocks'] = stockSerializer.data

        return Response(res)


# call AMPO
@api_view(['POST'])
def optimizePortfolio(request):
    if request.method == 'POST':
        print('Optimize start')
        data = request.data
        algo = data['algo']
        population = int(data['population'])
        iteration = int(data['iteration'])
        # algo='GA'
        portfolio_id = data['portfolio']
        portfolio = Portfolio.objects.get(id=portfolio_id)
        allowShort = portfolio.allowShort
        user_id = portfolio.owner.id
        weightedStocks = WeightedStock.objects.filter(portfolio=portfolio_id)
        serializer = WeightedStockSerializer(weightedStocks, many=True)
        stocks = serializer.data
        stockDict = {}
        result = {}
        for stock in stocks:
            stockid = stock['stock_id']
            stockObj = Stock.objects.get(id=stockid)
            dailyReturn = getattr(stockObj, 'dailyReturn')
            symbol = getattr(stockObj, 'symbol')
            stockDict[symbol] = dailyReturn
        optimizer = Optimizer()
        response = {}
        result = optimizer.runOptimizer(stockDict, algo, allowShort, population, iteration)
        response['best_solution'], response['out'] = result[0], result[1]
        for i in range(len(stocks)):
            weightedStock = WeightedStock.objects.get(id=stocks[i]['id'])
            weightedStock.weight = response['best_solution'][i]
            weightedStock.save()
        temp = Portfolio.objects.get(id=portfolio_id)
        temp.hasOpitimized = True
        temp.save()
        return Response(response)

@api_view(['POST'])
def analyzePortfolio(request):
    if request.method == 'POST':
        portfolio_id = request.data['portfolio_id']
        weightedStocks = WeightedStock.objects.filter(portfolio=portfolio_id)
        serializer = WeightedStockSerializer(weightedStocks, many=True)
        stocks = serializer.data
        # tickers = []
        # for stock in stocks:
        #     tickers.append(stock['symbol'])
        # print('********************Downloading stock data*****************')
        # stockPriceDf18 = yf.download(tickers, group_by='Ticker', start="2018-01-02", end="2018-01-03")
        # stockPriceDf19 = yf.download(tickers, group_by='Ticker', start="2019-01-02", end="2019-01-03")
        # stockPriceDf20 = yf.download(tickers, group_by='Ticker', start="2020-01-02", end="2020-01-03")
        # stockPriceDf21 = yf.download(tickers, group_by='Ticker', start="2021-01-04", end="2021-01-05")
        # stockPriceDf18end = yf.download(tickers, group_by='Ticker', start="2018-12-29", end="2018-12-30")
        # stockPriceDf19end = yf.download(tickers, group_by='Ticker', start="2020-01-01", end="2020-01-01")
        # stockPriceDf20end = yf.download(tickers, group_by='Ticker', start="2021-01-01", end="2021-01-01")
        # stockPriceDf21end = yf.download(tickers, group_by='Ticker', start="2022-01-01", end="2022-01-01")
        # stockPriceDf = pd.concat([stockPriceDf18, stockPriceDf18end, stockPriceDf19, stockPriceDf19end, stockPriceDf20, stockPriceDf20end, stockPriceDf21, stockPriceDf21end])
        # print('********************Trimming stock data*********************')
        # trimmedStockPriceDf = stockPriceDf.dropna(axis=0, how='all')
        # trimmedStockPriceDf = trimmedStockPriceDf.dropna(axis=1)
        # for ticker in tickers:
        #     try:
        #         trimmedStockPriceDf = trimmedStockPriceDf.drop([(ticker,'Open'),(ticker,'High'),(ticker,'Low'),(ticker,'Close'),(ticker,'Volume')], axis = 1)
        #     except:
        #         continue
        # trimmedStockPriceDf.columns = trimmedStockPriceDf.columns.droplevel(1)
        # trimmedStockPriceDf.reset_index(drop=True, inplace=True)
        # tdict = trimmedStockPriceDf.to_dict()
        # res = []
        # for stock in stocks:
        #     temp = {}
        #     temp['symbol'] = stock['symbol']
        #     temp['name'] = stock['name']
        #     temp['sector'] = stock['sector']
        #     temp['weight'] = stock['weight']
        #     temp['prices'] = {'start2018' : tdict[stock['symbol']][0],
        #                       'end2018' : tdict[stock['symbol']][1],
        #                       'start2019' : tdict[stock['symbol']][2],
        #                       'end2019' : tdict[stock['symbol']][3],
        #                       'start2020' : tdict[stock['symbol']][4],
        #                       'end2020' : tdict[stock['symbol']][5],
        #                       'start2021' : tdict[stock['symbol']][6],
        #                       'end2021' : tdict[stock['symbol']][7],
        #                      }
        #     res.append(temp)
        res = []
        for stock in stocks:
            temp = {}
            temp['symbol'] = stock['symbol']
            temp['name'] = stock['name']
            temp['sector'] = stock['sector']
            temp['weight'] = stock['weight']
            temp['prices'] = {'start2018' : stock['start2018'],
                              'end2018' : stock['end2018'],
                              'start2019' : stock['start2019'],
                              'end2019' : stock['end2019'],
                              'start2020' : stock['start2020'],
                              'end2020' : stock['end2020'],
                              'start2021' : stock['start2021'],
                              'end2021' : stock['end2021'],
                             }
            res.append(temp)
        return Response({'analyzeResult' : res})



@api_view(['GET'])
def getAllStock(request):
    if request.method == 'GET':
        allStocks = Stock.objects.all()
        serializer = StockSerializer(allStocks, many=True)
        return JsonResponse(serializer.data, safe=False)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class GoogleLogin(TokenObtainPairView):
    permission_classes = (AllowAny, ) # AllowAny for login
    serializer_class = SocialLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(get_tokens_for_user(user))
        else:
            raise ValueError('Not serializable')

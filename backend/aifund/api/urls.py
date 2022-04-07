from django.urls import path
from aifund.api.views import(
    createPortfolio,
    getAllPortfolio,
    addStockToPortfolio,
    optimizePortfolio,
    getAllStock,
    GoogleLogin,
    getOnePortfolio,
    getSpecificStocks,
    portfolioOverview,
    analyzePortfolio,
    deletePortfolio,
    updatePortfolio,
    getStockData,
)
from rest_framework_simplejwt import views as jwt_views

app_name = "account"

urlpatterns = [
    # portfolio
    path('createPortfolio/', createPortfolio, name='register'),
    path('deletePortfolio/', deletePortfolio, name='delete Portfolio'),
    path('updatePortfolio/', updatePortfolio, name='update Portfolio'),
    path('portfolioOverview/', portfolioOverview, name='portfolioOverview'),
    path('getPortfolio/', getOnePortfolio, name='getPortfolio'),
    path('getAllPortfolio/', getAllPortfolio, name='portfolio-list'),
    path('addStockToPortfolio/', addStockToPortfolio, name='addStockToPortfolio'),
    path('optimizePortfolio/', optimizePortfolio, name='optimizePortfolio'),
    path('analyzePortfolio/', analyzePortfolio, name='analyzePortfolio'),
    # stock
    path('stock-list/', getAllStock, name='stock list'),
    path('getSpecificStocks/', getSpecificStocks, name='get specific stocks'),
    path('getStockData/', getStockData, name='getStockData'),
    path('token/obtain/', GoogleLogin.as_view()),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]

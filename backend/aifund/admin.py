from django.contrib import admin
from aifund.models import Portfolio, WeightedStock, Stock, SocialAccount

# Register your models here.
@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('id','name','owner','createDate','lastModified','allowShort','hasOpitimized')

@admin.register(WeightedStock)
class WeightedStockAdmin(admin.ModelAdmin):
    list_display = ('id','portfolio','stock','weight')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id','symbol','name','sector')

@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('id','provider','unique_id','user')
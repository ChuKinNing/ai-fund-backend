from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

# Create your models here.
class Portfolio(models.Model):
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    createDate = models.DateField(auto_now_add=True)
    lastModified = models.DateField(auto_now=True)
    allowShort = models.BooleanField(default=False)
    hasOpitimized = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Stock(models.Model):
    symbol = models.CharField(max_length=10, blank=True, null=True, unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    sector = models.CharField(max_length=50, blank=True, null=True)
    dailyReturn = ArrayField(models.FloatField(max_length=20, blank=True, null=True), null=True)
    start2018 = models.FloatField(max_length=20, blank=True, null=True)
    end2018 = models.FloatField(max_length=20, blank=True, null=True)
    start2019 = models.FloatField(max_length=20, blank=True, null=True)
    end2019 = models.FloatField(max_length=20, blank=True, null=True)
    start2020 = models.FloatField(max_length=20, blank=True, null=True)
    end2020 = models.FloatField(max_length=20, blank=True, null=True)
    start2021 = models.FloatField(max_length=20, blank=True, null=True)
    end2021 = models.FloatField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return str(self.id)
        

class WeightedStock(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock,on_delete=models.CASCADE)
    weight = models.FloatField(max_length=20, default=0)

    def __str__(self):
        return self.portfolio.name

class SocialAccount(models.Model):
    provider = models.CharField(max_length=200, default='google')
    unique_id = models.CharField(max_length=200)
    user = models.ForeignKey(User, related_name='social', on_delete=models.CASCADE)
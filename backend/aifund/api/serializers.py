from rest_framework import serializers
from django.contrib.auth.models import User
from google.oauth2 import id_token
from google.auth.transport import requests

from backend.settings import SOCIAL_GOOGLE_CLIENT_ID
from aifund.models import *


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['id','name', 'owner','createDate','lastModified','allowShort', 'hasOpitimized']

class StockSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='symbol')
    stock_id = serializers.IntegerField(source='id')
    class Meta:
        model = Stock
        fields = ['stock_id','label','name','sector']
        ordering = ('label',)

class WeightedStockSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source='stock.symbol')
    name = serializers.CharField(source='stock.name')
    sector = serializers.CharField(source='stock.sector')
    stock_id = serializers.IntegerField(source='stock.id')
    start2018 = serializers.IntegerField(source='stock.start2018')
    end2018 = serializers.IntegerField(source='stock.end2018')
    start2019 = serializers.IntegerField(source='stock.start2019')
    end2019 = serializers.IntegerField(source='stock.end2019')
    start2020 = serializers.IntegerField(source='stock.start2020')
    end2020 = serializers.IntegerField(source='stock.end2020')
    start2021 = serializers.IntegerField(source='stock.start2021')
    end2021 = serializers.IntegerField(source='stock.end2021')

    class Meta:
        model = WeightedStock
        fields = ['id','portfolio', 'symbol', 'weight', 'name', 'sector', 'stock_id', 'start2018', 'end2018', 'start2019', 'end2019','start2020', 'end2020','start2021', 'end2021']
    
class SocialLoginSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def verify_token(self, token):
        """
        驗證 id_token 是否正確

        token: JWT
        """
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), SOCIAL_GOOGLE_CLIENT_ID)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            if idinfo['aud'] not in [SOCIAL_GOOGLE_CLIENT_ID]:
                raise ValueError('Could not verify audience.')
            # Success
            return idinfo
        except ValueError:
            pass

    def create(self, validated_data):
        idinfo = self.verify_token(validated_data.get('token'))
        if idinfo:
            # User not exists
            if not SocialAccount.objects.filter(unique_id=idinfo['sub']).exists():
                user = User.objects.create_user(
                    username=f"{idinfo['name']} {idinfo['email']}", # Username has to be unique
                    first_name=idinfo['given_name'],
                    # last_name=idinfo['family_name'],
                    email=idinfo['email']
                )
                SocialAccount.objects.create(
                    user=user,
                    unique_id=idinfo['sub']
                )
                return user
            else:
                social = SocialAccount.objects.get(unique_id=idinfo['sub'])
                return social.user
        else:
            raise ValueError("Incorrect Credentials")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

# class StockBrowsingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Stock
#         fields = ['id', 'symbol','name','sector']
#         ordering = ('symbol',)

from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}


class StaticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Static
        fields = ('rate')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'productType', 'expiry',
                  'expiryDate', 'contractSize')


class SubProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubProduct
        fields = ('id', 'name', 'callPut', 'product_id', 'strike')


class StreamPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamPrice
        fields = ('bid', 'offer', 'ts',
                  'subProduct_id')


class GreeksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Greeks
        fields = ('iv', 'delta', 'gamma', 'vega', 'theta', 'rho', 'ts')


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id', 'buy', 'size',
                  'avgPrice', 'lastTradeTs', 'subProduct')


class PnlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pnl
        fields = ('id', 'ts', 'value', 'productType', 'subProduct')


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade

        fields = ('id', 'size', 'price', 'ts',
                  'closed', 'position', 'subProduct', 'buy', 'sizeLeft')


# class MovieSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Movie
#         fields = ('id', 'title', 'description', 'nbr_ratings', 'avg_rating')


# class RatingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Rating
#         fields = ('id', 'movie', 'user', 'stars')

import redis
from .models import *
from .views import StreamPriceViewSet, SubProductViewSet, ProductViewSet
from .serializers import StreamPriceSerializer, SubProductSerializer, ProductSerializer
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
import time
import simplejson as json
from django.http import JsonResponse
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from django.core import serializers
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
import timeit
import operator
import argparse
import math
import scipy.stats as stats
import mibian
# from impvol import imp_vol, lfmoneyness, impvol_bisection


######    REDIS    ########
redisServer = redis.StrictRedis(host='localhost', port=6379, db=0)

######    CONFIG    ########
config_data = ""

with open('./../crypto/config.json') as config_file:
    config_data = json.load(config_file)

exchanges_watchlist = config_data['exchanges_watchlist']
tickers_watchlist = config_data['tickers_watchlist']

############################


def addUserToWS(type):

    if type == 'Platform':

        channel_layer = get_channel_layer()

        # load product and subproduct views
        queryset = Product.objects.all()
        data = serializers.serialize("json", queryset)

        async_to_sync(channel_layer.group_send)(
            "tradingData",
            {
                "type": "broadcast",
                "data": {"type": "querySetProduct", "content": data}
            }
        )

        queryset = SubProduct.objects.all()
        data = serializers.serialize("json", queryset)

        async_to_sync(channel_layer.group_send)(
            "tradingData",
            {
                "type": "broadcast",
                "data": {"type": "querySetSubProduct", "content": data}
            }
        )

        queryset = StreamPrice.objects.all()
        data = serializers.serialize("json", queryset)

        async_to_sync(channel_layer.group_send)(
            "tradingData",
            {
                "type": "broadcast",
                "data": {"type": "querySetStreamPrice", "content": data}
            }
        )

        # calculate greeks
        calculateAllGreeks(firstTime=True)

        schedPlatform.resume()

        redisServer.incr("wsPlatformUsers")
        print(json.loads(redisServer.get("wsPlatformUsers")),
              "user connected to Platform WS")

    elif type == 'Crypto':

        if json.loads(redisServer.get("wsCryptoUsers")) == 0:
            schedCrypto.resume()

        redisServer.incr("wsCryptoUsers")
        print(json.loads(redisServer.get("wsCryptoUsers")), "user connected to WS")


def removeUserFromWS(type):

    if type == 'Platform':

        redisServer.decr("wsPlatformUsers")
        if redisServer.get("wsPlatformUsers") == 0:
            schedPlatform.pause()

        print(json.loads(redisServer.get("wsPlatformUsers")),
              "user connected to Platform WS")

    elif type == 'Crypto':
        redisServer.decr("wsCryptoUsers")
        if redisServer.get("wsCryptoUsers") == 0:
            schedCrypto.pause()

        print(json.loads(redisServer.get("wsCryptoUsers")), "user connected to WS")


#### Trading Platform ####

def sendStreamToWS():

    # global lastMessage
    channel_layer = get_channel_layer()
    lastMessage = json.loads(redisServer.get("wsLastMessage"))
    lastGreeksUpdate = json.loads(redisServer.get("wsLastGreeksUpdate"))

    streamPrices = [json.loads(item) for item in redisServer.hvals(
        'streamPrices')]

    streamPricesUpdated = [
        item for item in streamPrices if item["ts"] > lastMessage]

    async_to_sync(channel_layer.group_send)(
        "tradingData",
        {
            "type": "broadcast",
            "data": {"type": "streamPrice", "content": streamPricesUpdated}
        }
    )

    # lastMessage = datetime.timestamp(datetime.now())
    redisServer.set("wsLastMessage", datetime.timestamp(datetime.now()))

    # update greeks every 60 seconds
    if (datetime.timestamp(datetime.now()) - lastGreeksUpdate) > 60:
        redisServer.set("wsLastGreeksUpdate",
                        datetime.timestamp(datetime.now()))
        calculateAllGreeks(firstTime=False)

    # start_time = timeit.default_timer()
    # elapsed = timeit.default_timer() - start_time
    # print(elapsed)


def calculateAllGreeks(firstTime: bool):

    rate = json.loads(redisServer.get("staticRate"))

    timeNow = timezone.now()
    greeksData = []

    greeks = Greeks.objects.all()

    for greekObj in greeks:

        subProductId = greekObj.pk
        subProduct = SubProduct.objects.get(id=subProductId)
        product = Product.objects.get(id=subProduct.product_id)

        spotSubProductId = product.hedgeSubProductId

        spotStreamPrice = StreamPrice.objects.get(pk=spotSubProductId)
        spotPrice = (spotStreamPrice.bid + spotStreamPrice.offer) / 2

        strike = subProduct.strike

        optionStreamPrice = StreamPrice.objects.get(pk=subProductId)
        optionPrice = (optionStreamPrice.bid + optionStreamPrice.offer) / 2

        callPut = subProduct.callPut

        timeToExpiry = convertDatesToTimeToExpiry(
            product.expiryTime, timeNow)

        if callPut == 'C':
            optionObj = mibian.BS(
                [spotPrice, strike, rate, timeToExpiry], callPrice=optionPrice)

            if greekObj.iv != optionObj.impliedVolatility or firstTime == True:

                call = mibian.BS([spotPrice, strike, rate, timeToExpiry],
                                 volatility=optionObj.impliedVolatility)

                greeks = {'subProductId': subProductId, 'iv': optionObj.impliedVolatility, 'delta': call.callDelta,
                          'gamma': call.gamma, 'vega': call.vega, 'theta': call.callTheta, 'rho': call.callRho}

                greeksData.append(greeks)

                greekObj.iv = optionObj.impliedVolatility
                greekObj.delta = call.callDelta
                greekObj.gamma = call.gamma
                greekObj.vega = call.vega
                greekObj.theta = call.callTheta
                greekObj.rho = call.callRho
                greekObj.ts = timeNow
                if greekObj.iv:
                    greekObj.save()
                else:
                    print("iv is null")

        elif callPut == 'P':

            optionObj = mibian.BS(
                [spotPrice, strike, rate, timeToExpiry], putPrice=optionPrice)

            if greekObj.iv != optionObj.impliedVolatility or firstTime == True:

                put = mibian.BS([spotPrice, strike, rate, timeToExpiry],
                                volatility=optionObj.impliedVolatility)

                greeks = {'subProductId': subProductId, 'iv': optionObj.impliedVolatility, 'delta': put.putDelta,
                          'gamma': put.gamma, 'vega': put.vega, 'theta': put.putTheta, 'rho': put.putRho}

                greeksData.append(greeks)

                greekObj.iv = optionObj.impliedVolatility
                greekObj.delta = put.putDelta
                greekObj.gamma = put.gamma
                greekObj.vega = put.vega
                greekObj.theta = put.putTheta
                greekObj.rho = put.putRho
                greekObj.ts = timeNow
                if greekObj.iv:
                    greekObj.save()
                else:
                    print("iv is null")

    if len(greeksData) > 0:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "tradingData",
            {
                "type": "broadcast",
                "data": {"type": "greeksData", "content": json.dumps(greeksData)}
            }
        )


def convertDatesToTimeToExpiry(farDate, closeDate):
    return (farDate - closeDate).total_seconds() / 86400


#### Crypto dashboard ####


class Price:
    ###

    #

    ###
    def __init__(self, exchange, symbol_data):
        self.exchange = exchange
        self.symbol = symbol_data['symbol']
        self.update(symbol_data)

    def update(self, symbol_data):
        self.bid = symbol_data['bid']
        self.bidVolume = symbol_data['bidVolume']
        self.ask = symbol_data['ask']
        self.askVolume = symbol_data['askVolume']

    def __str__(self):
        return f'{self.exchange} - {self.symbol}: {self.bid} / {self.ask}'

    def __repr__(self):
        return self.__str__()


class Opportunity:

    def __init__(self, price_obj_to_sell, price_obj_to_buy):
        self.price_obj_to_sell = price_obj_to_sell
        self.price_obj_to_buy = price_obj_to_buy
        self.scalp = self.calculate()

    def calculate(self):
        return round(100*(self.price_obj_to_sell.bid - self.price_obj_to_buy.ask) / self.price_obj_to_buy.ask, 3)

    def getData(self):
        data = {'symbol': self.price_obj_to_sell.symbol, 'sellPrice': self.price_obj_to_sell.bid, 'sellExchange': self.price_obj_to_sell.exchange,
                'buyPrice': self.price_obj_to_buy.ask, 'buyExchange': self.price_obj_to_buy.exchange, 'scalp': self.scalp}
        return data

    def __str__(self):
        # return f'{self.price_to_sell.symbol} => {self.scalp} %'
        data = {'symbol': self.price_obj_to_sell.symbol, 'sellPrice': self.price_obj_to_sell.bid, 'sellExchange': self.price_obj_to_sell.exchange,
                'buyPrice': self.price_obj_to_buy.ask, 'buyExchange': self.price_obj_to_buy.exchange, 'scalp': self.scalp}
        return json.dumps(data, use_decimal=True)

    def __repr__(self):
        return self.__str__()


def analyse_prices():

    opportunities_list = []

    for symbol in price_dict:
        # list of price objects sorted by bid descending order
        obj_sorted_by_bid = [obj for obj in price_dict[symbol].values()]
        obj_sorted_by_bid.sort(key=lambda x: x.bid, reverse=True)

        # list of price objects sorted by ask ascending order
        obj_sorted_by_ask = [obj for obj in price_dict[symbol].values()]
        obj_sorted_by_ask.sort(key=lambda x: x.ask)

        # sell the highest bid, buy the lowest offer
        scalp = (
            obj_sorted_by_bid[0].bid - obj_sorted_by_ask[0].ask) / obj_sorted_by_ask[0].ask

        if scalp > 0:
            opportunities_list.append(Opportunity(
                obj_sorted_by_bid[0], obj_sorted_by_ask[0]))
            # print(obj_sorted_by_bid[0].symbol, ": sell on", obj_sorted_by_bid[0].exchange,
            #       "and buy on:", obj_sorted_by_ask[0].exchange, "for +", round(scalp*100, 3), "% gross")

    opportunities_list.sort(key=lambda x: x.scalp, reverse=True)
    return list(opportunities_list)


def asyncLoadRedis():

    for exchange in exchanges_watchlist:
        if redisServer.hexists('crypto', exchange):
            exchange_data = json.loads(
                redisServer.hget('crypto', exchange))

            # populate price_dict, key=symbol, containing a dict of key=exchange
            for symbol_data in exchange_data:

                # create price object
                my_object = Price(exchange, symbol_data)

                # new key=symbol
                if my_object.symbol not in price_dict:
                    price_dict[my_object.symbol] = {}

                # new sub dict key=exchange
                if exchange not in price_dict[my_object.symbol]:
                    price_dict[my_object.symbol][exchange] = my_object
                # update prices
                else:
                    price_dict[my_object.symbol][exchange].update(
                        symbol_data)

    opportunities_list = analyse_prices()
    return opportunities_list


def sendOpportunitiesToWS():

    opportunities_list = asyncLoadRedis()
    opportunities_data = []
    for item in opportunities_list:
        opportunities_data.append(item.getData())

    channel_layer = get_channel_layer()
    # print(opportunities_data)
    async_to_sync(channel_layer.group_send)(
        "crypto",
        {
            "type": "broadcast",
            "data": {"type": "opportunities", "content": json.dumps(opportunities_data, use_decimal=True)}
        }
    )


#### "MAIN" ####


def initRedisValues():
    redisServer.set("wsPlatformUsers", 0)
    redisServer.set("wsLastMessage", datetime.timestamp(datetime.now()))

    queryset = Static.objects.get()
    redisServer.set("staticRate", queryset.rate)

    redisServer.set("wsLastGreeksUpdate", datetime.timestamp(
        datetime.now() - timedelta(seconds=120)))

    redisServer.set("wsCryptoUsers", 0)
    redisServer.set("wsCryptoLastMessage", datetime.timestamp(datetime.now()))


initRedisValues()

#### Trading platform ####
schedPlatform = BackgroundScheduler()
schedPlatform.add_job(sendStreamToWS, 'interval', seconds=1)
schedPlatform.start()
schedPlatform.pause()

#### Crypto dashboard ####
price_dict = {}
opportunities_list = []

schedCrypto = BackgroundScheduler()
schedCrypto.add_job(sendOpportunitiesToWS, 'interval', seconds=1)
schedCrypto.start()
schedCrypto.pause()

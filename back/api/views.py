from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.safestring import mark_safe

import redis
import json
from datetime import datetime

from .models import *
from .serializers import *

redisServer = redis.StrictRedis(host='localhost', port=6379, db=0)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class StaticViewSet(viewsets.ModelViewSet):
    queryset = Static.objects.all()
    serializer_class = StaticSerializer
    permission_classes = (IsAuthenticated,)


@method_decorator(cache_page(60*60), name='dispatch')
class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)


@method_decorator(cache_page(60*60), name='dispatch')
class SubProductViewSet(viewsets.ModelViewSet):

    queryset = SubProduct.objects.all()
    serializer_class = SubProductSerializer
    permission_classes = (IsAuthenticated,)


class StreamPriceViewSet(viewsets.ModelViewSet):

    queryset = StreamPrice.objects.all()
    serializer_class = StreamPriceSerializer
    permission_classes = (IsAuthenticated,)

    # authentication_classes = (TokenAuthentication, )
    # permission_classes = (IsAuthenticated, )


class GreeksViewSet(viewsets.ModelViewSet):

    queryset = Greeks.objects.all()
    serializer_class = GreeksSerializer
    permission_classes = (IsAuthenticated,)


class PositionViewSet(viewsets.ModelViewSet):

    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['GET'])
    def positions(self, request, pk=None):

        user = request.user
        positions = Position.objects.filter(user=user)
        positionsSerialized = PositionSerializer(positions, many=True)

        response = {'positions': positionsSerialized.data}
        return Response(response, status=status.HTTP_200_OK)

        pass


class PnlViewSet(viewsets.ModelViewSet):

    queryset = Pnl.objects.all()
    serializer_class = PnlSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['GET'])
    def dailyPnl(self, request, pk=None):
        user = request.user
        # timezone.localtime(timezone.now())

        pnlTotal = Pnl.objects.filter(
            user=user, ts__gte=timezone.now().replace(hour=0, minute=0, second=0)).aggregate(Sum('value'))
        print(pnlTotal['value__sum'])

        if (pnlTotal['value__sum'] is not None):
            pnlTotal['value__sum'] = round(pnlTotal['value__sum'], 2)
        else:
            pnlTotal['value__sum'] = 0

        response = {'message': 'dailyPnl',
                    'value': pnlTotal['value__sum']}

        return Response(response, status=status.HTTP_200_OK)


class TradeViewSet(viewsets.ModelViewSet):

    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
    permission_classes = (IsAuthenticated,)

    # front end is retrieving the last 100 trades at startup
    @action(detail=False, methods=['GET'])
    def trades(self, request, pk=None):

        user = request.user
        trades = Trade.objects.filter(user=user).order_by('ts')[:100]
        tradesSerialized = TradeSerializer(trades, many=True)

        response = {'trades': tradesSerialized.data}
        return Response(response, status=status.HTTP_200_OK)

        pass

    # when a new trade is received from the front end, we update position, trade and pnl
    # we send back the updated position and the new trade details
    @action(detail=False, methods=['POST'])
    def newOrder(self, request, pk=None):

        user = request.user
        size = request.data['size']
        buy = request.data['buy']

        pnlFeedback = []

        subProductId = request.data['subProductId']
        subProduct = SubProduct.objects.get(id=subProductId)

        streamPrice = redisServer.hgetall('streamPrices')
        streamPrice = json.loads(
            redisServer.hget('streamPrices', subProductId))

        if (buy == 1):
            buy = True
            price = streamPrice['offer']
        else:
            buy = False
            price = streamPrice['bid']

        newTrade: Trade
        position: Position

        # find if position already exists
        try:
            position = Position.objects.get(
                subProduct=subProductId, user=user)

            # if positionSize = 0, just add the trade
            if position.size == 0:
                position.size += size
                position.avgPrice = price
                position.buy = buy
                newTrade = Trade.objects.create(
                    position=position, subProduct=subProduct, user=user, buy=buy, size=size, sizeLeft=size, price=price)
                position.save()
            else:

                # if we increase the position
                if (position.buy == buy):

                    newTrade = Trade.objects.create(
                        position=position, subProduct=subProduct, user=user, buy=buy, size=size, sizeLeft=size, price=price)
                    position.avgPrice = round((
                        position.avgPrice * position.size + price * size) / (position.size + size), 5)

                    position.size += size
                    position.save()

                # if we reverse the position and close some trades
                else:

                    # find trades to close
                    trades = Trade.objects.filter(
                        subProduct=subProductId, user=user, closed=False)
                    trades = trades.order_by('ts')
                    product = Product.objects.get(id=subProduct.product_id)

                    newTradeSizeLeft = size
                    newTradeClosed = False

                    for trade in trades:

                        if newTradeSizeLeft == 0:
                            break
                        else:
                            closingSize = min(trade.sizeLeft, newTradeSizeLeft)

                            # if we bought
                            if trade.buy == True:
                                pnlValue = round(
                                    closingSize * (-trade.price + price) * product.contractSize, 5)
                            # if we sold
                            else:
                                pnlValue = round(
                                    closingSize * (trade.price - price) * product.contractSize, 5)
                                # print(subProduct)
                                # print(subProduct.id)
                            pnl = Pnl.objects.create(
                                value=pnlValue, productType=product.productType, subProduct=subProduct, user=user)

                            pnlFeedback.append(pnl)

                            trade.sizeLeft -= closingSize
                            if trade.sizeLeft == 0:
                                trade.closed = True

                            trade.save()

                            newTradeSizeLeft -= closingSize
                            position.size -= closingSize
                            if newTradeSizeLeft == 0:
                                newTradeClosed = True

                    # closed all opened trades, still some left over
                    if newTradeSizeLeft > 0:
                        position.buy = buy
                        position.size = newTradeSizeLeft
                        position.avgPrice = price

                    if position.size == 0:
                        position.avgPrice = 0

                    position.save()

                    # add the new trade (we didn't before otherwise it gets looped)
                    newTrade = Trade.objects.create(
                        position=position, subProduct=subProduct, user=user, buy=buy, size=size, sizeLeft=newTradeSizeLeft, price=price, closed=newTradeClosed)

            # we only send back the new trade, the front end doesn't care about sizeLeft, closed etc
            tradeSerialized = TradeSerializer(newTrade, many=False)
            positionSerialized = PositionSerializer(position, many=False)
            pnlSerialized = PnlSerializer(pnlFeedback, many=True)
            response = {'trade': tradeSerialized.data,
                        'position': positionSerialized.data,
                        'pnl': pnlSerialized.data}
            return Response(response, status=status.HTTP_200_OK)

        # if the position for this subProduct didn't exist before
        except:

            position = Position.objects.create(
                subProduct=subProduct, user=user, buy=buy, size=size, avgPrice=price)
            newTrade = Trade.objects.create(
                position=position, subProduct=subProduct, user=user, buy=buy, size=size, sizeLeft=size, price=price)

            tradeSerialized = TradeSerializer(newTrade, many=False)
            positionSerialized = PositionSerializer(position, many=False)
            response = {'trade': tradeSerialized.data,
                        'position': positionSerialized.data,
                        'pnl': ''}
            return Response(response, status=status.HTTP_200_OK)

        # class MovieViewSet(viewsets.ModelViewSet):
        #     queryset = Movie.objects.all()
        #     serializer_class = MovieSerializer
        #     authentication_classes = (TokenAuthentication, )
        #     permission_classes = (IsAuthenticated, )
        #
        #     @action(detail=True, methods=['POST'])
        #     def rate_movie(self, request, pk=None):
        #         if 'stars' in request.data:
        #             movie = Movie.objects.get(id=pk)
        #             stars = request.data['stars']
        #             user = request.user
        #             # print(user)
        #             # user = User.objects.get(id=1)
        #             try:
        #                 rating = Rating.objects.get(user=user.id, movie=movie.id)
        #                 rating.stars = stars
        #                 rating.save()
        #                 serializer = RatingSerializer(rating, many=False)
        #                 response = {'message': 'Rating updated',
        #                             'result': serializer.data}
        #                 return Response(response, status=status.HTTP_200_OK)
        #             except:

        #                 rating = Rating.objects.create(
        #                     user=user, movie=movie, stars=stars)
        #                 serializer = RatingSerializer(rating, many=False)
        #                 response = {'message': 'Rating created',
        #                             'result': serializer.data}
        #                 return Response(response, status=status.HTTP_200_OK)

        #         else:
        #             response = {'message': 'You need to provide a rating'}
        #             return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # class RatingViewSet(viewsets.ModelViewSet):
        #     queryset = Rating.objects.all()
        #     serializer_class = RatingSerializer
        #     authentication_classes = (TokenAuthentication, )
        #     permission_classes = (IsAuthenticated, )

        #     def update(self, request, *args, **kwargs):
        #         response = {'message': "You can't update rating like that"}
        #         return Response(response, status=status.HTTP_400_BAD_REQUEST)

        #     def create(self, request, *args, **kwargs):
        #         response = {'message': "You can't create rating like that"}
        #         return Response(response, status=status.HTTP_400_BAD_REQUEST)

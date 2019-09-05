from typing import Dict
import mysql.connector
import sys
import requests
import time
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from datetime import datetime
from decimal import Decimal

import traceback
import logging

from trading_ig import (IGService, IGStreamService)
from trading_ig.config import config
from trading_ig.lightstreamer import Subscription

import simplejson as json
import redis

######    REDIS    ########

redisServer = redis.StrictRedis(host='localhost', port=6379, db=0)

######    CONFIG    ########

config_data = ""


with open('config.json') as config_file:
    config_data = json.load(config_file)


mydb = mysql.connector.connect(
    host=config_data['database']['host'],
    user=config_data['database']['user'],
    passwd=config_data['database']['passwd'],
    database=config_data['database']['database']
)


class IGServiceConfig(object):
    username = config_data['IG']['username']
    password = config_data['IG']['password']
    api_key = config_data['IG']['api_key']
    acc_type = config_data['IG']['acc_type']
    acc_number = config_data['IG']['acc_number']


mycursor = mydb.cursor()

priceObj = {}


def onPriceUpdate(item_update):
    global priceObj
    print(item_update['name'],
          item_update['values']['BID'], item_update['values']['OFFER'])
    priceObj[item_update['name']].update(
        item_update['values']['BID'], item_update['values']['OFFER'])


class Price:

    def __init__(self, dbItem):

        self.bid = dbItem[0]
        self.offer = dbItem[1]
        self.ts = datetime.fromtimestamp(dbItem[2])
        self.streamPriceId = dbItem[3]
        self.subProductId = dbItem[4]
        self.lastSaved = self.ts
        self.subProductName = dbItem[5]

    def update(self, bid, offer):
        if bid != "":
            self.bid = bid
        if offer != "":
            self.offer = offer

        self.ts = datetime.now()  # datetime.timestamp(datetime.now())

        redisServer.hset('streamPrices', self.subProductId, json.dumps(
            {"bid": Decimal(self.bid), "offer": Decimal(self.offer), "subProduct_id": self.subProductId, "ts": datetime.timestamp(self.ts)}, use_decimal=True))

    def saveToDB(self, savedTs):
        if self.ts > self.lastSaved and (self.ts - self.lastSaved).seconds > 1:
            self.lastSaved = savedTs
            sql = "UPDATE api_streamprice SET bid = %s, offer = %s, ts = %s WHERE subProduct_id = %s"
            val = (self.bid, self.offer, datetime.timestamp(
                savedTs), self.streamPriceId)
            mycursor.execute(sql, val)
            mydb.commit()

    def __str__(self):
        # {datetime.fromtimestamp(self.ts)}"
        return f"{self.subProductName} =  bid = {self.bid} | offer = {self.offer} @ {self.ts}"


def preload():

    sql = ("SELECT * from api_streamprice, api_subproduct WHERE api_streamprice.subProduct_id = api_subproduct.id")
    mycursor.execute(sql)
    streamPrice = mycursor.fetchall()

    priceDico = {}
    for item in streamPrice:
        # key = name
        priceDico[item[5]] = Price(item)

    return priceDico


def saveToDB():
    global priceObj

    now = datetime.now()
    for key in priceObj.keys():
        priceObj[key].saveToDB(now)


async def asyncLoadSubProducts():
    global priceObj
    priceObj = preload()
    return


def main():

    # setup
    global priceObj

    # logging.basicConfig(level=logging.INFO)
    config = IGServiceConfig()
    ig_service = IGService(
        config.username, config.password, config.api_key, config.acc_type
    )
    ig_stream_service = IGStreamService(ig_service)
    ig_session = ig_stream_service.create_session()

    accounts = ig_session[u'accounts']
    for account in accounts:
        if account[u'accountId'] == config.acc_number:
            accountId = account[u'accountId']
            break
    ig_stream_service.connect(accountId)

    # save to DB thread
    sched = BackgroundScheduler()
    sched.add_job(saveToDB, 'interval', seconds=5)
    sched.start()

    # Making a new Subscription in MERGE mode
    subscriptionCap = 38
    subscriptionCurrent = 0
    i = 0
    listSubscription = []
    while i < len(priceObj):
        items = list(priceObj.keys())[i:i+subscriptionCap]
        subscription_prices = Subscription(
            mode="MERGE",
            items=items,
            fields=["BID", "OFFER"]
        )
        subscription_prices.addlistener(onPriceUpdate)
        sub_key_prices = ig_stream_service.ls_client.subscribe(
            subscription_prices)
        listSubscription.append(sub_key_prices)
        time.sleep(2)
        # print(subscription_prices)
        print(items)
        i += subscriptionCap

    input("{0:-^80}\n".format("Press Enter to close"))

    # Disconnecting
    ig_stream_service.disconnect()


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncLoadSubProducts())
    loop.close()
    print("SubProducts loaded")

    main()


import time
import simplejson as json
import asyncio
import ccxt.async_support as ccxt
import redis


######    REDIS    ########

redisServer = redis.StrictRedis(host='localhost', port=6379, db=0)

######    CONFIG    ########

config_data = ""

with open('config.json') as config_file:
    config_data = json.load(config_file)

exchanges_watchlist = config_data['exchanges_watchlist']
tickers_watchlist = config_data['tickers_watchlist']

rules_dict = {}
rules_dict["\"BTC/USD\""] = "\"BTC/USDT\""

######    CCXT    #######

exchanges = []

for exchange in exchanges_watchlist:
    exchange_class = getattr(ccxt, exchange)
    exchange_obj = exchange_class({
        'apiKey': config_data['exchanges'][exchange]['apiKey'],
        'secret': config_data['exchanges'][exchange]['secret'],
        'timeout': 30000,
        'enableRateLimit': True,
    })
    exchanges.append(exchange_obj)


##############

def uniformize_symbols(data, rules_dict):
    """
    uniformize symbol names of json data, for ex Kraken uses BTC/USD, we want to display it as BTC/USDT like the others

    Parameters
    ----------
    data
        json data which has been dumped to a string

    rules_dict
        dictionary of rules used to replace

    Returns
    -------
    data
        our uniformized json data
    """

    for old, new in rules_dict.items():
        data = data.replace(old, new)

    return data


async def async_client(exchange):

    """
    Looping on exchanges for polling

    Parameters
    ----------
    exchange
        exchange name (ie- 'binance')

    Returns
    -------
    yield exchange + tickers info
        {'exchange': 'binance', 'tickers': {'LTC/BTC': {'symbol': 'LTC/BTC', 'timestamp': 1567380127738, 'datetime': '2019-09-01T23:22:07.738Z', 'high': 0.006955, 'low': 0.006689, 'bid': 0.006787, 'bidVolume': 49.27, 'ask': 0.006792 ...
    """

    client = getattr(ccxt, exchange.id)()
    tickers = await client.fetch_tickers(tickers_watchlist)
    await client.close()

    return {"exchange": exchange.id, "tickers": tickers}


async def continuous_yielding():
    """
    Looping on exchanges for polling

    Parameters
    ----------
    None

    Returns
    -------
    yield list of tickers info
        [{'exchange': 'binance', 'tickers': {'LTC/BTC': {'symbol': 'LTC/BTC', 'timestamp': 1567380127738, 'datetime': '2019-09-01T23:22:07.738Z', 'high': 0.006955, 'low': 0.006689, 'bid': 0.006787, 'bidVolume': 49.27, 'ask': 0.006792 ...]

    """

    while True:

        try:
            input_coroutines = [async_client(exchange)
                                for exchange in exchanges]
            tickers = await asyncio.gather(*input_coroutines, return_exceptions=True)

            yield tickers
            # 2 for now or the max of all exchanges of their rateLimit / 1000
            await asyncio.sleep(2)

        except ccxt.BaseError as e:
            print("Error -> ", type(e).__name__, str(e), str(e.args))
            await exchange.close()
            raise e


async def continous_two_way():
    """
    Used to continously poll the exchanges for the ticker_watchlist to get live bid/ask
    Store in Redis cache as: name=crypto | key=the_exchange_name | (symbol, bid, ask)

    Parameters
    ----------
    None

    Returns
    -------
    Store tuples in Redis
        name: crypto, key: exchange, tuple:[('LTC/BTC', 0.006692, 103.95, 0.006696, 12.65), ('BTC/USDT', 9776.83, 0.020453, 9778.27, 0.007295)]
    """

    async for feedback in continuous_yielding():

        for exchange in feedback:

            my_data = json.dumps([{'symbol': tickers['symbol'], 'bid': tickers['bid'], 'bidVolume': tickers['bidVolume'], 'ask': tickers['ask'], 'askVolume': tickers['askVolume']}
                                  for tickers in exchange['tickers'].values() if tickers['symbol'] in tickers_watchlist], use_decimal=True)

            my_data = uniformize_symbols(my_data, rules_dict)
            redisServer.hset('crypto', exchange['exchange'], my_data)

            print(my_data)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(continous_two_way())

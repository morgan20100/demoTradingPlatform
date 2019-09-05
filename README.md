# DemoTradingPlatform
[Work in progress] Demo Trading Platform Futures &amp; Options + Crypto arbitrage dashboard
Screenshot attached



## Working on a demo trading platform for futures / options in Python:
• I get the live prices from an online broker using websockets and put them in cache in Redis and every 5 secs in my SQL database\
• Django for the backend, Angular for the front end\
• I am connecting the back to front in websockets for pushing the live prices from my cache, API otherwise for http requests\
• One part of the platform is a typical future / fx trading interface with orders, trade blotter, positions & PnL\
• The second part of the platform is a mix between Eurex and a simplified version of Optiver’s, where I display the option prices with deltas, IV, strike positions etc. I built the risk module displaying the greeks per product/expiry (cash deltas, gammas and others) and MtM


## Crypto pair dashboard:
• Connecting to different crypto exchanges to retrieve bid/ask of a watchlist\
• Prices are then processed and filtered to find arbitrage "opportunities" between exchanges (gross margin for now), stored in cache then pushed to the front with websockets

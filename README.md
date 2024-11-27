## Steps to run as volume

If running in trading bot folder

`$ docker run --name v2_trade -v$(pwd)/app:/app --env-file .env bash`

Steps for building docker image

`docker --debug build . -t v2_trade`



## Sample API string for kraken

Kraken
`limit_order = trade.create_order(
                ordertype="market",
                side="buy",
                volume=10,
                pair=coin_kraken)`

coinbase

`rest_client.market_order_buy(client_order_id='00054353401', product_id='BTC-USDC',quote_size='1')`

### Reference links

Kraken API
https://github.com/btschwertfeger



Coinbase API
  https://docs.cdp.coinbase.com/advanced-trade/docs/sdk-rest-client-trade/
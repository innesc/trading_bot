## Steps to run as volume

### Steps for local development within a container (must be running)

Steps for building docker image

`docker --debug build . -t v3_trade`

Running in trading bot folder

`docker run -v$(pwd)/app:/app --env-file .env v3_trade `

Container needs to still be running our cant attach to container

`docker exec -it <cointainer id> bash`

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
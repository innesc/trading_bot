import time
import pandas as pd
from coinbase.rest import RESTClient
from datetime import datetime
import os
from kraken.spot import  Funding, Market, Trade, User
import logging
from dotenv import load_dotenv
load_dotenv()

CB_SECRET = os.getenv("CB_SECRET")
CB_API_KEY = os.getenv("CB_API_KEY")
KRAKEN_API_KEY = os.getenv("kraken_api_key")
KRAKEN_SECRET_KEY = os.getenv("kraken_private_key")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.addHandler(logging.StreamHandler())

def trade_buy_coin(rest_client,
                    price=None,
                    coin_coin="",
                    volume=0.0001,
                    buffer=0.05,
                    cancel=True):
    '''
    https://docs.cdp.coinbase.com/advanced-trade/docs/sdk-rest-client-trade/
    Works
    #rest_client.market_order_buy(client_order_id='00054353401', product_id='BTC-USDC',quote_size='1')
    '''
   
    try:
        limit_order = rest_client.limit_order_gtc_buy(
            client_order_id="00000002",
            product_id=coin_coin,
            base_size=str(volume),
            limit_price=str(price))
        print(limit_order)
    except Exception as e:
        # Log the full error details
        logger.error(f"Error placing limit order: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.content}")


    if cancel:
        limit_order_id = limit_order["order_id"]
        rest_client.cancel_orders(order_ids=[limit_order_id])


def trade_buy_kraken(trade,
                    price=None,
                    coin_coin="BTC-USD",
                    coin_kraken="BTC/CAD",
                    volume=0.0001,
                    buffer=0.05,
                    cancel=True):
    
    '''
    Works
limit_order = trade.create_order(
                ordertype="market",
                side="buy",
                volume=10,
                pair=coin_kraken,
            )
    '''

    try:
        limit_order = trade.create_order(
                ordertype="limit",
                side="buy",
                volume=volume,
                pair=coin_kraken,
                price=price ,
            )
        print(limit_order)
    except Exception as e:
        
        logger.error(f"Error placing limit order kraken: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.content}")

    if cancel:
        trade.cancel_all_orders()


def sell_kraken(trade,
                price=None,
                coin_coin="",
                coin_kraken="",
                volume=0.0001,
                buffer=0.05,
                cancel=True):
    '''
    Will sell if buy on coin
    '''

    try:
        limit_order = trade.create_order(
            ordertype='limit',
            side='sell',
            volume=volume,
            pair=coin_kraken,
            price=price
            )
        print(limit_order)
    except Exception as e:
        logger.error(f"Error placing limit order kraken: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.content}")


    if cancel:
        trade.cancel_all_orders()



def sell_coin(rest_client, volume, coin_coin, price):
    '''
    will sell if buy on kraken
    '''

    try:
        limit_order = rest_client.limit_order_gtc_sell(
            client_order_id="00000002",
            product_id=coin_coin,
            base_size=str(volume),
            limit_price=str(price))
        
        print(limit_order)
    except Exception as e:
        # Log the full error details
        logger.error(f"Error placing limit order: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.content}")

    return rest_client, limit_order



def coinbase_scan(rest_client):
    """scans for the price of the coins listed in coins_list 
    """
    
    price = rest_client.get_products()
    df = pd.DataFrame(price['products'])
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    df['logging_time'] = now

    return df

def get_price_kraken(coin):
    market = Market()

    #:return: The ticker(s) including ask, bid, close, volume, vwap, high, low, todays open and more
    data = market.get_ticker()
    df = pd.DataFrame(data)
    
    print("This ran")
    logger.debug(df[coin].loc['a'])


    return df[coin].loc['a'][0]

def assess():
    """Trivial version. Dies immediately"""
    return False

def orchestration(
                    buffer=0.05,
                    volume=0.0001,
                    coin_coin='BTC-USDC',
                    kraken_coin='BTC/USDC',
                    kraken_market='TBTCUSD'
                    ):
    
    rest_client = RESTClient(
                        api_secret=CB_SECRET,
                        api_key=CB_API_KEY,
                        base_url='api.coinbase.com'
                        )
    
    trade = Trade(key=KRAKEN_API_KEY, secret=KRAKEN_SECRET_KEY )

    price_krak = get_price_kraken( kraken_market)
    logger.info(f"The price in kraken {price_krak}")

    price_coin = rest_client.get_products()
    df = pd.DataFrame(price_coin['products'])
    price_coin = df[df['product_id']==coin_coin]['price']
    logger.info(f"The price in coin {price_coin}")

    price_krak = float(price_krak )
    price_coin= float(price_coin)
    print(f"price coin: {price_coin}  price kraken {price_krak}")

    if price_krak > (price_coin + buffer * price_coin ):

        print("buy coin sell kraken")
        sell_kraken(trade,
                price=price_krak,
                coin_coin=coin_coin,
                coin_kraken=kraken_coin,
                volume=volume,
                buffer=0,
                cancel=False)
        
        trade_buy_coin(rest_client,
                    price=price_coin,
                    coin_coin=coin_coin,
                    volume=volume,
                    buffer=0,
                    cancel=False)
    
    elif (price_krak +buffer * price_krak) < price_coin :
        print("buy kraken sell coin")
        trade_buy_kraken(trade,
                    price=price_krak,
                    coin_coin=coin_coin,
                    coin_kraken=kraken_coin,
                    volume=volume,
                    buffer=0,
                    cancel=True)

        sell_coin(rest_client, volume=volume,coin_coin=coin_coin, price=price_coin)
    
    return assess()

if __name__ == "__main__":
    #Docker up --env-file .env
    
    print('test I can change again')
    #print(CB_API_KEY)
    #print(CB_SECRET)


    RUN = True


    while RUN:
        RUN = orchestration(
                    buffer=0.00,
                    volume=0.0001,
                    coin_coin='BTC-USDC',
                    kraken_coin='BTC/USDC')
        logger.info(f"Loop ran with RUN as {RUN}")
        time.sleep(1)
    



import time
import pandas as pd
from coinbase.rest import RESTClient
from datetime import datetime
import os
from kraken.spot import  Funding, Market, Trade, User
import logging
import random
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
                   count,
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
            client_order_id=str(count),
            product_id=coin_coin,
            base_size=str(volume),
            limit_price=str(price))
        print(limit_order)
    except Exception as e:
        # Log the full error details
        logger.error(f"Error placing limit order: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.content}")

    print(f"value of cancel: {cancel}")

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



def sell_coin(rest_client, count, volume, coin_coin, price):
    '''
    will sell if buy on kraken
    '''

    try:
        limit_order = rest_client.limit_order_gtc_sell(
            client_order_id=str(count),
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


    return (float(df[coin].loc['a'][0]) +  float(df[coin].loc['b'][0])) / 2

def assess(count: int, traded: bool, count_trades: int, threshold=2) -> bool:
    """
    Determine if a trade attempt is allowed.

    Parameters:
    count (int): The current trade count.
    traded (bool): A flag indicating if a trade has already been attempted.
    count_trades (int): The total number of trades in the trading session.

    Returns:
    bool: False if a trade has been attempted, True otherwise.
    """
    # Check if a trade has already been made
    if (traded & (count_trades > threshold)):
        # No further trade attempts allowed
        return False
    else:
        # Trade attempt is allowed
        return True
    
def orchestration(
                    buffer=0.05,
                    volume=0.0001,
                    coin_coin='BTC-USDC',
                    kraken_coin='BTC/USDC',
                    count=1,
                    kraken_market='TBTCUSD',
                    count_trades=0
                    ):
    """
    Orchestration function for trading bot
    Parameters:
    buffer (float): how much more expensive the kraken price must be than the coin price
    volume (float): how many coins to trade
    coin_coin (str): id of the coin on coinbase
    kraken_coin (str): id of the coin on kraken
    count (int): a counter to keep track of the trade number
    kraken_market (str): market to get the price from in kraken
    
    Returns:
    bool: whether a trade was made or not
    """
    rest_client = RESTClient(
                        api_secret=CB_SECRET,
                        api_key=CB_API_KEY,
                        base_url='api.coinbase.com'
                        )
    
    trade = Trade(key=KRAKEN_API_KEY, secret=KRAKEN_SECRET_KEY )

    # Get the price from Kraken
    price_krak = get_price_kraken( kraken_market)
    logger.info(f"The price in kraken {price_krak}")

    # Get the price from Coinbase
    price_coin = rest_client.get_products()
    df = pd.DataFrame(price_coin['products'])
    price_coin = df[df['product_id']==coin_coin]['price']
    logger.info(f"The price in coin {price_coin}")

    price_krak = float(price_krak )
    price_coin= float(price_coin)
    print(f"price coin: {price_coin}  price kraken {price_krak}")

    traded = False
    if price_krak > (price_coin + buffer * price_coin ):

        print("buy coin sell kraken")
        # Buy on Kraken
        sell_kraken(trade,
                price=price_krak,
                coin_coin=coin_coin,
                coin_kraken=kraken_coin,
                volume=volume,
                buffer=0,
                cancel=False)
        
        print("buy coin worked")
        # Buy on Coinbase
        trade_buy_coin(rest_client,
                       count,
                    price=price_coin,
                    coin_coin=coin_coin,
                    volume=volume,
                    buffer=0,
                    cancel=False)
        print("buy coin worked 2")
        traded = True
        count_trades = count_trades + 1
    elif (price_krak +buffer * price_krak) < price_coin :
        print("buy kraken sell coin")
        # Buy on Kraken
        trade_buy_kraken(trade,
                    price=price_krak,
                    coin_coin=coin_coin,
                    coin_kraken=kraken_coin,
                    volume=volume,
                    buffer=0,
                    cancel=False)
        print("buy kraken sell coin")

        print("sell coin worked")
        # Sell on Coinbase
        sell_coin(rest_client, count, volume=volume,coin_coin=coin_coin, price=price_coin)
        print("sell coin worked 2")
        traded = True
        count_trades = count_trades + 1
    return assess(count, traded, count_trades), count_trades

if __name__ == "__main__":
    #Docker up --env-file .env
    
    print('test I can change again')
    #print(CB_API_KEY)
    #print(CB_SECRET)


    RUN = True
    count = 0
    count_trades = 0

    while RUN:
        count += 1
        RUN, count_trades = orchestration(
                    buffer=0.00,
                    volume=0.0001,
                    coin_coin='BTC-USDC',
                    kraken_coin='BTC/USDC',
                    count=count,
                    count_trades=count_trades
                    )
        logger.info(f"Loop ran with count as {count}")
        logger.info(f"Loop ran with trade count as {count_trades}")
        time.sleep(1)
    



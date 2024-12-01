import time
import pandas as pd
from coinbase.rest import RESTClient
from datetime import datetime
import os
from kraken.spot import  Funding, Market, Trade, User
import logging
import json
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
    """
    Place a limit buy order on coinbase using the REST client
    Parameters:
    rest_client (RESTClient): Instance of the REST Client
    count (int): Client order ID
    price (float, None): Price at which to place the order. If None, use the current price
    coin_coin (str): The coin pair to trade
    volume (float): The amount of the coin to buy
    buffer (float): The buffer to apply to the price
    cancel (bool): Whether to cancel any existing limit orders after placing this one
    """
    try:
        # If price is None, use the current price
        if price is None:
            product = rest_client.get_product(coin_coin)
            price = float(product["price"])
            price = str(int(((price - buffer*price)//1)))

        # Place the limit order
        limit_order = rest_client.limit_order_gtc_buy(
            client_order_id=str(count),
            product_id=coin_coin,
            base_size=str(volume),
            limit_price=price)
        print(limit_order)
    except Exception as e:
        # Log the full error details
        logger.error(f"Error placing limit order: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.content}")

    print(f"value of cancel: {cancel}")

    if cancel:
        # Cancel any existing limit orders
        limit_order_id = limit_order["order_id"]
        rest_client.cancel_orders(order_ids=[limit_order_id])


def trade_buy_kraken(trade,
                    price=None,
                    coin_coin="BTC-USD",
                    coin_kraken="BTC/CAD",
                    volume=0.0001,
                    buffer=0.05,
                    cancel=True):
    """
    Place a limit buy order on Kraken using the kraken.spot.Trade client
    Parameters:
    trade (kraken.spot.Trade): Instance of the Trade client
    price (float, None): Price at which to place the order. If None, use the current price
    coin_coin (str): The coin pair to trade
    coin_kraken (str): The coin pair on kraken
    volume (float): The amount of the coin to buy
    buffer (float): The buffer to apply to the price
    cancel (bool): Whether to cancel any existing limit orders after placing this one
    
    """
    try:
        # If price is None, use the current price
        if price is None:
            product = trade.get_product(coin_coin)
            price = float(product["price"])
            price = str(int(((price - buffer*price)//1)))

        # Place the limit order
        limit_order = trade.create_order(
                ordertype="limit",
                side="buy",
                volume=volume,
                pair=coin_kraken,
                price=price ,
            )
        print(limit_order)
    except Exception as e:
        # Log the full error details
        logger.error(f"Error placing limit order kraken: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.content}")

    if cancel:
        # Cancel any existing limit orders
        limit_order_id = limit_order["order_id"]
        trade.cancel_all_orders(order_ids=[limit_order_id])


def get_account_balances_BTC():

    user = User(key=KRAKEN_API_KEY, secret=KRAKEN_SECRET_KEY)
    account_balance = user.get_account_balance()

    client = RESTClient(
                        api_secret=CB_SECRET,
                        api_key=CB_API_KEY,
                        base_url='api.coinbase.com'
                        )
    accounts = client.get_accounts()['accounts']
    print(accounts)
    coin_USDC = [account for account in accounts if (account['name'] in [ 'USDC Wallet'])][0]['available_balance']['value']
    coin_BTC = [account for account in accounts if (account['name'] in ['BTC Wallet'])][0]['available_balance']['value']
    

    total_portfolio = pd.DataFrame({'USDC': [float(account_balance['USDC']) + float(coin_USDC)], 'BTC':[float(account_balance['XXBT']) + float(coin_BTC)]})
    print(total_portfolio)

    return total_portfolio


def get_account_balances():

    user = User(key=KRAKEN_API_KEY, secret=KRAKEN_SECRET_KEY)
    account_balance = user.get_account_balance()

    client = RESTClient(
                        api_secret=CB_SECRET,
                        api_key=CB_API_KEY,
                        base_url='api.coinbase.com'
                        )
    accounts = client.get_accounts()['accounts']
    print(accounts)
    coin_USDC = [account for account in accounts if (account['name'] in [ 'USDC Wallet'])][0]['available_balance']['value']
    coin_other_names 
    coin_other_balance = [account for account in accounts if (account['name'] in ['BTC Wallet'])][0]['available_balance']['value']
    

    total_portfolio = pd.DataFrame({'USDC': [float(account_balance['USDC']) + float(coin_USDC)], '':[float(account_balance['XXBT']) + float(coin_other)]})
    print(total_portfolio)

    return total_portfolio

def sell_kraken(trade,
                price=None,
                coin_coin="",
                coin_kraken="",
                volume=0.0001,
                buffer=0.05,
                cancel=True):
    '''
    Will sell if buy on coin
    Parameters:
    trade (kraken.spot.Trade): Instance of the Trade client
    price (float, None): Price at which to place the sell order. If None, use the current price
    coin_coin (str): The coin pair to sell
    coin_kraken (str): The coin pair on kraken
    volume (float): The amount of the coin to sell
    buffer (float): The buffer to apply to the price
    cancel (bool): Whether to cancel any existing limit orders after placing this one
    '''
    try:
        # If price is None, use the current price
        if price is None:
            market = trade.get_ticker()
            price = market[coin_kraken]['c'][0]

        # Place the limit sell order
        limit_order = trade.create_order(
            ordertype='limit',
            side='sell',
            volume=volume,
            pair=coin_kraken,
            price=price
            )
        print(limit_order)
    except Exception as e:
        # Log the full error details
        logger.error(f"Error placing limit order kraken: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.content}")

    if cancel:
        # Cancel any existing limit orders
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
    """
    Gets the current price of a coin on Kraken.
a
    Parameters
    ----------
    coin : str
        The coin to get the price for. For example, 'BTC/CAD'.

    Returns
    -------
    float
        The current price of the coin on Kraken.
    """
    market = Market()

    # Get the ticker for the coin
    data = market.get_ticker()
    df = pd.DataFrame(data)
    
    logger.debug(df[coin].loc['a'])
    logger.debug(df[coin].loc['b'])

    # Calculate the mean of the ask and bid prices.  #:return: The ticker(s) including ask, bid, close, volume, vwap, high, low, todays open and more
    return (float(df[coin].loc['a'][0]) +  float(df[coin].loc['b'][0])) / 2


def price_logger(price_krak, price_coin, coin_coin, path_csv='/Users/clintoninnes/Desktop/programming/python_stuff/2024/trading_bot/temp.csv'):
    
    """
    Logs prices of coin on kraken and coinbase.

    Parameters
    ----------
    price_krak : float
        The price of the coin on kraken.
    price_coin : float
        The price of the coin on coinbase.
    coin_coin : str
        The coin being traded.
    path_csv : str
        The path to where the csv will be saved
    Returns
    -------
    None
    """
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if os.path.isfile(path_csv) == False :
        df = pd.DataFrame({'time':[now],'price_krak':[price_krak], 'price_coin':[price_coin], 'coin_coin':[coin_coin]})
        df.to_csv(path_csv, index=False)
    else:
        df_all = pd.read_csv(path_csv)
        df = df_all.append(pd.DataFrame({'time':[now],'price_krak':[price_krak], 'price_coin':[price_coin], 'coin_coin':[coin_coin]}))
        df.to_csv(path_csv, index=False)
        


def assess(count: int, traded: bool, count_trades: int, threshold=5, logging_path='/Users/clintoninnes/Desktop/programming/python_stuff/2024/trading_bot/trading_bot_accounts.csv') -> bool:
    """
    Determine if a trade attempt is allowed.

    Parameters:
    count (int): The current trade count.
    traded (bool): A flag indicating if a trade has already been attempted.
    count_trades (int): The total number of trades in the trading session.

    Returns:
    bool: False if a trade has been attempted, True otherwise.
    """
    

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if os.path.isfile(logging_path) == False :
        df =  get_account_balances()
        df.to_csv(logging_path, index=False)
    else:
        df_all = pd.read_csv(logging_path)
        df =  get_account_balances()
        df_all = df_all.append(df)
        df_all.to_csv(logging_path, index=False)
        

    # Check if a trade has already been made
    if (traded & (count_trades > threshold)):
        # No further trade attempts allowed
        return False
    else:
        # Trade attempt is allowed
        return True
    
def orchestration(
                    buffer: float = 0.05,
                    volume: float = 0.0001,
                    coinbase_coin: str = 'BTC-USDC',
                    kraken_coin: str = 'BTC/USDC',
                    count: int = 1,
                    kraken_market: str = 'XBTUSDC',
                    count_trades: int = 0,
                    live_trade: bool = True
                    ) -> tuple:
    """
    Orchestration function for trading bot. This function will trade if the price of the coin on Kraken is higher than the
    price of the coin on Coinbase, and the difference is bigger than the buffer.

    Parameters:
    buffer (float): how much more expensive the kraken price must be than the coin price
    volume (float): how many coins to trade
    coinbase_coin (str): id of the coin on coinbase
    kraken_coin (str): id of the coin on kraken
    count (int): a counter to keep track of the trade number
    kraken_market (str): market to get the price from in kraken
    
    Returns:
    tuple: whether a trade was made or not, and the new count_trades
    """
    rest_client = RESTClient(
                        api_secret=CB_SECRET,
                        api_key=CB_API_KEY,
                        base_url='api.coinbase.com',
                        )
    
    trade = Trade(key=KRAKEN_API_KEY, secret=KRAKEN_SECRET_KEY )

    # Get the price from Kraken
    kraken_price = get_price_kraken(kraken_market)
    logger.info(f"The price in kraken {kraken_price}")

    # Get the price from Coinbase
    price_coin = rest_client.get_products()
    df = pd.DataFrame(price_coin['products'])
    price_coin = df[df['product_id']== coinbase_coin]['price']
    coinbase_price = float(price_coin)

    logger.info(f"The price in coin {coinbase_price}")

    # Check if we should trade
    traded = False
    if live_trade:
        if kraken_price > (coinbase_price + buffer * coinbase_price):
            # Buy on Kraken
            sell_kraken(trade,
                        price=kraken_price,
                        coin_coin=coinbase_coin,
                        coin_kraken=kraken_coin,
                        volume=volume,
                        buffer=0,
                        cancel=False)
            
            # Buy on Coinbase
            trade_buy_coin(rest_client,
                        count,
                        price=coinbase_price,
                        coin_coin=coinbase_coin,
                        volume=volume,
                        buffer=0,
                        cancel=False)
            traded = True
            count_trades += 1
        elif (kraken_price + buffer * kraken_price) < coinbase_price:
            # Buy on Kraken
            trade_buy_kraken(trade,
                        price=kraken_price,
                        coin_coin=coinbase_coin,
                        coin_kraken=kraken_coin,
                        volume=volume,
                        cancel=False)
            # Sell on Coinbase
            sell_coin(rest_client, count, volume=volume,coin_coin=coinbase_coin, price=coinbase_price)
            traded = True
            count_trades = count_trades + 1
    
    price_logger(kraken_price, coinbase_price, coinbase_coin)
    return assess(count, traded, count_trades), count_trades

if __name__ == "__main__":
    
    print('test I can change again')


    RUN = False
    count = 0
    count_trades = 0

    while RUN:
        count += 1
        RUN, count_trades = orchestration(
                    buffer=0.02,
                    volume=0.0001,
                    coinbase_coin='BTC-USDC',
                    kraken_coin='BTC/USDC',
                    count=count,
                    count_trades=count_trades,
                    live_trade=False
                    )
        logger.info(f"Loop ran with count as {count}")
        logger.info(f"Loop ran with trade count as {count_trades}")
        time.sleep(30)
    while True:
        logger.info(f"Loop ran with trade count as {count_trades}")
        logger.info("test mounted as volume")
        time.sleep(1000)    
    



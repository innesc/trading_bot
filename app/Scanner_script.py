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


def kraken_scan():
    market = Market()

    #:return: The ticker(s) including ask, bid, close, volume, vwap, high, low, todays open and more
    data = market.get_ticker()
    df = pd.DataFrame(data)

    df = (df.loc['a',:] + df.loc['b',:]) / 2

    df['logging time kraken'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return df

def coinbase_scan():
    """scans for the price of the coins listed in coins_list 
    """
    
    rest_client = RESTClient(
                            api_secret=CB_SECRET,
                            api_key=CB_API_KEY,
                            base_url='api.coinbase.com'
                            )

    price = rest_client.get_products()
    df = pd.DataFrame(price['products'])
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    df['logging_time'] = now

    return df

def log_both():
    df_coinbase = coinbase_scan()
    df_kraken = kraken_scan()
    df_kraken.columns = [col + '_from_kraken' for col in df_kraken.columns]
    df_coinbase.columns = [col + '_from_coin' for col in df_coinbase.columns]


    return pd.Concat([df_kraken, df_coinbase], axis=0)




if __name__ == "__main__":


    PATH = os.getenv('PATH_CSV')
    RUN = True
    FIRST = True
    if not FIRST:
        Data = pd.read_csv(PATH)
    else:
        Data = log_both()

    while RUN:
        time.sleep(2)
        df = log_both()
        Data = pd.concat([Data,df])
        Data.to_csv(PATH)



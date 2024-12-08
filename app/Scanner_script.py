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
    for col in df.columns:
        df[col] = df[col].map(lambda x: x[0])


    df = ((df.loc['a',:].astype(float) + df.loc['b',:].astype(float)) / 2)

    df['logging time kraken'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return df.to_frame().T

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
    df.index = df.product_id
    df = df['price'].to_frame().T
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    df['logging_time'] = now
    df.index=range(len(df))
    return df


def put_in_csv(f, CSV_PATH):
    """Puts the output of a function into a csv in an append manner
    
    If the file does not exist, it will create it and put the data in it.
    If the file exists, it will append the new data to the existing file
    
    :param f: a function that returns a dataframe
    :param CSV_PATH: the path to the csv file
    """
    if os.path.isfile(CSV_PATH) == False :
        # If the file does not exist, create it and put the data in it
        df = f()
        df.to_csv(CSV_PATH, index=False)
    else:
        # If the file exists, append the new data to the existing file
        df_all = pd.read_csv(CSV_PATH)
        df = f()
        df_all = pd.concat([df_all,df])
        df_all.to_csv(CSV_PATH, index=False)

def log_both():
    df_coinbase = coinbase_scan()
    df_kraken = kraken_scan()
    df_kraken.columns = [col + '_from_kraken' for col in df_kraken.columns]
    df_coinbase.columns = [col + '_from_coin' for col in df_coinbase.columns]

    return pd.concat([df_kraken, df_coinbase], axis=1)

#@put_in_csv(CSV_PATH='total_markey.csv')
def log_both_v2():
    df_coinbase = coinbase_scan()
    df_kraken = kraken_scan()
    df_kraken.columns = [col + '_from_kraken' for col in df_kraken.columns]
    df_coinbase.columns = [col + '_from_coin' for col in df_coinbase.columns]

    return pd.concat([df_kraken, df_coinbase], axis=1)


if __name__ == "__main__":


    PATH = os.getenv('PATH_CSV')
    RUN = True
    FIRST = True
    if not FIRST:
        Data = pd.read_csv(PATH)
    else:
        Data = log_both()
    while RUN:
        time.sleep(15)
        df = log_both()
        Data = pd.concat([Data,df])
        Data.to_csv(PATH)
        print(f"This many rows and columns logged {str(Data.shape)}")



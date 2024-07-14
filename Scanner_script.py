import time
import pandas as pd
from coinbase.rest import RESTClient
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

CB_SECRET = os.getenv("CB_SECRET")
CB_API_KEY = os.getenv("CB_API_KEY")


def coinbase_scan(rest_client):
    """scans for the price of the coins listed in coins_list 
    """
    
    price = rest_client.get_products()
    df = pd.DataFrame(price['products'])
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    df['logging_time'] = now

    return df

if __name__ == "__main__":

    print(CB_API_KEY)
    print(CB_SECRET)
    

    rest_client = RESTClient(
                            api_secret=CB_SECRET,
                            api_key=CB_API_KEY,
                            base_url='api.coinbase.com'
                            )
    
    PATH = os.getenv('PATH_CSV')
    RUN = True
    FIRST = True
    if not FIRST:
        Data = pd.read_csv(PATH)
    else:
        Data = coinbase_scan(rest_client)

    while RUN:
        time.sleep(10)
        df = coinbase_scan(rest_client)
        Data = pd.concat([Data,df])
        Data.to_csv(PATH)



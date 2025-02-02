# Crypto Arbitrage Trading Bot

## What is it ?

Simple trading bot for trading between crypto exchanges.

## Features

- **Real-Time Price Monitoring**: Continuously monitors the prices of selected cryptocurrencies on two exchanges.
- **Arbitrage Detection**: Identifies price differences between the two exchanges that exceed a predefined threshold.
- **Automated Trading**: Executes buy and sell orders automatically to capitalize on arbitrage opportunities.
- **Risk Management**: Stop executation if previous strategy failed to execute plus stop loss prevention.
- **Logging and Reporting**: Logs all trades and provides detailed reports for analysis.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.11 or higher
- pip (Python package manager)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/innesc/trading_bot.git](https://github.com/innesc/trading_bot.git
   cd trading_bot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Configuration**:
   - Rename `create .env`.
   - Fill in the required fields with your API keys and other configuration details. ENsure you have accounts on kraken and coinbase with required API settings

## Configuration

The `.env` file contains all the necessary settings for the bot:

```
CB_SECRET=<coinbase secret>
CB_API_KEY= <Coinbase api key>
PATH_CSV=<PATH to save prices>
kraken_private_key= <Kraken key>
kraken_api_key= <Kraken API key>
```


## Usage

To start the bot, run the following command:

```bash
python tading_bot.py
```

The bot will start monitoring the prices on the two exchanges and execute trades when arbitrage opportunities are detected.


## Steps to run as docker container

### Steps for local development within a container (must be running)

Steps for building docker image

`docker --debug build . -t <tag name>`

Running in trading bot folder

`docker run -v$(pwd)/app:/app --env-file .env <tag name> `

Container needs to still be running our cant attach to container

`docker exec -it <cointainer id> bash`



## Disclaimer

This bot is for educational purposes only. Trading cryptocurrencies involves significant risk, and you should only trade with money you can afford to lose. The authors of this project are not responsible for any losses you may incur.

## Support

Limitted. Although for any issues or questions, please open an issue on the GitHub repository or contact the maintainers directly.

## Reference links

Kraken API
https://github.com/btschwertfeger


Coinbase API
  https://docs.cdp.coinbase.com/advanced-trade/docs/sdk-rest-client-trade/

---

**Happy Trading!** 🚀




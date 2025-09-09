# src/basic_bot.py
import logging
import time
from typing import Dict, Optional
from binance.client import Client


# Setup logging
logger = logging.getLogger("binance_bot")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("bot.log")
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class BasicBot:
    """
    Core Binance Futures USDT-M Testnet bot wrapper.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.client.API_URL = "https://testnet.binancefuture.com"
        logger.info("Initialized Binance client (testnet=%s)", testnet)
        time.sleep(0.2)

    def get_balance(self):
        try:
            balance = self.client.futures_account_balance()
            logger.info("Fetched balance.")
            return balance
        except Exception as e:
            logger.exception("Error fetching balance: %s", e)
            return None

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:
        try:
            logger.info("Placing MARKET order: %s %s %s", side, quantity, symbol)
            res = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=quantity
            )
            logger.info("Market order response: %s", res)
            return res
        except Exception as e:
            logger.exception("Market order failed: %s", e)
            return None

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Optional[Dict]:
        try:
            logger.info("Placing LIMIT order: %s %s %s @ %s", side, quantity, symbol, price)
            res = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                timeInForce="GTC",
                quantity=quantity,
                price=str(price)
            )
            logger.info("Limit order response: %s", res)
            return res
        except Exception as e:
            logger.exception("Limit order failed: %s", e)
            return None

    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, stop_price: float, limit_price: float):
        try:
            logger.info("Placing STOP-LIMIT order: %s %s %s stop=%s limit=%s",
                        side, quantity, symbol, stop_price, limit_price)
            res = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="STOP",
                stopPrice=str(stop_price),
                price=str(limit_price),
                quantity=quantity,
                timeInForce="GTC"
            )
            logger.info("Stop-limit order response: %s", res)
            return res
        except Exception as e:
            logger.exception("Stop-limit order failed: %s", e)
            return None

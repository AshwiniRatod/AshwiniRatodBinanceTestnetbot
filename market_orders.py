# src/market_orders.py
"""
Market order CLI and shared BasicBot implementation.

Usage:
    python src/market_orders.py BTCUSDT BUY 0.001
"""
import os
import time
import argparse
import logging
from typing import Optional, Dict, Any

from dotenv import load_dotenv

# Load .env
load_dotenv()

# Setup logging to bot.log and console
logger = logging.getLogger("binance_bot")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler("bot.log")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(ch)

# Import python-binance Client lazily
try:
    from binance.client import Client
except Exception:
    try:
        from binance import Client
    except Exception as e:
        logger.exception("python-binance not found. Install with: pip install python-binance")
        raise

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


class BasicBot:
    """
    Minimal Binance Futures Bot.
    Supports balance fetching and MARKET orders.
    """
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        if not api_key or not api_secret:
            raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET must be set in .env")
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            # enforce testnet base URL (for some versions of python-binance)
            try:
                self.client.API_URL = "https://testnet.binancefuture.com"
            except Exception:
                pass
            logger.info("Binance client initialized (testnet=%s)", testnet)
            time.sleep(0.2)
        except Exception as e:
            logger.exception("Failed to initialize Binance client: %s", e)
            raise

    def get_balance(self) -> Optional[Any]:
        try:
            bal = self.client.futures_account_balance()
            logger.info("Fetched futures balance.")
            return bal
        except Exception as e:
            logger.exception("Error fetching balance: %s", e)
            return None

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:
        try:
            side = side.upper()
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


# --------- Validation Helpers ----------
def validate_symbol(s: str) -> str:
    if not s or not s.isalnum():
        raise argparse.ArgumentTypeError("Symbol must be alphanumeric, e.g., BTCUSDT")
    return s.upper()


def validate_side(s: str) -> str:
    s = s.upper()
    if s not in ("BUY", "SELL"):
        raise argparse.ArgumentTypeError("Side must be BUY or SELL")
    return s


def validate_positive_float(s: str) -> float:
    try:
        v = float(s)
    except ValueError:
        raise argparse.ArgumentTypeError("Must be a number")
    if v <= 0:
        raise argparse.ArgumentTypeError("Must be > 0")
    return v


# --------- Wrapper for Flask (fixes your error) ----------
def place_market_order(symbol: str, side: str, quantity: float):
    """
    Convenience wrapper so Flask app can call:
        from src import market_orders
        market_orders.place_market_order("BTCUSDT", "BUY", 0.001)
    """
    bot = BasicBot(API_KEY, API_SECRET, testnet=True)
    return bot.place_market_order(symbol, side, quantity)


# --------- CLI Support ----------
def main():
    parser = argparse.ArgumentParser(description="Place a MARKET order on Binance Futures Testnet (USDT-M)")
    parser.add_argument("symbol", type=validate_symbol, help="Symbol, e.g., BTCUSDT")
    parser.add_argument("side", type=validate_side, help="BUY or SELL")
    parser.add_argument("quantity", type=validate_positive_float, help="Quantity (base asset)")
    args = parser.parse_args()

    bot = BasicBot(API_KEY, API_SECRET, testnet=True)

    bal = bot.get_balance()
    print("Futures Testnet Balance:")
    if bal:
        for a in bal:
            print(f"{a['asset']}: {a['balance']}")

    resp = bot.place_market_order(symbol=args.symbol, side=args.side, quantity=args.quantity)
    print("\nOrder response:")
    print(resp)


if __name__ == "__main__":
    main()

# src/advanced/stop_limit.py
import argparse
import os
from dotenv import load_dotenv
from basic_bot import BasicBot

load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


def main():
    parser = argparse.ArgumentParser(description="Place a STOP-LIMIT order on Binance Futures Testnet")
    parser.add_argument("symbol", help="e.g., BTCUSDT")
    parser.add_argument("side", choices=["BUY", "SELL"])
    parser.add_argument("quantity", type=float)
    parser.add_argument("stop_price", type=float)
    parser.add_argument("limit_price", type=float)
    args = parser.parse_args()

    bot = BasicBot(API_KEY, API_SECRET, testnet=True)
    resp = bot.place_stop_limit_order(args.symbol, args.side, args.quantity, args.stop_price, args.limit_price)
    print("Stop-Limit Order Response:", resp)


if __name__ == "__main__":
    main()

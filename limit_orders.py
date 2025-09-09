# src/limit_orders.py
"""
Limit order CLI using BasicBot from market_orders.py.

Usage:
    python src/limit_orders.py BTCUSDT BUY 0.001 30000
"""
import argparse
from dotenv import load_dotenv

# Import shared BasicBot and logger from market_orders

from src.market_orders import BasicBot, validate_symbol, validate_side, validate_positive_float, API_KEY, API_SECRET, logger

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Place a LIMIT order on Binance Futures Testnet (USDT-M)")
    parser.add_argument("symbol", type=validate_symbol, help="Symbol, e.g., BTCUSDT")
    parser.add_argument("side", type=validate_side, help="BUY or SELL")
    parser.add_argument("quantity", type=validate_positive_float, help="Quantity (base asset)")
    parser.add_argument("price", type=validate_positive_float, help="Limit price (quote asset)")
    args = parser.parse_args()

    bot = BasicBot(API_KEY, API_SECRET, testnet=True)
    resp = bot.place_limit_order(args.symbol, args.side, args.quantity, args.price) if hasattr(bot, "place_limit_order") else None

    # If place_limit_order isn't defined on BasicBot (we kept BasicBot minimal), implement inline call:
    if resp is None:
        try:
            # Call client directly to place limit order
            resp = bot.client.futures_create_order(
                symbol=args.symbol,
                side=args.side,
                type="LIMIT",
                timeInForce="GTC",
                quantity=args.quantity,
                price=str(args.price)
            )
            logger.info("Limit order response: %s", resp)
        except Exception as e:
            logger.exception("Limit order failed: %s", e)
            resp = None

    print("Limit Order Response:")
    print(resp)


if __name__ == "__main__":
    main()

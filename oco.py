# src/advanced/oco.py
"""
Simulated OCO (One-Cancels-the-Other) for USDT-M Futures.
Places a take-profit LIMIT and a STOP-LIMIT (STOP) order.
This script only places both orders and prints responses. Cancel/monitor logic is not implemented here
(because that requires a separate watcher or websocket/polling loop).
Usage example:
    python src/advanced/oco.py BTCUSDT BUY 0.001 35000 30000 29900
Arguments:
    symbol side quantity tp_price stop_price stop_limit_price
"""
import argparse
from dotenv import load_dotenv

# import BasicBot, API env and logger from market_orders
from src.market_orders import BasicBot, validate_symbol, validate_side, validate_positive_float, API_KEY, API_SECRET, logger


load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Simulate OCO by placing TP LIMIT and STOP-LIMIT orders (Futures Testnet)")
    parser.add_argument("symbol", type=validate_symbol)
    parser.add_argument("side", type=validate_side)
    parser.add_argument("quantity", type=validate_positive_float)
    parser.add_argument("tp_price", type=validate_positive_float, help="Take-profit limit price")
    parser.add_argument("stop_price", type=validate_positive_float, help="Stop trigger price")
    parser.add_argument("stop_limit_price", type=validate_positive_float, help="Stop-limit price")
    args = parser.parse_args()

    bot = BasicBot(API_KEY, API_SECRET, testnet=True)
    # Take profit is opposite side (if you BUY to open, you SELL to close)
    close_side = "SELL" if args.side == "BUY" else "BUY"

    try:
        tp = bot.client.futures_create_order(
            symbol=args.symbol,
            side=close_side,
            type="LIMIT",
            timeInForce="GTC",
            quantity=args.quantity,
            price=str(args.tp_price)
        )
        logger.info("Take-profit LIMIT order placed: %s", tp)
    except Exception as e:
        logger.exception("Failed to place take-profit LIMIT order: %s", e)
        tp = None

    try:
        sl = bot.client.futures_create_order(
            symbol=args.symbol,
            side=close_side,
            type="STOP",
            stopPrice=str(args.stop_price),
            price=str(args.stop_limit_price),
            quantity=args.quantity,
            timeInForce="GTC"
        )
        logger.info("Stop-LIMIT order placed: %s", sl)
    except Exception as e:
        logger.exception("Failed to place STOP-LIMIT order: %s", e)
        sl = None

    print("OCO Simulation Results:")
    print({"take_profit": tp, "stop_limit": sl})


if __name__ == "__main__":
    main()

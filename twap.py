# src/advanced/twap.py
"""
Simple TWAP implementation that splits a total quantity into slices and places market orders at intervals.
Usage:
    python src/advanced/twap.py BTCUSDT BUY 0.01 5 10
Arguments:
    symbol side total_quantity slices interval_seconds
"""
import argparse
import time
from dotenv import load_dotenv

from src.market_orders import (
    BasicBot,
    validate_symbol,
    validate_side,
    validate_positive_float,
    API_KEY,
    API_SECRET,
    logger,
)


load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="TWAP: split large order into slices over time (market orders).")
    parser.add_argument("symbol", type=validate_symbol)
    parser.add_argument("side", type=validate_side)
    parser.add_argument("total_quantity", type=validate_positive_float)
    parser.add_argument("slices", type=int, help="Number of slices (integer > 0)")
    parser.add_argument("interval_seconds", type=int, help="Seconds between slices")
    args = parser.parse_args()

    if args.slices <= 0:
        raise SystemExit("slices must be > 0")

    bot = BasicBot(API_KEY, API_SECRET, testnet=True)

    qty_per_slice = args.total_quantity / args.slices
    results = []
    for i in range(args.slices):
        logger.info("TWAP slice %d/%d : placing market order %s %s %s", i+1, args.slices, args.side, qty_per_slice, args.symbol)
        res = bot.place_market_order(args.symbol, args.side, qty_per_slice)
        results.append(res)
        if i < args.slices - 1:
            time.sleep(args.interval_seconds)

    print("TWAP Results:")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()

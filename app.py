import sys
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
from src import market_orders, limit_orders
from src.advanced import oco, twap

app = Flask(__name__)
app.secret_key = "testnet_secret"
logging.basicConfig(filename="bot.log", level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# ---------------- CLI Mode ---------------- #
def cli_mode():
    if len(sys.argv) > 1:
        order_type = sys.argv[1].lower()
        try:
            if order_type == "market":
                _, _, symbol, side, qty = sys.argv
                market_orders.place_market_order(symbol, side, float(qty))

            elif order_type == "limit":
                _, _, symbol, side, qty, price = sys.argv
                limit_orders.place_limit_order(symbol, side, float(qty), float(price))

            elif order_type == "oco":
                _, _, symbol, side, qty, price, stop, limit_price = sys.argv
                oco.place_oco_order(symbol, side, float(qty), float(price), float(stop), float(limit_price))

            elif order_type == "twap":
                _, _, symbol, side, qty, chunks, interval = sys.argv
                twap.place_twap_order(symbol, side, float(qty), int(chunks), int(interval))

            else:
                print("Invalid order type. Use: market, limit, oco, twap")
        except Exception as e:
            logging.error(f"CLI error: {e}")
            print(f"❌ Error: {e}")
        sys.exit(0)


# ---------------- Flask Frontend ---------------- #
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/trade", methods=["GET", "POST"])
def trade():
    order_response = None
    if request.method == "POST":
        try:
            symbol = request.form["symbol"]
            side = request.form["side"]
            order_type = request.form["order_type"]
            qty = float(request.form["quantity"])

            if order_type == "MARKET":
                order_response = market_orders.place_market_order(symbol, side, qty)

            elif order_type == "LIMIT":
                price = float(request.form["price"])
                order_response = limit_orders.place_limit_order(symbol, side, qty, price)

            elif order_type == "OCO":
                price = float(request.form["price"])
                stop = float(request.form["stop"])
                limit_price = float(request.form["limit_price"])
                order_response = oco.place_oco_order(symbol, side, qty, price, stop, limit_price)

            elif order_type == "TWAP":
                chunks = int(request.form["chunks"])
                interval = int(request.form["interval"])
                order_response = twap.place_twap_order(symbol, side, qty, chunks, interval)

            flash("✅ Order placed successfully!", "success")
        except Exception as e:
            logging.error(f"Flask error: {e}")
            flash(f"❌ Error: {e}", "danger")

    return render_template("trade.html", order_response=order_response)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_mode()  # run in CLI mode
    else:
        app.run(debug=True)  # run in Web mode

import os
import json
import time
import math
from datetime import datetime, UTC
from uuid import uuid4
from coinbase.rest import RESTClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ORDER_HISTORY_FILE = "order_history.json"
PRODUCT_ID = "BTC-USD"
QUOTE_AMOUNT = "10"  # USD
PRICE_DISCOUNT = 0.98
TIF_HOURS = 24
FALLBACK_DAYS = 3


def load_order_history():
    if not os.path.exists(ORDER_HISTORY_FILE):
        return []
    with open(ORDER_HISTORY_FILE, "r") as f:
        return json.load(f)


def save_order_history(history):
    with open(ORDER_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def main():
    
    api_key = os.getenv("COINBASE_API_KEY")
    api_secret = os.getenv("COINBASE_API_SECRET")

    print(f"API Key: {api_key}, API Secret: {api_secret}")


    if not api_key or not api_secret:
        print("Missing credentials.")
        return

    client = RESTClient(api_key=api_key, api_secret=api_secret)
    # now = datetime.now(UTC)
    now = datetime.utcnow()
    history = load_order_history()

    # Step 1: Cancel stale unfilled limit orders
    open_orders = client.list_orders(product_id=PRODUCT_ID, order_status="OPEN")
    for order in open_orders.orders:
        created_time = datetime.fromisoformat(order.created_time.replace("Z", "+00:00"))
        age = (now - created_time).total_seconds() / 3600
        if age > TIF_HOURS:
            client.cancel_orders(order_ids=[order.order_id])
            print(f"Canceled stale order: {order.order_id}")

    # Step 2: Check fallback condition
    recent_limit_orders = [
        o for o in history
        if o["type"] == "limit" and (now - datetime.fromisoformat(o["time"])).days < FALLBACK_DAYS
    ]
    any_filled = any(o.get("filled", False) for o in recent_limit_orders)

    if not any_filled and len(recent_limit_orders) >= FALLBACK_DAYS:
        # Place market order
        try:
            result = client.market_order_buy(
                client_order_id=str(uuid4()),
                product_id=PRODUCT_ID,
                quote_size=QUOTE_AMOUNT
            )
            print("Fallback: Market buy placed.")
            history.append({"type": "market", "filled": True, "time": now.isoformat()})
        except Exception as e:
            print(f"Market buy failed: {e}")
    else:
        # Step 3: Place limit order at 2% discount
        try:
            product = client.get_product(product_id=PRODUCT_ID)
            current_price = float(product["price"])
            limit_price = str(math.floor(current_price * PRICE_DISCOUNT * 100) / 100)  # round to cents
            base_size = str(round(float(QUOTE_AMOUNT) / float(limit_price), 6))  # max precision

            result = client.limit_order_gtc_buy(
                client_order_id=str(uuid4()),
                product_id=PRODUCT_ID,
                base_size=base_size,
                limit_price=limit_price
            )
            print(f"Limit order placed at ${limit_price} for {base_size} BTC.")
            history.append({"type": "limit", "filled": False, "time": now.isoformat()})
        except Exception as e:
            print(f"Limit order failed: {e}")

    save_order_history(history)


if __name__ == "__main__":
    main()

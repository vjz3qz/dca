import os
import json
import math
import requests
from datetime import datetime, timezone
from uuid import uuid4
from coinbase.rest import RESTClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ORDER_HISTORY_FILE = "order_history.json"
PRODUCT_ID = "BTC-USD"
BASE_QUOTE_AMOUNT = 1  # USD
# PRICE_DISCOUNT = 0.98
TIF_HOURS = 24
FALLBACK_DAYS = 3

# 🪜 Laddered Limit Orders: Split adjusted_quote across tiers
TIERS = [0.998, 0.996, 0.994, 0.992, 0.985, 0.975, 0.96]  # price levels
SPLITS = [0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.10]  # corresponding USD allocations (must sum to 1.0)

def load_order_history():
    if not os.path.exists(ORDER_HISTORY_FILE):
        return []
    with open(ORDER_HISTORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Corrupt order history file — starting fresh.")
            return []

def save_order_history(history):
    tmp_file = ORDER_HISTORY_FILE + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(history, f, indent=2)
    os.replace(tmp_file, ORDER_HISTORY_FILE)

def update_order_statuses(client, history):
    """Update status for any order missing a 'filled' key."""
    for order in history:
        if "order_id" not in order or "filled" in order:
            continue
        try:
            order_info = client.get_order(order_id=order["order_id"])
            status = order_info.get("status", "").lower()
            if status:
                order["status"] = status
                order["filled"] = status == "filled"
            else:
                print(f"⚠️ No status found for order {order['order_id']}")
        except Exception as e:
            print(f"⚠️ Error checking order {order.get('order_id')}: {e}")

def fetch_fear_greed_index():
    try:
        resp = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        resp.raise_for_status()
        return int(resp.json()["data"][0]["value"])
    except Exception as e:
        print(f"Failed to fetch Fear & Greed Index: {e}")
        return 50  # Neutral default

def calculate_adjusted_quote(current_price, last_price, base_amount):
    if current_price <= 0.9 * last_price:
        smart_factor = 2.0
    elif current_price >= 1.1 * last_price:
        smart_factor = 0.5
    else:
        smart_factor = 1.0

    fgi = fetch_fear_greed_index()
    if fgi <= 20:
        fgi_factor = 1.5
    elif fgi >= 80:
        fgi_factor = 0.5
    else:
        fgi_factor = 1.0

    adjusted = round(base_amount * smart_factor * fgi_factor, 2)
    print(f"[SmartDCA] Current: {current_price}, Last: {last_price} | Smart: {smart_factor}, FGI: {fgi} → Factor: {fgi_factor} | Adjusted Quote: ${adjusted}")
    return adjusted

def get_all_orders(client, product_id, status):
    all_orders = []
    cursor = None
    while True:
        response = client.list_orders(product_id=product_id, order_status=status, cursor=cursor)
        all_orders.extend(response.orders)
        if not response.has_next:
            break
        cursor = response.cursor
    return all_orders

def safe_get_price(client, product_id):
    try:
        return float(client.get_product(product_id=product_id)["price"])
    except Exception as e:
        print(f"⚠️ Failed to fetch product price: {e}")
        return 0.0

def main():
    api_key = os.getenv("COINBASE_API_KEY")
    api_secret = os.getenv("COINBASE_API_SECRET")
    if not api_key or not api_secret:
        print("Missing credentials.")
        return

    client = RESTClient(api_key=api_key, api_secret=api_secret)
    now = datetime.now(timezone.utc)
    history = load_order_history()

    # Update status of previous orders
    update_order_statuses(client, history)

    # Step 1: Cancel stale unfilled limit orders
    open_orders = client.list_orders(product_id=PRODUCT_ID, order_status="OPEN")
    for order in open_orders.orders:
        created_time = datetime.fromisoformat(order.created_time.replace("Z", "+00:00"))
        age = (now - created_time).total_seconds() / 3600
        if age > TIF_HOURS:
            client.cancel_orders(order_ids=[order.order_id])
            print(f"Canceled stale order: {order.order_id}")

    # Step 2: Determine last filled buy price
    filled_orders = get_all_orders(client, PRODUCT_ID, "FILLED")
    buy_fills = [o for o in filled_orders if o.side == "BUY"]

    try:
        price_str = buy_fills[0].average_filled_price or buy_fills[0].price
        last_price = float(price_str)
    except (IndexError, TypeError, ValueError):
        print("⚠️ Could not determine last filled buy price. Falling back to market price.")
        last_price = safe_get_price(client, PRODUCT_ID)

    # Step 3: Get current market price and adjust quote
    current_price = safe_get_price(client, PRODUCT_ID)
    adjusted_quote = str(calculate_adjusted_quote(current_price, last_price, BASE_QUOTE_AMOUNT))

    # Step 4: Check fallback condition using only recent OPEN and FILLED limit buys
    open_orders = get_all_orders(client, PRODUCT_ID, "OPEN")
    filled_orders = get_all_orders(client, PRODUCT_ID, "FILLED")

    recent_limit_buys = []
    for order in open_orders + filled_orders:
        try:
            order_time = datetime.fromisoformat(order.created_time.replace("Z", "+00:00"))
            if (
                (now - order_time).days < FALLBACK_DAYS and
                order.side == "BUY" and
                order.order_type == "LIMIT"
            ):
                recent_limit_buys.append(order)
        except Exception as e:
            print(f"⚠️ Skipping malformed order: {e}")

    any_filled = any(o.status == "FILLED" for o in recent_limit_buys)

    if not any_filled and len(recent_limit_buys) >= FALLBACK_DAYS:
        try:
            result = client.market_order_buy(
                client_order_id=str(uuid4()),
                product_id=PRODUCT_ID,
                quote_size=adjusted_quote
            )
            if result.success:
                order_id = result.success_response["order_id"]
                print("📉 Fallback triggered: Market buy placed.")
                history.append({
                    "type": "market",
                    "filled": True,
                    "order_id": order_id,
                    "price": current_price,
                    "time": now.isoformat()
                })
        except Exception as e:
            print(f"⚠️ Market buy failed: {e}")
    else:

        for discount, fraction in zip(TIERS, SPLITS):
            try:
                tier_quote = float(adjusted_quote) * fraction
                limit_price = round(current_price * discount, 2)
                base_size = round(tier_quote / limit_price, 6)

                result = client.limit_order_gtc_buy(
                    client_order_id=str(uuid4()),
                    product_id=PRODUCT_ID,
                    base_size=str(base_size),
                    limit_price=str(limit_price)
                )

                if result.success:
                    order_id = result.success_response["order_id"]
                    print(f"✅ Laddered limit order placed: ${limit_price} for {base_size} BTC.")
                    existing_ids = {o["order_id"] for o in history}
                    if order_id not in existing_ids:
                        history.append({
                            "type": "limit",
                            "filled": False,
                            "order_id": order_id,
                            "price": current_price,
                            "limit_price": limit_price,
                            "fraction": fraction,
                            "time": now.isoformat()
                        })
                else:
                    raise RuntimeError(f"❌ Laddered order failed: {result.error_response}")
            except Exception as e:
                print(f"⚠️ Exception placing laddered order at {discount*100:.1f}%: {e}")

    save_order_history(history)

if __name__ == "__main__":
    main()

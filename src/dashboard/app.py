from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta, timezone
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("flask_secret_key", "dev-secret-key")

from dotenv import load_dotenv
load_dotenv()
import os

from execute_alpaca import AlpacaTradingClient

paper_account = 'PA3N0GG8CCZE'
ALPACA_API_KEY = os.getenv("alpaca_api_key")
ALPACA_SECRET_KEY = os.getenv("alpaca_secret_key")
ALPACA_BASE_URL = os.getenv("alpaca_base_url")
DEBUG_TEST_MODE = os.getenv("DEBUG_TEST_MODE", "false").lower() == "true"
SIMULATED_TRADING = os.getenv("SIMULATED_TRADING", "false").lower() == "true"
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Track pending orders for status updates
pending_orders = {}
simulated_holdings = None
simulated_transactions = []


def get_trading_client():
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        return None
    return AlpacaTradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)


def can_trade_now(trading_client):

    if not trading_client:
        return False
    try:
        clock = trading_client.get_clock()
        is_open = bool(getattr(clock, "is_open", False))
        next_open = getattr(clock, "next_open", None)
        next_close = getattr(clock, "next_close", None)
        print(f"Market status: is_open={is_open}, next_open={next_open}, next_close={next_close}")
        return is_open
    except Exception as e:
        print(f"Error occurred while checking trading hours: {e}")
        return False


def get_equity_value(trading_client):
    if not trading_client:
        return 0.0
    try:
        account = trading_client.get_account()
        return float(account.equity or 0)
    except Exception:
        return 0.0


def get_cash_available(trading_client):
    if not trading_client:
        return 0.0
    try:
        account = trading_client.get_account()
        return float(account.cash or 0)
    except Exception:
        return 0.0


def get_buying_power(trading_client):
    if not trading_client:
        return 0.0
    try:
        account = trading_client.get_account()
        return float(account.buying_power or 0)
    except Exception:
        return 0.0


def get_demo_holdings():
    return [
        {"symbol": "AAPL", "qty": 18, "avg_entry_price": 172.35, "market_value": 3214.00, "unrealized_pl": 124.50, "unrealized_plpc": 0.04},
        {"symbol": "MSFT", "qty": 12, "avg_entry_price": 360.70, "market_value": 4328.80, "unrealized_pl": 186.00, "unrealized_plpc": 0.04},
        {"symbol": "NVDA", "qty": 9, "avg_entry_price": 915.10, "market_value": 8240.50, "unrealized_pl": 612.30, "unrealized_plpc": 0.08},
    ]


def get_demo_watchlist():
    return [
        {"symbol": "AAPL", "name": "Apple Inc.", "asset_class": "Equity", "type": "Equity", "category": "Technology"},
        {"symbol": "MSFT", "name": "Microsoft Corp.", "asset_class": "Equity", "type": "Equity", "category": "Technology"},
        {"symbol": "NVDA", "name": "NVIDIA Corp.", "asset_class": "Equity", "type": "Equity", "category": "Semiconductors"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "asset_class": "Equity", "type": "Equity", "category": "Consumer"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "asset_class": "Equity", "type": "Equity", "category": "Communication"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "asset_class": "Equity", "type": "Equity", "category": "Communication"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "asset_class": "Equity", "type": "Equity", "category": "Automotive"},
        {"symbol": "AMD", "name": "Advanced Micro Devices", "asset_class": "Equity", "type": "Equity", "category": "Semiconductors"},
    ]


def get_simulated_holdings():
    global simulated_holdings
    if simulated_holdings is None:
        simulated_holdings = get_demo_holdings()
    return simulated_holdings


def execute_simulated_trade(symbol, qty, side):
    holdings = get_simulated_holdings()
    holding = next((item for item in holdings if item["symbol"] == symbol), None)
    price = float(holding["avg_entry_price"]) if holding else 100.0

    if side == "SELL":
        if not holding or float(holding["qty"]) < qty:
            return False, f"Not enough simulated shares of {symbol} to sell."
        holding["qty"] = float(holding["qty"]) - qty
        if holding["qty"] <= 0:
            holdings.remove(holding)
    else:
        if holding:
            holding["qty"] = float(holding["qty"]) + qty
        else:
            holdings.append({
                "symbol": symbol,
                "qty": qty,
                "avg_entry_date": datetime.now().date().isoformat(),
                "avg_entry_price": price,
                "market_value": price * qty,
                "unrealized_pl": 0,
                "unrealized_plpc": 0,
            })

    simulated_transactions.insert(0, {
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "price": price,
        "executed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Filled",
    })
    del simulated_transactions[50:]
    return True, None


def get_holdings(trading_client):
    demo_holdings = get_demo_holdings()

    if SIMULATED_TRADING:
        return get_simulated_holdings()

    if not trading_client:
        return demo_holdings

    try:
        if not can_trade_now(trading_client) and not DEBUG_TEST_MODE:
            return demo_holdings

        positions = trading_client.get_all_positions()
        if positions:
            return positions

        return positions

    except Exception:
        return demo_holdings if DEBUG_TEST_MODE else []


def get_symbol_value(item):
    if isinstance(item, dict):
        return item.get("symbol")
    return getattr(item, "symbol", None)


def normalize_holding(holding):
    if isinstance(holding, dict):
        return holding.copy()

    return {
        "symbol": getattr(holding, "symbol", None),
        "qty": getattr(holding, "qty", 0),
        "avg_entry_date": getattr(holding, "avg_entry_date", None),
        "avg_entry_price": getattr(holding, "avg_entry_price", None),
        "market_value": getattr(holding, "market_value", None),
        "unrealized_pl": getattr(holding, "unrealized_pl", None),
        "unrealized_plpc": getattr(holding, "unrealized_plpc", None),
    }


def format_transaction_time(value):
    if not value:
        return None
    if isinstance(value, datetime):
        timestamp = value
    else:
        value = str(value).replace("Z", "+00:00")
        try:
            timestamp = datetime.fromisoformat(value)
        except ValueError:
            return str(value)

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone().strftime("%Y-%m-%d %H:%M:%S")


def get_recent_transactions(trading_client, limit=50):
    if SIMULATED_TRADING:
        return simulated_transactions[:limit]
    if not trading_client:
        return []

    try:
        transactions = []
        for order in trading_client.get_recent_orders(limit=limit):
            status = str(getattr(order, "status", "unknown")).split(".")[-1].replace("_", " ").title()
            transactions.append({
                "symbol": getattr(order, "symbol", ""),
                "side": str(getattr(order, "side", "")).split(".")[-1].upper(),
                "qty": getattr(order, "filled_qty", None) if status == "Filled" else getattr(order, "qty", 0),
                "price": getattr(order, "filled_avg_price", None),
                "executed_at": format_transaction_time(
                    getattr(order, "filled_at", None) or getattr(order, "submitted_at", None)
                ),
                "status": status,
            })
        return transactions
    except Exception as e:
        print(f"Error occurred while fetching recent transactions: {e}")
        return []


def get_wash_sale_events(trading_client, lookback_days=61):
    """Build wash-sale candidates from Alpaca's filled order history."""
    if SIMULATED_TRADING or not trading_client:
        return []

    try:
        after = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        fills = trading_client.get_filled_orders(after=after, limit=500)
    except Exception as e:
        print(f"Error occurred while fetching wash sale data: {e}")
        return []

    def fill_value(fill, name, default=None):
        value = getattr(fill, name, default)
        return value if value is not None else default

    normalized = []
    for fill in fills:
        timestamp = fill_value(fill, "filled_at") or fill_value(fill, "submitted_at")
        if not timestamp:
            continue
        if not isinstance(timestamp, datetime):
            try:
                timestamp = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            except ValueError:
                continue
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        qty = float(fill_value(fill, "filled_qty", 0) or 0)
        price = float(fill_value(fill, "filled_avg_price", 0) or 0)
        if qty <= 0 or price <= 0:
            continue
        normalized.append({
            "symbol": str(fill_value(fill, "symbol", "")).upper(),
            "side": str(fill_value(fill, "side", "")).split(".")[-1].upper(),
            "qty": qty,
            "price": price,
            "timestamp": timestamp,
        })

    lots = {}
    losses = []
    for fill in sorted(normalized, key=lambda item: item["timestamp"]):
        symbol = fill["symbol"]
        symbol_lots = lots.setdefault(symbol, [])
        if fill["side"] == "BUY":
            symbol_lots.append({"qty": fill["qty"], "price": fill["price"]})
            continue
        if fill["side"] != "SELL":
            continue

        remaining = fill["qty"]
        loss = 0.0
        sold_qty = 0.0
        while remaining > 0 and symbol_lots:
            lot = symbol_lots[0]
            matched_qty = min(remaining, lot["qty"])
            realized = (fill["price"] - lot["price"]) * matched_qty
            if realized < 0:
                loss += realized
                sold_qty += matched_qty
            lot["qty"] -= matched_qty
            remaining -= matched_qty
            if lot["qty"] <= 0:
                symbol_lots.pop(0)
        if loss < 0:
            losses.append({
                "symbol": symbol,
                "sale_date": fill["timestamp"],
                "loss": loss,
                "qty": sold_qty,
            })

    events = []
    for sale in losses:
        window_start = sale["sale_date"] - timedelta(days=30)
        window_end = sale["sale_date"] + timedelta(days=30)
        replacements = [
            fill for fill in normalized
            if fill["symbol"] == sale["symbol"]
            and fill["side"] == "BUY"
            and window_start <= fill["timestamp"] <= window_end
        ]
        days_remaining = max(0, (window_end.date() - datetime.now(timezone.utc).date()).days)
        if replacements:
            status = "Wash Sale"
        elif days_remaining:
            status = "Monitoring"
        else:
            status = "Clear"
        events.append({
            "symbol": sale["symbol"],
            "sale_date": sale["sale_date"].astimezone().strftime("%Y-%m-%d"),
            "loss": sale["loss"],
            "status": status,
            "days_remaining": days_remaining,
        })
    return sorted(events, key=lambda item: item["sale_date"], reverse=True)

def get_pending_sell_orders(trading_client):
    if not trading_client:
        return []

    try:
        open_orders = trading_client.get_recent_orders(limit=50)
        pending_sells = []
        for order in open_orders:
            side = str(getattr(order, "side", "")).split(".")[-1].upper()
            status = str(getattr(order, "status", "")).split(".")[-1].lower()
            order_type = str(getattr(order, "order_type", "")).split(".")[-1].lower()
            if side != "SELL" or order_type != "market" or status in {
                "filled", "canceled", "cancelled", "rejected", "expired", "done_for_day",
            }:
                continue

            total_qty = float(getattr(order, "qty", 0) or 0)
            filled_qty = float(getattr(order, "filled_qty", 0) or 0)
            remaining_qty = max(0, total_qty - filled_qty)
            if remaining_qty:
                pending_sells.append({
                    "symbol": getattr(order, "symbol", ""),
                    "qty": remaining_qty,
                })
        return pending_sells
    except Exception as e:
        print(f"Error occurred while fetching pending sell orders: {e}")
        return []


def adjust_holdings_for_pending_orders(holdings, pending_sell_orders=None):
    pending_sell_orders = pending_sell_orders or []
    for holding in holdings:
        symbol = holding.get("symbol")
        current_qty = float(holding.get("qty") or 0)
        reserved_sell_qty = sum(
            order["qty"] for order in pending_sell_orders if order["symbol"] == symbol
        )

        if not pending_sell_orders:
            for order in pending_orders.values():
                if order["symbol"] == symbol and order["side"] == "SELL":
                    reserved_sell_qty += float(order.get("pending_qty") or order.get("qty") or 0)

        adjusted_qty = max(0, current_qty - reserved_sell_qty)
        holding["qty"] = int(adjusted_qty) if adjusted_qty.is_integer() else adjusted_qty

    return holdings


def filter_nonzero_holdings(holdings):
    return [holding for holding in holdings if float(holding.get("qty") or 0) > 0]


def get_market_watchlist(trading_client, search_query="", stock_type="", category="", limit=20):
    search_term = (search_query or "").strip().lower()
    stock_type_filter = (stock_type or "").strip().lower()
    category_filter = (category or "").strip().lower()

    if not trading_client:
        assets = get_demo_watchlist()
    else:
        try:
            assets = trading_client.get_all_assets()
            tradable_assets = []
            for asset in assets:
                if getattr(asset, "tradable", False) and getattr(asset, "status", None) == "active":
                    # asset_type = str(getattr(asset, "asset_class", "") or "").replace("_", " ").title()
                    asset_class = str(getattr(asset, "asset_class", "") or "").replace("_", " ").title()
                    asset_name = str(getattr(asset, "name", "") or "").strip()
                    if 'ETF' in asset_name:
                        asset_class = "ETF"
                    asset_category = str(getattr(asset, "exchange", "") or "").strip() or "Unknown"
                    tradable_assets.append({
                        "symbol": getattr(asset, "symbol", ""),
                        "name": asset_name,
                        "asset_class": asset_class or "Equity",
                        # "type": asset_type or "Equity",
                        "category": asset_category,
                    })
            assets = tradable_assets if tradable_assets else get_demo_watchlist()
        except Exception as e:
            print(f"Error occurred while fetching market watchlist: {e}")
            assets = get_demo_watchlist() if DEBUG_TEST_MODE else []

    filtered = []
    for asset in assets:
        symbol = str(asset.get("symbol", "")).lower()
        name = str(asset.get("name", "")).lower()
        asset_class = str(asset.get("asset_class", "")).lower()
        asset_category = str(asset.get("category", "")).lower()

        if search_term and search_term not in symbol and search_term not in name:
            continue
        if stock_type_filter and stock_type_filter not in asset_class:
            continue
        if category_filter and category_filter not in asset_category:
            continue

        filtered.append(asset)

    if limit is not None:
        return filtered[:limit]
    return filtered


@app.route("/")
def main():
    trading_client = get_trading_client()
    equity = get_equity_value(trading_client)
    buying_power = get_buying_power(trading_client)
    pending_sell_orders = get_pending_sell_orders(trading_client)
    holdings = adjust_holdings_for_pending_orders(
        [normalize_holding(holding) for holding in get_holdings(trading_client)],
        pending_sell_orders,
    )
    holdings = filter_nonzero_holdings(holdings)
    recent_transactions = get_recent_transactions(trading_client)
    recent_transactions = [{**i, 'side': i['side'].split('.')[-1]} for i in recent_transactions]
    search_query = (request.args.get("search") or "").strip()
    stock_type = (request.args.get("stock_type") or "").strip()
    category = (request.args.get("category") or "").strip()
    market_watchlist = get_market_watchlist(trading_client, search_query, stock_type, category)

    return render_template(
        "main.html",
        equity=equity,
        buying_power=buying_power,
        holdings=holdings,
        market_watchlist=market_watchlist,
        search_query=search_query,
        stock_type=stock_type,
        category=category,
        pending_orders=pending_orders,
        recent_transactions=recent_transactions,
    )


@app.route("/dashboard")
def dashboard():
    trading_client = get_trading_client()
    equity = get_equity_value(trading_client)
    return render_template(
        "dashboard.html",
        equity=equity,
        wash_sale_events=get_wash_sale_events(trading_client),
    )


@app.route("/portfolio")
def portfolio():
    trading_client = get_trading_client()
    equity = get_equity_value(trading_client)
    return render_template("portfolio.html", equity=equity)


@app.route("/assets")
def assets_page():
    trading_client = get_trading_client()
    equity = get_equity_value(trading_client)
    search_query = (request.args.get("search") or "").strip()
    stock_type = (request.args.get("stock_type") or "").strip()
    category = (request.args.get("category") or "").strip()
    page = max(1, int(request.args.get("page", 1) or 1))
    per_page = 20

    all_assets = get_market_watchlist(trading_client, search_query, stock_type, category, limit=None)
    total_pages = max(1, (len(all_assets) + per_page - 1) // per_page)
    page = min(page, total_pages)
    start_index = (page - 1) * per_page
    market_watchlist = all_assets[start_index:start_index + per_page]

    return render_template(
        "assets.html",
        equity=equity,
        market_watchlist=market_watchlist,
        search_query=search_query,
        stock_type=stock_type,
        category=category,
        page=page,
        total_pages=total_pages,
        total_assets=len(all_assets),
        pending_orders=pending_orders,
    )


@app.route("/execute_trade", methods=["POST"])
def execute_trade():
    symbol = (request.form.get("symbol") or "AAPL").upper()
    qty = int(request.form.get("qty") or 1)
    side = (request.form.get("side") or "BUY").upper()
    print(f"Executing trade: {side} {qty} shares of {symbol}")
    current_page = request.form.get("currentPage")
    trading_client = get_trading_client()
    print(f"Current page: {current_page}")
    if SIMULATED_TRADING:
        success, error = execute_simulated_trade(symbol, qty, side)
        if success:
            flash(f"Order filled: {side} {qty} {symbol} @ simulated market price", "success")
        else:
            flash(error, "danger")
        return redirect(current_page or url_for("main"))

    if trading_client is None:
        flash("No trading client available. Using demo mode.", "info")
        return redirect(current_page or url_for("main"))

    if not can_trade_now(trading_client) and not DEBUG_TEST_MODE:
        flash("Market is currently closed. Your order will be placed but won't fill until market opens.", "warning")
        return redirect(current_page)

    order = trading_client.submit_market_order(symbol, qty, side)
    if isinstance(order, tuple) and order[1] == 400:
        flash(f"Order failed: {order[0]}", "danger")
        return redirect(current_page)

    filled_qty = int(getattr(order, "filled_qty", 0) or 0)
    pending_qty = int(getattr(order, "pending_qty", 0) or 0)
    order_status = str(getattr(order, "status", "unknown")).lower()
    order_id = str(getattr(order, "id", "unknown"))
    
    # Store order for status tracking
    pending_orders[order_id] = {
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "status": order_status,
        "filled_qty": filled_qty,
        "pending_qty": pending_qty,
        "order_id": order_id,
    }
    
    # Debug logging
    print(f"Order submitted - ID: {order_id}, Status: {order_status}")
    print(f"  Filled: {filled_qty}, Pending: {pending_qty}")
    
    # Handle various Alpaca order statuses
    if "filled" in order_status and filled_qty > 0:
        flash(f"✓ Order filled: {side} {filled_qty} {symbol} @ market price", "success")
        if order_id in pending_orders:
            del pending_orders[order_id]
    elif "rejected" in order_status or "canceled" in order_status:
        flash(f"✗ Order {order_status}: {side} {qty} {symbol}", "danger")
        if order_id in pending_orders:
            del pending_orders[order_id]
    elif "pending" in order_status or pending_qty > 0:
        flash(f"⏱ Order pending: {side} {qty} {symbol}", "info")
    else:
        flash(f"Order submitted: {side} {qty} {symbol}", "info")
    
    return redirect(current_page)


@app.route("/check_order_status/<order_id>", methods=["GET"])
def check_order_status(order_id):
    """Check status of a pending order and update it"""
    import json
    
    if order_id not in pending_orders:
        return json.dumps({
            "status": "not_found",
            "completed": True,
            "display_status": "—",
            "order_id": order_id,
        }), 200
    
    trading_client = get_trading_client()
    if not trading_client:
        return json.dumps(pending_orders[order_id]), 200
    
    try:
        # Fetch latest order status from Alpaca
        order = trading_client.get_order(order_id)
        if not order:
            return json.dumps(pending_orders[order_id]), 200
            
        order_status = str(getattr(order, "status", "unknown")).lower()
        filled_qty = int(getattr(order, "filled_qty", 0) or 0)
        pending_qty = int(getattr(order, "pending_qty", 0) or 0)
        
        # Update stored order
        pending_orders[order_id].update({
            "status": order_status,
            "filled_qty": filled_qty,
            "pending_qty": pending_qty,
        })
        
        # Remove from pending if filled or rejected
        if "filled" in order_status or "rejected" in order_status or "canceled" in order_status:
            result = pending_orders[order_id].copy()
            del pending_orders[order_id]
            result["completed"] = True
            return json.dumps(result), 200
        
        # Format status for display
        if "filled" in order_status:
            result = pending_orders[order_id].copy()
            result["display_status"] = f"✓ Filled ({filled_qty})"
        elif "rejected" in order_status:
            result = pending_orders[order_id].copy()
            result["display_status"] = "✗ Rejected"
        else:
            result = pending_orders[order_id].copy()
            result["display_status"] = f"⏱ Pending ({pending_qty})"
        
        return json.dumps(result), 200
    except Exception as e:
        print(f"Error checking order status: {e}")
        return json.dumps({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
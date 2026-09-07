from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest, GetOrdersRequest
from alpaca.trading.requests import GetPortfolioHistoryRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import LimitOrderRequest

from dotenv import load_dotenv
load_dotenv()
import os

paper_account = 'PA3N0GG8CCZE'
ALPACA_API_KEY = os.getenv("alpaca_api_key")
ALPACA_SECRET_KEY = os.getenv("alpaca_secret_key")
ALPACA_BASE_URL = os.getenv("alpaca_base_url")


class AlpacaTradingClient:
    def __init__(self, api_key, secret_key, base_url, paper=True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.paper = paper
        self.client = TradingClient(self.api_key, self.secret_key, paper=self.paper)

    def get_account(self):
        return self.client.get_account()

    def get_portfolio_history(self, start=None, end=None):
        history_filter = GetPortfolioHistoryRequest(
            start=start,
            end=end,
            timeframe="1D",
        )
        return self.client.get_portfolio_history(history_filter)

    def get_clock(self):
        return self.client.get_clock()
    
    def get_all_positions(self):
        return self.client.get_all_positions()

    def get_positions(self):
        positions = self.get_all_positions()
        for p in positions:
            print("Symbol:", p.symbol)
            print("Qty:", p.qty)
            print("Market Value:", p.market_value)
            print("Avg Entry:", p.avg_entry_price)
            print("Unrealized PnL:", p.unrealized_pl)
            print("Unrealized %:", p.unrealized_plpc)
            print("-" * 30)
        return positions

    def get_all_assets(self):
        search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
        assets = self.client.get_all_assets(search_params)
        return assets

    def submit_market_order(self, symbol, qty, side="BUY"):
        order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
        market_order_data = MarketOrderRequest(
                            symbol=symbol,
                            qty=qty,
                            side=order_side,
                            time_in_force=TimeInForce.DAY,
                            )

        market_order = self.client.submit_order(order_data=market_order_data)
        return market_order
    
    def submit_limit_order(self, symbol, qty, limit_price, order_type):
        side = OrderSide.BUY if order_type.upper() == "BUY" else OrderSide.SELL
        limit_order_data = LimitOrderRequest(
                    symbol=symbol,
                    limit_price=limit_price,
                    notional=qty,
                    side=side,
                    time_in_force=TimeInForce.FOK
                   )

        # Limit order
        limit_order = self.client.submit_order(
                        order_data=limit_order_data
                    )
        return limit_order

    def get_order(self, order_id):
        """Get order status by order ID"""
        return self.client.get_order_by_id(order_id)

    def get_recent_orders(self, limit=10, after=None):
        """Get orders from Alpaca, optionally after an ISO timestamp."""
        request = GetOrdersRequest(
            status=QueryOrderStatus.ALL,
            limit=limit,
            nested=True,
            after=after,
        )
        return self.client.get_orders(filter=request)

    def get_filled_orders(self, after=None, limit=500):
        """Get filled orders used for realized P/L and wash-sale monitoring."""
        orders = self.get_recent_orders(limit=limit, after=after)
        return [
            order for order in orders
            if str(getattr(order, "status", "")).split(".")[-1].lower() == "filled"
        ]

if __name__ == "__main__":
    trading_client = AlpacaTradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    account = trading_client.get_account()
    print("Account Equity:", account.equity)

    # Get all positions
    trading_client.get_positions()

    # Get all crypto assets
    assets = trading_client.get_all_assets()
    asset = assets[0]
    print(f"Symbol: {asset.symbol}, Name: {asset.name}, Status: {asset.status}, Tradable: {asset}")
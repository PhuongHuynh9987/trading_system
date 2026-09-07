import yfinance as yf


class StockData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None

    def fetch_data(self, period="1y", interval="1d"):
        self.data = yf.download(self.ticker, period=period, interval=interval)
        self.data = self.data.dropna()
        return self.data
    
    def main(self):

        data = self.fetch_data()
        print(data)

if  __name__ == "__main__":
    stock = StockData("AAPL")
    stock.main()

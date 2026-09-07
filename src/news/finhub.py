import requests
from dotenv import load_dotenv
import os
load_dotenv()

url='https://financialmodelingprep.com/stable/search-symbol'


API_KEY = os.getenv("finhub_api_key")
symbol = "AAPL"

# url = "https://finnhub.io/api/v1/quote"
params = {"query": symbol, "apikey": API_KEY}

resp = requests.get(url, params=params)
data = resp.json()

print(data)  # contains current price, high, low, etc.
import requests
from dotenv import load_dotenv
import os
load_dotenv()

from bs4 import BeautifulSoup

API_KEY = os.getenv("alpha_advantage_api_key")

url = "https://www.alphavantage.co/query"

params = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": "AAPL",
    "apikey": API_KEY
}

response = requests.get(url, params=params)
data = response.json()

print(data)


def scrape_cnbc():
    url = "https://www.cnbc.com/quotes/AMD"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = soup.find_all('div', class_='LatestNews-container')
    news_data = []
    for item in news_items:
        title = item.find('a').text.strip()
        description = item.find('div', class_='LatestNews-summary').text.strip()
        date = item.find('time')['datetime']
        source = item.find('span', class_='LatestNews-source').text.strip()

        news_data.append({
            "title": title,
            "description": description,
            "date": date,
            "source": source
        })
    print(news_data)

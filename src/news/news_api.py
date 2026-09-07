import requests
from dotenv import load_dotenv
import os
load_dotenv()

from bs4 import BeautifulSoup

class NewsAPI:
    def __init__(self, url):
        self.api_key = os.getenv("newsapi_api_key")
        self.url = url

    def fetch_news(self, query):
        params = {
            "q": query,
            "apiKey": self.api_key,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 10
        }
        response = requests.get(self.url, params=params)
        data = response.json()
        return data["articles"]

    def scrape_news(self):

        html = requests.get(self.url, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")

        paragraphs = soup.find_all("p")
        full_text = " ".join([p.get_text() for p in paragraphs])

        return full_text

    def analyze_title_sentiment(self, title):
        positive_words = ["beat", "surge", "profit", "growth", "record high"]
        negative_words = ["fall", "drop", "loss", "crash", "miss"]

        title = title.lower()
        score = 0

        for w in positive_words:
            if w in title:
                score += 1

        for w in negative_words:
            if w in title:
                score -= 1

        print(f"Title: {title}")
        print(f"Sentiment Score: {score}")

    def sentiment_score(self, news_data):
        """
            This function takes in a list of news articles and calculates a sentiment score for each article based on the title and description. 
            Using some NLP techniques, we can assign a sentiment score to each article and then aggregate these scores to get an overall sentiment for the stock.
        """
        url = news_data[0]['url']
        title = news_data[0]['title']
        self.analyze_title_sentiment(title)
        self.scrape_news(url)

if __name__ == "__main__":
    url = "https://newsapi.org/v2/everything"

    news_api = NewsAPI(url)
    news = news_api.fetch_news()
    news_api.sentiment_score(news)
   
   
   

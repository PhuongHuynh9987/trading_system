import requests
from dotenv import load_dotenv
import os
load_dotenv()

from textblob import TextBlob


API_KEY = os.getenv("perigon_api_key")
print(f"Perigon API Key: {API_KEY}")

url = 'https://api.perigon.io/v1/articles/all'
headers = {
    'Authorization': f'Bearer {API_KEY}'
}           

response = requests.get(url, headers=headers, params={'query': 'AAPL'})
data = response.json()
print(data)


def sentiment_score_news(news_data):
    for article in news_data:
        title = article["title"]
        description = article["description"]

        title_sentiment = TextBlob(title).sentiment.polarity
        description_sentiment = TextBlob(description).sentiment.polarity

        overall_sentiment = (title_sentiment + description_sentiment) / 2

        print(f"Title: {title}")
        print(f"Description: {description}")
        print(f"Sentiment Score: {overall_sentiment}")
        print("-" * 50)



def sentiment_score(text):
    positive_words = ["beat", "surge", "profit", "growth", "record high"]
    negative_words = ["fall", "drop", "loss", "crash", "miss"]

    text = text.lower()
    score = 0

    for w in positive_words:
        if w in text:
            score += 1

    for w in negative_words:
        if w in text:
            score -= 1

    return score

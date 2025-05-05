import requests
import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime

# Load .env variables
load_dotenv()

# News API and MongoDB config from the environment
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Function to get financial news from NewsAPI
def get_financial_news():
    url = f'https://newsapi.org/v2/everything?q=financial&apiKey={NEWS_API_KEY}&language=en'
    response = requests.get(url)
    
    if response.status_code == 200:
        news_data = response.json()
        return news_data['articles']
    else:
        print(f"Error fetching data from NewsAPI: {response.status_code}")
        return []

# Function to connect to MongoDB
def connect_to_mongo():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    return collection

# Function to store news in MongoDB
def store_news_in_mongo(news_articles):
    collection = connect_to_mongo()

    for article in news_articles:
        article_data = {
            "title": article["title"],
            "description": article["description"],
            "content": article["content"],
            "publishedAt": article["publishedAt"],
            "url": article["url"],
            "source": article["source"]["name"],
            "retrievedAt": datetime.now()
        }

        # Insert the news article into the MongoDB collection
        collection.insert_one(article_data)

# Function to collect financial data and store in MongoDB
def collect_financial_data():
    print("Fetching financial news...")
    news_articles = get_financial_news()

    if news_articles:
        print(f"Found {len(news_articles)} articles. Storing in MongoDB...")
        store_news_in_mongo(news_articles)
        print("News articles stored in MongoDB.")
    else:
        print("No news articles found.")

# Run the data collection process
if __name__ == "__main__":
    collect_financial_data()

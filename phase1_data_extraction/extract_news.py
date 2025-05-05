# extract_news.py

import logging
from datetime import datetime, timedelta, timezone
from newsapi import NewsApiClient
import config
import database  # this is your own database.py module

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_financial_news(query: str, collection_name: str):
    newsapi = NewsApiClient(api_key=config.NEWS_API_KEY)

    end_date = datetime.now(timezone.utc) - timedelta(hours=config.DEFAULT_DELAY_HOURS)
    start_date = end_date - timedelta(days=3)

    from_date = start_date.date().isoformat()
    to_date = end_date.date().isoformat()

    logger.info(f"Fetching articles from {from_date} to {to_date} for query: {query}")

    response = newsapi.get_everything(
        q=query,
        language='en',
        sort_by='publishedAt',
        page_size=100,
        from_param=from_date,
        to=to_date
    )

    articles = response.get("articles", [])
    logger.info(f"Fetched {len(articles)} articles")

    inserted_count = database.insert_articles(collection_name, articles)
    logger.info(f"Inserted {inserted_count} new articles into collection: {collection_name}")

if __name__ == "__main__":
    collect_financial_news("finance OR economy OR stock market", "financial_news")

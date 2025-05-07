# extract_news.py

import logging
from datetime import datetime, timedelta, timezone
from newsapi import NewsApiClient
import config
import database
from urllib.parse import urlparse, urlunparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define stricter financial sources
FINANCIAL_SOURCES = [
    'bloomberg.com', 'cnbc.com', 'financialpost.com',
    'reuters.com', 'marketwatch.com', 'wsj.com', 'ft.com'
]

# Clean URL for deduplication
def normalize_url(url):
    try:
        parsed = urlparse(url)
        clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
        return clean_url
    except:
        return url

# Filter for financial sources only
def is_financial_source(url):
    return any(domain in url for domain in FINANCIAL_SOURCES)

def process_articles(raw_articles):
    cleaned = []
    for a in raw_articles:
        url = normalize_url(a.get("url", ""))
        if not url or not is_financial_source(url):
            continue

        cleaned.append({
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "content": a.get("content", ""),
            "publishedAt": a.get("publishedAt", ""),
            "source": a.get("source", {}).get("name", ""),
            "url": url,
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
            "sentiment": None  # Placeholder for future sentiment analysis
        })
    return cleaned

def collect_financial_news(query: str, collection_name: str):
    newsapi = NewsApiClient(api_key=config.NEWS_API_KEY)

    end_date = datetime.now(timezone.utc) - timedelta(hours=config.DEFAULT_DELAY_HOURS)
    start_date = end_date - timedelta(days=3)

    from_date = start_date.date().isoformat()
    to_date = end_date.date().isoformat()

    logger.info(f"Fetching financial news from {from_date} to {to_date} for query: {query}")

    try:
        response = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='publishedAt',
            page_size=100,
            from_param=from_date,
            to=to_date
        )
        raw_articles = response.get("articles", [])
        logger.info(f"Fetched {len(raw_articles)} raw articles")
        
        filtered_articles = process_articles(raw_articles)
        logger.info(f"Filtered to {len(filtered_articles)} financial articles")

        inserted_count = database.insert_articles(collection_name, filtered_articles)
        logger.info(f"Inserted {inserted_count} new articles into collection: {collection_name}")

    except Exception as e:
        logger.error(f"Failed to fetch or insert articles: {e}")

if __name__ == "__main__":
    collect_financial_news("finance OR economy OR stock market OR S&P 500", "financial_news")

#Extract_news
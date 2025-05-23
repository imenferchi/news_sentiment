# extract_news.py

import logging
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, urlunparse

from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException

import config
import database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Your whitelist of domains for filtering ───────────────────────────────────
FINANCIAL_SOURCES = {
    'bloomberg.com', 'cnbc.com', 'financialpost.com',
    'reuters.com', 'marketwatch.com', 'wsj.com', 'ft.com',
    'forbes.com', 'investopedia.com'
}

# ─── Corresponding NewsAPI source-IDs for top-headlines ───────────────────────
FINANCIAL_SOURCE_IDS = [
    'bloomberg', 'cnbc', 'financial-post',
    'reuters', 'marketwatch', 'the-wall-street-journal', 'financial-times',
    'forbes', 'investopedia'
]

# ─── Macro-focused queries for S&P 500–related news ─────────────────────────
MACRO_QUERIES = [
    "S&P 500 OR SPX AND (Federal Reserve OR Fed OR interest rate)",
    "S&P 500 OR SPX AND (inflation OR CPI OR PPI)",
    "S&P 500 OR SPX AND (GDP OR economic growth)",
    "S&P 500 OR SPX AND (unemployment OR unemployment rate)",
    "S&P 500 OR SPX AND (volatility OR VIX OR market volatility)",
    "S&P 500 OR SPX AND (earnings OR earnings season)",
    "S&P 500 OR SPX AND (merger OR acquisition OR M&A)"
]

# Keywords for basic macro relevance check
MACRO_KEYWORDS = [
    's&p 500', 'spx', 'fed', 'federal reserve', 'interest rate',
    'inflation', 'cpi', 'ppi', 'gdp', 'economic growth',
    'unemployment', 'vix', 'volatility', 'earnings',
    'merger', 'acquisition'
]


def normalize_url(url: str) -> str:
    """Strip query params and fragments for dedupe."""
    try:
        p = urlparse(url)
        return urlunparse((p.scheme, p.netloc, p.path, '', '', ''))
    except:
        return url


def is_financial_source(url: str) -> bool:
    """Check that the domain is in our whitelist."""
    netloc = urlparse(url).netloc.lower()
    return any(domain in netloc for domain in FINANCIAL_SOURCES)


def article_matches_macro(text: str) -> bool:
    """Ensure the article mentions at least one macro keyword."""
    lower = text.lower()
    return any(kw in lower for kw in MACRO_KEYWORDS)


def process_articles(raw: list) -> list:
    """Filter, normalize, and shape raw NewsAPI articles."""
    out = []
    now = datetime.now(timezone.utc).isoformat()
    for a in raw:
        title = a.get("title", "") or ""
        desc = a.get("description", "") or ""
        # Light macro check
        if not article_matches_macro(title + " " + desc):
            continue
        url = normalize_url(a.get("url", "") or "")
        if not url or not is_financial_source(url):
            continue
        out.append({
            "title":       title,
            "description": desc,
            "content":     a.get("content", "") or "",
            "publishedAt": a.get("publishedAt", "") or "",
            "source":      a.get("source", {}).get("name", ""),
            "url":         url,
            "fetchedAt":   now,
            "sentiment":   None
        })
    return out


def collect_financial_news(query: str, collection_name: str):
    """
    Fetch and insert S&P 500–related macroeconomic news.
    Only new URLs are added; existing documents remain intact.
    """
    newsapi = NewsApiClient(api_key=config.NEWS_API_KEY)

    # Enforce free-plan delay & lookback
    delay_h = max(config.DEFAULT_DELAY_HOURS, 24)
    end_dt  = datetime.now(timezone.utc) - timedelta(hours=delay_h)
    lookback = getattr(config, "LOOKBACK_DAYS", 30)
    start_dt = end_dt - timedelta(days=lookback)

    from_date = start_dt.date().isoformat()
    to_date   = end_dt.date().isoformat()
    logger.info(f"Fetching '{query}' from {from_date} to {to_date} (delay={delay_h}h)…")

    raw_articles = []
    seen_urls   = set(
        doc["url"] for doc in database.db[collection_name].find({}, {"url":1})
    )

    # 1) Paginate /everything
    page_size = 100
    page      = 1
    max_pages = getattr(config, "MAX_PAGES", 30)

    while True:
        try:
            resp = newsapi.get_everything(
                q=query,
                from_param=from_date,
                to=to_date,
                language='en',
                sort_by='publishedAt',
                page=page,
                page_size=page_size
            )
        except NewsAPIException as err:
            info = err.args[0]
            if info.get("code") == "parameterInvalid":
                m = re.search(r"as far back as (\d{4}-\d{2}-\d{2})", info.get("message",""))
                if m:
                    allowed = m.group(1)
                    new_start = datetime.fromisoformat(allowed) + timedelta(days=1)
                    from_date = new_start.date().isoformat()
                    logger.warning(f"Too-far-back: shifting from_date → {from_date} and retrying page {page}")
                    continue
            raise

        batch = resp.get("articles", [])
        if not batch:
            break

        for art in batch:
            url = normalize_url(art.get("url", "") or "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                raw_articles.append(art)

        logger.info(f"  /everything page {page}: fetched {len(batch)} articles, unique so far={len(raw_articles)}")
        if len(batch) < page_size or page >= max_pages:
            break
        page += 1

    # 2) Fetch top-headlines matching macro query
    sources_param = ",".join(FINANCIAL_SOURCE_IDS)
    page = 1
    while True:
        top = newsapi.get_top_headlines(
            q=query,
            sources=sources_param,
            language='en',
            page=page,
            page_size=page_size
        ).get("articles", [])
        if not top:
            break

        for art in top:
            url = normalize_url(art.get("url", "") or "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                raw_articles.append(art)

        logger.info(f"  top-headlines page {page}: +{len(top)} articles (unique total={len(raw_articles)})")
        if len(top) < page_size:
            break
        page += 1

    logger.info(f"Total new unique raw articles: {len(raw_articles)}")

    # 3) Filter & insert only new ones
    filtered = process_articles(raw_articles)
    logger.info(f"After filtering to financial & macro relevance: {len(filtered)} articles")

    inserted = database.insert_articles(collection_name, filtered)
    logger.info(f"Inserted {inserted} new docs into '{collection_name}'")

if __name__ == "__main__":
    for q in MACRO_QUERIES:
        logger.info(f"\n===== Running macro query: {q} =====")
        collect_financial_news(q, "financial_news")
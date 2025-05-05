from pymongo import MongoClient
import certifi  
import config

client = MongoClient(config.MONGODB_URI, tlsCAFile=certifi.where())  # ← use certifi bundle
db = client[config.MONGO_DB_NAME]

def insert_articles(collection_name, articles):
    if not articles:
        return 0

    collection = db[collection_name]

    # Get URLs already in the DB to prevent duplicates
    try:
        existing_urls = set(doc["url"] for doc in collection.find({}, {"url": 1}) if "url" in doc)
    except Exception as e:
        print(f"Failed to fetch existing URLs: {e}")
        return 0

    new_articles = []
    for article in articles:
        url = article.get("url")
        if url and url not in existing_urls:
            new_articles.append(article)

    if new_articles:
        try:
            collection.insert_many(new_articles)
        except Exception as e:
            print(f"Failed to insert articles: {e}")
            return 0

    return len(new_articles)

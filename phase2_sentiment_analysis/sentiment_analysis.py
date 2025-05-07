import sys
import os
import logging
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.nn.functional import softmax
from datetime import datetime, timezone

# --- Fix the import path so Python can find database.py ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phase1_data_extraction')))

import database  

# --- Logging setup ---
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

# --- Load FinBERT model and tokenizer ---
MODEL_NAME = "yiyanghkust/finbert-tone"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(MODEL_NAME)

# --- Analyze sentiment from given text ---
def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = softmax(outputs.logits, dim=1).squeeze()
    labels = ["positive", "negative", "neutral"]
    sentiment = labels[torch.argmax(probs).item()]
    return sentiment

# --- Analyze and update all articles missing sentiment ---
def analyze_and_update_articles(collection_name):
    collection = database.db[collection_name]
    articles = collection.find({"sentiment": None})

    for article in articles:
        _id = article["_id"]
        content = article.get("content") or article.get("description") or article.get("title")
        if not content:
            continue

        try:
            sentiment = analyze_sentiment(content)
            collection.update_one(
                {"_id": _id},
                {
                    "$set": {
                        "sentiment": sentiment,
                        "sentimentAnalyzedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            logger.info(f"Updated article {_id} with sentiment: {sentiment}")
        except Exception as e:
            logger.error(f"Failed to analyze sentiment for article {_id}: {e}")

# --- Entry point ---
if __name__ == "__main__":
    analyze_and_update_articles("financial_news")

#Sentiment 
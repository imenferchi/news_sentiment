import sys
import os
from datetime import datetime
from collections import defaultdict
from statistics import mean

# Add phase1_data_extraction to path for importing database module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phase1_data_extraction')))
import database  # Your MongoDB setup from phase1

db = database.db

# Mapping of sentiment labels to numerical values
SENTIMENT_SCORES = {
    "positive": 1,
    "neutral": 0,
    "negative": -1
}

def summarize_sentiment(input_collection="financial_news", output_collection="daily_sentiment_summary"):
    # Fetch only articles with analyzed sentiment
    articles = db[input_collection].find({
        "sentiment": {"$in": list(SENTIMENT_SCORES.keys())}
    })

    grouped = defaultdict(list)

    # Group scores by date
    for article in articles:
        published_at = article.get("publishedAt")
        sentiment = article.get("sentiment")

        if not published_at or sentiment not in SENTIMENT_SCORES:
            continue

        try:
            date = published_at.split("T")[0]  # Extract "YYYY-MM-DD"
            score = SENTIMENT_SCORES[sentiment]
            grouped[date].append(score)
        except Exception as e:
            print(f"Skipping article due to error: {e}")

    if not grouped:
        print("No valid sentiment data found.")
        return

    # Save daily summaries to MongoDB
    output = db[output_collection]
    for date, scores in grouped.items():
        avg_score = mean(scores)
        output.update_one(
            {"date": date},
            {"$set": {
                "date": date,
                "average_score": avg_score,
                "count": len(scores),
                "computedAt": datetime.utcnow().isoformat()
            }},
            upsert=True
        )

    print(f"Saved sentiment summaries for {len(grouped)} days to '{output_collection}'.")

if __name__ == "__main__":
    summarize_sentiment()
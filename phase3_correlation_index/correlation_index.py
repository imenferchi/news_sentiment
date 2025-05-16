# phase3_correlation_index/correlation_index.py

import sys
import os
from datetime import datetime, timezone
from collections import defaultdict

# --- Fix the import path so Python can find database.py ---
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'phase1_data_extraction')
    )
)
import database  

# alias the db handle you already configured there
db = database.db


def _date_from_iso(iso_ts: str) -> str:
    """
    Extract just the YYYY-MM-DD portion of an ISO8601 timestamp.
    e.g. "2025-05-04T14:30:10Z" → "2025-05-04"
    """
    return iso_ts.split("T", 1)[0]


def _classify_overall(avg_score: float) -> str:
    """
    Classify average score into overall sentiment:
      - avg >= 0: Overall Positive
      - avg <  0: Overall Negative
    """
    return "overall_positive" if avg_score >= 0 else "overall_negative"


def compute_correlation_index(
    source_collection: str = "daily_sentiment_summary",
    output_collection: str = "correlation_index"
):
    """
    Reads daily summaries, computes correlation index placeholder,
    classifies overall sentiment, and upserts results.
    """
    src = db[source_collection]
    out = db[output_collection]

    # Load all summaries with date & average_score
    daily_docs = list(src.find({}, {"date": 1, "average_score": 1}))
    if not daily_docs:
        print("No daily summaries found in the source collection.")
        return

    # Build a map: { "2025-05-04": 0.3333, ... }
    scores_by_date = {
        doc["date"]: doc["average_score"]
        for doc in daily_docs
        if "average_score" in doc
    }

    # Upsert each day's correlation and overall sentiment
    for day, avg in sorted(scores_by_date.items()):
        overall = _classify_overall(avg)
        out.update_one(
            {"date": day},
            {"$set": {
                "date": day,
                "correlation_with_market": avg,       # placeholder
                "overall_sentiment": overall,
                "computedAt": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )

    print(f"Correlation index computed for {len(scores_by_date)} days.")


if __name__ == "__main__":
    compute_correlation_index()
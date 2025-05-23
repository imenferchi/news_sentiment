#!/usr/bin/env python3
import os
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

# ─── Load ENV vars from phase1_data_extraction/.env ───────────────────────────
root     = Path(__file__).parent.parent
env_path = root / "phase1_data_extraction" / ".env"
if not env_path.exists():
    raise FileNotFoundError(f"Could not find .env at {env_path}")
load_dotenv(env_path)

# ─── Read Mongo connection info ────────────────────────────────────────────────
MONGODB_URI   = os.getenv("MONGODB_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "fear_index_db")
if not MONGODB_URI:
    raise RuntimeError("Please set MONGODB_URI in your .env")

# ─── Connect to MongoDB Atlas ──────────────────────────────────────────────────
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db     = client[MONGO_DB_NAME]


def compute_return_sentiment_match(
    corr_coll_name: str = "correlation_index",
    ret_coll_name:  str = "sp500_daily_returns",
    out_coll_name:  str = "return_sentiment_match"
):
    """
    For each date in `corr_coll_name`, fetch overall_sentiment and
    match it against the S&P 500 daily return in `ret_coll_name`.
    Writes 1 for agreement (positive/positive or negative/negative),
    0 for disagreement. Skips dates with zero return or missing data.
    Finally, computes and prints the percentage of matches.
    """
    corr_coll = db[corr_coll_name]
    ret_coll  = db[ret_coll_name]
    out_coll  = db[out_coll_name]

    hits = 0
    total = 0
    skipped = 0

    cursor = corr_coll.find({}, {"date": 1, "overall_sentiment": 1})
    for doc in cursor:
        date = doc.get("date")
        overall = doc.get("overall_sentiment")
        if not date or overall not in ("overall_positive", "overall_negative"):
            skipped += 1
            continue

        ret_doc = ret_coll.find_one({"Date": date}, {"Return": 1})
        if not ret_doc or "Return" not in ret_doc:
            skipped += 1
            continue

        ret_val = ret_doc["Return"]
        if ret_val is None or ret_val == 0:
            skipped += 1
            continue

        # Determine labels
        ret_label  = "positive" if ret_val > 0 else "negative"
        sent_label = "positive" if overall == "overall_positive" else "negative"

        # Compare
        match = 1 if ret_label == sent_label else 0

        # Upsert result
        out_coll.update_one(
            {"date": date},
            {"$set": {
                "date":              date,
                "overall_sentiment": overall,
                "return":            ret_val,
                "match":             match,
                "computedAt":        datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )

        total += 1
        hits += match

    # Compute percentage
    percent = (hits / total * 100) if total > 0 else 0

    print(f"Processed {total + skipped} dates ({total} evaluated, {skipped} skipped).")
    print(
        f"According to our program, {percent:.2f}% of times the overall sentiment "
        f"analysis has matched the daily return of the S&P500"
    )


if __name__ == "__main__":
    compute_return_sentiment_match()

"""sentiment_analysis.py

Enriches previously stored financial news with sentiment labels using FinBERT
(ProsusAI/finbert) served through the Hugging Face Inference API.

The script reads the first *batch_size* articles in <collection_name> that
have ``sentiment == None``, submits each article’s full text to FinBERT, and
stores:
    * sentiment:   "positive" | "negative" | "neutral"
    * sentimentScores: the raw probability distribution returned by FinBERT
    * sentimentAnalyzedAt: UTC ISO‑timestamp of the analysis

Required additions to your project:
--------------------------------------------------------------------------
* ``config.HF_API_KEY`` – the personal access token for Hugging Face with
  "Inference Endpoints" permission (set it or export the env‑var
  ``HUGGINGFACE_API_KEY``).
* ``database.fetch_articles_without_sentiment`` – fetch docs where
  ``sentiment`` is *null*.
* ``database.update_article_sentiments`` – bulk‑update by ``_id``.

Run it daily after ``extract_news.py`` either manually or via a scheduler
(Cron, Airflow, Prefect…).
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Dict, List, Tuple

import requests
import config
import database

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# FinBERT via Hugging Face Inference API
# ---------------------------------------------------------------------------
HF_API_URL: str = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
HF_API_KEY: str | None = os.getenv("HUGGINGFACE_API_KEY", getattr(config, "HF_API_KEY", None))

if HF_API_KEY is None:
    raise RuntimeError(
        "No Hugging Face API key found – set HUGGINGFACE_API_KEY or config.HF_API_KEY"
    )

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}
TIMEOUT = 30  # seconds per request


def analyze_sentiment(text: str, top_k: int | None = 3) -> Tuple[str, Dict[str, float]]:
    """Return (dominant_sentiment, probability_dict).

    The FinBERT model emits *positive*, *negative*, *neutral* with scores that
    sum to ~1.  We map them directly; if the user only needs positive/negative,
    treat neutral as whichever non‑neutral score is higher or leave as neutral
    – adjust as needed.
    """

    payload: Dict = {"inputs": text}
    if top_k is not None:
        payload["parameters"] = {"top_k": top_k}

    try:
        resp = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("FinBERT request failed: %s", exc)
        raise

    predictions: List[Dict[str, float]] = resp.json()
    label_scores = {p["label"].lower(): p["score"] for p in predictions}

    positive = label_scores.get("positive", 0.0)
    negative = label_scores.get("negative", 0.0)
    neutral = label_scores.get("neutral", 0.0)

    # Reduce to three‑way – adjust logic to drop neutral if desired
    if neutral >= max(positive, negative):
        dominant = "neutral"
    else:
        dominant = "positive" if positive >= negative else "negative"

    return dominant, label_scores


def update_article_sentiments(collection_name: str, batch_size: int = 50) -> None:
    """Update the next *batch_size* articles lacking sentiment labels."""

    pending = database.fetch_articles_without_sentiment(collection_name, limit=batch_size)
    if not pending:
        logger.info("No pending articles in collection '%s'", collection_name)
        return

    updates: List[Dict] = []
    for art in pending:
        # Concatenate available text fields
        text_parts = [art.get("title", ""), art.get("description", ""), art.get("content", "")]
        full_text = "\n".join([p for p in text_parts if p])

        try:
            sentiment, scores = analyze_sentiment(full_text)
        except Exception:
            continue  # skip failed article but keep processing others

        updates.append(
            {
                "_id": art["_id"],
                "sentiment": sentiment,
                "sentimentScores": scores,
                "sentimentAnalyzedAt": datetime.utcnow().isoformat(),
            }
        )

    if updates:
        modified = database.update_article_sentiments(collection_name, updates)
        logger.info("Updated %s articles with sentiment labels.", modified)


if __name__ == "__main__":
    update_article_sentiments("financial_news")

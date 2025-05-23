#!/usr/bin/env python3
import os
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import quote_plus

import yfinance as yf
import pandas as pd
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

# ─── 0) Load ENV vars from your phase1_data_extraction/.env ────────────────────
# Assumes this script sits in phase3_correlation_index or similar
root = Path(__file__).parent.parent
env_path = root / "phase1_data_extraction" / ".env"
if not env_path.exists():
    raise FileNotFoundError(f"No .env found at {env_path}")
load_dotenv(env_path)

# Now these come from .env:
#   MONGODB_URI=mongodb+srv://… 
#   MONGO_DB_NAME=fear_index_db
#   (and NEWS_API_KEY if you care)
MONGODB_URI   = os.getenv("MONGODB_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "fear_index_db")
if not MONGODB_URI:
    raise RuntimeError("Please set MONGODB_URI in your .env")

# ─── 1) Compute date range ─────────────────────────────────────────────────────
end_date   = datetime.today()
start_date = end_date - timedelta(days=365)

# ─── 2) Download S&P 500 data ──────────────────────────────────────────────────
ticker = "^GSPC"
raw = yf.download(
    ticker,
    start=start_date.strftime("%Y-%m-%d"),
    end=end_date.strftime("%Y-%m-%d"),
    progress=False,
    auto_adjust=False
)

# ─── 3) Compute daily returns ─────────────────────────────────────────────────
df = raw[["Close"]].copy()
df["Return"] = df["Close"].pct_change()
df = df.reset_index()

# ─── 4) Flatten MultiIndex columns if needed ─────────────────────────────────
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [
        col[0] if col[1] in ("", None, ticker) else col[1]
        for col in df.columns
    ]

# ─── 5) Format Date & prepare records ─────────────────────────────────────────
df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
records = df.to_dict("records")

# ─── 6) Connect to MongoDB Atlas ──────────────────────────────────────────────
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db     = client[MONGO_DB_NAME]
coll   = db["sp500_daily_returns"]

# ─── 7) Clear & Insert ───────────────────────────────────────────────────────
coll.delete_many({})
res = coll.insert_many(records)
print(f"Inserted {len(res.inserted_ids)} docs into '{MONGO_DB_NAME}.sp500_daily_returns'")

# config.py

import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
DEFAULT_DELAY_HOURS = int(os.getenv("DEFAULT_DELAY_HOURS", "12"))

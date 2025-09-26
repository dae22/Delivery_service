import os

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
REDIS_URL = os.getenv("REDIS_URL")
DB_URL_SYNC = os.getenv("DB_URL_SYNC")

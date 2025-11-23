import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # === Flask settings ===
    DEBUG = os.getenv("DEBUG", "False") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY")

    # === Database settings ===
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT"))
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")

    # === Other project settings ===

    if not all([SECRET_KEY, DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME]):
        raise ValueError(f"Missing necessary environment variables in {__file__}")

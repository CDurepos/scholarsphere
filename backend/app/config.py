import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).resolve().parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    # === Flask static settings ===
    STRICT_SLASHES = False

    # === Flask env variable settings ===
    DEBUG = os.getenv("DEBUG", "False") == "True"

    # === Database env variable settings ===
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT"))
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")

    # === JWT Settings ===
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production") #TODO
    JWT_ACCESS_TOKEN_EXPIRATION_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRATION_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRATION_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRATION_DAYS", "7"))

    # === Other project settings ===
    LLAMA_ACCESS_TOKEN = os.getenv("LLAMA_ACCESS_TOKEN")

    # === Validation ===
    if not all([DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME, LLAMA_ACCESS_TOKEN]):
        raise ValueError(f"Missing necessary environment variables in {__file__}")

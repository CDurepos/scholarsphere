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

    # === Other project settings ===

    # === Validation ===
    if not all([DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME]):
        raise ValueError(f"Missing necessary environment variables in {__file__}")

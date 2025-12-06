import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


class ScrapeConfig:
    # === Database configuration ===
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASS", ""),
        "database": os.getenv("DB_NAME", "scholarsphere"),
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
        "autocommit": False,
    }

    # === Other project settings ===
    LLAMA_ACCESS_TOKEN = os.getenv("LLAMA_ACCESS_TOKEN")

    # === Validation ===
    if not all([DB_CONFIG["host"], DB_CONFIG["port"], DB_CONFIG["user"], DB_CONFIG["password"], DB_CONFIG["database"]]):
        raise ValueError(f"Missing necessary environment variables in {__file__}")
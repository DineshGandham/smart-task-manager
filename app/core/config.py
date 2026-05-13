# -----------------------------------------------------------
# CONFIGURATION MODULE (core/config.py)
# -----------------------------------------------------------
# Purpose:
# Centralized configuration management for the application.
# Loads environment variables from `.env` file using Pydantic
# and provides a cached Settings object across the app.
# -----------------------------------------------------------


from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Settings class:
    - Reads values from environment variables or `.env` file
    - Provides default values if not defined
    - Ensures type safety and validation
    """

    APP_ENV : str = "development"
    APP_NAME : str = "Smart Task Manager"
    APP_VERSION : str = "0.1.0"
    DATA_FILE_PATH : str = "data/db.json"

    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/smarttaskdb"
    
    CORS_ORIGINS : list[str] = ["*"]
    GEMINI_API_KEY : str = ""
    OPENAI_API_KEY : str = ""

    # -------------------------------------------------------
    # Pydantic Settings Configuration
    # -------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file= ".env",  # Load variables from `.env` file
        env_file_encoding= "utf-8",
        extra= "ignore"
    )

# -----------------------------------------------------------
# SETTINGS INSTANCE (CACHED)
# -----------------------------------------------------------
# This function ensures:
# - Settings object is created only once (singleton behavior)
# - Avoids re-reading `.env` multiple times
# - Improves performance
# -----------------------------------------------------------

@lru_cache
def get_settings() -> Settings:
    return Settings()
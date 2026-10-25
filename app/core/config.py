"""Application configuration and environment settings."""

import re
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """UrbanLens application settings."""

    # Project
    PROJECT_NAME: str = "UrbanLens API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # MongoDB Atlas
    MONGODB_URI: str = ""
    MONGODB_DB: str = "urbanlens"
    MONGODB_CONNECT_TIMEOUT_MS: int = 4000
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 4000
    MONGODB_SOCKET_TIMEOUT_MS: int = 6000
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_MIN_POOL_SIZE: int = 5

    # Pagination limits
    DEFAULT_PAGE: int = 1
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def safe_mongodb_uri(self) -> str:
        """Return MongoDB URI with password redacted for logging and safe inspection."""
        if not self.MONGODB_URI:
            return ""
        # Redact password in mongodb:// or mongodb+srv://
        return re.sub(r":([^@]+)@", ":***@", self.MONGODB_URI)


settings = Settings()

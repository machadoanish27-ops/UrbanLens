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

    # Live Intelligence Providers
    PROVIDER_TIMEOUT_SECONDS: float = 8.0
    OPENAQ_API_KEY: str | None = None
    OPENAQ_BASE_URL: str = "https://api.openaq.org/v3"
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    FRANKFURTER_BASE_URL: str = "https://api.frankfurter.dev/v1"
    EXCHANGERATE_API_BASE_URL: str = "https://open.er-api.com/v6"
    NOMINATIM_BASE_URL: str = "https://nominatim.openstreetmap.org"
    NOMINATIM_USER_AGENT: str = "UrbanLens/0.1.0 (urbanlens@urbanlens.local)"
    OSRM_BASE_URL: str = "http://router.project-osrm.org"
    OVERPASS_BASE_URL: str = "https://overpass-api.de/api/interpreter"
    OVERPASS_FALLBACK_URLS: list[str] = [
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
    ]
    OVERPASS_MAX_RETRIES: int = 2
    OVERPASS_COOLDOWN_SECONDS: float = 60.0
    GTFS_FEEDS: dict[str, str] = {}

    # Distributed Cache Layer (Redis + In-Memory Fallback)
    REDIS_URL: str | None = None
    REDIS_ENABLED: bool = False
    REDIS_CONNECT_TIMEOUT_MS: int = 1500
    REDIS_SOCKET_TIMEOUT_MS: int = 1500
    CACHE_DEFAULT_TTL_SECONDS: float = 300.0
    CACHE_STALE_TTL_MULTIPLIER: float = 4.0

    # RAG Knowledge Layer
    EMBEDDING_PROVIDER: str = "hash"
    EMBEDDING_DIMENSION: int = 128
    KNOWLEDGE_CHUNK_SIZE: int = 600
    KNOWLEDGE_CHUNK_OVERLAP: int = 100
    KNOWLEDGE_DEFAULT_TOP_K: int = 5

    # Groq LLM Intelligence Layer
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "openai/gpt-oss-120b"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT_SECONDS: float = 30.0
    GROQ_API_KEY: str | None = None
    LLM_CACHE_TTL_SECONDS: float = 300.0

    # Secondary LLM Provider (Failover Redundancy)
    SECONDARY_LLM_ENABLED: bool = False
    SECONDARY_LLM_PROVIDER: str = "secondary"
    SECONDARY_LLM_BASE_URL: str = "https://api.openai.com/v1"
    SECONDARY_LLM_API_KEY: str | None = None
    SECONDARY_LLM_MODEL: str = "gpt-4o-mini"
    SECONDARY_LLM_TIMEOUT_SECONDS: float = 25.0

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_INTELLIGENCE: str = "15/minute"
    RATE_LIMIT_LIVE_PROVIDERS: str = "30/minute"

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

    # Lowercase property accessors for LLM settings
    @property
    def groq_api_key(self) -> str | None:
        return self.GROQ_API_KEY

    @property
    def llm_provider(self) -> str:
        return self.LLM_PROVIDER

    @property
    def llm_model(self) -> str:
        return self.LLM_MODEL

    @property
    def llm_temperature(self) -> float:
        return self.LLM_TEMPERATURE

    @property
    def llm_max_tokens(self) -> int:
        return self.LLM_MAX_TOKENS

    @property
    def llm_timeout_seconds(self) -> float:
        return self.LLM_TIMEOUT_SECONDS

    @property
    def llm_cache_ttl_seconds(self) -> float:
        return self.LLM_CACHE_TTL_SECONDS

    @property
    def safe_groq_api_key(self) -> str:
        """Return redacted representation of Groq API key for logging."""
        if not self.GROQ_API_KEY:
            return "not_configured"
        key = self.GROQ_API_KEY.strip()
        if len(key) <= 8:
            return "***"
        return f"{key[:4]}...{key[-4:]}"

    @property
    def safe_secondary_llm_api_key(self) -> str:
        """Return redacted representation of secondary LLM API key for logging."""
        if not self.SECONDARY_LLM_API_KEY:
            return "not_configured"
        key = self.SECONDARY_LLM_API_KEY.strip()
        if len(key) <= 8:
            return "***"
        return f"{key[:4]}...{key[-4:]}"

    @property
    def safe_redis_url(self) -> str:
        """Return Redis URL with credentials redacted."""
        if not self.REDIS_URL:
            return "not_configured"
        return re.sub(r":([^@]+)@", ":***@", self.REDIS_URL)


settings = Settings()

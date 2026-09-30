"""Application settings loaded from environment (root `.env` / process env)."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Twelve-factor configuration. Never put real secrets here — env only."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_ENV: str = "development"
    APP_NAME: str = "CivicPulse"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"
    BACKEND_PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://civicpulse:civicpulse@localhost:5432/civicpulse"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+psycopg2://", 1)
            if v.startswith("postgresql://") and not v.startswith("postgresql+"):
                return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Auth (demo boundary only — not production auth)
    JWT_SECRET: str = "change-me-dev-only-not-a-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 720

    # AI provider selection (default local env = all mocks, no keys needed)
    AI_STT_PROVIDER: str = "mock"
    AI_LLM_PROVIDER: str = "mock"
    AI_EMBEDDING_PROVIDER: str = "mock"
    GEOCODING_PROVIDER: str = "mock"

    # AI provider credentials and model configurations
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_MODEL: str = "gpt-4o-mini"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()

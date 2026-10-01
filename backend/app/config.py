from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Starkbank DLP - Governança de Uso de IA"
    database_url: str = "postgresql+psycopg://dlp:dlp@localhost:5432/dlp"

    jwt_secret: str = "troque-este-segredo-em-producao"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    pseudonymization_key: str = "troque-esta-chave-em-producao"

    classifier_backend: str = "rules"

    cors_origins: list[str] = ["http://localhost:3000"]

    seed_on_startup: bool = True
    admin_email: str = "admin@starkbank.local"
    admin_password: str = "admin123"


@lru_cache
def get_settings() -> Settings:
    return Settings()

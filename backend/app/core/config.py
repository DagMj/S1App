from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'S1 Eksamen API'
    app_env: str = 'dev'
    app_debug: bool = True
    api_prefix: str = '/api/v1'

    database_url: str = 'sqlite:///./s1_mvp.db'

    jwt_secret_key: str = 'change-me-in-production'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60 * 24

    cors_origins: str = 'http://localhost:5173,http://localhost:3000'

    asset_storage_backend: str = 'local'  # local | s3
    assets_dir: Path = Path('app/assets/generated')
    assets_local_url_prefix: str = '/assets'

    s3_endpoint_url: str | None = None
    s3_region_name: str | None = None
    s3_bucket_name: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_key_prefix: str = 'generated'
    assets_public_base_url: str | None = None

    ai_fallback_enabled: bool = True

    # Sett disse i .env for å opprette en admin-bruker automatisk ved oppstart.
    # Eksisterende bruker oppgraderes til admin hvis e-posten finnes allerede.
    seed_admin_email: str | None = None
    seed_admin_password: str | None = None
    seed_admin_full_name: str = 'Administrator'


@lru_cache
def get_settings() -> Settings:
    return Settings()

from __future__ import annotations

from functools import lru_cache
from typing import Literal, Sequence
from urllib.parse import urlparse

from pydantic import AnyHttpUrl, Field, ValidationError, field_validator, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl


class Settings(BaseSettings):
    # Configuración de carga: lee variables del entorno y del archivo .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,   # permite DATABASE_URL y database_url
        extra="ignore",         # ignora variables no declaradas
    )

    # App
    app_name: str = "Datilera"
    environment: Literal["dev", "staging", "prod"] = "dev"
    debug: bool = True

    # Base de datos (async)
    # Debe ser un driver async válido: mysql+aiomysql, postgresql+asyncpg, sqlite+aiosqlite
    database_url: str = Field(validation_alias="DATABASE_URL")
    REDIS_URL: str = Field(validation_alias="REDIS_URL")
    MEDIA_DIR: str = Field(validation_alias="MEDIA_DIR")
    GEMINI_API_KEY: str = Field(validation_alias="GEMINI_API_KEY")
    PDF_DIR: str = Field(validation_alias="PDF_DIR", default="pdfs")

    # Seguridad / Auth
    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: Literal["HS256", "RS256", "ES256"] = "HS256"
    jwt_exp_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Trusted hosts (Starlette)
    trusted_hosts: list[str] = Field(default_factory=list, alias="TRUSTED_HOSTS")

    # CORS / Frontend
    cors_origins: Sequence[AnyHttpUrl] = Field(default_factory=list)
    cors_allow_credentials: bool = True
    cors_allow_methods: Sequence[str] = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
    cors_allow_headers: Sequence[str] = ("Authorization", "Content-Type")
    STATIC_DIR: str = Field(validation_alias="STATIC_DIR")
    TEMPLATES_DIR: str = Field(validation_alias="TEMPLATES_DIR")

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    sql_echo: bool = False

    # Pool / Engine hints (usados por tu session.py)
    sql_pool_size: int = 10
    sql_max_overflow: int = 20
    sql_pool_recycle: int = 1800              # 30 min
    sql_isolation: str | None = None          # p.ej., "READ COMMITTED"

    # Utilidad derivada para saber si es SQLite
    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite+aiosqlite://")

    # Validaciones ------------------------------------------------------------

    @field_validator("database_url")
    @classmethod
    def _validate_db_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("DATABASE_URL no puede estar vacío")
        ok_prefix = (
            v.startswith("mysql+aiomysql://")
            or v.startswith("postgresql+asyncpg://")
            or v.startswith("sqlite+aiosqlite://")
        )
        if not ok_prefix:
            raise ValueError(
                "DATABASE_URL debe usar un driver asíncrono: "
                "mysql+aiomysql:// | postgresql+asyncpg:// | sqlite+aiosqlite://"
            )
        # Validación rápida de componentes
        parsed = urlparse(v)
        if parsed.scheme.startswith("sqlite"):
            # sqlite puede ser válido sin netloc
            return v
        if not parsed.hostname:
            raise ValueError("DATABASE_URL debe incluir hostname")
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_csv(cls, v):
        # Permite definir CORS_ORIGINS como CSV en .env
        # CORS_ORIGINS=https://app.local,https://admin.local
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            return [x.strip() for x in s.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as ex:
        # Eleva con mensaje claro para fallar rápido en arranque
        raise RuntimeError(f"Error de configuración: {ex}") from ex

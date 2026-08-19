from __future__ import annotations

from functools import lru_cache
from typing import Literal, Sequence
from urllib.parse import urlparse

from pydantic import AnyHttpUrl, Field, ValidationError, field_validator, AliasChoices, model_validator
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
    environment: Literal["dev", "staging", "prod"] = Field(
        default="dev",
        validation_alias=AliasChoices("ENVIRONMENT", "ENV"),
    )
    debug: bool | None = None

    # Base de datos (async)
    # Debe ser un driver async válido: mysql+aiomysql, postgresql+asyncpg, sqlite+aiosqlite
    database_url: str = Field(validation_alias="DATABASE_URL")
    REDIS_URL: str = Field(validation_alias="REDIS_URL")
    MEDIA_DIR: str = Field(validation_alias="MEDIA_DIR")
    GEMINI_API_KEY: str = Field(validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", validation_alias="GEMINI_MODEL")
    PDF_DIR: str = Field(validation_alias="PDF_DIR", default="pdfs")

    # Seguridad / Auth
    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: Literal["HS256", "RS256", "ES256"] = "HS256"
    jwt_exp_minutes: int = Field(
        default=60,
        validation_alias=AliasChoices("JWT_EXP_MINUTES", "ACCESS_EXPIRE_MIN"),
        ge=5,
        le=1440,
    )
    refresh_token_expire_days: int = Field(
        default=7,
        validation_alias=AliasChoices("REFRESH_TOKEN_EXPIRE_DAYS", "REFRESH_EXPIRE_DAYS"),
        ge=1,
        le=90,
    )

    # Trusted hosts (Starlette)
    trusted_hosts: str = Field(default="", alias="TRUSTED_HOSTS")

    # CORS / Frontend
    cors_origins: str = Field(
        default="",
        validation_alias=AliasChoices("CORS_ORIGINS", "ALLOWED_ORIGINS"),
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: Sequence[str] = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
    cors_allow_headers: Sequence[str] = ("Authorization", "Content-Type")
    STATIC_DIR: str = Field(validation_alias="STATIC_DIR")
    TEMPLATES_DIR: str = Field(validation_alias="TEMPLATES_DIR")

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    sql_echo: bool = False

    # Pool / Engine hints (usados por tu session.py)
    sql_pool_size: int = 50
    sql_max_overflow: int = 50
    sql_pool_recycle: int = 1800              # 30 min
    sql_isolation: str | None = None          # p.ej., "READ COMMITTED"

    # Utilidad derivada para saber si es SQLite
    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite+aiosqlite://")

    @property
    def is_production(self) -> bool:
        return self.environment == "prod"

    @property
    def effective_debug(self) -> bool:
        """En producción el modo debug nunca puede quedar activo por omisión."""
        return self.debug if self.debug is not None else self.environment == "dev"

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip().rstrip("/") for item in self.cors_origins.split(",") if item.strip()]

    @property
    def trusted_host_list(self) -> list[str]:
        return [item.strip() for item in self.trusted_hosts.split(",") if item.strip()]

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

    @model_validator(mode="after")
    def _validate_security_settings(self) -> "Settings":
        self.jwt_secret = self.jwt_secret.strip()
        if self.environment == "prod" and len(self.jwt_secret) < 32:
            raise ValueError("JWT_SECRET debe contener al menos 32 caracteres en producción")
        if self.environment == "prod" and not self.cors_origin_list:
            raise ValueError("CORS_ORIGINS debe configurarse explícitamente en producción")
        return self


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as ex:
        # Eleva con mensaje claro para fallar rápido en arranque
        raise RuntimeError(f"Error de configuración: {ex}") from ex

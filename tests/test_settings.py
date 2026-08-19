import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def _base_settings(**overrides):
    values = {
        "DATABASE_URL": "mysql+aiomysql://test:test@localhost:3306/datilera",
        "REDIS_URL": "redis://localhost:6379/0",
        "MEDIA_DIR": "media",
        "PDF_DIR": "pdfs",
        "STATIC_DIR": "app/interfaces/web/static",
        "TEMPLATES_DIR": "app/interfaces/web/templates",
        "GEMINI_API_KEY": "test",
        "JWT_SECRET": "a" * 40,
        "CORS_ORIGINS": "https://app.example.com",
    }
    if "ALLOWED_ORIGINS" in overrides:
        values.pop("CORS_ORIGINS")
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_aliases_historicos_siguen_funcionando(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    settings = _base_settings(
        ENV="staging",
        ACCESS_EXPIRE_MIN="30",
        REFRESH_EXPIRE_DAYS="14",
        ALLOWED_ORIGINS="https://uno.example.com,https://dos.example.com",
    )
    assert settings.environment == "staging"
    assert settings.jwt_exp_minutes == 30
    assert settings.refresh_token_expire_days == 14
    assert settings.cors_origin_list == ["https://uno.example.com", "https://dos.example.com"]


def test_produccion_rechaza_secreto_debil():
    with pytest.raises(ValidationError):
        _base_settings(ENVIRONMENT="prod", JWT_SECRET="debil")


def test_debug_por_defecto_solo_en_desarrollo():
    assert _base_settings(ENVIRONMENT="dev").effective_debug is True
    assert _base_settings(ENVIRONMENT="prod").effective_debug is False

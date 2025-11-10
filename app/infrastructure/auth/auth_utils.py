# app/infrastructure/auth/auth_utils.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from passlib.context import CryptContext
import jwt

from app.config.settings import Settings, get_settings
from app.kernel.domain.seguridad.ports import AbstractHasher, AbstractTokenService

_settings: Settings = get_settings()
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasslibHasher(AbstractHasher):
    def hash_password(self, password: str) -> str:
        return _pwd_context.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        return _pwd_context.verify(password, password_hash)

class PyJWTTokenService(AbstractTokenService):
    def __init__(self, settings: Settings | None = None):
        self._settings = settings or _settings

    def _create_token(self, payload: dict, expires_delta: timedelta) -> str:
        now = datetime.now(timezone.utc)
        payload = {**payload, "exp": now + expires_delta, "iat": now}
        return jwt.encode(payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm)

    def create_access_token(self, user_id: int, sede_id: int, permisos: List[str]) -> str:
        payload = {"sub": str(user_id), "sede": str(sede_id), "type": "access", "pms": permisos}
        return self._create_token(payload, timedelta(minutes=self._settings.jwt_exp_minutes))

    def create_refresh_token(self, user_id: int, jti: str) -> str:
        payload = {"sub": str(user_id), "jti": jti, "type": "refresh"}
        return self._create_token(payload, timedelta(days=self._settings.refresh_token_expire_days))

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self._settings.jwt_secret, algorithms=[self._settings.jwt_algorithm])

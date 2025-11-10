# app/kernel/application/seguridad/csrf.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Protocol
import secrets

class ICsrfService(Protocol):
    def emitir(self) -> str: ...
    def validar(self, token: str) -> bool: ...

class CsrfService(ICsrfService):
    def emitir(self) -> str: return secrets.token_urlsafe(32)
    def validar(self, token: str) -> bool: return bool(token and len(token) >= 32)

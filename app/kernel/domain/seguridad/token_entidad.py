# app/kernel/domain/seguridad/token_entidad.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, model_validator


class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    access_token: str
    refresh_token: str
    usuario_id: int

    expiracion_minutos: int = 15

    creado_en: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expira_en: Optional[AwareDatetime] = None

    revocado: bool = False

    @model_validator(mode="after")
    def _compute_expiry(self) -> "Token":
        if self.expira_en is None:
            self.expira_en = self.creado_en + timedelta(minutes=self.expiracion_minutos)
        return self

    def esta_expirado(self) -> bool:
        return datetime.now(timezone.utc) > (self.expira_en or self.creado_en)

    def revocar(self) -> None:
        self.revocado = True

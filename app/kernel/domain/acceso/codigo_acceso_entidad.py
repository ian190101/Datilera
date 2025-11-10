# app/kernel/domain/acceso/codigo_acceso_entidad.py
from __future__ import annotations

from datetime import datetime, date, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, AwareDatetime

from app.kernel.domain.acceso.estado_codigo_entidad import EstadoCodigo


class CodigoAcceso(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,          # permite construir desde objetos/ORM
        use_enum_values=True,          # serializa EstadoCodigo como su valor
        validate_assignment=True,      # revalida en asignaciones posteriores
    )

    id: int
    sede_id: int
    gestion: int
    rol_id: int
    usuario_destino_id: Optional[int] = None
    alumno_id: Optional[int] = None

    max_cuentas: int = Field(ge=0)
    cuentas_creadas: int = Field(ge=0)

    codigo: str = Field(min_length=6, max_length=6, description="Código de 6 caracteres alfanuméricos")
    expira_en: Optional[date] = None

    estado: EstadoCodigo

    whatsapp_numero: str
    whatsapp_message_id: Optional[str] = None
    enviado: bool = False
    enviado_en: Optional[AwareDatetime] = None

    entregado_a: Optional[str] = None
    observaciones: Optional[str] = None
    creado_por: Optional[int] = None

    creado_en: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actualizado_en: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # --- Validadores ---

    @field_validator("codigo")
    @classmethod
    def _codigo_6_alfanumerico(cls, v: str) -> str:
        v2 = v.strip().upper()
        if len(v2) != 6 or not v2.isalnum():
            raise ValueError("El código debe tener exactamente 6 caracteres alfanuméricos")
        return v2

    @field_validator("cuentas_creadas")
    @classmethod
    def _cuentas_no_superan_max(cls, v: int, info) -> int:
        max_cuentas = info.data.get("max_cuentas")
        if max_cuentas is not None and v > max_cuentas:
            raise ValueError("cuentas_creadas no puede superar max_cuentas")
        return v

    @field_validator("enviado_en", "creado_en", "actualizado_en", mode="before")
    @classmethod
    def _tz_aware(cls, v):
        # Acepta naive y los lleva a UTC; si ya es aware, lo retorna.
        if v is None:
            return v
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

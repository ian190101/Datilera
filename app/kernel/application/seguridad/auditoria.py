# app/kernel/application/seguridad/puertos_auditoria.py
from typing import Protocol, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field

class EventoSeguridad(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    usuario_id: Optional[int] = None
    sede_id: Optional[int] = None
    accion: str
    entidad: Optional[str] = None
    entidad_id: Optional[int] = None
    ip: Optional[str] = None
    creado_en: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class IAuditoriaRepo(Protocol):
    async def registrar(self, ev: EventoSeguridad) -> None: ...

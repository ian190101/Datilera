# app/kernel/domain/auditoria/auditoria_accion_entidad.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

ACCIONES_PERMITIDAS = {
    "create", "update", "delete", "login", "logout",
    "upload", "download", "approve", "reject", "refresh",
    "assign_role", "assign_permission",
}

class AuditoriaAccion(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int | None = None
    usuario_id: Optional[int] = None
    sede_id: Optional[int] = None

    entidad: str
    entidad_id: Optional[str] = None
    accion: str

    datos_antes: Dict[str, Any] = Field(default_factory=dict)
    datos_despues: Dict[str, Any] = Field(default_factory=dict)

    ip: Optional[str] = None
    user_agent: Optional[str] = None
    sesion_id: Optional[int] = None

    creado_en: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("accion")
    @classmethod
    def _accion_valida(cls, v: str) -> str:
        if v not in ACCIONES_PERMITIDAS:
            raise ValueError(f"Acción no permitida: {v}")
        return v

    @field_validator("datos_antes", "datos_despues", mode="before")
    @classmethod
    def _normalizar_dict(cls, v):
        return v or {}

    def generar_resumen(self) -> str:
        return (
            f"[{self.creado_en.isoformat()}] Acción '{self.accion}' sobre entidad '{self.entidad}' "
            f"(ID: {self.entidad_id}) por usuario {self.usuario_id or 'anónimo'} desde IP {self.ip or 'desconocida'}."
        )

    def comparar_datos(self) -> Dict[str, Dict[str, Optional[str]]]:
        diferencias: Dict[str, Dict[str, Optional[str]]] = {}
        claves = set(self.datos_antes.keys()) | set(self.datos_despues.keys())
        for clave in claves:
            a = self.datos_antes.get(clave)
            d = self.datos_despues.get(clave)
            if a != d:
                diferencias[clave] = {"antes": a, "despues": d}
        return diferencias

    def es_accion_valida(self) -> bool:
        return self.accion in ACCIONES_PERMITIDAS

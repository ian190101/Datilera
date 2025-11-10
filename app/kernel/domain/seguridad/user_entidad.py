# app/kernel/domain/seguridad/user_entidad.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, field_validator

from .rol_entidad import Rol, Accion
from .preferencias_usuario_entidad import PreferenciasUsuario


class Usuario(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    nombre_usuario: str
    contrasena: str
    rol: Rol
    sede_id: int
    activo: bool = True
    foto_perfil: Optional[str] = None

    fecha_creacion: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ultimo_login: Optional[AwareDatetime] = None

    preferencias: PreferenciasUsuario = Field(default_factory=PreferenciasUsuario)

    @field_validator("foto_perfil")
    @classmethod
    def _ext_imagen(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.lower().endswith((".jpg", ".jpeg", ".png")):
            raise ValueError("Formato de imagen no válido")
        return v

    def cambiar_contrasena(self, nueva_contrasena: str) -> None:
        self.contrasena = nueva_contrasena

    def desactivar(self) -> None:
        self.activo = False

    def activar(self) -> None:
        self.activo = True

    def cambiar_foto(self, nueva_foto: str) -> None:
        self.foto_perfil = nueva_foto  # validador asegura extensión válida

    def tiene_permiso(self, recurso: str, accion: Accion) -> bool:
        return self.rol.tiene_permiso(recurso, accion)

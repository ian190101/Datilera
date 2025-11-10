# app/kernel/domain/seguridad/preferencias_usuario_entidad.py
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator


class PreferenciasUsuario(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    tema: str = "claro"           # "claro" / "oscuro"
    notificaciones: bool = True
    idioma: str = "es"

    @field_validator("tema")
    @classmethod
    def _tema_valido(cls, v: str) -> str:
        if v not in {"claro", "oscuro"}:
            raise ValueError("Tema inválido")
        return v

    def cambiar_tema(self, nuevo_tema: str) -> None:
        self.tema = nuevo_tema

    def activar_notificaciones(self) -> None:
        self.notificaciones = True

    def desactivar_notificaciones(self) -> None:
        self.notificaciones = False

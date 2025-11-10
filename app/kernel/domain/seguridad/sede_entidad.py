# app/kernel/domain/seguridad/sede_entidad.py
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Sede(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    nombre: str
    dominio: str
    ubicacion: str
    activa: bool = True

    def desactivar(self) -> None:
        self.activa = False

    def activar(self) -> None:
        self.activa = True

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional


@dataclass
class Turno:
    id: int
    sede_id: int
    nombre: str
    hora_inicio: time
    hora_fin: time
    descripcion: Optional[str] = None
    activo: bool = True
    orden: Optional[int] = None
    creado_en: datetime = None
    actualizado_en: Optional[datetime] = None

    def __post_init__(self):
        if not (self.nombre or "").strip():
            raise ValueError("El nombre del turno es obligatorio.")
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser menor a la hora de fin.")
        self.creado_en = self.creado_en or datetime.utcnow()

    # --- Comportamiento de dominio ---
    def cambiar_horario(self, nueva_inicio: time, nueva_fin: time) -> None:
        if nueva_inicio >= nueva_fin:
            raise ValueError("La hora de inicio debe ser menor a la hora de fin.")
        self.hora_inicio = nueva_inicio
        self.hora_fin = nueva_fin
        self.actualizado_en = datetime.utcnow()

    def desactivar(self) -> None:
        if not self.activo:
            return
        self.activo = False
        self.actualizado_en = datetime.utcnow()

    def activar(self) -> None:
        if self.activo:
            return
        self.activo = True
        self.actualizado_en = datetime.utcnow()
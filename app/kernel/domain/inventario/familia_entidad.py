# app/kernel/domain/inventario/familia_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Familia:
    """
    Entidad Familia (agrupa categorías: uniformes, materiales, ingredientes, limpieza, activos, etc.).
    """
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True
    creado_en: datetime = None

    def __post_init__(self):
        if not (self.nombre or "").strip():
            raise ValueError("El nombre de la familia es obligatorio.")
        self.creado_en = self.creado_en or datetime.utcnow()

    def activar(self) -> None:
        self.activo = True

    def desactivar(self) -> None:
        self.activo = False
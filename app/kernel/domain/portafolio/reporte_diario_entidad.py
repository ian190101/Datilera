# app/kernel/domain/portafolio/reporte_diario_entidad.py
from __future__ import annotations
from datetime import date, datetime
from typing import Optional


class ReporteDiario:
    """
    Entidad **ReporteDiario** (portafolio).
    - `contenido` obligatorio (texto del reporte).
    - Se envía a tutores (lógica de notificación fuera del dominio de entidades).
    """
    def __init__(
        self,
        id: int,
        paralelo_id: int,
        profesora_id: int,
        fecha: date,
        contenido: str,
        creado_en: Optional[datetime] = None,
        actualizado_en: Optional[datetime] = None,
    ):
        c = (contenido or "").strip()
        if not c:
            raise ValueError("El contenido del reporte diario es obligatorio.")
        self.id = id
        self.paralelo_id = paralelo_id
        self.profesora_id = profesora_id
        self.fecha = fecha
        self.contenido = c
        self.creado_en = creado_en or datetime.utcnow()
        self.actualizado_en = actualizado_en or self.creado_en

    def actualizar_contenido(self, nuevo_contenido: str) -> None:
        c = (nuevo_contenido or "").strip()
        if not c:
            raise ValueError("El contenido no puede quedar vacío.")
        self.contenido = c
        self.actualizado_en = datetime.utcnow()

    def resumen(self, max_chars: int = 160) -> str:
        txt = self.contenido.replace("\n", " ").strip()
        return txt if len(txt) <= max_chars else txt[: max_chars - 1] + "…"

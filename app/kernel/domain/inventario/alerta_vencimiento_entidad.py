# app/kernel/domain/inventario/alerta_vencimiento_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class AlertaVencimiento:
    """
    Alerta por vencimiento de lote/ítem. La lógica de avisos 5/3/1 días
    se programa en la capa de aplicación (scheduler); esta entidad
    solo persiste el registro y su estado de notificación.
    """
    id: int
    item_id: int
    sede_id: int
    fecha_vencimiento: date
    lote: Optional[str] = None
    notificada: bool = False
    creado_en: datetime = None

    def __post_init__(self):
        self.creado_en = self.creado_en or datetime.utcnow()

    def marcar_notificada(self) -> None:
        self.notificada = True
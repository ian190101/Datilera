# app/kernel/domain/inventario/alerta_vencimiento_entidad.py
from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field

class AlertaVencimiento(BaseModel):
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
    
    # default_factory maneja la creación de la fecha automáticamente
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    def marcar_notificada(self) -> None:
        """Actualiza el estado de notificación a True."""
        self.notificada = True
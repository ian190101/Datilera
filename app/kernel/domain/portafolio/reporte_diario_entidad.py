# app/kernel/domain/portafolio/reporte_diario_entidad.py
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field


class ReporteDiario(BaseModel):
    # Configuración Nueva (Pydantic V2)
    model_config = ConfigDict(from_attributes=True)

    id: int
    alumno_id: int
    profesora_id: int
    fecha: date
    
    # CORREGIDO: Debe coincidir con la base de datos
    contenido: Optional[str] = None 
    
    enviado: bool
    enviado_en: Optional[datetime] = None
    confirmado: bool
    confirmado_en: Optional[datetime] = None

    @computed_field
    def esta_pendiente(self) -> bool:
        return not self.enviado

    @computed_field
    def esta_completo(self) -> bool:
        return self.enviado and self.confirmado
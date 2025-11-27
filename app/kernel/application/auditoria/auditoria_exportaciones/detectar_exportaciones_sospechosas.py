# app/kernel/application/auditoria/auditoria_exportaciones/detectar_exportaciones_sospechosas.py

"""
Caso de Uso: Detectar Exportaciones Sospechosas
"""
from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaExportacion
from app.infrastructure.db.repositories.auditoria import AuditoriaExportacionesRepository


# ===== DTO =====

class DetectarExportacionesSospechosasDTO(BaseModel):
    """DTO para detectar exportaciones sospechosas."""
    umbral_registros: int = Field(default=1000, ge=100, le=100000)
    ventana_horas: int = Field(default=1, ge=1, le=168)  # Máximo 1 semana


# ===== Caso de Uso =====

class DetectarExportacionesSospechosasCU:
    """
    Caso de Uso: Detectar Exportaciones Masivas Sospechosas.
    
    Responsabilidad: Identificar exportaciones que superan umbrales de seguridad.
    Según HU: Detectar exportaciones masivas sospechosas.
    Debe ejecutarse periódicamente o al registrar exportaciones grandes.
    """
    
    def __init__(self, repo: AuditoriaExportacionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: DetectarExportacionesSospechosasDTO) -> List[AuditoriaExportacion]:
        """
        Detecta exportaciones masivas en ventana de tiempo.
        
        Args:
            dto: Configuración de detección
            
        Returns:
            Lista de exportaciones sospechosas
        """
        models = await self.repo.detectar_exportaciones_masivas(
            umbral_registros=dto.umbral_registros,
            ventana_horas=dto.ventana_horas
        )
        
        return [AuditoriaExportacion.model_validate(m) for m in models]

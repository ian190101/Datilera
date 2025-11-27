# app/kernel/application/auditoria/auditoria_exportaciones/marcar_exportacion_descargada.py

"""
Caso de Uso: Marcar Exportación como Descargada
"""
from __future__ import annotations
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import (
    AuditoriaExportacion,
    ExportacionAuditoriaNoEncontrada,
    ExportacionYaDescargada,
)
from app.infrastructure.db.repositories.auditoria import AuditoriaExportacionesRepository


# ===== DTO =====

class MarcarExportacionDescargadaDTO(BaseModel):
    """DTO para marcar exportación como descargada."""
    exportacion_id: int = Field(..., gt=0)


# ===== Caso de Uso =====

class MarcarExportacionDescargadaCU:
    """
    Caso de Uso: Marcar Exportación como Descargada.
    
    Responsabilidad: Registrar cuando un archivo exportado es descargado.
    Útil para auditoría de acceso a datos exportados.
    """
    
    def __init__(self, repo: AuditoriaExportacionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: MarcarExportacionDescargadaDTO) -> AuditoriaExportacion:
        """
        Marca una exportación como descargada.
        
        Args:
            dto: ID de la exportación
            
        Returns:
            Entidad actualizada
            
        Raises:
            ExportacionAuditoriaNoEncontrada: Si no existe
            ExportacionYaDescargada: Si ya fue descargada
        """
        # Verificar que existe
        model = await self.repo.obtener_por_id(dto.exportacion_id)
        if model is None:
            raise ExportacionAuditoriaNoEncontrada(dto.exportacion_id)
        
        # Verificar que no esté ya descargada
        exportacion = AuditoriaExportacion.model_validate(model)
        if exportacion.fue_descargada():
            raise ExportacionYaDescargada(dto.exportacion_id)
        
        # Marcar como descargada
        await self.repo.marcar_descargado(dto.exportacion_id)
        
        # Retornar actualizada
        model_actualizado = await self.repo.obtener_por_id(dto.exportacion_id)
        return AuditoriaExportacion.model_validate(model_actualizado)

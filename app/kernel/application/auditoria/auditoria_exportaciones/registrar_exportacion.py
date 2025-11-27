# app/kernel/application/auditoria/auditoria_exportaciones/registrar_exportacion.py

"""
Caso de Uso: Registrar Exportación
"""
from __future__ import annotations
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaExportacion
from app.infrastructure.db.repositories.auditoria import AuditoriaExportacionesRepository


# ===== DTO =====

class RegistrarExportacionDTO(BaseModel):
    """DTO para registrar una exportación."""
    usuario_id: Optional[int] = Field(None, gt=0)
    sede_id: Optional[int] = Field(None, gt=0)
    tipo: str = Field(..., min_length=1, max_length=50)
    formato: str = Field(..., min_length=1, max_length=20)
    total_registros: int = Field(..., ge=0)
    filtros: Optional[Dict[str, Any]] = None
    columnas: Optional[List[str]] = None
    ruta_archivo: Optional[str] = Field(None, max_length=500)
    exitoso: bool = True
    mensaje_error: Optional[str] = None


# ===== Caso de Uso =====

class RegistrarExportacionCU:
    """
    Caso de Uso: Registrar Exportación.
    
    Responsabilidad: Registrar una exportación de datos.
    Según HU: "Auditar todas las exportaciones (Excel/PDF)".
    Crítico para cumplimiento GDPR y detectar exportaciones sospechosas.
    """
    
    def __init__(self, repo: AuditoriaExportacionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: RegistrarExportacionDTO) -> AuditoriaExportacion:
        """
        Registra una exportación de datos.
        
        Args:
            dto: Datos de la exportación
            
        Returns:
            Entidad de dominio AuditoriaExportacion
        """
        # Registrar en infraestructura
        model = await self.repo.registrar(
            usuario_id=dto.usuario_id,
            sede_id=dto.sede_id,
            tipo=dto.tipo,
            formato=dto.formato,
            total_registros=dto.total_registros,
            filtros=dto.filtros,
            columnas=dto.columnas,
            ruta_archivo=dto.ruta_archivo,
            exitoso=dto.exitoso,
            mensaje_error=dto.mensaje_error,
        )
        
        # Mapear a entidad de dominio
        return AuditoriaExportacion.model_validate(model)

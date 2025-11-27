# app/kernel/application/auditoria/auditoria_acciones/limpiar_acciones_antiguas.py

"""
Caso de Uso: Limpiar Acciones Antiguas
"""
from __future__ import annotations
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.auditoria import AuditoriaAccionesRepository


# ===== DTO =====

class LimpiarAccionesAntiguasDTO(BaseModel):
    """DTO para limpiar acciones antiguas."""
    dias: int = Field(default=90, ge=1, le=3650)  # Máximo 10 años


# ===== Caso de Uso =====

class LimpiarAccionesAntiguasCU:
    """
    Caso de Uso: Limpiar Acciones Antiguas.
    
    Responsabilidad: Eliminar eventos de auditoría antiguos para gestión de espacio.
    Según HU: Los registros deben conservarse hasta eliminación manual.
    Este CU debe ejecutarse manualmente o mediante tarea programada.
    """
    
    def __init__(self, repo: AuditoriaAccionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: LimpiarAccionesAntiguasDTO) -> int:
        """
        Limpia acciones de auditoría más antiguas que N días.
        
        Args:
            dto: Configuración de limpieza
            
        Returns:
            Cantidad de registros eliminados
        """
        cantidad_eliminada = await self.repo.limpiar_antiguos(dias=dto.dias)
        return cantidad_eliminada

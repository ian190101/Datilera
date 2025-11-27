# app/kernel/application/auditoria/auditoria_acciones/obtener_accion.py

"""
Caso de Uso: Obtener Acción de Auditoría
"""
from __future__ import annotations
from typing import Optional

from app.kernel.domain.auditoria import AuditoriaAccion, AccionAuditoriaNoEncontrada
from app.infrastructure.db.repositories.auditoria import AuditoriaAccionesRepository


class ObtenerAccionCU:
    """
    Caso de Uso: Obtener Acción de Auditoría por ID.
    
    Responsabilidad: Recuperar una acción específica.
    """
    
    def __init__(self, repo: AuditoriaAccionesRepository):
        self.repo = repo
    
    async def ejecutar(self, auditoria_id: int) -> AuditoriaAccion:
        """
        Obtiene una acción de auditoría por su ID.
        
        Args:
            auditoria_id: ID de la acción
            
        Returns:
            Entidad de dominio AuditoriaAccion
            
        Raises:
            AccionAuditoriaNoEncontrada: Si no existe la acción
        """
        model = await self.repo.obtener_por_id(auditoria_id)
        
        if model is None:
            raise AccionAuditoriaNoEncontrada(auditoria_id)
        
        return AuditoriaAccion.model_validate(model)

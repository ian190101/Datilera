# app/kernel/application/auditoria/auditoria_prompts_ia/detectar_prompts_sensibles.py

"""
Caso de Uso: Detectar Prompts con Datos Sensibles
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaPromptIA
from app.infrastructure.db.repositories.auditoria import AuditoriaPromptsIARepository


# ===== DTO =====

class DetectarPromptsSensiblesDTO(BaseModel):
    """DTO para detectar prompts con datos sensibles."""
    sede_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=500)


# ===== Caso de Uso =====

class DetectarPromptsSensiblesCU:
    """
    Caso de Uso: Detectar Prompts con Datos Sensibles.
    
    Responsabilidad: Identificar consultas que contienen información sensible.
    Según HU: Datos sensibles como alergias, medicación deben protegerse.
    Crítico para cumplimiento de privacidad.
    """
    
    def __init__(self, repo: AuditoriaPromptsIARepository):
        self.repo = repo
    
    async def ejecutar(self, dto: DetectarPromptsSensiblesDTO) -> List[AuditoriaPromptIA]:
        """
        Detecta prompts que contienen datos sensibles.
        
        Args:
            dto: Filtros de búsqueda
            
        Returns:
            Lista de prompts con datos sensibles
        """
        models = await self.repo.listar_con_datos_sensibles(
            sede_id=dto.sede_id,
            desde=dto.desde,
            limit=dto.limit
        )
        
        return [AuditoriaPromptIA.model_validate(m) for m in models]

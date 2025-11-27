# app/kernel/application/auditoria/auditoria_prompts_ia/listar_prompts_ia.py

"""
Caso de Uso: Listar Prompts IA
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaPromptIA
from app.infrastructure.db.repositories.auditoria import AuditoriaPromptsIARepository


# ===== DTOs =====

class ListarPromptsPorUsuarioDTO(BaseModel):
    """DTO para listar prompts por usuario."""
    usuario_id: int = Field(..., gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    categoria: Optional[str] = Field(None, max_length=50)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ListarPromptsPorSedeDTO(BaseModel):
    """DTO para listar prompts por sede."""
    sede_id: int = Field(..., gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ListarPromptsConDatosSensiblesDTO(BaseModel):
    """DTO para listar prompts con datos sensibles."""
    sede_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=500)


class ListarPromptsFallidosDTO(BaseModel):
    """DTO para listar prompts fallidos."""
    usuario_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=500)


# ===== Caso de Uso =====

class ListarPromptsIACU:
    """
    Caso de Uso: Listar Prompts IA.
    
    Responsabilidad: Recuperar historial de consultas a IA.
    """
    
    def __init__(self, repo: AuditoriaPromptsIARepository):
        self.repo = repo
    
    async def por_usuario(self, dto: ListarPromptsPorUsuarioDTO) -> List[AuditoriaPromptIA]:
        """Lista prompts de un usuario."""
        models = await self.repo.listar_por_usuario(
            usuario_id=dto.usuario_id,
            desde=dto.desde,
            hasta=dto.hasta,
            categoria=dto.categoria,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaPromptIA.model_validate(m) for m in models]
    
    async def por_sede(self, dto: ListarPromptsPorSedeDTO) -> List[AuditoriaPromptIA]:
        """Lista prompts de una sede."""
        models = await self.repo.listar_por_sede(
            sede_id=dto.sede_id,
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaPromptIA.model_validate(m) for m in models]
    
    async def con_datos_sensibles(self, dto: ListarPromptsConDatosSensiblesDTO) -> List[AuditoriaPromptIA]:
        """Lista prompts que contienen datos sensibles."""
        models = await self.repo.listar_con_datos_sensibles(
            sede_id=dto.sede_id,
            desde=dto.desde,
            limit=dto.limit
        )
        return [AuditoriaPromptIA.model_validate(m) for m in models]
    
    async def fallidos(self, dto: ListarPromptsFallidosDTO) -> List[AuditoriaPromptIA]:
        """Lista prompts fallidos."""
        models = await self.repo.listar_fallidos(
            usuario_id=dto.usuario_id,
            desde=dto.desde,
            limit=dto.limit
        )
        return [AuditoriaPromptIA.model_validate(m) for m in models]

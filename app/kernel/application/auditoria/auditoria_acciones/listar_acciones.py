# app/kernel/application/auditoria/auditoria_acciones/listar_acciones.py

"""
Caso de Uso: Listar Acciones de Auditoría
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaAccion
from app.infrastructure.db.repositories.auditoria import AuditoriaAccionesRepository


# ===== DTOs =====

class ListarAccionesPorUsuarioDTO(BaseModel):
    """DTO para listar acciones por usuario."""
    usuario_id: int = Field(..., gt=0)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ListarAccionesPorSedeDTO(BaseModel):
    """DTO para listar acciones por sede."""
    sede_id: int = Field(..., gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ListarAccionesPorEntidadDTO(BaseModel):
    """DTO para listar acciones por entidad."""
    entidad: str = Field(..., min_length=1, max_length=120)
    entidad_id: Optional[str] = Field(None, max_length=64)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ListarAccionesPorNivelDTO(BaseModel):
    """DTO para listar acciones por nivel."""
    nivel: str = Field(..., min_length=1, max_length=20)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ListarErroresDTO(BaseModel):
    """DTO para listar errores."""
    sede_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ===== Caso de Uso =====

class ListarAccionesCU:
    """
    Caso de Uso: Listar Acciones de Auditoría.
    
    Responsabilidad: Recuperar listas de eventos de auditoría con filtros.
    """
    
    def __init__(self, repo: AuditoriaAccionesRepository):
        self.repo = repo
    
    async def por_usuario(self, dto: ListarAccionesPorUsuarioDTO) -> List[AuditoriaAccion]:
        """Lista acciones de un usuario."""
        models = await self.repo.listar_por_usuario(
            usuario_id=dto.usuario_id,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaAccion.model_validate(m) for m in models]
    
    async def por_sede(self, dto: ListarAccionesPorSedeDTO) -> List[AuditoriaAccion]:
        """Lista acciones de una sede."""
        models = await self.repo.listar_por_sede(
            sede_id=dto.sede_id,
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaAccion.model_validate(m) for m in models]
    
    async def por_entidad(self, dto: ListarAccionesPorEntidadDTO) -> List[AuditoriaAccion]:
        """Lista acciones de una entidad."""
        models = await self.repo.listar_por_entidad(
            entidad=dto.entidad,
            entidad_id=dto.entidad_id,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaAccion.model_validate(m) for m in models]
    
    async def por_nivel(self, dto: ListarAccionesPorNivelDTO) -> List[AuditoriaAccion]:
        """Lista acciones por nivel de severidad."""
        models = await self.repo.listar_por_nivel(
            nivel=dto.nivel,
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaAccion.model_validate(m) for m in models]
    
    async def errores(self, dto: ListarErroresDTO) -> List[AuditoriaAccion]:
        """Lista solo errores."""
        models = await self.repo.listar_errores(
            sede_id=dto.sede_id,
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaAccion.model_validate(m) for m in models]

# app/kernel/application/auditoria/auditoria_exportaciones/listar_exportaciones.py

"""
Caso de Uso: Listar Exportaciones
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaExportacion
from app.infrastructure.db.repositories.auditoria import AuditoriaExportacionesRepository


# ===== DTOs =====

class ListarExportacionesPorUsuarioDTO(BaseModel):
    """DTO para listar exportaciones por usuario."""
    usuario_id: int = Field(..., gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    tipo: Optional[str] = Field(None, max_length=50)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ListarExportacionesPorSedeDTO(BaseModel):
    """DTO para listar exportaciones por sede."""
    sede_id: int = Field(..., gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ListarExportacionesPorTipoDTO(BaseModel):
    """DTO para listar exportaciones por tipo."""
    tipo: str = Field(..., min_length=1, max_length=50)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ListarExportacionesFallidasDTO(BaseModel):
    """DTO para listar exportaciones fallidas."""
    sede_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=500)


# ===== Caso de Uso =====

class ListarExportacionesCU:
    """
    Caso de Uso: Listar Exportaciones.
    
    Responsabilidad: Recuperar historial de exportaciones con filtros.
    """
    
    def __init__(self, repo: AuditoriaExportacionesRepository):
        self.repo = repo
    
    async def por_usuario(self, dto: ListarExportacionesPorUsuarioDTO) -> List[AuditoriaExportacion]:
        """Lista exportaciones de un usuario."""
        models = await self.repo.listar_por_usuario(
            usuario_id=dto.usuario_id,
            desde=dto.desde,
            hasta=dto.hasta,
            tipo=dto.tipo,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaExportacion.model_validate(m) for m in models]
    
    async def por_sede(self, dto: ListarExportacionesPorSedeDTO) -> List[AuditoriaExportacion]:
        """Lista exportaciones de una sede."""
        models = await self.repo.listar_por_sede(
            sede_id=dto.sede_id,
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaExportacion.model_validate(m) for m in models]
    
    async def por_tipo(self, dto: ListarExportacionesPorTipoDTO) -> List[AuditoriaExportacion]:
        """Lista exportaciones por tipo."""
        models = await self.repo.listar_por_tipo(
            tipo=dto.tipo,
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaExportacion.model_validate(m) for m in models]
    
    async def fallidas(self, dto: ListarExportacionesFallidasDTO) -> List[AuditoriaExportacion]:
        """Lista exportaciones fallidas."""
        models = await self.repo.listar_fallidas(
            sede_id=dto.sede_id,
            desde=dto.desde,
            limit=dto.limit
        )
        return [AuditoriaExportacion.model_validate(m) for m in models]

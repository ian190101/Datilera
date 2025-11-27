# app/kernel/application/auditoria/auditoria_acciones/buscar_acciones_cu.py

"""
Caso de Uso: Buscar Acciones de Auditoría
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaAccion
from app.infrastructure.db.repositories.auditoria import AuditoriaAccionesRepository


# ===== DTOs =====

class BuscarPorDescripcionDTO(BaseModel):
    """DTO para buscar por descripción."""
    termino: str = Field(..., min_length=1)
    sede_id: Optional[int] = Field(None, gt=0)
    limit: int = Field(default=50, ge=1, le=100)


class BuscarPorEndpointDTO(BaseModel):
    """DTO para buscar por endpoint."""
    endpoint: str = Field(..., min_length=1, max_length=255)
    metodo_http: Optional[str] = Field(None, max_length=10)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class BuscarPorIPDTO(BaseModel):
    """DTO para buscar por IP."""
    ip: str = Field(..., min_length=7, max_length=50)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ===== Caso de Uso =====

class BuscarAccionesCU:
    """
    Caso de Uso: Buscar Acciones de Auditoría.
    
    Responsabilidad: Búsqueda avanzada de eventos de auditoría.
    """
    
    def __init__(self, repo: AuditoriaAccionesRepository):
        self.repo = repo
    
    async def por_descripcion(self, dto: BuscarPorDescripcionDTO) -> List[AuditoriaAccion]:
        """Busca acciones por texto en descripción."""
        models = await self.repo.buscar_por_descripcion(
            termino=dto.termino,
            sede_id=dto.sede_id,
            limit=dto.limit
        )
        return [AuditoriaAccion.model_validate(m) for m in models]
    
    async def por_endpoint(self, dto: BuscarPorEndpointDTO) -> List[AuditoriaAccion]:
        """Busca acciones por endpoint."""
        models = await self.repo.listar_por_endpoint(
            endpoint=dto.endpoint,
            metodo_http=dto.metodo_http,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaAccion.model_validate(m) for m in models]
    
    async def por_ip(self, dto: BuscarPorIPDTO) -> List[AuditoriaAccion]:
        """Busca acciones por dirección IP."""
        models = await self.repo.listar_por_ip(
            ip=dto.ip,
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit,
            offset=dto.offset
        )
        return [AuditoriaAccion.model_validate(m) for m in models]

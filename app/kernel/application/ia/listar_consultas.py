# app/kernel/application/ia/listar_consultas.py

from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.kernel.domain.ia import IAConsulta
from app.infrastructure.db.repositories.ia import IAConsultasRepository


class ListarConsultasPorUsuarioDTO(BaseModel):
    usuario_id: int = Field(..., gt=0)
    proveedor: Optional[str] = Field(None, max_length=50)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ListarConsultasPorProveedorDTO(BaseModel):
    proveedor: str = Field(..., min_length=1, max_length=50)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)


class ListarConsultasCU:
    """
    Caso de Uso: Listar consultas IA.
    """

    def __init__(self, repo: IAConsultasRepository):
        self.repo = repo

    async def por_usuario(self, dto: ListarConsultasPorUsuarioDTO) -> List[IAConsulta]:
        models = await self.repo.listar_por_usuario(
            usuario_id=dto.usuario_id,
            proveedor=dto.proveedor,
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit,
            offset=dto.offset,
        )
        return [IAConsulta.model_validate(m) for m in models]

    async def por_proveedor(self, dto: ListarConsultasPorProveedorDTO) -> List[IAConsulta]:
        models = await self.repo.listar_por_proveedor(
            proveedor=dto.proveedor,
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit,
        )
        return [IAConsulta.model_validate(m) for m in models]

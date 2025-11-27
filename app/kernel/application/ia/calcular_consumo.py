# app/kernel/application/ia/calcular_consumo_cu.py

from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.ia import IAConsultasRepository


class CalcularConsumoIADTO(BaseModel):
    usuario_id: Optional[int] = Field(None, gt=0)
    proveedor: Optional[str] = Field(None, max_length=50)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None


class CalcularConsumoIACU:
    """
    Caso de Uso: Calcular consumo IA (tokens y costo).
    """

    def __init__(self, repo: IAConsultasRepository):
        self.repo = repo

    async def ejecutar(self, dto: CalcularConsumoIADTO) -> Dict[str, Any]:
        return await self.repo.calcular_consumo(
            usuario_id=dto.usuario_id,
            proveedor=dto.proveedor,
            desde=dto.desde,
            hasta=dto.hasta,
        )

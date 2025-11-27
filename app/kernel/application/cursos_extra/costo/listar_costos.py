# app/kernel/application/cursosextra/costo/listar_costos.py

"""
Caso de Uso: Listar Costos
"""
from datetime import datetime
from typing import List, Optional

from app.kernel.domain.cursos_extra import (
    CostoCursoExtra,
    CostoCursoExtraRepositoryPort,
)


class ListarCostosDTO:
    """DTO de entrada para listar costos."""
    def __init__(
        self,
        curso_id: int,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limite: int = 100,
        offset: int = 0,
    ):
        self.curso_id = curso_id
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.limite = limite
        self.offset = offset


class ListarCostos:
    """
    Caso de Uso: Listar costos de un curso con filtros.
    """
    
    def __init__(self, costo_repo: CostoCursoExtraRepositoryPort):
        self.costo_repo = costo_repo
    
    async def execute(self, dto: ListarCostosDTO) -> List[CostoCursoExtra]:
        """Ejecuta el caso de uso."""
        
        return await self.costo_repo.listar_por_curso(
            curso_id=dto.curso_id,
            fecha_desde=dto.fecha_desde,
            fecha_hasta=dto.fecha_hasta,
            limite=dto.limite,
            offset=dto.offset,
        )

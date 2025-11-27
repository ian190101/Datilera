# app/kernel/application/cursosextra/pago/consultar_pagos_curso.py

"""
Caso de Uso: Consultar Pagos de un Curso
"""
from datetime import date
from decimal import Decimal
from typing import Optional, List

from app.kernel.domain.cursos_extra import (
    PagoCursoExtra,
    PagoCursoExtraRepositoryPort,
)


class ConsultarPagosCursoDTO:
    """DTO de entrada para consultar pagos de un curso."""
    def __init__(
        self,
        curso_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limite: int = 100,
        offset: int = 0,
    ):
        self.curso_id = curso_id
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.limite = limite
        self.offset = offset


class ConsultarPagosCurso:
    """
    Caso de Uso: Consultar pagos de un curso con filtros.
    """
    
    def __init__(self, pago_repo: PagoCursoExtraRepositoryPort):
        self.pago_repo = pago_repo
    
    async def listar(self, dto: ConsultarPagosCursoDTO) -> List[PagoCursoExtra]:
        """Lista pagos del curso."""
        return await self.pago_repo.listar_por_curso(
            curso_id=dto.curso_id,
            fecha_desde=dto.fecha_desde,
            fecha_hasta=dto.fecha_hasta,
            limite=dto.limite,
            offset=dto.offset,
        )
    
    async def calcular_total(self, dto: ConsultarPagosCursoDTO) -> Decimal:
        """Calcula el total de pagos del curso."""
        return await self.pago_repo.calcular_total_por_curso(
            curso_id=dto.curso_id,
            fecha_desde=dto.fecha_desde,
            fecha_hasta=dto.fecha_hasta,
        )

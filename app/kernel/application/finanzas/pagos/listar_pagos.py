# app/application/finanzas/pagos/listar_pagos.py
"""
CU: Listar pagos por sede, con filtros y paginación.
"""
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import List, Optional

from app.kernel.domain.finanzas import Pago, MetodoPago
from app.kernel.domain.finanzas.ports import PagoRepositoryPort, LibroCajaRepositoryPort


@dataclass
class ListarPagosQuery:
    sede_id: int
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    categoria_id: Optional[int] = None
    metodo: Optional[MetodoPago] = None
    limit: int = 50
    offset: int = 0


@dataclass
class PagoListadoDTO:
    pago: Pago
    anulado: bool


class ListarPagosUseCase:
    """
    Lista pagos y marca 'anulado' si existe un contramovimiento EGRESO en libro de caja con pago_id igual.
    Requiere que el repo de libro implemente un verificador por pago_id (p.ej. existe_egreso_por_pago(pago_id)).
    """

    def __init__(self, pago_repo: PagoRepositoryPort, libro_repo: LibroCajaRepositoryPort):
        self.pago_repo = pago_repo
        self.libro_repo = libro_repo

    async def execute(self, q: ListarPagosQuery) -> List[PagoListadoDTO]:
        pagos = await self.pago_repo.listar_por_sede_y_periodo(
            sede_id=q.sede_id,
            fecha_inicio=q.fecha_inicio,
            fecha_fin=q.fecha_fin
        )
        # filtros adicionales en memoria si el repo aún no los soporta
        if q.categoria_id is not None:
            pagos = [p for p in pagos if p.categoria_id == q.categoria_id]
        if q.metodo is not None:
            pagos = [p for p in pagos if p.metodo == q.metodo]
        pagos = pagos[q.offset:q.offset + q.limit]

        result: List[PagoListadoDTO] = []
        for p in pagos:
            # se considera anulado cuando existe un egreso en libro_caja con pago_id == p.id
            anulado = await self.libro_repo.existe_egreso_por_pago(p.id)
            result.append(PagoListadoDTO(pago=p, anulado=anulado))
        return result

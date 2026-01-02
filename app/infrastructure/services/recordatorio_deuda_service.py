# app/application/services/recordatorio_deuda_service.py
from __future__ import annotations

from datetime import date
from typing import List, AsyncGenerator

from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort
from app.kernel.domain.finanzas.ports import (
    IEstadoCuentaNinoRepository,
    IPagoRepository,
    IPlanCuotaRepository,
)


class RecordatorioDeudaService:
    """
    Servicio de aplicación: determina quiénes tienen deuda pendiente
    y envía recordatorios. Reutiliza lógica de negocio sin acoplarse a HTTP.
    """

    def __init__(
        self,
        alumno_repo: AlumnoRepositoryPort,
        estado_cuenta_repo: IEstadoCuentaNinoRepository,
        pago_repo: IPagoRepository,
        cuota_repo: IPlanCuotaRepository,
    ) -> None:
        self.alumno_repo = alumno_repo
        self.estado_cuenta_repo = estado_cuenta_repo
        self.pago_repo = pago_repo
        self.cuota_repo = cuota_repo

    async def obtener_alumnos_con_deuda_pendiente(
        self,
        sede_id: int,
        fecha_corte: date,
    ) -> AsyncGenerator[int, None]:
        """
        Genera IDs de alumnos con saldo_pendiente > 0 al fecha_corte.
        Optimizado para procesar miles sin cargar todo en memoria.
        """
        # Opción 1: si tienes un índice en estado_cuenta.saldo_pendiente
        alumnos = await self.estado_cuenta_repo.listar_deudores(
            sede_id=sede_id,
            fecha_corte=fecha_corte,
        )

        for alumno_id, saldo in alumnos:
            if saldo > 0:
                yield alumno_id

    
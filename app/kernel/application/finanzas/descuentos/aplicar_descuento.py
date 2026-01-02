# app/kernel/application/finanzas/descuentos/aplicar_descuento_cu.py

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.services.jobqueue_service import JobQueueService
from app.kernel.domain.finanzas.descuento_entidad import DescuentoEntidad
from app.kernel.domain.finanzas.ports import ICalculadorDescuento
from app.kernel.domain.finanzas.errors import (
    DescuentoYaAplicadoError,
    TipoDescuentoInvalidoError,
)


class AplicarDescuentoRequest(BaseModel):
    """Request para aplicar descuento"""
    alumno_id: int = Field(..., gt=0, description="ID del alumno")
    sede_id: int = Field(..., gt=0, description="ID de la sede")
    tipo: str = Field(..., pattern="^(semestral|anual)$", description="Tipo de descuento")
    monto_base: Decimal = Field(..., gt=0, description="Monto mensualidad base para calcular descuento")
    periodo_inicio: date = Field(..., description="Inicio del período del descuento")
    periodo_fin: date = Field(..., description="Fin del período del descuento")
    aplicado_por: int = Field(..., gt=0, description="ID del usuario que aplica")


class AplicarDescuentoResponse(BaseModel):
    """Response con descuento aplicado"""
    descuento_id: int
    alumno_id: int
    tipo: str
    porcentaje: Decimal
    monto_descuento: Decimal
    monto_con_descuento: Decimal
    periodo_inicio: date
    periodo_fin: date
    estado: str
    aplicado_en: datetime


class AplicarDescuentoCU:
    """
    Aplica un descuento (3% semestral o 6% anual) a un alumno.
    """

    def __init__(
        self,
        descuento_repo: ICalculadorDescuento,
        uow: UnitOfWork,
        jobs: JobQueueService,
    ) -> None:
        self.descuento_repo = descuento_repo
        self.uow = uow
        self.jobs = jobs

    async def ejecutar(self, request: AplicarDescuentoRequest) -> AplicarDescuentoResponse:
        """Ejecuta el caso de uso"""

        # 1. Validar tipo de descuento
        if request.tipo not in ["semestral", "anual"]:
            raise TipoDescuentoInvalidoError(request.tipo)

        # 2. Calcular porcentaje según tipo
        porcentaje = Decimal("3.00") if request.tipo == "semestral" else Decimal("6.00")

        # 3. Verificar que no exista descuento activo del mismo tipo
        existe = await self.descuento_repo.existe_descuento_activo(
            alumno_id=request.alumno_id,
            sede_id=request.sede_id,
            tipo=request.tipo,
        )

        if existe:
            raise DescuentoYaAplicadoError(request.alumno_id, request.tipo)

        # 4. Calcular monto del descuento
        monto_descuento = (
            request.monto_base * porcentaje / Decimal("100")
        ).quantize(Decimal("0.01"))

        # 5. Crear entidad de descuento
        descuento = DescuentoEntidad(
            alumno_id=request.alumno_id,
            sede_id=request.sede_id,
            tipo=request.tipo,
            porcentaje=porcentaje,
            monto_descuento=monto_descuento,
            periodo_inicio=request.periodo_inicio,
            periodo_fin=request.periodo_fin,
            estado="activo",
            aplicado_por=request.aplicado_por,
            aplicado_en=datetime.utcnow(),
        )

        # 6. Persistir
        descuento_creado = await self.descuento_repo.crear(descuento)

        # 7. Commit transaccional
        await self.uow.commit()

        # 8. Recalcular recordatorios de pago para este alumno/sede
        self.jobs.enqueue_recalcular_recordatorios_cuenta(
            alumno_id=request.alumno_id,
            sede_id=request.sede_id,
        )

        # 9. Calcular monto final con descuento
        monto_con_descuento = request.monto_base - monto_descuento

        # 10. Retornar respuesta
        return AplicarDescuentoResponse(
            descuento_id=descuento_creado.id,
            alumno_id=descuento_creado.alumno_id,
            tipo=descuento_creado.tipo,
            porcentaje=descuento_creado.porcentaje,
            monto_descuento=descuento_creado.monto_descuento,
            monto_con_descuento=monto_con_descuento,
            periodo_inicio=descuento_creado.periodo_inicio,
            periodo_fin=descuento_creado.periodo_fin,
            estado=descuento_creado.estado,
            aplicado_en=descuento_creado.aplicado_en,
        )

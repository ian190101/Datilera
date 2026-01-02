# app/kernel/application/finanzas/planes_pago/crear_plan_pago.py

"""
Caso de Uso: Crear Plan de Pago Personalizado
HU: Planes para material/merienda (3400 Bs anuales)
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field

from app.infrastructure.services.jobqueue_service import JobQueueService
from app.infrastructure.db.uow import UnitOfWork  # ajusta ruta si difiere
from app.kernel.domain.finanzas.plan_pago_entidad import PlanPagoEntidad
from app.kernel.domain.finanzas.cuota_plan_pago_entidad import CuotaPlanPagoEntidad
from app.kernel.domain.finanzas.ports import (
    IPlanCuotaRepository,
    ICuotaPlanPagoRepository,
)
from app.kernel.domain.finanzas.errors import (
    PlanPagoYaExisteError,
    CuotaNoEncontradaError,
    MontoTotalInvalidoError,
)


# ==========================================
# DTOs
# ==========================================

class CrearPlanPagoRequest(BaseModel):
    """Request para crear plan de pago"""
    alumno_id: int = Field(..., gt=0)
    sede_id: int = Field(..., gt=0)
    tipo: str = Field(..., pattern="^(material|merienda|material_merienda)$")
    monto_total: Decimal = Field(..., gt=0, description="Monto total del plan")

    # Opciones de pago
    cuota_inicial: Optional[Decimal] = Field(
        None, ge=0, description="Cuota inicial (40% o 1000 Bs)"
    )
    cantidad_cuotas: int = Field(
        ..., ge=1, le=12, description="Número de cuotas mensuales"
    )

    # Fechas
    fecha_inicio: date = Field(default_factory=date.today)

    # Auditoría
    creado_por: int = Field(..., gt=0)


class CuotaResponse(BaseModel):
    """Cuota individual en el plan"""
    numero_cuota: int
    monto_cuota: Decimal
    fecha_vencimiento: date
    estado: str


class CrearPlanPagoResponse(BaseModel):
    """Response con plan creado"""
    plan_id: int
    alumno_id: int
    tipo: str
    monto_total: Decimal
    cuota_inicial: Decimal
    saldo_financiar: Decimal
    cantidad_cuotas: int
    monto_cuota: Decimal
    fecha_inicio: date
    fecha_fin: date
    cuotas: List[CuotaResponse]


# ==========================================
# Caso de Uso
# ==========================================

class CrearPlanPagoCU:
    """
    Crea un plan de pago personalizado para material/merienda.

    Reglas:
    - Monto total: 3400 Bs (configurable).
    - Cuota inicial: 40% o 1000 Bs (opcional).
    - Cuotas: 1 a 12 meses.
    - Vencimiento: día 10 de cada mes.
    - Redondeo boliviano en cuotas.
    """

    def __init__(
        self,
        plan_repo: IPlanCuotaRepository,
        cuota_repo: ICuotaPlanPagoRepository,
        uow: UnitOfWork,
        jobs: JobQueueService,
    ) -> None:
        self.plan_repo = plan_repo
        self.cuota_repo = cuota_repo
        self.uow = uow
        self.jobs = jobs

    async def ejecutar(self, request: CrearPlanPagoRequest) -> CrearPlanPagoResponse:
        """Ejecuta el caso de uso"""

        # 1. Verificar que no exista plan activo del mismo tipo
        existe = await self.plan_repo.existe_plan_activo(
            alumno_id=request.alumno_id,
            sede_id=request.sede_id,
            tipo=request.tipo,
        )

        if existe:
            raise PlanPagoYaExisteError(request.alumno_id, request.tipo)

        # 2. Validar cuota inicial
        cuota_inicial = request.cuota_inicial or Decimal("0.00")

        if cuota_inicial > request.monto_total:
            raise MontoTotalInvalidoError(
                "La cuota inicial no puede exceder el monto total"
            )

        # 3. Calcular saldo a financiar
        saldo_financiar = request.monto_total - cuota_inicial

        # 4. Calcular monto de cuota mensual
        if request.cantidad_cuotas < 1 or request.cantidad_cuotas > 12:
            raise CuotaNoEncontradaError(request.cantidad_cuotas, 1, 12)

        monto_cuota_base = saldo_financiar / Decimal(request.cantidad_cuotas)
        monto_cuota = self._redondear_boliviano(monto_cuota_base)

        # 5. Calcular fecha de fin (aproximación por meses)
        fecha_fin = request.fecha_inicio + timedelta(days=30 * request.cantidad_cuotas)

        # 6. Crear entidad de plan
        plan = PlanPagoEntidad(
            alumno_id=request.alumno_id,
            sede_id=request.sede_id,
            tipo=request.tipo,
            monto_total=request.monto_total,
            cuota_inicial=cuota_inicial,
            saldo_financiar=saldo_financiar,
            cantidad_cuotas=request.cantidad_cuotas,
            monto_cuota=monto_cuota,
            fecha_inicio=request.fecha_inicio,
            fecha_fin=fecha_fin,
            estado="activo",
            creado_por=request.creado_por,
        )

        # 7. Persistir plan
        plan_creado = await self.plan_repo.crear(plan)

        # 8. Generar cuotas
        cuotas: list[CuotaPlanPagoEntidad] = []

        # Tomamos el día 10 del mes de fecha_inicio como primer vencimiento lógico
        base = request.fecha_inicio.replace(day=10)

        for i in range(1, request.cantidad_cuotas + 1):
            mes = base.month + (i - 1)
            anio = base.year

            while mes > 12:
                mes -= 12
                anio += 1

            fecha_venc_cuota = date(anio, mes, 10)

            cuota = CuotaPlanPagoEntidad(
                plan_id=plan_creado.id,
                numero_cuota=i,
                monto_cuota=monto_cuota,
                fecha_vencimiento=fecha_venc_cuota,
                estado="pendiente",
            )
            cuotas.append(cuota)

        # 9. Persistir cuotas en lote
        cuotas_creadas = await self.cuota_repo.crear_lote(cuotas)

        # 10. Commit transaccional
        await self.uow.commit()

        # 11. Disparar recalculo de recordatorios para este alumno/sede
        # Job idempotente: revisa el estado de la cuenta y ajusta la agenda
        self.jobs.enqueue_recalcular_recordatorios_cuenta(
            alumno_id=plan_creado.alumno_id,
            sede_id=plan_creado.sede_id,
        )

        # 12. Construir respuesta
        cuotas_response = [
            CuotaResponse(
                numero_cuota=c.numero_cuota,
                monto_cuota=c.monto_cuota,
                fecha_vencimiento=c.fecha_vencimiento,
                estado=c.estado,
            )
            for c in cuotas_creadas
        ]

        return CrearPlanPagoResponse(
            plan_id=plan_creado.id,
            alumno_id=plan_creado.alumno_id,
            tipo=plan_creado.tipo,
            monto_total=plan_creado.monto_total,
            cuota_inicial=plan_creado.cuota_inicial,
            saldo_financiar=plan_creado.saldo_financiar,
            cantidad_cuotas=plan_creado.cantidad_cuotas,
            monto_cuota=plan_creado.monto_cuota,
            fecha_inicio=plan_creado.fecha_inicio,
            fecha_fin=plan_creado.fecha_fin,
            cuotas=cuotas_response,
        )

    def _redondear_boliviano(self, monto: Decimal) -> Decimal:
        """Redondeo boliviano (0, 0.50 o entero siguiente)"""
        parte_entera = int(monto)
        decimales = monto - Decimal(parte_entera)

        if decimales == Decimal("0.00"):
            return monto
        elif decimales <= Decimal("0.49"):
            return Decimal(parte_entera) + Decimal("0.50")
        elif decimales == Decimal("0.50"):
            return monto
        else:
            return Decimal(parte_entera + 1)

# app/kernel/application/finanzas/planes_pago/obtener_plan_pago_alumno_cu.py

"""
Caso de Uso: Obtener Plan de Pago de un Alumno
"""

from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field

from app.kernel.domain.finanzas.ports import (
    IPlanCuotaRepository,
    ICuotaPlanPagoRepository,
)
from app.kernel.domain.finanzas.errors import PlanPagoNoEncontradoError


# ==========================================
# DTOs
# ==========================================

class ObtenerPlanPagoRequest(BaseModel):
    """Request para obtener plan"""
    alumno_id: int = Field(..., gt=0)
    sede_id: int = Field(..., gt=0)


class CuotaDetalleResponse(BaseModel):
    """Detalle de cuota"""
    cuota_id: int
    numero_cuota: int
    monto_cuota: Decimal
    monto_pagado: Decimal
    mora: Decimal
    saldo: Decimal
    fecha_vencimiento: str
    fecha_pago: Optional[str] = None
    estado: str
    esta_vencida: bool


class ObtenerPlanPagoResponse(BaseModel):
    """Response con plan y cuotas"""
    plan_id: int
    alumno_id: int
    tipo: str
    monto_total: Decimal
    cuota_inicial: Decimal
    saldo_financiar: Decimal
    cantidad_cuotas: int
    monto_cuota: Decimal
    monto_pagado_total: Decimal
    saldo_pendiente: Decimal
    cuotas_pagadas: int
    cuotas_pendientes: int
    estado: str
    cuotas: List[CuotaDetalleResponse]


# ==========================================
# Caso de Uso
# ==========================================

class ObtenerPlanPagoAlumnoCU:
    """
    Obtiene el plan de pago activo de un alumno con el detalle de cuotas.
    """
    
    def __init__(
        self,
        plan_repo: IPlanCuotaRepository,
        cuota_repo: ICuotaPlanPagoRepository
    ):
        self.plan_repo = plan_repo
        self.cuota_repo = cuota_repo
    
    async def ejecutar(self, request: ObtenerPlanPagoRequest) -> ObtenerPlanPagoResponse:
        """Ejecuta el caso de uso"""
        
        # 1. Obtener plan activo del alumno
        plan = await self.plan_repo.obtener_por_alumno(
            alumno_id=request.alumno_id,
            sede_id=request.sede_id,
            solo_activo=True
        )
        
        if not plan:
            raise PlanPagoNoEncontradoError(0)
        
        # 2. Obtener todas las cuotas del plan
        cuotas = await self.cuota_repo.listar_por_plan(plan.id)
        
        # 3. Calcular totales
        monto_pagado_total = sum(c.monto_pagado for c in cuotas)
        saldo_pendiente = plan.monto_total - plan.cuota_inicial - monto_pagado_total
        
        cuotas_pagadas = sum(1 for c in cuotas if c.estado == 'pagada')
        cuotas_pendientes = len(cuotas) - cuotas_pagadas
        
        # 4. Construir detalle de cuotas
        cuotas_response = [
            CuotaDetalleResponse(
                cuota_id=c.id,
                numero_cuota=c.numero_cuota,
                monto_cuota=c.monto_cuota,
                monto_pagado=c.monto_pagado,
                mora=c.mora,
                saldo=c.calcular_saldo(),
                fecha_vencimiento=c.fecha_vencimiento.isoformat(),
                fecha_pago=c.fecha_pago.isoformat() if c.fecha_pago else None,
                estado=c.estado,
                esta_vencida=c.esta_vencida()
            )
            for c in cuotas
        ]
        
        # 5. Retornar respuesta
        return ObtenerPlanPagoResponse(
            plan_id=plan.id,
            alumno_id=plan.alumno_id,
            tipo=plan.tipo,
            monto_total=plan.monto_total,
            cuota_inicial=plan.cuota_inicial,
            saldo_financiar=plan.saldo_financiar,
            cantidad_cuotas=plan.cantidad_cuotas,
            monto_cuota=plan.monto_cuota,
            monto_pagado_total=monto_pagado_total,
            saldo_pendiente=saldo_pendiente,
            cuotas_pagadas=cuotas_pagadas,
            cuotas_pendientes=cuotas_pendientes,
            estado=plan.estado,
            cuotas=cuotas_response
        )

# app/kernel/application/finanzas/planes_pago/obtener_tabla_amortizacion_cu.py

"""
Caso de Uso: Obtener Tabla de Amortización
Genera tabla detallada de amortización del plan.
"""

from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from app.kernel.domain.finanzas.ports import (
    IPlanCuotaRepository,
    ICuotaPlanPagoRepository
)

from app.kernel.domain.finanzas.errors import PlanPagoNoEncontradoError


# ==========================================
# DTOs
# ==========================================

class ObtenerTablaAmortizacionRequest(BaseModel):
    """Request para obtener tabla"""
    plan_id: int = Field(..., gt=0)


class FilaAmortizacion(BaseModel):
    """Fila de la tabla de amortización"""
    numero_cuota: int
    fecha_vencimiento: str
    monto_cuota: Decimal
    monto_pagado: Decimal
    mora: Decimal
    saldo_cuota: Decimal
    saldo_plan_acumulado: Decimal
    estado: str


class ObtenerTablaAmortizacionResponse(BaseModel):
    """Response con tabla completa"""
    plan_id: int
    monto_total: Decimal
    cuota_inicial: Decimal
    saldo_inicial: Decimal
    tabla: List[FilaAmortizacion]


# ==========================================
# Caso de Uso
# ==========================================

class ObtenerTablaAmortizacionCU:
    """
    Genera tabla de amortización detallada.
    """
    
    def __init__(
        self,
        plan_repo: IPlanCuotaRepository,
        cuota_repo: ICuotaPlanPagoRepository
    ):
        self.plan_repo = plan_repo
        self.cuota_repo = cuota_repo
    
    async def ejecutar(self, request: ObtenerTablaAmortizacionRequest) -> ObtenerTablaAmortizacionResponse:
        """Ejecuta el caso de uso"""
        
        # 1. Obtener plan
        plan = await self.plan_repo.obtener_por_id(request.plan_id)
        if not plan:
            raise PlanPagoNoEncontradoError(request.plan_id)
        
        # 2. Obtener cuotas ordenadas
        cuotas = await self.cuota_repo.listar_por_plan(request.plan_id)
        cuotas_ordenadas = sorted(cuotas, key=lambda c: c.numero_cuota)
        
        # 3. Construir tabla
        tabla = []
        saldo_acumulado = plan.saldo_financiar
        
        for cuota in cuotas_ordenadas:
            saldo_cuota = cuota.calcular_saldo()
            saldo_acumulado -= cuota.monto_pagado
            
            fila = FilaAmortizacion(
                numero_cuota=cuota.numero_cuota,
                fecha_vencimiento=cuota.fecha_vencimiento.isoformat(),
                monto_cuota=cuota.monto_cuota,
                monto_pagado=cuota.monto_pagado,
                mora=cuota.mora,
                saldo_cuota=saldo_cuota,
                saldo_plan_acumulado=saldo_acumulado,
                estado=cuota.estado
            )
            tabla.append(fila)
        
        # 4. Retornar respuesta
        return ObtenerTablaAmortizacionResponse(
            plan_id=plan.id,
            monto_total=plan.monto_total,
            cuota_inicial=plan.cuota_inicial,
            saldo_inicial=plan.saldo_financiar,
            tabla=tabla
        )

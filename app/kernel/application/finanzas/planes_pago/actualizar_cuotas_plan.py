# app/kernel/application/finanzas/planes_pago/actualizar_cuotas_plan_cu.py

"""
Caso de Uso: Actualizar Cuotas de Plan de Pago
Permite modificar cuotas (adelantar pagos, modificar montos).
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.kernel.domain.finanzas.ports import (
    IPlanCuotaRepository,
    ICuotaPlanPagoRepository
)
from app.kernel.domain.finanzas.errors import (
    PlanPagoNoEncontradoError,
    CuotaNoEncontradaError,
    CuotaYaPagadaError
)


# ==========================================
# DTOs
# ==========================================

class ActualizarCuotaItem(BaseModel):
    """Item de cuota a actualizar"""
    cuota_id: int
    nuevo_monto: Optional[Decimal] = None
    nueva_fecha_vencimiento: Optional[date] = None


class ActualizarCuotasPlanRequest(BaseModel):
    """Request para actualizar cuotas"""
    plan_id: int = Field(..., gt=0)
    cuotas: List[ActualizarCuotaItem]
    actualizado_por: int = Field(..., gt=0)


class ActualizarCuotasPlanResponse(BaseModel):
    """Response con cuotas actualizadas"""
    plan_id: int
    cuotas_actualizadas: int
    mensaje: str


# ==========================================
# Caso de Uso
# ==========================================

class ActualizarCuotasPlanCU:
    """
    Actualiza cuotas de un plan de pago.
    
    Reglas:
    - No se pueden modificar cuotas pagadas.
    - Solo se pueden modificar montos y fechas de vencimiento.
    """
    
    def __init__(
        self,
        plan_repo: IPlanCuotaRepository,
        cuota_repo: ICuotaPlanPagoRepository
    ):
        self.plan_repo = plan_repo
        self.cuota_repo = cuota_repo
    
    async def ejecutar(self, request: ActualizarCuotasPlanRequest) -> ActualizarCuotasPlanResponse:
        """Ejecuta el caso de uso"""
        
        # 1. Verificar que el plan exista
        plan = await self.plan_repo.obtener_por_id(request.plan_id)
        if not plan:
            raise  PlanPagoNoEncontradoError(request.plan_id)
        
        # 2. Actualizar cada cuota
        contador = 0
        
        for item in request.cuotas:
            # Obtener cuota
            cuota = await self.cuota_repo.obtener_por_id(item.cuota_id)
            
            if not cuota:
                raise CuotaNoEncontradaError(item.cuota_id)
            
            # Validar que no esté pagada
            if cuota.estado == 'pagada':
                raise CuotaYaPagadaError(item.cuota_id)
            
            # Aplicar cambios
            if item.nuevo_monto is not None:
                cuota.monto_cuota = item.nuevo_monto
            
            if item.nueva_fecha_vencimiento is not None:
                cuota.fecha_vencimiento = item.nueva_fecha_vencimiento
            
            # Persistir
            await self.cuota_repo.actualizar(cuota)
            contador += 1
        
        # 3. Retornar respuesta
        return ActualizarCuotasPlanResponse(
            plan_id=request.plan_id,
            cuotas_actualizadas=contador,
            mensaje=f"Se actualizaron {contador} cuotas correctamente"
        )

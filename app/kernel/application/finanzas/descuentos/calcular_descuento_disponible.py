# app/kernel/application/finanzas/descuentos/calcular_descuento_disponible_cu.py

"""
Caso de Uso: Calcular Descuento Disponible
Consulta el descuento vigente de un alumno y calcula el monto con descuento.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.kernel.domain.finanzas.ports import ICalculadorDescuento


# ==========================================
# DTOs
# ==========================================

class CalcularDescuentoRequest(BaseModel):
    """Request para calcular descuento"""
    alumno_id: int = Field(..., gt=0, description="ID del alumno")
    sede_id: int = Field(..., gt=0, description="ID de la sede")
    monto_base: Decimal = Field(..., gt=0, description="Monto base a aplicar descuento")
    fecha: Optional[date] = None


class CalcularDescuentoResponse(BaseModel):
    """Response con cálculo de descuento"""
    tiene_descuento: bool
    tipo: Optional[str] = None
    porcentaje: Optional[Decimal] = None
    monto_descuento: Decimal = Field(default=Decimal('0.00'))
    monto_original: Decimal
    monto_con_descuento: Decimal
    vigente_desde: Optional[date] = None
    vigente_hasta: Optional[date] = None


# ==========================================
# Caso de Uso
# ==========================================

class CalcularDescuentoDisponibleCU:
    """
    Calcula el descuento disponible para un alumno en una fecha.
    
    Reglas:
    - Busca descuento activo y vigente.
    - Si no hay, retorna monto sin descuento.
    - Si hay, calcula y retorna monto con descuento.
    """
    
    def __init__(self, descuento_repo: ICalculadorDescuento):
        self.descuento_repo = descuento_repo
    
    async def ejecutar(self, request: CalcularDescuentoRequest) -> CalcularDescuentoResponse:
        """Ejecuta el caso de uso"""
        
        # 1. Obtener descuento vigente
        fecha_calculo = request.fecha or date.today()
        
        descuento = await self.descuento_repo.obtener_descuento_vigente(
            alumno_id=request.alumno_id,
            sede_id=request.sede_id,
            fecha=fecha_calculo
        )
        
        # 2. Si no hay descuento, retornar sin descuento
        if not descuento or not descuento.esta_vigente(fecha_calculo):
            return CalcularDescuentoResponse(
                tiene_descuento=False,
                monto_original=request.monto_base,
                monto_con_descuento=request.monto_base
            )
        
        # 3. Calcular monto con descuento
        monto_descuento = descuento.calcular_monto_descuento(request.monto_base)
        monto_con_descuento = request.monto_base - monto_descuento
        
        # 4. Retornar con descuento
        return CalcularDescuentoResponse(
            tiene_descuento=True,
            tipo=descuento.tipo,
            porcentaje=descuento.porcentaje,
            monto_descuento=monto_descuento,
            monto_original=request.monto_base,
            monto_con_descuento=monto_con_descuento,
            vigente_desde=descuento.periodo_inicio,
            vigente_hasta=descuento.periodo_fin
        )

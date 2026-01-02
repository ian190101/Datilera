# app/kernel/application/finanzas/prorrateo/calcular_prorrateo_cu.py

"""
Caso de Uso: Calcular Prorrateo Primer Mes
HU: Prorrateo basado en 20 días hábiles con regla de 3 días.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
import calendar

from pydantic import BaseModel, Field

from app.kernel.domain.finanzas.prorrateo_entidad import ProrrateoEntidad
from app.kernel.domain.finanzas.ports import ICalculadorProrrateo
from app.kernel.domain.finanzas.errors import (
    FechaInicioInvalidaError,
    ProrrateoError
)


# ==========================================
# DTOs
# ==========================================

class CalcularProrrateoRequest(BaseModel):
    """Request para calcular prorrateo"""
    alumno_id: int = Field(..., gt=0)
    sede_id: int = Field(..., gt=0)
    fecha_ingreso: date = Field(..., description="Fecha de primera asistencia")
    monto_mensual: Decimal = Field(..., gt=0, description="Monto mensual según turno")
    creado_por: Optional[int] = None


class CalcularProrrateoResponse(BaseModel):
    """Response con cálculo de prorrateo"""
    prorrateo_id: int
    alumno_id: int
    fecha_ingreso: date
    dias_cursados: int
    dias_mes: int
    monto_completo: Decimal
    monto_prorrateo: Decimal
    porcentaje_prorrateo: Decimal
    aplicado: bool
    se_difiere_siguiente_mes: bool
    mensaje: str


# ==========================================
# Caso de Uso
# ==========================================

class CalcularProrrateoCU:
    """
    Calcula el prorrateo del primer mes según fecha de ingreso.
    
    Reglas de negocio:
    - Si faltan 3 días o menos para fin de mes → cobrar desde el 1 del siguiente.
    - Cálculo: (monto_mensual / días_mes) * días_cursados.
    - Redondeo especial boliviano: 
    - ≤49¢ → 50¢
    - ≥51¢ → 1Bs
    - =50¢ → 50¢
    """
    
    def __init__(self, prorrateo_repo: ICalculadorProrrateo):
        self.prorrateo_repo = prorrateo_repo
    
    async def ejecutar(self, request: CalcularProrrateoRequest) -> CalcularProrrateoResponse:
        """Ejecuta el caso de uso"""
        
        # 1. Validar fecha de ingreso
        if request.fecha_ingreso > date.today():
            raise FechaInicioInvalidaError(
                request.fecha_ingreso.isoformat(),
                "La fecha de ingreso no puede ser futura"
            )
        
        # 2. Calcular días del mes
        _, dias_mes = calendar.monthrange(
            request.fecha_ingreso.year,
            request.fecha_ingreso.month
        )
        
        # 3. Calcular días restantes del mes
        dias_restantes = dias_mes - request.fecha_ingreso.day + 1
        
        # 4. Regla de 3 días: si quedan 3 o menos, diferir al siguiente mes
        if dias_restantes <= 3:
            # Crear registro indicando diferimiento
            prorrateo = ProrrateoEntidad(
                alumno_id=request.alumno_id,
                sede_id=request.sede_id,
                fecha_ingreso=request.fecha_ingreso,
                dias_cursados=0,
                dias_mes=dias_mes,
                monto_completo=request.monto_mensual,
                monto_prorrateo=Decimal('0.00'),
                aplicado=False,
                creado_por=request.creado_por
            )
            
            prorrateo_creado = await self.prorrateo_repo.crear(prorrateo)
            
            return CalcularProrrateoResponse(
                prorrateo_id=prorrateo_creado.id,
                alumno_id=prorrateo_creado.alumno_id,
                fecha_ingreso=prorrateo_creado.fecha_ingreso,
                dias_cursados=0,
                dias_mes=dias_mes,
                monto_completo=request.monto_mensual,
                monto_prorrateo=Decimal('0.00'),
                porcentaje_prorrateo=Decimal('0.00'),
                aplicado=False,
                se_difiere_siguiente_mes=True,
                mensaje=f"Quedan {dias_restantes} días. Se cobrará monto completo el siguiente mes."
            )
        
        # 5. Calcular prorrateo normal
        dias_cursados = dias_restantes
        
        # Cálculo base
        monto_calculado = (request.monto_mensual * Decimal(dias_cursados)) / Decimal(dias_mes)
        
        # 6. Aplicar redondeo boliviano
        monto_prorrateo = self._redondear_boliviano(monto_calculado)
        
        # 7. Crear entidad usando factory
        prorrateo = ProrrateoEntidad.calcular_prorrateo(
            alumno_id=request.alumno_id,
            fecha_ingreso=request.fecha_ingreso,
            monto_mensual=request.monto_mensual,
            sede_id=request.sede_id,
            creado_por=request.creado_por
        )
        
        # Sobrescribir con redondeo boliviano
        prorrateo.monto_prorrateo = monto_prorrateo
        
        # 8. Persistir
        prorrateo_creado = await self.prorrateo_repo.crear(prorrateo)
        
        # 9. Retornar respuesta
        return CalcularProrrateoResponse(
            prorrateo_id=prorrateo_creado.id,
            alumno_id=prorrateo_creado.alumno_id,
            fecha_ingreso=prorrateo_creado.fecha_ingreso,
            dias_cursados=prorrateo_creado.dias_cursados,
            dias_mes=prorrateo_creado.dias_mes,
            monto_completo=prorrateo_creado.monto_completo,
            monto_prorrateo=prorrateo_creado.monto_prorrateo,
            porcentaje_prorrateo=prorrateo_creado.calcular_porcentaje_prorrateo(),
            aplicado=prorrateo_creado.aplicado,
            se_difiere_siguiente_mes=False,
            mensaje=f"Prorrateo calculado: {dias_cursados} días de {dias_mes}"
        )
    
    def _redondear_boliviano(self, monto: Decimal) -> Decimal:
        """
        Redondeo especial boliviano (solo 50 centavos):
        - ≤0.49 → 0.50
        - =0.50 → 0.50
        - ≥0.51 → 1.00
        """
        parte_entera = int(monto)
        decimales = monto - Decimal(parte_entera)
        
        if decimales == Decimal('0.00'):
            return monto
        elif decimales <= Decimal('0.49'):
            return Decimal(parte_entera) + Decimal('0.50')
        elif decimales == Decimal('0.50'):
            return monto
        else:  # > 0.51
            return Decimal(parte_entera + 1)

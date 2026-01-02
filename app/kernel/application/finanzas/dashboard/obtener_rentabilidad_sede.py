"""
Caso de Uso: Obtener Rentabilidad por Sede
Endpoint: GET /api/v1/reportes/rentabilidad-sede
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Calcula rentabilidad = ingresos - egresos
2. Incluye margen de rentabilidad (%)
3. Comparativa con meses anteriores
4. Proyección de rentabilidad mensual
"""

from decimal import Decimal
from datetime import date
from typing import List, Dict, Any
from dateutil.relativedelta import relativedelta

from app.kernel.domain.finanzas.ports import (
    IPagoRepository,
    IEgresoRepository,
)


class RentabilidadMesDTO:
    """DTO para rentabilidad de un mes"""
    
    def __init__(
        self,
        mes: str,
        total_ingresos: Decimal,
        total_egresos: Decimal,
        rentabilidad_neta: Decimal,
        margen_rentabilidad: Decimal,  # Porcentaje
    ) -> None:
        self.mes = mes
        self.total_ingresos = total_ingresos
        self.total_egresos = total_egresos
        self.rentabilidad_neta = rentabilidad_neta
        self.margen_rentabilidad = margen_rentabilidad


class RentabilidadSedeDTO:
    """DTO de respuesta"""
    
    def __init__(
        self,
        sede_id: int,
        meses: List[RentabilidadMesDTO],
        rentabilidad_promedio_mensual: Decimal,
        margen_promedio: Decimal,
        proyeccion_anual: Decimal,
    ) -> None:
        self.sede_id = sede_id
        self.meses = meses
        self.rentabilidad_promedio_mensual = rentabilidad_promedio_mensual
        self.margen_promedio = margen_promedio
        self.proyeccion_anual = proyeccion_anual


class ObtenerRentabilidadSedeCU:
    """Caso de Uso: Obtener rentabilidad de sede"""
    
    def __init__(
        self,
        pago_repo: IPagoRepository,
        egreso_repo: IEgresoRepository,
    ) -> None:
        self.pago_repo = pago_repo
        self.egreso_repo = egreso_repo
    
    async def execute(
        self,
        sede_id: int,
        meses_atras: int = 6,
    ) -> RentabilidadSedeDTO:
        """
        Obtiene rentabilidad de una sede
        
        Args:
            sede_id: ID de la sede
            meses_atras: Cantidad de meses a evaluar (default: 6)
        
        Returns:
            RentabilidadSedeDTO con análisis de rentabilidad
        """
        hoy: date = date.today()
        meses_data: List[RentabilidadMesDTO] = []
        
        # Nombres de meses
        nombres_meses: List[str] = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        total_rentabilidad: Decimal = Decimal("0")
        total_margenes: Decimal = Decimal("0")
        meses_contados: int = 0
        
        for i in range(meses_atras - 1, -1, -1):
            mes_fecha: date = hoy - relativedelta(months=i)
            
            # Rango del mes
            fecha_inicio: date = date(mes_fecha.year, mes_fecha.month, 1)
            if mes_fecha.month == 12:
                fecha_fin: date = date(mes_fecha.year + 1, 1, 1)
            else:
                fecha_fin: date = date(mes_fecha.year, mes_fecha.month + 1, 1)
            
            # Ingresos del mes
            pagos: List[Dict[str, Any]] = await self.pago_repo.listar(
                sede_id=sede_id,
                fecha_desde=fecha_inicio,
                fecha_hasta=fecha_fin,
                incluir_anulados=False,
                limit=10000
            )
            ingresos_mes: Decimal = sum(
                (Decimal(str(p.get("monto_pagado", 0))) for p in pagos),
                Decimal("0")
            )
            
            # Egresos del mes
            egresos: List[Dict[str, Any]] = await self.egreso_repo.listar(
                sede_id=sede_id,
                fecha_desde=fecha_inicio,
                fecha_hasta=fecha_fin,
                incluir_anulados=False,
                limit=10000
            )
            egresos_mes: Decimal = sum(
                (Decimal(str(e.get("monto", 0))) for e in egresos),
                Decimal("0")
            )
            
            # Rentabilidad neta
            rentabilidad: Decimal = ingresos_mes - egresos_mes
            
            # Margen de rentabilidad (%)
            margen: Decimal = (
                (rentabilidad / ingresos_mes * 100)
                if ingresos_mes > 0 else Decimal("0")
            )
            
            nombre_mes: str = f"{nombres_meses[mes_fecha.month - 1]} {mes_fecha.year}"
            
            meses_data.append(
                RentabilidadMesDTO(
                    mes=nombre_mes,
                    total_ingresos=ingresos_mes,
                    total_egresos=egresos_mes,
                    rentabilidad_neta=rentabilidad,
                    margen_rentabilidad=margen,
                )
            )
            
            total_rentabilidad += rentabilidad
            total_margenes += margen
            meses_contados += 1
        
        # Calcular promedios
        rentabilidad_promedio: Decimal = (
            total_rentabilidad / meses_contados
            if meses_contados > 0 else Decimal("0")
        )
        
        margen_promedio: Decimal = (
            total_margenes / meses_contados
            if meses_contados > 0 else Decimal("0")
        )
        
        # Proyección anual (promedio mensual * 12)
        proyeccion_anual: Decimal = rentabilidad_promedio * 12
        
        return RentabilidadSedeDTO(
            sede_id=sede_id,
            meses=meses_data,
            rentabilidad_promedio_mensual=rentabilidad_promedio,
            margen_promedio=margen_promedio,
            proyeccion_anual=proyeccion_anual,
        )

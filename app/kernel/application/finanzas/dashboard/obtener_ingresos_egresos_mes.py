"""
Caso de Uso: Obtener Reporte Ingresos vs Egresos por Mes
Endpoint: GET /api/v1/reportes/ingresos-egresos-mes
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Compara ingresos vs egresos por mes (últimos 12 meses)
2. Incluye saldo neto (ingresos - egresos)
3. Formato: {mes: "Enero 2025", ingresos: 50000, egresos: 30000, saldo: 20000}
"""

from decimal import Decimal
from datetime import date
from typing import List, Dict, Any
from dateutil.relativedelta import relativedelta

from app.kernel.domain.finanzas.ports import IPagoRepository, IEgresoRepository


class IngresosEgresosItemDTO:
    """DTO para un mes en el reporte"""
    
    def __init__(
        self,
        mes: str,
        total_ingresos: Decimal,
        total_egresos: Decimal,
        saldo_neto: Decimal,
    ) -> None:
        self.mes = mes
        self.total_ingresos = total_ingresos
        self.total_egresos = total_egresos
        self.saldo_neto = saldo_neto


class IngresosEgresosMesDTO:
    """DTO de respuesta"""
    
    def __init__(
        self,
        sede_id: int,
        meses: List[IngresosEgresosItemDTO],
        total_ingresos_periodo: Decimal,
        total_egresos_periodo: Decimal,
        saldo_neto_periodo: Decimal,
    ) -> None:
        self.sede_id = sede_id
        self.meses = meses
        self.total_ingresos_periodo = total_ingresos_periodo
        self.total_egresos_periodo = total_egresos_periodo
        self.saldo_neto_periodo = saldo_neto_periodo


class ObtenerIngresosEgresosMesCU:
    """Caso de Uso: Obtener ingresos vs egresos por mes"""
    
    def __init__(
        self,
        pago_repo: IPagoRepository,
        egreso_repo: IEgresoRepository,
    ) -> None:
        self.pago_repo = pago_repo
        self.egreso_repo = egreso_repo
    
    async def execute(self, sede_id: int, meses_atras: int = 12) -> IngresosEgresosMesDTO:
        """
        Obtiene ingresos vs egresos por mes
        
        Args:
            sede_id: ID de la sede
            meses_atras: Cantidad de meses a consultar (default: 12)
        
        Returns:
            IngresosEgresosMesDTO con comparativa mensual
        """
        hoy: date = date.today()
        meses_data: List[IngresosEgresosItemDTO] = []
        total_ingresos_acum: Decimal = Decimal("0")
        total_egresos_acum: Decimal = Decimal("0")
        
        # Nombres de meses
        nombres_meses: List[str] = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
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
            
            # Saldo neto
            saldo_neto: Decimal = ingresos_mes - egresos_mes
            
            nombre_mes: str = f"{nombres_meses[mes_fecha.month - 1]} {mes_fecha.year}"
            
            meses_data.append(
                IngresosEgresosItemDTO(
                    mes=nombre_mes,
                    total_ingresos=ingresos_mes,
                    total_egresos=egresos_mes,
                    saldo_neto=saldo_neto,
                )
            )
            
            total_ingresos_acum += ingresos_mes
            total_egresos_acum += egresos_mes
        
        return IngresosEgresosMesDTO(
            sede_id=sede_id,
            meses=meses_data,
            total_ingresos_periodo=total_ingresos_acum,
            total_egresos_periodo=total_egresos_acum,
            saldo_neto_periodo=total_ingresos_acum - total_egresos_acum,
        )

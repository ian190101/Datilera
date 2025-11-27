# app/kernel/application/cursosextra/reportes/generar_reporte_financiero.py

"""
Caso de Uso: Generar Reporte Financiero de Curso
"""
from datetime import date
from decimal import Decimal
from typing import Optional, Dict, List

from app.kernel.domain.cursos_extra import (
    CursoExtraRepositoryPort,
    PagoCursoExtraRepositoryPort,
    CostoCursoExtraRepositoryPort,
    BalanceCursoExtraRepositoryPort,
    IngresoCursoExtraRepositoryPort,
    CursoExtraNoEncontrado,
)


class GenerarReporteFinancieroDTO:
    """DTO de entrada para generar reporte financiero."""
    def __init__(
        self,
        curso_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ):
        self.curso_id = curso_id
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta


class ReporteFinancieroResult:
    """Resultado del reporte financiero."""
    def __init__(
        self,
        curso_id: int,
        nombre_curso: str,
        instructor: str,
        total_ingresos: Decimal,
        total_gastos: Decimal,
        ganancia_bruta: Decimal,
        ganancia_institucion: Decimal,
        ganancia_instructor: Decimal,
        porcentaje_institucion: Decimal,
        total_pendiente: Decimal,
        total_pagado: Decimal,
        inscritos_actuales: int,
        cupo_maximo: int,
    ):
        self.curso_id = curso_id
        self.nombre_curso = nombre_curso
        self.instructor = instructor
        self.total_ingresos = total_ingresos
        self.total_gastos = total_gastos
        self.ganancia_bruta = ganancia_bruta
        self.ganancia_institucion = ganancia_institucion
        self.ganancia_instructor = ganancia_instructor
        self.porcentaje_institucion = porcentaje_institucion
        self.total_pendiente = total_pendiente
        self.total_pagado = total_pagado
        self.inscritos_actuales = inscritos_actuales
        self.cupo_maximo = cupo_maximo


class GenerarReporteFinanciero:
    """
    Caso de Uso: Generar reporte financiero completo de un curso.
    
    Incluye:
    - Ingresos totales (con filtro de fecha opcional)
    - Gastos totales (con filtro de fecha opcional)
    - Ganancia bruta y distribución
    - Saldos pendientes
    - Estadísticas de inscripciones
    """
    
    def __init__(
        self,
        curso_repo: CursoExtraRepositoryPort,
        pago_repo: PagoCursoExtraRepositoryPort,
        costo_repo: CostoCursoExtraRepositoryPort,
        balance_repo: BalanceCursoExtraRepositoryPort,
        ingreso_repo: IngresoCursoExtraRepositoryPort,
    ):
        self.curso_repo = curso_repo
        self.pago_repo = pago_repo
        self.costo_repo = costo_repo
        self.balance_repo = balance_repo
        self.ingreso_repo = ingreso_repo
    
    async def execute(self, dto: GenerarReporteFinancieroDTO) -> ReporteFinancieroResult:
        """Ejecuta el caso de uso."""
        
        # Obtener curso
        curso = await self.curso_repo.obtener_por_id(dto.curso_id)
        if not curso:
            raise CursoExtraNoEncontrado(dto.curso_id)
        
        # Calcular ingresos (con filtro de fecha)
        total_ingresos = await self.pago_repo.calcular_total_por_curso(
            curso_id=dto.curso_id,
            fecha_desde=dto.fecha_desde,
            fecha_hasta=dto.fecha_hasta,
        )
        
        # Calcular gastos (con filtro de fecha - convertir date a datetime)
        from datetime import datetime, time
        fecha_desde_dt = None
        fecha_hasta_dt = None
        
        if dto.fecha_desde:
            fecha_desde_dt = datetime.combine(dto.fecha_desde, time.min)
        if dto.fecha_hasta:
            fecha_hasta_dt = datetime.combine(dto.fecha_hasta, time.max)
        
        # Para gastos necesitamos obtener la lista y sumar manualmente si hay filtro de fecha
        if fecha_desde_dt or fecha_hasta_dt:
            costos = await self.costo_repo.listar_por_curso(
                curso_id=dto.curso_id,
                fecha_desde=fecha_desde_dt,
                fecha_hasta=fecha_hasta_dt,
            )
            total_gastos = sum(c.monto for c in costos)
        else:
            total_gastos = await self.costo_repo.calcular_total_por_curso(dto.curso_id)
        
        # Calcular ganancias
        ganancia_bruta = total_ingresos - total_gastos
        ganancia_institucion = (ganancia_bruta * curso.porcentaje_institucion) / Decimal("100")
        ganancia_instructor = ganancia_bruta - ganancia_institucion
        
        # Calcular saldos
        total_pendiente = await self.balance_repo.calcular_total_pendiente(dto.curso_id)
        total_pagado = await self.balance_repo.calcular_total_pagado(dto.curso_id)
        
        return ReporteFinancieroResult(
            curso_id=curso.id,
            nombre_curso=curso.nombre,
            instructor=curso.instructor,
            total_ingresos=total_ingresos,
            total_gastos=total_gastos,
            ganancia_bruta=ganancia_bruta,
            ganancia_institucion=ganancia_institucion,
            ganancia_instructor=ganancia_instructor,
            porcentaje_institucion=curso.porcentaje_institucion,
            total_pendiente=total_pendiente,
            total_pagado=total_pagado,
            inscritos_actuales=curso.inscritos_actuales,
            cupo_maximo=curso.cupo_maximo,
        )

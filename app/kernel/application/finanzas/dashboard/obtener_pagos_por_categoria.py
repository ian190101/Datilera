"""
Caso de Uso: Obtener Distribución de Pagos por Categoría
Endpoint: GET /api/v1/reportes/pagos-categoria
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Agrupa pagos por categoría de pago
2. Calcula total y porcentaje por categoría
3. Periodo configurable (mes actual, últimos 3/6/12 meses)
"""

from decimal import Decimal
from datetime import date
from typing import List, Dict, Any, Optional
from dateutil.relativedelta import relativedelta

from app.kernel.domain.finanzas.ports import (
    IPagoRepository,
    ICategoriaPagoRepository,
)


class PagoCategoriaTotalDTO:
    """DTO para total de una categoría"""
    
    def __init__(
        self,
        categoria_id: int,
        categoria_nombre: str,
        total_pagos: Decimal,
        cantidad_transacciones: int,
        porcentaje_del_total: Decimal,
    ) -> None:
        self.categoria_id = categoria_id
        self.categoria_nombre = categoria_nombre
        self.total_pagos = total_pagos
        self.cantidad_transacciones = cantidad_transacciones
        self.porcentaje_del_total = porcentaje_del_total


class PagosPorCategoriaDTO:
    """DTO de respuesta"""
    
    def __init__(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date,
        categorias: List[PagoCategoriaTotalDTO],
        total_general: Decimal,
        transacciones_totales: int,
    ) -> None:
        self.sede_id = sede_id
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.categorias = categorias
        self.total_general = total_general
        self.transacciones_totales = transacciones_totales


class ObtenerPagosPorCategoriaCU:
    """Caso de Uso: Obtener distribución de pagos por categoría"""
    
    def __init__(
        self,
        pago_repo: IPagoRepository,
        categoria_pago_repo: ICategoriaPagoRepository,
    ) -> None:
        self.pago_repo = pago_repo
        self.categoria_pago_repo = categoria_pago_repo
    
    async def execute(
        self,
        sede_id: int,
        meses_atras: int = 1,  # 1 = mes actual, 3 = últimos 3 meses, etc.
    ) -> PagosPorCategoriaDTO:
        """
        Obtiene distribución de pagos por categoría
        
        Args:
            sede_id: ID de la sede
            meses_atras: Cantidad de meses a consultar (1, 3, 6, 12)
        
        Returns:
            PagosPorCategoriaDTO con distribución por categoría
        """
        # 1. Calcular rango de fechas
        hoy: date = date.today()
        fecha_hasta: date = date(hoy.year, hoy.month + 1, 1) if hoy.month < 12 else date(hoy.year + 1, 1, 1)
        fecha_desde: date = fecha_hasta - relativedelta(months=meses_atras)
        
        # 2. Obtener todos los pagos del periodo
        pagos: List[Dict[str, Any]] = await self.pago_repo.listar(
            sede_id=sede_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            incluir_anulados=False,
            limit=10000
        )
        
        # 3. Agrupar por categoría
        pagos_por_categoria: Dict[int, List[Dict[str, Any]]] = {}
        
        for pago in pagos:
            categoria_id: Optional[int] = pago.get("categoria_pago_id")
            
            if categoria_id is None:
                categoria_id = 0  # Sin categoría
            
            if categoria_id not in pagos_por_categoria:
                pagos_por_categoria[categoria_id] = []
            
            pagos_por_categoria[categoria_id].append(pago)
        
        # 4. Calcular totales por categoría
        categorias_dto: List[PagoCategoriaTotalDTO] = []
        total_general: Decimal = Decimal("0")
        transacciones_totales: int = len(pagos)
        
        for categoria_id, pagos_cat in pagos_por_categoria.items():
            # Calcular total de la categoría
            total_categoria: Decimal = sum(
                (Decimal(str(p.get("monto_pagado", 0))) for p in pagos_cat),
                Decimal("0")
            )
            
            # Obtener nombre de categoría
            if categoria_id == 0:
                categoria_nombre: str = "Sin categoría"
            else:
                categoria_dict: Optional[Dict[str, Any]] = await self.categoria_pago_repo.obtener_por_id(categoria_id)
                categoria_nombre = categoria_dict.get("nombre", f"Categoría {categoria_id}") if categoria_dict else "Desconocida"
            
            categorias_dto.append(
                PagoCategoriaTotalDTO(
                    categoria_id=categoria_id,
                    categoria_nombre=categoria_nombre,
                    total_pagos=total_categoria,
                    cantidad_transacciones=len(pagos_cat),
                    porcentaje_del_total=Decimal("0"),  # Se calcula después
                )
            )
            
            total_general += total_categoria
        
        # 5. Calcular porcentajes
        for categoria_dto in categorias_dto:
            categoria_dto.porcentaje_del_total = (
                (categoria_dto.total_pagos / total_general * 100)
                if total_general > 0 else Decimal("0")
            )
        
        # 6. Ordenar por total descendente
        categorias_dto.sort(key=lambda x: x.total_pagos, reverse=True)
        
        return PagosPorCategoriaDTO(
            sede_id=sede_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            categorias=categorias_dto,
            total_general=total_general,
            transacciones_totales=transacciones_totales,
        )

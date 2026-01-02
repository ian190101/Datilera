"""
Caso de Uso: Obtener Historial de Transferencias
Endpoint: GET /api/v1/finanzas/conciliacion/historial
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Lista historial de conciliaciones (depósitos y transferencias)
2. Filtros: fecha_desde, fecha_hasta, tipo, estado
3. Paginación: limit/offset
4. Incluye detalles de cada operación
"""

from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any, Optional

from app.kernel.domain.finanzas.ports import IConciliacionRepository


class ConciliacionHistorialDTO:
    """DTO para una conciliación en el historial"""
    
    def __init__(
        self,
        conciliacion_id: int,
        tipo: str,  # DEPOSITO | TRANSFERENCIA
        fecha_operacion: datetime,
        monto_total: Decimal,
        cantidad_transacciones: int,
        banco: str,
        cuenta_bancaria: str,
        numero_documento: str,  # Boleta o transferencia
        estado: str,  # DEPOSITADO | TRANSFERIDO | VERIFICADA | CON_DIFERENCIAS
        registrado_por: str,
        verificado: bool,
    ) -> None:
        self.conciliacion_id = conciliacion_id
        self.tipo = tipo
        self.fecha_operacion = fecha_operacion
        self.monto_total = monto_total
        self.cantidad_transacciones = cantidad_transacciones
        self.banco = banco
        self.cuenta_bancaria = cuenta_bancaria
        self.numero_documento = numero_documento
        self.estado = estado
        self.registrado_por = registrado_por
        self.verificado = verificado


class HistorialTransferenciasDTO:
    """DTO de respuesta"""
    
    def __init__(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date,
        conciliaciones: List[ConciliacionHistorialDTO],
        total_registros: int,
        total_depositado_periodo: Decimal,
        total_transferido_periodo: Decimal,
        pagina_actual: int,
        total_paginas: int,
    ) -> None:
        self.sede_id = sede_id
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.conciliaciones = conciliaciones
        self.total_registros = total_registros
        self.total_depositado_periodo = total_depositado_periodo
        self.total_transferido_periodo = total_transferido_periodo
        self.pagina_actual = pagina_actual
        self.total_paginas = total_paginas


class ObtenerHistorialTransferenciasCU:
    """
    Caso de Uso: Obtener historial de transferencias
    
    Adaptado para usar ports.py actual:
    - IConciliacionRepository.listar()
    """
    
    def __init__(self, conciliacion_repo: IConciliacionRepository) -> None:
        self.conciliacion_repo = conciliacion_repo
    
    async def execute(
        self,
        sede_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        tipo: Optional[str] = None,  # DEPOSITO | TRANSFERENCIA
        limit: int = 50,
        offset: int = 0,
    ) -> HistorialTransferenciasDTO:
        """
        Obtiene historial de conciliaciones
        
        Args:
            sede_id: ID de la sede
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            tipo: Tipo de operación (opcional)
            limit: Cantidad de resultados por página
            offset: Offset para paginación
        
        Returns:
            HistorialTransferenciasDTO con historial
        """
        # 1. Obtener conciliaciones de la sede
        conciliaciones: List[Dict[str, Any]] = await self.conciliacion_repo.listar(
            sede_id=sede_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limit=10000  # Obtener todas para filtrar manualmente
        )
        
        # 2. Filtrar por tipo si se especifica
        if tipo:
            conciliaciones = [
                c for c in conciliaciones
                if c.get("tipo", "").upper() == tipo.upper()
            ]
        
        # 3. Calcular totales del periodo
        total_depositado: Decimal = sum(
            (Decimal(str(c.get("monto_total", 0))) for c in conciliaciones
             if c.get("tipo") == "DEPOSITO"),
            Decimal("0")
        )
        
        total_transferido: Decimal = sum(
            (Decimal(str(c.get("monto_total", 0))) for c in conciliaciones
             if c.get("tipo") == "TRANSFERENCIA"),
            Decimal("0")
        )
        
        # 4. Aplicar paginación manual
        total_registros: int = len(conciliaciones)
        conciliaciones_pagina: List[Dict[str, Any]] = conciliaciones[offset:offset + limit]
        
        # 5. Construir DTOs
        conciliaciones_dto: List[ConciliacionHistorialDTO] = [
            ConciliacionHistorialDTO(
                conciliacion_id=c["id"],
                tipo=c.get("tipo", "DEPOSITO"),
                fecha_operacion=c.get("fecha_conciliacion", datetime.now()),
                monto_total=Decimal(str(c.get("monto_total", 0))),
                cantidad_transacciones=c.get("cantidad_transacciones", 0),
                banco=c.get("banco", "No especificado"),
                cuenta_bancaria=c.get("cuenta_bancaria", "N/A"),
                numero_documento=c.get("numero_boleta", "N/A"),
                estado=c.get("estado", "PENDIENTE"),
                registrado_por=c.get("registrado_por_nombre", "Sistema"),
                verificado=c.get("estado") in ["VERIFICADA", "CON_DIFERENCIAS"],
            )
            for c in conciliaciones_pagina
        ]
        
        # 6. Calcular paginación
        total_paginas: int = (total_registros + limit - 1) // limit if limit > 0 else 1
        pagina_actual: int = (offset // limit) + 1 if limit > 0 else 1
        
        return HistorialTransferenciasDTO(
            sede_id=sede_id,
            fecha_desde=fecha_desde or date.today(),
            fecha_hasta=fecha_hasta or date.today(),
            conciliaciones=conciliaciones_dto,
            total_registros=total_registros,
            total_depositado_periodo=total_depositado,
            total_transferido_periodo=total_transferido,
            pagina_actual=pagina_actual,
            total_paginas=total_paginas,
        )

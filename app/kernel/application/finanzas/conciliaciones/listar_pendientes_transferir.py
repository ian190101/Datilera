"""
Caso de Uso: Listar Pagos Pendientes de Transferir
Endpoint: GET /api/v1/finanzas/conciliacion/pendientes
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Lista pagos en estado "DEPOSITADO" pendientes de transferir
2. Agrupa por fecha de depósito
3. Calcula total pendiente por sede
4. Incluye antigüedad de depósito (días desde depósito)
"""

from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any

from app.kernel.domain.finanzas.ports import IPagoRepository


class PagoPendienteTransferirDTO:
    """DTO para pago pendiente de transferir"""
    
    def __init__(
        self,
        pago_id: int,
        alumno_id: int,
        alumno_nombre: str,
        monto: Decimal,
        fecha_pago: datetime,
        fecha_deposito: datetime,
        dias_desde_deposito: int,
        numero_boleta_deposito: str,
        metodo_pago: str,
    ) -> None:
        self.pago_id = pago_id
        self.alumno_id = alumno_id
        self.alumno_nombre = alumno_nombre
        self.monto = monto
        self.fecha_pago = fecha_pago
        self.fecha_deposito = fecha_deposito
        self.dias_desde_deposito = dias_desde_deposito
        self.numero_boleta_deposito = numero_boleta_deposito
        self.metodo_pago = metodo_pago


class PendientesTransferirDTO:
    """DTO de respuesta"""
    
    def __init__(
        self,
        sede_id: int,
        pagos_pendientes: List[PagoPendienteTransferirDTO],
        total_pendiente: Decimal,
        cantidad_pagos: int,
        fecha_consulta: datetime,
    ) -> None:
        self.sede_id = sede_id
        self.pagos_pendientes = pagos_pendientes
        self.total_pendiente = total_pendiente
        self.cantidad_pagos = cantidad_pagos
        self.fecha_consulta = fecha_consulta


class ListarPendientesTransferirCU:
    """
    Caso de Uso: Listar pagos pendientes de transferir
    
    Adaptado para usar ports.py actual:
    - IPagoRepository.listar() con filtros
    """
    
    def __init__(self, pago_repo: IPagoRepository) -> None:
        self.pago_repo = pago_repo
    
    async def execute(self, sede_id: int) -> PendientesTransferirDTO:
        """
        Lista pagos pendientes de transferir
        
        Args:
            sede_id: ID de la sede
        
        Returns:
            PendientesTransferirDTO con pagos pendientes
        """
        # 1. Obtener todos los pagos de la sede
        pagos: List[Dict[str, Any]] = await self.pago_repo.listar(
            sede_id=sede_id,
            incluir_anulados=False,
            limit=10000
        )
        
        # 2. Filtrar solo pagos en estado DEPOSITADO
        pagos_depositados: List[Dict[str, Any]] = [
            p for p in pagos
            if p.get("estado_conciliacion", "PENDIENTE") == "DEPOSITADO"
        ]
        
        # 3. Construir DTOs
        pagos_dto: List[PagoPendienteTransferirDTO] = []
        total_pendiente: Decimal = Decimal("0")
        
        for pago in pagos_depositados:
            fecha_deposito: datetime = pago.get("fecha_deposito", pago.get("fecha_pago"))
            dias_desde_deposito: int = (date.today() - fecha_deposito.date()).days
            
            monto: Decimal = Decimal(str(pago.get("monto_pagado", 0)))
            
            pagos_dto.append(
                PagoPendienteTransferirDTO(
                    pago_id=pago["id"],
                    alumno_id=pago.get("alumno_id", 0),
                    alumno_nombre=pago.get("alumno_nombre", "Desconocido"),
                    monto=monto,
                    fecha_pago=pago.get("fecha_pago", datetime.now()),
                    fecha_deposito=fecha_deposito,
                    dias_desde_deposito=dias_desde_deposito,
                    numero_boleta_deposito=pago.get("numero_boleta_deposito", "N/A"),
                    metodo_pago=pago.get("metodo_pago", "EFECTIVO"),
                )
            )
            
            total_pendiente += monto
        
        # 4. Ordenar por antigüedad (más antiguos primero)
        pagos_dto.sort(key=lambda x: x.dias_desde_deposito, reverse=True)
        
        return PendientesTransferirDTO(
            sede_id=sede_id,
            pagos_pendientes=pagos_dto,
            total_pendiente=total_pendiente,
            cantidad_pagos=len(pagos_dto),
            fecha_consulta=datetime.now(),
        )

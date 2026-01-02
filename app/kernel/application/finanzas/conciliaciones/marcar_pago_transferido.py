"""
Caso de Uso: Marcar Pago como Transferido a Cuenta Principal
Endpoint: POST /api/v1/finanzas/conciliacion/marcar-transferido
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Marca pagos depositados como "TRANSFERIDO" a cuenta principal
2. Registra número de transferencia bancaria
3. Actualiza estado de conciliación
4. Solo pagos en estado "DEPOSITADO" pueden transferirse
5. Auditoría completa del proceso
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.kernel.domain.finanzas.ports import (
    IPagoRepository,
    IConciliacionRepository,
)
from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort
from app.kernel.domain.finanzas.errors import (
    PagoNoEncontradoError,
    PagoError,
)


class PagoTransferidoDTO:
    """DTO de respuesta para pago marcado como transferido"""
    
    def __init__(
        self,
        pago_id: int,
        monto_transferido: Decimal,
        numero_transferencia: str,
        fecha_transferencia: datetime,
        estado_anterior: str,
        estado_nuevo: str,
    ) -> None:
        self.pago_id = pago_id
        self.monto_transferido = monto_transferido
        self.numero_transferencia = numero_transferencia
        self.fecha_transferencia = fecha_transferencia
        self.estado_anterior = estado_anterior
        self.estado_nuevo = estado_nuevo


class ResultadoTransferenciaDTO:
    """DTO de respuesta para operación de transferencia"""
    
    def __init__(
        self,
        conciliacion_id: int,
        pagos_transferidos: List[PagoTransferidoDTO],
        total_transferido: Decimal,
        cantidad_pagos: int,
        fecha_operacion: datetime,
    ) -> None:
        self.conciliacion_id = conciliacion_id
        self.pagos_transferidos = pagos_transferidos
        self.total_transferido = total_transferido
        self.cantidad_pagos = cantidad_pagos
        self.fecha_operacion = fecha_operacion


class MarcarPagoTransferidoCU:
    """
    Caso de Uso: Marcar pagos como transferidos a cuenta principal
    
    Adaptado para usar ports.py actual:
    - IPagoRepository.obtener_por_id()
    - IConciliacionRepository.crear()
    - IAuditoriaAccionesRepository.registrar()
    """
    
    def __init__(
        self,
        pago_repo: IPagoRepository,
        conciliacion_repo: IConciliacionRepository,
        auditoria_repo: AuditoriaAccionRepositoryPort,
    ) -> None:
        self.pago_repo = pago_repo
        self.conciliacion_repo = conciliacion_repo
        self.auditoria_repo = auditoria_repo
    
    async def execute(
        self,
        pagos_ids: List[int],
        numero_transferencia: str,
        fecha_transferencia: datetime,
        banco_origen: str,
        cuenta_origen: str,
        banco_destino: str,
        cuenta_destino: str,
        usuario_id: int,
        sede_id: int,
    ) -> ResultadoTransferenciaDTO:
        """
        Marca pagos como transferidos a cuenta principal
        
        Args:
            pagos_ids: Lista de IDs de pagos a marcar como transferidos
            numero_transferencia: Número de la transferencia bancaria
            fecha_transferencia: Fecha/hora de la transferencia
            banco_origen: Banco de origen
            cuenta_origen: Cuenta de origen
            banco_destino: Banco de destino (cuenta principal)
            cuenta_destino: Cuenta de destino
            usuario_id: ID del usuario que registra
            sede_id: ID de la sede
        
        Returns:
            ResultadoTransferenciaDTO con resultado de la operación
        
        Raises:
            PagoNoEncontradoError: Si algún pago no existe
            EstadoPagoInvalidoError: Si algún pago no está en estado DEPOSITADO
        """
        # 1. Validar todos los pagos antes de procesar
        pagos_validados: List[Dict[str, Any]] = await self._validar_pagos_depositados(
            pagos_ids, sede_id
        )
        
        # 2. Calcular total a transferir
        total_transferencia: Decimal = sum(
            (Decimal(str(p.get("monto_pagado", 0))) for p in pagos_validados),
            Decimal("0")
        )
        
        # 3. Crear registro de conciliación
        conciliacion_id: int = await self.conciliacion_repo.crear({
            "tipo": "TRANSFERENCIA",
            "fecha_conciliacion": fecha_transferencia,
            "monto_total": str(total_transferencia),
            "banco": f"{banco_origen} -> {banco_destino}",
            "cuenta_bancaria": cuenta_destino,
            "numero_boleta": numero_transferencia,  # Reutilizar campo
            "cantidad_transacciones": len(pagos_ids),
            "estado": "TRANSFERIDO",
            "registrado_por_id": usuario_id,
            "sede_id": sede_id,
            "metadata": {
                "pagos_ids": pagos_ids,
                "banco_origen": banco_origen,
                "cuenta_origen": cuenta_origen,
                "banco_destino": banco_destino,
                "cuenta_destino": cuenta_destino,
            }
        })
        
        # 4. Marcar cada pago como transferido
        pagos_transferidos_dto: List[PagoTransferidoDTO] = []
        
        for pago in pagos_validados:
            pago_id: int = pago["id"]
            estado_anterior: str = pago.get("estado_conciliacion", "DEPOSITADO")
            
            # Actualizar estado del pago
            await self._actualizar_estado_pago(
                pago_id=pago_id,
                estado_nuevo="TRANSFERIDO",
                conciliacion_id=conciliacion_id,
                numero_transferencia=numero_transferencia,
                fecha_transferencia=fecha_transferencia,
            )
            
            pagos_transferidos_dto.append(
                PagoTransferidoDTO(
                    pago_id=pago_id,
                    monto_transferido=Decimal(str(pago.get("monto_pagado", 0))),
                    numero_transferencia=numero_transferencia,
                    fecha_transferencia=fecha_transferencia,
                    estado_anterior=estado_anterior,
                    estado_nuevo="TRANSFERIDO",
                )
            )
        
        # 5. Registrar auditoría
        await self.auditoria_repo.registrar({
            "accion": "MARCAR_TRANSFERIDO",
            "modulo": "FINANZAS",
            "entidad": "CONCILIACION",
            "entidad_id": conciliacion_id,
            "usuario_id": usuario_id,
            "sede_id": sede_id,
            "detalles": {
                "pagos_ids": pagos_ids,
                "total_transferido": str(total_transferencia),
                "numero_transferencia": numero_transferencia,
                "banco_origen": banco_origen,
                "banco_destino": banco_destino,
            },
            "fecha": datetime.now(),
        })
        
        return ResultadoTransferenciaDTO(
            conciliacion_id=conciliacion_id,
            pagos_transferidos=pagos_transferidos_dto,
            total_transferido=total_transferencia,
            cantidad_pagos=len(pagos_ids),
            fecha_operacion=datetime.now(),
        )
    
    async def _validar_pagos_depositados(
        self, pagos_ids: List[int], sede_id: int
    ) -> List[Dict[str, Any]]:
        """Valida que todos los pagos estén en estado DEPOSITADO"""
        pagos_validados: List[Dict[str, Any]] = []
        
        for pago_id in pagos_ids:
            # Obtener pago
            pago: Optional[Dict[str, Any]] = await self.pago_repo.obtener_por_id(pago_id)
            
            if not pago:
                raise PagoNoEncontradoError(f"Pago {pago_id} no encontrado")
            
            # Validar que pertenece a la sede
            if pago.get("sede_id") != sede_id:
                raise PagoNoEncontradoError(
                    f"Pago {pago_id} no pertenece a la sede {sede_id}"
                )
            
            # Validar que no esté anulado
            if pago.get("anulado", False):
                raise PagoError(f"Pago {pago_id} está anulado")
            
            # Validar que esté en estado DEPOSITADO
            estado_conciliacion: str = pago.get("estado_conciliacion", "PENDIENTE")
            if estado_conciliacion != "DEPOSITADO":
                raise PagoError(
                    f"Pago {pago_id} no está en estado DEPOSITADO (actual: {estado_conciliacion})"
                )
            
            pagos_validados.append(pago)
        
        return pagos_validados
    
    async def _actualizar_estado_pago(
        self,
        pago_id: int,
        estado_nuevo: str,
        conciliacion_id: int,
        numero_transferencia: str,
        fecha_transferencia: datetime,
    ) -> None:
        """Actualiza el estado de conciliación de un pago"""
        # Implementar en infrastructure adapter
        pass

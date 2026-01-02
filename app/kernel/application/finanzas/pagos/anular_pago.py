# app/application/use_cases/finanzas/anular_pago.py
"""
Caso de uso: Anular un pago existente.
Arquitectura hexagonal - Solo usa puertos, no implementaciones concretas.
"""
from datetime import datetime

from app.kernel.domain.finanzas.pago_entidad import PagoAnular
from app.kernel.domain.finanzas.ports import (
    IPagoRepository,
    IEstadoCuentaNinoRepository,
    ILibroCajaRepository,
)
from app.kernel.domain.finanzas.errors import (
    PagoNoEncontradoError,
    PagoYaAnuladoError,
    PagoError,
)


class AnularPagoUC:
    """
    Caso de uso: Anular un pago existente.
    
    Flujo:
    1. Obtener pago usando puerto
    2. Validar que existe y no está anulado
    3. Anular el pago usando puerto
    4. Actualizar estado de cuenta del alumno (revertir)
    5. Registrar anulación en libro de caja (como egreso de reversión)
    6. Retornar confirmación
    """

    def __init__(
        self,
        pago_repo: IPagoRepository,
        estado_cuenta_repo: IEstadoCuentaNinoRepository,
        libro_caja_repo: ILibroCajaRepository
    ):
        """
        Constructor con inyección de dependencias por puertos.
        
        Args:
            pago_repo: Puerto del repositorio de pagos
            estado_cuenta_repo: Puerto del repositorio de estado de cuenta
            libro_caja_repo: Puerto del repositorio de libro de caja
        """
        self._pago_repo = pago_repo
        self._estado_cuenta_repo = estado_cuenta_repo
        self._libro_caja_repo = libro_caja_repo

    async def execute(
        self,
        pago_id: int,
        datos: PagoAnular
    ) -> bool:
        """
        Anula un pago existente.
        
        Args:
            pago_id: ID del pago a anular
            datos: Schema Pydantic con motivo y usuario (ya validados)
            
        Returns:
            True si se anuló correctamente
            
        Raises:
            PagoNoEncontradoError: Si el pago no existe
            PagoYaAnuladoError: Si el pago ya está anulado
            PagoError: Para otros errores de negocio
        """
        # ✅ 1. Pydantic ya validó motivo (>=10 caracteres) y anulado_por (>0)
        
        # ✅ 2. Obtener pago usando el puerto
        pago_dict = await self._pago_repo.obtener_por_id(pago_id)
        
        if not pago_dict:
            raise PagoNoEncontradoError(
                f"Pago con ID {pago_id} no encontrado"
            )
        
        # ✅ 3. Validar que no esté anulado
        if pago_dict.get('anulado', False):
            raise PagoYaAnuladoError(
                f"El pago {pago_id} ya está anulado"
            )
        
        # ✅ 4. Obtener datos del pago
        monto = pago_dict.get('monto_pagado')
        alumno_id = pago_dict.get('alumno_id')
        sede_id = pago_dict.get('sede_id')
        
        if not monto or monto <= 0:
            raise PagoError(
                f"Pago {pago_id} tiene monto inválido: {monto}"
            )
        
        # ✅ 5. Anular el pago usando el puerto
        try:
            success = await self._pago_repo.anular(
                pago_id=pago_id,
                anulado_por_id=datos.anulado_por,
                motivo=datos.motivo_anulacion
            )
            
            if not success:
                raise PagoError(f"No se pudo anular el pago {pago_id}")
                
        except Exception as e:
            raise PagoError(f"Error al anular el pago: {str(e)}")
        
        # ✅ 6. Revertir estado de cuenta del alumno
        try:
            await self._estado_cuenta_repo.registrar_cargo(
                alumno_id=alumno_id,
                monto=monto
            )
        except Exception as e:
            raise PagoError(
                f"Pago {pago_id} anulado pero falló reversión de estado de cuenta: {str(e)}"
            )
        
        # ✅ 7. Registrar anulación en libro de caja (como egreso de reversión)
        try:
            await self._libro_caja_repo.registrar_egreso(
                monto=monto,
                fecha=datetime.utcnow(),
                registrado_por_id=datos.anulado_por,
                observaciones=f"Anulación de pago ID {pago_id}. Motivo: {datos.motivo_anulacion}",
                egreso_id=None,
                sede_id=sede_id
            )
        except Exception as e:
            raise PagoError(
                f"Pago {pago_id} anulado pero falló registro en libro de caja: {str(e)}"
            )
        
        return True

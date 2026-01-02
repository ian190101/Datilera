# app/kernel/application/finanzas/pagos/registrar_pago_cu.py
"""
Caso de uso: Registrar un pago de alumno.
Arquitectura hexagonal - Solo usa puertos, no implementaciones concretas.
"""

from datetime import datetime

from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.services.jobqueue_service import JobQueueService
from app.kernel.domain.finanzas.pago_entidad import PagoCreate
from app.kernel.domain.finanzas.ports import (
    IPagoRepository,
    IEstadoCuentaNinoRepository,
    ILibroCajaRepository,
    ICategoriaPagoRepository,
)
from app.kernel.domain.finanzas.errors import (
    ComprobantePagoYaExisteError,
    PagoError,
    CategoriaPagoNoEncontradaError,
    CategoriaPagoInactivaError,
    AlumnoSinDeudaError,
)


class RegistrarPagoUC:
    """
    Caso de uso: Registrar un pago de alumno.

    Flujo:
    1. Validar categoría de pago (existe y activa)
    2. Verificar duplicidad de comprobante (si aplica)
    3. Crear registro de pago
    4. Actualizar estado de cuenta del alumno
    5. Registrar movimiento en libro de caja
    6. Commit transaccional
    7. Disparar recalculo de recordatorios
    """

    def __init__(
        self,
        pago_repo: IPagoRepository,
        estado_cuenta_repo: IEstadoCuentaNinoRepository,
        libro_caja_repo: ILibroCajaRepository,
        categoria_pago_repo: ICategoriaPagoRepository,
        uow: UnitOfWork,
        jobs: JobQueueService,
    ) -> None:
        """
        Constructor con inyección de dependencias por puertos.
        """
        self._pago_repo = pago_repo
        self._estado_cuenta_repo = estado_cuenta_repo
        self._libro_caja_repo = libro_caja_repo
        self._categoria_pago_repo = categoria_pago_repo
        self._uow = uow
        self._jobs = jobs

    async def execute(self, datos: PagoCreate) -> int:
        """
        Registra un nuevo pago.
        """
        # 1. Pydantic ya validó monto (>0) y método de pago

        # 2. Validar categoría de pago
        categoria = await self._categoria_pago_repo.obtener_por_id(
            datos.categoria_pago_id
        )

        if not categoria:
            raise CategoriaPagoNoEncontradaError(
                f"Categoría de pago {datos.categoria_pago_id} no encontrada"
            )

        if not categoria.get("activo", True):
            raise CategoriaPagoInactivaError(
                f"La categoría de pago '{categoria.get('nombre')}' está inactiva"
            )

        # 3. Verificar duplicidad de comprobante
        if datos.numero_comprobante:
            existe = await self._pago_repo.verificar_duplicado_comprobante(
                datos.numero_comprobante
            )
            if existe:
                raise ComprobantePagoYaExisteError(
                    f"Ya existe un pago con el comprobante '{datos.numero_comprobante}'"
                )

        # 4. Crear pago usando el puerto
        try:
            pago_id = await self._pago_repo.crear(
                alumno_id=datos.alumno_id,
                monto_pagado=datos.monto_pagado,
                fecha_pago=datos.fecha_pago,
                metodo_pago=datos.metodo_pago,
                categoria_pago_id=datos.categoria_pago_id,
                numero_comprobante=datos.numero_comprobante,
                observaciones=datos.observaciones,
                registrado_por=datos.registrado_por,
                sede_id=datos.sede_id,
            )
        except Exception as e:
            raise PagoError(f"Error al crear el pago: {str(e)}")

        # 5. Actualizar estado de cuenta del alumno
        try:
            await self._estado_cuenta_repo.registrar_pago(
                alumno_id=datos.alumno_id,
                monto=datos.monto_pagado,
            )
        except Exception as e:
            raise PagoError(
                f"Pago creado (ID: {pago_id}) pero falló actualización de estado de cuenta: {str(e)}"
            )

        # 6. Registrar en libro de caja
        try:
            await self._libro_caja_repo.registrar_ingreso(
                monto=datos.monto_pagado,
                fecha=datos.fecha_pago,
                registrado_por_id=datos.registrado_por,
                observaciones=f"Pago de alumno ID {datos.alumno_id} - {datos.metodo_pago}",
                pago_id=pago_id,
                sede_id=datos.sede_id,
            )
        except Exception as e:
            raise PagoError(
                f"Pago creado (ID: {pago_id}) pero falló registro en libro de caja: {str(e)}"
            )

        # 7. Commit transaccional
        await self._uow.commit()

        # 8. Disparar recalculo de recordatorios para este alumno/sede
        # El job debe ser idempotente: revisa el estado de la cuenta y ajusta agenda
        self._jobs.enqueue_recalcular_recordatorios_cuenta(
            alumno_id=datos.alumno_id,
            sede_id=datos.sede_id,
        )

        return pago_id

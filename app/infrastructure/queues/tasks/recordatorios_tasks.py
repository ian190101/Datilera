# app/infrastructure/tasks/recordatorios_tasks.py
from __future__ import annotations

import asyncio
from datetime import date

from app.infrastructure.db.session import get_session
from app.infrastructure.services.recordatorio_deuda_service import RecordatorioDeudaService
from app.infrastructure.notificaciones.service import NotificacionesService
# Repositorios
from app.infrastructure.db.repositories.alumnos.alumnos_repo import AlumnosRepository
from app.infrastructure.db.repositories.finanzas.estado_cuenta_nino_repo import EstadoCuentaNinoRepository
from app.infrastructure.db.repositories.finanzas.pagos_repo import PagosRepository
from app.infrastructure.db.repositories.finanzas.planes_cuotas_repo import PlanesCuotasRepository
# 1. Agregamos el import del nuevo repo
from app.infrastructure.db.repositories.alumnos.tutores_repo import TutoresRepository



def enviar_recordatorios_pagos_sede(sede_id: int, fecha_10_mes: str) -> None:
    asyncio.run(_enviar_async(sede_id, fecha_10_mes))


async def _enviar_async(sede_id: int, fecha_10_mes: str) -> None:
    fecha_10 = date.fromisoformat(fecha_10_mes)

    async with get_session() as session:
        # Repositorios
        alumno_repo = AlumnosRepository(session)
        estado_cuenta_repo = EstadoCuentaNinoRepository(session)
        pago_repo = PagosRepository(session)
        cuota_repo = PlanesCuotasRepository(session)
        # 2. Instanciamos el repositorio de Tutores
        tutores_repo = TutoresRepository(session)

        # Servicios de aplicación
        deuda_service = RecordatorioDeudaService(
            alumno_repo=alumno_repo,
            estado_cuenta_repo=estado_cuenta_repo,
            pago_repo=pago_repo,
            cuota_repo=cuota_repo,
        )

        notif_service = NotificacionesService(session)

        # Iteramos los alumnos que tienen deuda calculada
        async for alumno_id in deuda_service.obtener_alumnos_con_deuda_pendiente(
            sede_id=sede_id,
            fecha_corte=fecha_10,
        ):
            alumno = await alumno_repo.obtener_por_id(alumno_id)
            if not alumno:
                continue

            # 3. CAMBIO: Usamos tutores_repo en lugar de alumno_repo
            # Usamos listar_por_alumno para obtener los responsables específicos de este deudor.
            # (No usamos "activos" sino todos los asociados, según instrucción)
            tutores = await tutores_repo.listar_por_alumno(alumno_id)

            for tutor in tutores:
                await notif_service.enviar_notificacion(
                    tutor_id=tutor.id,
                    usuario_id=tutor.usuario_id,
                    alumno_nombre=alumno.nombre,  # Asumiendo que alumno tiene attr nombre o nombres
                    sede_id=sede_id,
                    fecha_corte=fecha_10,
                )

        await session.commit()
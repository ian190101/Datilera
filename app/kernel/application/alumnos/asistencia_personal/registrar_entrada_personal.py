from datetime import date, datetime, time
from typing import Optional

from app.kernel.domain.alumnos.asistencia_personal_entidad import AsistenciaPersonalEntidad
from app.kernel.domain.alumnos.ports import AsistenciaPersonalRepositoryPort
from app.kernel.domain.alumnos.errors import AsistenciaDuplicadaError, AsistenciaFechaFuturaError


class RegistrarEntradaPersonalCU:
    """Registrar entrada de un miembro del personal."""

    def __init__(self, asistencia_repo: AsistenciaPersonalRepositoryPort):
        self.asistencia_repo = asistencia_repo

    async def ejecutar(
        self,
        personal_id: int,
        sede_id: int,
        fecha: Optional[date] = None,
        hora_entrada: Optional[time] = None,
        observaciones: Optional[str] = None,
    ) -> AsistenciaPersonalEntidad:
        hoy = date.today()
        fecha = fecha or hoy
        if fecha > hoy:
            raise AsistenciaFechaFuturaError()

        existente = await self.asistencia_repo.obtener_por_personal_fecha(personal_id, fecha)
        if existente and existente.hora_entrada is not None:
            raise AsistenciaDuplicadaError("personal", personal_id, str(fecha))

        ahora_time = datetime.utcnow().time()
        asistencia = AsistenciaPersonalEntidad(
            personal_id=personal_id,
            sede_id=sede_id,
            fecha=fecha,
            hora_entrada=hora_entrada or ahora_time,
            observaciones=observaciones,
            creado_en=datetime.utcnow(),
        )

        if existente:
            mezcla = AsistenciaPersonalEntidad(
                **{**existente.model_dump(), **asistencia.model_dump(exclude_unset=True)}
            )
            return await self.asistencia_repo.actualizar(existente.id, mezcla)

        return await self.asistencia_repo.crear(asistencia)

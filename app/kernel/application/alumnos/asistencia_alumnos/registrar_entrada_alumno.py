from datetime import date, datetime, time
from typing import Optional

from app.kernel.domain.alumnos.asistencia_alumno_entidad import AsistenciaAlumnoEntidad
from app.kernel.domain.alumnos.ports import AsistenciaAlumnosRepositoryPort
from app.kernel.domain.alumnos.errors import (
    AsistenciaDuplicadaError,
    AsistenciaFechaFuturaError,
)


class RegistrarEntradaAlumnoCU:
    """Registrar entrada (y opcionalmente retraso) de un alumno."""

    def __init__(self, asistencia_repo: AsistenciaAlumnosRepositoryPort):
        self.asistencia_repo = asistencia_repo

    async def ejecutar(
        self,
        alumno_id: int,
        sede_id: int,
        fecha: Optional[date] = None,
        hora_entrada: Optional[time] = None,
        hora_retraso: Optional[time] = None,
        observaciones: Optional[str] = None,
        registrado_por_id: Optional[int] = None,
    ) -> AsistenciaAlumnoEntidad:
        hoy = date.today()
        fecha = fecha or hoy
        if fecha > hoy:
            raise AsistenciaFechaFuturaError()

        existente = await self.asistencia_repo.obtener_por_alumno_fecha(alumno_id, fecha)
        if existente and existente.hora_entrada is not None:
            raise AsistenciaDuplicadaError("alumno", alumno_id, str(fecha))

        ahora_time = datetime.utcnow().time()
        asistencia = AsistenciaAlumnoEntidad(
            alumno_id=alumno_id,
            sede_id=sede_id,
            fecha=fecha,
            hora_entrada=hora_entrada or ahora_time,
            hora_retraso=hora_retraso,
            observaciones=observaciones,
            creado_en=datetime.utcnow(),
            registrado_por_id=registrado_por_id,
        )

        if existente:
            # actualizar registro existente (por ejemplo, creado masivo sin hora_entrada)
            asistencia_completa = AsistenciaAlumnoEntidad(
                **{**existente.model_dump(), **asistencia.model_dump(exclude_unset=True)}
            )
            return await self.asistencia_repo.actualizar(existente.id, asistencia_completa)

        return await self.asistencia_repo.crear(asistencia)

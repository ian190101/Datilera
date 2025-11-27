from datetime import datetime, time, date
from typing import Optional

from app.kernel.domain.alumnos.asistencia_alumno_entidad import AsistenciaAlumnoEntidad
from app.kernel.domain.alumnos.ports import AsistenciaAlumnosRepositoryPort
from app.kernel.domain.alumnos.errors import AsistenciaNoEncontradaError


class RegistrarSalidaAlumnoCU:
    """Registrar salida de un alumno."""

    def __init__(self, asistencia_repo: AsistenciaAlumnosRepositoryPort):
        self.asistencia_repo = asistencia_repo

    async def ejecutar(
        self,
        alumno_id: int,
        fecha: Optional[date] = None,
        hora_salida: Optional[time] = None,
        observaciones: Optional[str] = None,
    ) -> AsistenciaAlumnoEntidad:
        fecha = fecha or date.today()
        asistencia = await self.asistencia_repo.obtener_por_alumno_fecha(alumno_id, fecha)
        if not asistencia:
            raise AsistenciaNoEncontradaError()

        data = asistencia.model_dump()
        data["hora_salida"] = hora_salida or datetime.utcnow().time()
        if observaciones is not None:
            data["observaciones"] = observaciones
        actualizado = AsistenciaAlumnoEntidad(**data)
        return await self.asistencia_repo.actualizar(asistencia.id, actualizado)

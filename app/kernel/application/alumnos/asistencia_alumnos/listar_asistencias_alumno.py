from typing import List, Optional
from datetime import date

from app.kernel.domain.alumnos.asistencia_alumno_entidad import AsistenciaAlumnoEntidad
from app.kernel.domain.alumnos.ports import AsistenciaAlumnosRepositoryPort


class ListarAsistenciasAlumnoCU:
    """Listar asistencias de un alumno en un rango de fechas."""

    def __init__(self, asistencia_repo: AsistenciaAlumnosRepositoryPort):
        self.asistencia_repo = asistencia_repo

    async def ejecutar(
        self,
        alumno_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> List[AsistenciaAlumnoEntidad]:
        return await self.asistencia_repo.listar_por_alumno(alumno_id, fecha_desde, fecha_hasta)

from typing import Dict, Any, List
from datetime import date

from app.kernel.domain.alumnos.asistencia_alumno_entidad import AsistenciaAlumnoEntidad
from app.kernel.domain.alumnos.ports import AsistenciaAlumnosRepositoryPort


class ObtenerReporteAsistenciaAlumnoCU:
    """Obtener resumen de asistencia de un alumno."""

    def __init__(self, asistencia_repo: AsistenciaAlumnosRepositoryPort):
        self.asistencia_repo = asistencia_repo

    async def ejecutar(
        self,
        alumno_id: int,
        fecha_desde: date,
        fecha_hasta: date,
    ) -> Dict[str, Any]:
        asistencias: List[AsistenciaAlumnoEntidad] = await self.asistencia_repo.listar_por_alumno(
            alumno_id, fecha_desde, fecha_hasta
        )

        total_dias = len(asistencias)
        asistio = sum(1 for a in asistencias if a.asistio())
        faltas = total_dias - asistio
        con_retraso = sum(1 for a in asistencias if a.tiene_retraso())

        return {
            "alumno_id": alumno_id,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "total_registros": total_dias,
            "asistencias": asistio,
            "faltas": faltas,
            "retrasos": con_retraso,
        }

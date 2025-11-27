from typing import Dict, Any, List
from datetime import date

from app.kernel.domain.alumnos.asistencia_personal_entidad import AsistenciaPersonalEntidad
from app.kernel.domain.alumnos.ports import AsistenciaPersonalRepositoryPort


class ObtenerReporteAsistenciaPersonalCU:
    """Obtener resumen de asistencia del personal de una sede en un periodo."""

    def __init__(self, asistencia_repo: AsistenciaPersonalRepositoryPort):
        self.asistencia_repo = asistencia_repo

    async def ejecutar(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date,
    ) -> Dict[str, Any]:
        # Aquí podrías tener un método más especializado en el repo; por ahora listamos día por día.
        registros: List[AsistenciaPersonalEntidad] = []
        dia = fecha_inicio
        while dia <= fecha_fin:
            registros.extend(await self.asistencia_repo.listar_por_sede_fecha(sede_id, dia))
            dia = date.fromordinal(dia.toordinal() + 1)

        total = len(registros)
        con_entrada = sum(1 for r in registros if r.hora_entrada is not None)

        return {
            "sede_id": sede_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "registros": total,
            "presentes": con_entrada,
        }

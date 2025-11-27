from typing import List
from datetime import date

from app.kernel.domain.alumnos.asistencia_personal_entidad import AsistenciaPersonalEntidad
from app.kernel.domain.alumnos.ports import AsistenciaPersonalRepositoryPort


class ListarAsistenciasPersonalCU:
    """Listar asistencias de personal para una sede y fecha."""

    def __init__(self, asistencia_repo: AsistenciaPersonalRepositoryPort):
        self.asistencia_repo = asistencia_repo

    async def ejecutar(self, sede_id: int, fecha: date) -> List[AsistenciaPersonalEntidad]:
        return await self.asistencia_repo.listar_por_sede_fecha(sede_id, fecha)

from typing import List

from app.kernel.domain.alumnos.alumno_paralelo_entidad import AlumnoParaleloEntidad
from app.kernel.domain.alumnos.ports import AlumnosParalelosRepositoryPort


class ListarAlumnosParaleloCU:
    """Listar alumnos asignados a un paralelo."""

    def __init__(self, alumnos_paralelos_repo: AlumnosParalelosRepositoryPort):
        self.alumnos_paralelos_repo = alumnos_paralelos_repo

    async def ejecutar(self, paralelo_id: int) -> List[AlumnoParaleloEntidad]:
        return await self.alumnos_paralelos_repo.listar_por_paralelo(paralelo_id)

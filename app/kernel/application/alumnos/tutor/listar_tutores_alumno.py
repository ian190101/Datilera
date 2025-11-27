from typing import List

from app.kernel.domain.alumnos.alumno_tutor_entidad import AlumnoTutorEntidad
from app.kernel.domain.alumnos.ports import AlumnoTutorRepositoryPort


class ListarTutoresAlumnoCU:
    """Listar tutores asociados a un alumno."""

    def __init__(self, relacion_repo: AlumnoTutorRepositoryPort):
        self.relacion_repo = relacion_repo

    async def ejecutar(self, alumno_id: int) -> List[AlumnoTutorEntidad]:
        return await self.relacion_repo.listar_por_alumno(alumno_id)

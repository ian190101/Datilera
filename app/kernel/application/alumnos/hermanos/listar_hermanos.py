from typing import List

from app.kernel.domain.alumnos.alumno_hermano_entidad import AlumnoHermanoEntidad
from app.kernel.domain.alumnos.ports import AlumnosHermanosRepositoryPort


class ListarHermanosCU:
    """Listar hermanos de un alumno."""

    def __init__(self, hermanos_repo: AlumnosHermanosRepositoryPort):
        self.hermanos_repo = hermanos_repo

    async def ejecutar(self, alumno_id: int) -> List[AlumnoHermanoEntidad]:
        hermanos = await self.hermanos_repo.listar_por_alumno(alumno_id)
        return sorted(hermanos, key=lambda h: h.lugar_ocupa)

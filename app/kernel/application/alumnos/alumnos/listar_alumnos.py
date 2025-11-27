# app/application/alumnos/alumnos/listar_alumnos.py

from typing import List, Optional

from app.kernel.domain.alumnos.alumno_entidad import AlumnoEntidad
from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort


class ListarAlumnosCU:
    """Caso de uso: Listar alumnos con diferentes filtros"""

    def __init__(self, alumno_repo: AlumnoRepositoryPort):
        self.alumno_repo = alumno_repo

    async def por_sede(
        self, 
        sede_id: int, 
        solo_activos: bool = True
    ) -> List[AlumnoEntidad]:
        """Listar alumnos de una sede"""
        return await self.alumno_repo.listar_por_sede(sede_id, solo_activos)

    async def por_turno(
        self, 
        turno_id: int, 
        solo_activos: bool = True
    ) -> List[AlumnoEntidad]:
        """Listar alumnos de un turno"""
        return await self.alumno_repo.listar_por_turno(turno_id, solo_activos)

    async def todos(self, solo_activos: bool = True) -> List[AlumnoEntidad]:
        """Listar todos los alumnos del sistema"""
        # Implementar según necesidad (podría requerir paginación)
        pass

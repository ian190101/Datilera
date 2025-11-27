from datetime import datetime

from app.kernel.domain.alumnos.alumno_paralelo_entidad import AlumnoParaleloEntidad
from app.kernel.domain.alumnos.ports import (
    AlumnoRepositoryPort,
    AlumnosParalelosRepositoryPort,
)
from app.kernel.domain.alumnos.errors import (
    AlumnoNoEncontradoError,
    AsignacionParaleloDuplicadaError,
)


class AsignarAlumnoParaleloCU:
    """Asignar un alumno a un paralelo."""

    def __init__(
        self,
        alumno_repo: AlumnoRepositoryPort,
        alumnos_paralelos_repo: AlumnosParalelosRepositoryPort,
    ):
        self.alumno_repo = alumno_repo
        self.alumnos_paralelos_repo = alumnos_paralelos_repo

    async def ejecutar(
        self,
        alumno_id: int,
        paralelo_id: int,
        asignado_por_id: int,
    ) -> AlumnoParaleloEntidad:
        alumno = await self.alumno_repo.obtener_por_id(alumno_id)
        if not alumno:
            raise AlumnoNoEncontradoError(alumno_id=alumno_id)

        existentes = await self.alumnos_paralelos_repo.listar_por_alumno(alumno_id)
        for a in existentes:
            if a.paralelo_id == paralelo_id:
                raise AsignacionParaleloDuplicadaError(alumno_id=alumno_id, paralelo_id=paralelo_id)

        asignacion = AlumnoParaleloEntidad(
            alumno_id=alumno_id,
            paralelo_id=paralelo_id,
            asignado_por_id=asignado_por_id,
            creado_en=datetime.utcnow(),
        )
        return await self.alumnos_paralelos_repo.crear(asignacion)

from app.kernel.domain.alumnos.ports import AlumnosParalelosRepositoryPort
from app.kernel.domain.alumnos.errors import AsignacionParaleloNoEncontradaError


class EliminarAsignacionParaleloCU:
    """Eliminar asignación alumno–paralelo."""

    def __init__(self, alumnos_paralelos_repo: AlumnosParalelosRepositoryPort):
        self.alumnos_paralelos_repo = alumnos_paralelos_repo

    async def ejecutar(self, asignacion_id: int) -> bool:
        actual = await self.alumnos_paralelos_repo.obtener_por_id(asignacion_id)
        if not actual:
            raise AsignacionParaleloNoEncontradaError(asignacion_id=asignacion_id)
        return await self.alumnos_paralelos_repo.eliminar(asignacion_id)

from app.kernel.domain.alumnos.ports import TutorRepositoryPort
from app.kernel.domain.alumnos.errors import TutorNoEncontradoError, TutorSinAlumnosError


class EliminarTutorCU:
    """Eliminar (o desactivar) un tutor."""

    def __init__(self, tutor_repo: TutorRepositoryPort):
        self.tutor_repo = tutor_repo

    async def ejecutar(self, tutor_id: int) -> bool:
        tutor = await self.tutor_repo.obtener_por_id(tutor_id)
        if not tutor:
            raise TutorNoEncontradoError(tutor_id=tutor_id)

        # Regla de negocio futura: verificar si tiene alumnos activos, etc.
        # Ej: if await self.tutor_repo.tiene_alumnos_activos(tutor_id): raise TutorSinAlumnosError(tutor_id)

        return await self.tutor_repo.eliminar(tutor_id)

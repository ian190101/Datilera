from app.kernel.domain.alumnos.ports import AlumnoTutorRepositoryPort
from app.kernel.domain.alumnos.errors import RelacionAlumnoTutorNoEncontradaError


class EliminarRelacionTutorCU:
    """Eliminar relación alumno-tutor."""

    def __init__(self, relacion_repo: AlumnoTutorRepositoryPort):
        self.relacion_repo = relacion_repo

    async def ejecutar(self, relacion_id: int) -> bool:
        actual = await self.relacion_repo.obtener_por_id(relacion_id)
        if not actual:
            raise RelacionAlumnoTutorNoEncontradaError()
        return await self.relacion_repo.eliminar(relacion_id)

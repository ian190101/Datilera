from app.kernel.domain.alumnos.ports import AlumnosHermanosRepositoryPort
from app.kernel.domain.alumnos.errors import HermanoNoEncontradoError


class EliminarHermanoCU:
    """Eliminar registro de hermano."""

    def __init__(self, hermanos_repo: AlumnosHermanosRepositoryPort):
        self.hermanos_repo = hermanos_repo

    async def ejecutar(self, hermano_id: int) -> bool:
        hermano = await self.hermanos_repo.obtener_por_id(hermano_id)
        if not hermano:
            raise HermanoNoEncontradoError(hermano_id=hermano_id)
        return await self.hermanos_repo.eliminar(hermano_id)

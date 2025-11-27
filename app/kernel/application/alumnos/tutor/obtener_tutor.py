from app.kernel.domain.alumnos.tutor_entidad import TutorEntidad
from app.kernel.domain.alumnos.ports import TutorRepositoryPort
from app.kernel.domain.alumnos.errors import TutorNoEncontradoError


class ObtenerTutorCU:
    """Obtener tutor por ID o documento."""

    def __init__(self, tutor_repo: TutorRepositoryPort):
        self.tutor_repo = tutor_repo

    async def por_id(self, tutor_id: int) -> TutorEntidad:
        tutor = await self.tutor_repo.obtener_por_id(tutor_id)
        if not tutor:
            raise TutorNoEncontradoError(tutor_id=tutor_id)
        return tutor

    async def por_documento(self, documento: str) -> TutorEntidad:
        tutor = await self.tutor_repo.obtener_por_documento(documento)
        if not tutor:
            raise TutorNoEncontradoError(documento=documento)
        return tutor

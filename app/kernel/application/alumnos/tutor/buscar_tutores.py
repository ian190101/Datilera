from typing import List

from app.kernel.domain.alumnos.tutor_entidad import TutorEntidad
from app.kernel.domain.alumnos.ports import TutorRepositoryPort


class BuscarTutoresCU:
    """Buscar tutores por nombre o documento."""

    def __init__(self, tutor_repo: TutorRepositoryPort):
        self.tutor_repo = tutor_repo

    async def ejecutar(self, termino: str) -> List[TutorEntidad]:
        return await self.tutor_repo.buscar(termino.strip())

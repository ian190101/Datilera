from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.academico.horarios import Horario
from app.infrastructure.db.repositories.base import BaseRepository


class HorariosRepository(BaseRepository[Horario]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Horario)

    async def exists_nombre_ci(self, *, nombre: str, excluir_id: int | None = None) -> bool:
        condiciones = [func.lower(Horario.nombre) == nombre.strip().lower()]
        if excluir_id is not None:
            condiciones.append(Horario.id != excluir_id)
        resultado = await self.session.execute(select(Horario.id).where(*condiciones).limit(1))
        return resultado.scalar_one_or_none() is not None

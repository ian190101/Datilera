# app/infrastructure/db/repositories/inscripcion/formularios_respuestas_repo.py
from typing import List  # <-- esto es nuevo
from sqlalchemy import select  # <-- esto es nuevo
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inscripcion import FormularioRespuesta


class FormularioRespuestaRepository(BaseRepository[FormularioRespuesta]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, FormularioRespuesta)
    async def listar_por_seccion(self, formulario_id: int, seccion: str) -> List[FormularioRespuesta]:  # <-- esto es nuevo
        res = await self.session.execute(  # <-- esto es nuevo
            select(FormularioRespuesta).where(  # <-- esto es nuevo
                FormularioRespuesta.formulario_id == formulario_id,  # <-- esto es nuevo
                FormularioRespuesta.seccion == seccion  # <-- esto es nuevo
            )  # <-- esto es nuevo
        )  # <-- esto es nuevo
        return res.scalars().all()  # <-- esto es nuevo
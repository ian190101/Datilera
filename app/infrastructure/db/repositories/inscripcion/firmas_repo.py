# app/infrastructure/db/repositories/inscripcion/firmas_repo.py
from typing import Optional  # <-- esto es nuevo
from sqlalchemy import select, delete  # <-- esto es nuevo
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inscripcion import Firma


class FirmaRepository(BaseRepository[Firma]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Firma)
    async def obtener_por_formulario_y_tipo(self, formulario_id: int, tipo: str) -> Optional[Firma]:  # <-- esto es nuevo
        res = await self.session.execute(  # <-- esto es nuevo
            select(Firma).where(Firma.formulario_id == formulario_id, Firma.tipo_firmante == tipo)  # <-- esto es nuevo
        )  # <-- esto es nuevo
        return res.scalar_one_or_none()  # <-- esto es nuevo

    async def crear_o_reemplazar(self, formulario_id: int, tipo: str, payload: dict) -> Firma:  # <-- esto es nuevo
        await self.session.execute(  # <-- esto es nuevo
            delete(Firma).where(Firma.formulario_id == formulario_id, Firma.tipo_firmante == tipo)  # <-- esto es nuevo
        )  # <-- esto es nuevo
        firma = Firma(**payload)  # <-- esto es nuevo
        self.session.add(firma)  # <-- esto es nuevo
        await self.session.flush()  # <-- esto es nuevo
        await self.session.refresh(firma)  # <-- esto es nuevo
        return firma  # <-- esto es nuevo

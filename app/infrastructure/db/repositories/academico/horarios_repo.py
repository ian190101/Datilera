# app/infrastructure/db/repositories/academico/horarios_repo.py
"""Repositorio para la entidad Horario."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence
from app.infrastructure.db.models.academico.horarios import Horario as HorarioModel
from app.infrastructure.db.repositories.base import BaseRepository

class HorariosRepository(BaseRepository[HorarioModel]):
    """Repositorio concreto para gestionar horarios."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, HorarioModel)
    
    async def list_ordenados(self) -> Sequence[HorarioModel]:
        """
        Lista horarios ordenados por hora de inicio.
        
        Returns:
            Lista de horarios ordenados
        """
        stmt = select(self.model).order_by(self.model.hora_inicio)
        result = await self.session.execute(stmt)
        return result.scalars().all()

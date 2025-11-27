# app/infrastructure/db/repositories/academico/horarios_paralelos_repo.py
"""Repositorio para la entidad HorarioParalelo."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Sequence
from datetime import date
from app.infrastructure.db.models.academico.horarios_paralelos import HorarioParalelo as HorarioParaleloModel
from app.infrastructure.db.repositories.base import BaseRepository

class HorariosParalelosRepository(BaseRepository[HorarioParaleloModel]):
    """Repositorio concreto para gestionar relaciones horario-paralelo."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, HorarioParaleloModel)
    
    async def list_by_paralelo(self, paralelo_id: int) -> Sequence[HorarioParaleloModel]:
        """
        Lista todas las asignaciones de horario de un paralelo.
        
        Args:
            paralelo_id: ID del paralelo
        
        Returns:
            Lista de horarios del paralelo
        """
        stmt = select(self.model).where(
            self.model.paralelo_id == paralelo_id
        ).order_by(self.model.desde.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def list_vigentes_by_paralelo(
        self, 
        paralelo_id: int, 
        fecha: date | None = None
    ) -> Sequence[HorarioParaleloModel]:
        """
        Lista horarios vigentes de un paralelo en una fecha.
        
        Args:
            paralelo_id: ID del paralelo
            fecha: Fecha de referencia (por defecto hoy)
        
        Returns:
            Lista de horarios vigentes
        """
        if fecha is None:
            fecha = date.today()
        
        stmt = select(self.model).where(
            self.model.paralelo_id == paralelo_id,
            self.model.desde <= fecha,
            self.model.hasta >= fecha
        ).order_by(self.model.desde.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def delete(self, id_: int) -> None:
        """
        Elimina físicamente una asignación horario-paralelo.
        
        Args:
            id_: ID de la asignación a eliminar
        """
        stmt = delete(self.model).where(self.model.id == id_)
        await self.session.execute(stmt)

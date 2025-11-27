# app/infrastructure/db/repositories/academico/paralelos_repo.py
"""Repositorio para la entidad Paralelo."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Sequence
from app.infrastructure.db.models.academico.paralelos import Paralelo as ParaleloModel
from app.infrastructure.db.repositories.base import BaseRepository

class ParalelosRepository(BaseRepository[ParaleloModel]):
    """Repositorio concreto para gestionar paralelos."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ParaleloModel)
    
    async def list_by_grupo(self, grupo_id: int) -> Sequence[ParaleloModel]:
        """
        Lista todos los paralelos de un grupo.
        
        Args:
            grupo_id: ID del grupo
        
        Returns:
            Lista de paralelos del grupo
        """
        stmt = select(self.model).where(
            self.model.grupo_id == grupo_id
        ).order_by(self.model.id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def delete(self, id_: int) -> None:
        """
        Elimina físicamente un paralelo.
        
        Args:
            id_: ID del paralelo a eliminar
        """
        stmt = delete(self.model).where(self.model.id == id_)
        await self.session.execute(stmt)

# app/infrastructure/db/repositories/academico/grupos_repo.py
"""Repositorio para la entidad Grupo."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence
from app.infrastructure.db.models.academico.grupos import Grupo as GrupoModel
from app.infrastructure.db.repositories.base import BaseRepository

class GruposRepository(BaseRepository[GrupoModel]):
    """Repositorio concreto para gestionar grupos."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, GrupoModel)
    
    async def list_by_sede(self, sede_id: int) -> Sequence[GrupoModel]:
        """
        Lista todos los grupos de una sede.
        
        Args:
            sede_id: ID de la sede
        
        Returns:
            Lista de grupos de la sede
        """
        stmt = select(self.model).where(
            self.model.sede_id == sede_id
        ).order_by(self.model.gestion.desc(), self.model.letra)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def list_by_sede_gestion(self, sede_id: int, gestion: int) -> Sequence[GrupoModel]:
        """
        Lista grupos de una sede en una gestión específica.
        
        Args:
            sede_id: ID de la sede
            gestion: Año de gestión
        
        Returns:
            Lista de grupos filtrados
        """
        stmt = select(self.model).where(
            self.model.sede_id == sede_id,
            self.model.gestion == gestion
        ).order_by(self.model.letra)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def list_activos_by_sede(self, sede_id: int) -> Sequence[GrupoModel]:
        """
        Lista solo los grupos activos de una sede.
        
        Args:
            sede_id: ID de la sede
        
        Returns:
            Lista de grupos activos
        """
        stmt = select(self.model).where(
            self.model.sede_id == sede_id,
            self.model.activo == True
        ).order_by(self.model.gestion.desc(), self.model.letra)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def soft_delete(self, id_: int) -> None:
        """
        Desactiva un grupo (soft delete).
        
        Args:
            id_: ID del grupo a desactivar
        """
        await self.update(id_, {"activo": False})

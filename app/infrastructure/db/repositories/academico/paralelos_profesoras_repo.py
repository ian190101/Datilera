# app/infrastructure/db/repositories/academico/paralelos_profesoras_repo.py
"""Repositorio para la entidad ParaleloProfesor."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Sequence
from datetime import date
from app.infrastructure.db.models.academico.paralelos_profesoras import ParaleloProfesora as ParaleloProfesoraModel
from app.infrastructure.db.repositories.base import BaseRepository

class ParalelosProfesorasRepository(BaseRepository[ParaleloProfesoraModel]):
    """Repositorio concreto para gestionar relaciones paralelo-profesor."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ParaleloProfesoraModel)
    
    async def list_by_paralelo(self, paralelo_id: int) -> Sequence[ParaleloProfesoraModel]:
        """
        Lista todas las asignaciones de profesores de un paralelo.
        
        Args:
            paralelo_id: ID del paralelo
        
        Returns:
            Lista de profesores asignados al paralelo
        """
        stmt = select(self.model).where(
            self.model.paralelo_id == paralelo_id
        ).order_by(self.model.desde.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def list_by_profesor(self, profesor_id: int) -> Sequence[ParaleloProfesoraModel]:
        """
        Lista todas las asignaciones de un profesor.
        
        Args:
            profesor_id: ID del profesor
        
        Returns:
            Lista de paralelos asignados al profesor
        """
        stmt = select(self.model).where(
            self.model.profesor_id == profesor_id
        ).order_by(self.model.gestion.desc(), self.model.desde.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def list_vigentes_by_paralelo(
        self, 
        paralelo_id: int, 
        fecha: date | None = None
    ) -> Sequence[ParaleloProfesoraModel]:
        """
        Lista profesores vigentes de un paralelo en una fecha.
        
        Args:
            paralelo_id: ID del paralelo
            fecha: Fecha de referencia (por defecto hoy)
        
        Returns:
            Lista de profesores vigentes
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
    
    async def list_vigentes_by_profesor(
        self, 
        profesor_id: int, 
        fecha: date | None = None
    ) -> Sequence[ParaleloProfesoraModel]:
        """
        Lista paralelos vigentes asignados a un profesor en una fecha.
        
        Args:
            profesor_id: ID del profesor
            fecha: Fecha de referencia (por defecto hoy)
        
        Returns:
            Lista de paralelos vigentes del profesor
        """
        if fecha is None:
            fecha = date.today()
        
        stmt = select(self.model).where(
            self.model.profesor_id == profesor_id,
            self.model.desde <= fecha,
            self.model.hasta >= fecha
        ).order_by(self.model.gestion.desc(), self.model.desde.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def delete(self, id_: int) -> None:
        """
        Elimina físicamente una asignación paralelo-profesor.
        
        Args:
            id_: ID de la asignación a eliminar
        """
        stmt = delete(self.model).where(self.model.id == id_)
        await self.session.execute(stmt)

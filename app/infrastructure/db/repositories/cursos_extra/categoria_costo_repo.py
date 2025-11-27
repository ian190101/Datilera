"""
Repositorio para operaciones de Categorías de Costo de Cursos Extra.
"""
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.cursos_extra import CategoriaCostoCursoExtra


class CategoriaCostoCursoExtraRepository(BaseRepository[CategoriaCostoCursoExtra]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CategoriaCostoCursoExtra)

    async def listar_por_curso(
        self,
        curso_id: int,
        activo: Optional[bool] = None
    ) -> List[CategoriaCostoCursoExtra]:
        """Lista categorías de un curso."""
        query = select(CategoriaCostoCursoExtra).where(
            CategoriaCostoCursoExtra.curso_extra_id == curso_id
        )

        if activo is not None:
            query = query.where(CategoriaCostoCursoExtra.activo == activo)

        query = query.order_by(CategoriaCostoCursoExtra.nombre)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def activar_desactivar(
        self,
        categoria_id: int,
        activo: bool
    ) -> Optional[CategoriaCostoCursoExtra]:
        """Activa o desactiva una categoría."""
        query = update(CategoriaCostoCursoExtra).where(
            CategoriaCostoCursoExtra.id == categoria_id
        ).values(activo=activo).returning(CategoriaCostoCursoExtra)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def existe_por_nombre(
        self,
        nombre: str,
        curso_id: int,
        excluir_id: Optional[int] = None
    ) -> bool:
        """Verifica si existe una categoría con ese nombre en el curso."""
        conditions = [
            CategoriaCostoCursoExtra.curso_extra_id == curso_id,
            CategoriaCostoCursoExtra.nombre.ilike(nombre)
        ]

        if excluir_id is not None:
            conditions.append(CategoriaCostoCursoExtra.id != excluir_id)

        query = select(CategoriaCostoCursoExtra).where(and_(*conditions))

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def buscar_por_nombre(
        self,
        nombre: str,
        curso_id: Optional[int] = None,
        limite: int = 20
    ) -> List[CategoriaCostoCursoExtra]:
        """Busca categorías por nombre."""
        query = select(CategoriaCostoCursoExtra).where(
            CategoriaCostoCursoExtra.nombre.ilike(f"%{nombre}%")
        )

        if curso_id is not None:
            query = query.where(CategoriaCostoCursoExtra.curso_extra_id == curso_id)

        query = query.order_by(CategoriaCostoCursoExtra.nombre).limit(limite)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def contar_por_curso(self, curso_id: int, activo: Optional[bool] = None) -> int:
        """Cuenta categorías de un curso."""
        from sqlalchemy import func

        query = select(func.count(CategoriaCostoCursoExtra.id)).where(
            CategoriaCostoCursoExtra.curso_extra_id == curso_id
        )

        if activo is not None:
            query = query.where(CategoriaCostoCursoExtra.activo == activo)

        result = await self.session.execute(query)
        return result.scalar() or 0

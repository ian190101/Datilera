# app/infrastructure/db/repositories/finanzas/categorias_egreso_repo.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models.finanzas import CategoriaEgreso as CategoriaEgresoModel
from app.kernel.domain.finanzas import CategoriaEgreso


class CategoriaEgresoRepository:
    """Repositorio para gestión de categorías de egreso"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, categoria: CategoriaEgreso) -> CategoriaEgreso:
        """Crea una nueva categoría de egreso"""
        modelo = CategoriaEgresoModel(
            sede_id=categoria.sede_id,
            nombre=categoria.nombre,
            descripcion=categoria.descripcion,
            activo=categoria.activa
        )
        self.session.add(modelo)
        await self.session.flush()
        await self.session.refresh(modelo)
        
        return self._to_entity(modelo)

    async def obtener_por_id(self, categoria_id: int) -> Optional[CategoriaEgreso]:
        """Obtiene una categoría por ID"""
        stmt = select(CategoriaEgresoModel).where(CategoriaEgresoModel.id == categoria_id)
        result = await self.session.execute(stmt)
        modelo = result.scalar_one_or_none()
        return self._to_entity(modelo) if modelo else None

    async def listar_por_sede(self, sede_id: int, solo_activas: bool = True) -> List[CategoriaEgreso]:
        """Lista categorías de egreso de una sede"""
        stmt = select(CategoriaEgresoModel).where(CategoriaEgresoModel.sede_id == sede_id)
        
        if solo_activas:
            stmt = stmt.where(CategoriaEgresoModel.activo == True)
        
        stmt = stmt.order_by(CategoriaEgresoModel.nombre)
        result = await self.session.execute(stmt)
        modelos = result.scalars().all()
        
        return [self._to_entity(m) for m in modelos]

    async def actualizar(self, categoria: CategoriaEgreso) -> CategoriaEgreso:
        """Actualiza una categoría de egreso"""
        stmt = select(CategoriaEgresoModel).where(CategoriaEgresoModel.id == categoria.id)
        result = await self.session.execute(stmt)
        modelo = result.scalar_one()
        
        modelo.nombre = categoria.nombre
        modelo.descripcion = categoria.descripcion
        modelo.activo = categoria.activa
        
        await self.session.flush()
        await self.session.refresh(modelo)
        
        return self._to_entity(modelo)

    async def existe_nombre_en_sede(self, sede_id: int, nombre: str, excluir_id: Optional[int] = None) -> bool:
        """Verifica si existe una categoría con ese nombre en la sede"""
        stmt = select(CategoriaEgresoModel).where(
            CategoriaEgresoModel.sede_id == sede_id,
            CategoriaEgresoModel.nombre == nombre
        )
        
        if excluir_id:
            stmt = stmt.where(CategoriaEgresoModel.id != excluir_id)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _to_entity(self, modelo: CategoriaEgresoModel) -> CategoriaEgreso:
        """Convierte modelo SQLAlchemy a entidad de dominio"""
        return CategoriaEgreso(
            id=modelo.id,
            sede_id=modelo.sede_id,
            nombre=modelo.nombre,
            descripcion=modelo.descripcion,
            activa=modelo.activo,
            creado_en=modelo.creado_en
        )

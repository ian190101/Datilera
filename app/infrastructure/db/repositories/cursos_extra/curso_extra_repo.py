"""
Repositorio para operaciones de Cursos Extra.
"""
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.cursos_extra import CursoExtra


class CursoExtraRepository(BaseRepository[CursoExtra]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CursoExtra)

    async def obtener_por_sede(
        self,
        sede_id: int,
        activo: Optional[bool] = None,
        gestion: Optional[int] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[CursoExtra]:
        """Lista cursos de una sede con filtros opcionales."""
        query = select(CursoExtra).where(CursoExtra.sede_id == sede_id)

        if activo is not None:
            query = query.where(CursoExtra.activo == activo)

        if gestion is not None:
            query = query.where(CursoExtra.gestion == gestion)

        query = query.order_by(
            CursoExtra.fecha_inicio.desc()
        ).limit(limite).offset(offset)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def activar_desactivar(self, curso_id: int, activo: bool) -> Optional[CursoExtra]:
        """Activa o desactiva un curso."""
        query = update(CursoExtra).where(
            CursoExtra.id == curso_id
        ).values(activo=activo).returning(CursoExtra)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def incrementar_inscritos(self, curso_id: int) -> Optional[CursoExtra]:
        """Incrementa el contador de inscritos actuales."""
        query = update(CursoExtra).where(
            CursoExtra.id == curso_id
        ).values(
            inscritos_actuales=CursoExtra.inscritos_actuales + 1
        ).returning(CursoExtra)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def decrementar_inscritos(self, curso_id: int) -> Optional[CursoExtra]:
        """Decrementa el contador de inscritos actuales."""
        query = update(CursoExtra).where(
            and_(
                CursoExtra.id == curso_id,
                CursoExtra.inscritos_actuales > 0
            )
        ).values(
            inscritos_actuales=CursoExtra.inscritos_actuales - 1
        ).returning(CursoExtra)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def verificar_cupos_disponibles(self, curso_id: int) -> bool:
        """Verifica si hay cupos disponibles."""
        query = select(CursoExtra).where(
            and_(
                CursoExtra.id == curso_id,
                CursoExtra.inscritos_actuales < CursoExtra.cupo_maximo
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def buscar_por_nombre(
        self,
        nombre: str,
        sede_id: Optional[int] = None,
        limite: int = 20
    ) -> List[CursoExtra]:
        """Busca cursos por nombre (búsqueda parcial)."""
        query = select(CursoExtra).where(
            CursoExtra.nombre.ilike(f"%{nombre}%")
        )

        if sede_id is not None:
            query = query.where(CursoExtra.sede_id == sede_id)

        query = query.order_by(CursoExtra.nombre).limit(limite)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obtener_por_instructor(
        self,
        instructor: str,
        sede_id: Optional[int] = None
    ) -> List[CursoExtra]:
        """Lista cursos por instructor."""
        query = select(CursoExtra).where(
            CursoExtra.instructor.ilike(f"%{instructor}%")
        )

        if sede_id is not None:
            query = query.where(CursoExtra.sede_id == sede_id)

        query = query.order_by(CursoExtra.fecha_inicio.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obtener_activos_con_cupos(self, sede_id: int) -> List[CursoExtra]:
        """Obtiene cursos activos que aún tienen cupos disponibles."""
        query = select(CursoExtra).where(
            and_(
                CursoExtra.sede_id == sede_id,
                CursoExtra.activo == True,
                CursoExtra.inscritos_actuales < CursoExtra.cupo_maximo
            )
        ).order_by(CursoExtra.fecha_inicio)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obtener_por_rango_fechas(
        self,
        fecha_desde: date,
        fecha_hasta: date,
        sede_id: Optional[int] = None
    ) -> List[CursoExtra]:
        """Obtiene cursos en un rango de fechas."""
        query = select(CursoExtra).where(
            or_(
                and_(
                    CursoExtra.fecha_inicio >= fecha_desde,
                    CursoExtra.fecha_inicio <= fecha_hasta
                ),
                and_(
                    CursoExtra.fecha_fin.isnot(None),
                    CursoExtra.fecha_fin >= fecha_desde,
                    CursoExtra.fecha_fin <= fecha_hasta
                )
            )
        )

        if sede_id is not None:
            query = query.where(CursoExtra.sede_id == sede_id)

        query = query.order_by(CursoExtra.fecha_inicio)

        result = await self.session.execute(query)
        return result.scalars().all()

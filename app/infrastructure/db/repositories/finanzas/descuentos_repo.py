# app/infrastructure/db/repositories/finanzas/descuentos_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from typing import Optional, Sequence
from datetime import date

from app.infrastructure.db.models.finanzas import Descuento


class DescuentosRepository:
    """Repositorio para gestión de descuentos."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def crear(self, data: dict) -> Descuento:
        """Crear un nuevo descuento."""
        descuento = Descuento(**data)
        self.session.add(descuento)
        await self.session.commit()
        await self.session.refresh(descuento)
        return descuento
    
    async def obtener_por_id(self, id: int) -> Optional[Descuento]:
        """Obtener descuento por ID."""
        result = await self.session.execute(
            select(Descuento).where(Descuento.id == id)
        )
        return result.scalar_one_or_none()
    
    async def obtener_activo_por_alumno(self, alumno_id: int) -> Optional[Descuento]:
        """Obtener descuento activo de un alumno.
        
        Retorna el descuento vigente (estado='activo' y periodo no vencido).
        """
        fecha_actual = date.today()
        result = await self.session.execute(
            select(Descuento).where(
                and_(
                    Descuento.alumno_id == alumno_id,
                    Descuento.estado == 'activo',
                    Descuento.periodo_inicio <= fecha_actual,
                    Descuento.periodo_fin >= fecha_actual
                )
            ).order_by(Descuento.periodo_fin.desc())
        )
        return result.scalar_one_or_none()
    
    async def listar_por_alumno(
        self, 
        alumno_id: int,
        solo_activos: bool = False
    ) -> Sequence[Descuento]:
        """Listar todos los descuentos de un alumno."""
        query = select(Descuento).where(Descuento.alumno_id == alumno_id)
        
        if solo_activos:
            query = query.where(Descuento.estado == 'activo')
        
        query = query.order_by(Descuento.aplicado_en.desc())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def listar_por_sede(
        self,
        sede_id: int,
        tipo: Optional[str] = None,
        estado: Optional[str] = None
    ) -> Sequence[Descuento]:
        """Listar descuentos de una sede con filtros opcionales."""
        query = select(Descuento).where(Descuento.sede_id == sede_id)
        
        if tipo:
            query = query.where(Descuento.tipo == tipo)
        if estado:
            query = query.where(Descuento.estado == estado)
        
        query = query.order_by(Descuento.aplicado_en.desc())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def actualizar(self, id: int, data: dict) -> Optional[Descuento]:
        """Actualizar descuento (ej: cambiar estado a 'vencido' o 'cancelado')."""
        descuento = await self.obtener_por_id(id)
        if descuento:
            for key, value in data.items():
                setattr(descuento, key, value)
            await self.session.commit()
            await self.session.refresh(descuento)
        return descuento
    
    async def cancelar(self, id: int) -> Optional[Descuento]:
        """Cancelar un descuento (cambiar estado a 'cancelado')."""
        return await self.actualizar(id, {'estado': 'cancelado'})
    
    async def verificar_elegibilidad(
        self, 
        alumno_id: int,
        tipo_descuento: str
    ) -> bool:
        """Verificar si un alumno puede aplicar un descuento.
        
        Retorna False si ya tiene un descuento activo del mismo tipo.
        """
        descuento_activo = await self.obtener_activo_por_alumno(alumno_id)
        
        if descuento_activo and descuento_activo.tipo == tipo_descuento:
            return False
        
        return True

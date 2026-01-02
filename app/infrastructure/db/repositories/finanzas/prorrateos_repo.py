# app/infrastructure/db/repositories/finanzas/prorrateos_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import Optional, Sequence
from datetime import date

from app.infrastructure.db.models.finanzas import Prorrateo


class ProrrateosRepository:
    """Repositorio para gestión de prorrateos."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def crear(self, data: dict) -> Prorrateo:
        """Crear un nuevo cálculo de prorrateo."""
        prorrateo = Prorrateo(**data)
        self.session.add(prorrateo)
        await self.session.commit()
        await self.session.refresh(prorrateo)
        return prorrateo
    
    async def obtener_por_id(self, id: int) -> Optional[Prorrateo]:
        """Obtener prorrateo por ID."""
        result = await self.session.execute(
            select(Prorrateo).where(Prorrateo.id == id)
        )
        return result.scalar_one_or_none()
    
    async def obtener_por_alumno(
        self, 
        alumno_id: int,
        solo_aplicados: bool = False
    ) -> Optional[Prorrateo]:
        """Obtener prorrateo de un alumno.
        
        Generalmente un alumno solo tiene un prorrateo (primer mes).
        """
        query = select(Prorrateo).where(Prorrateo.alumno_id == alumno_id)
        
        if solo_aplicados:
            query = query.where(Prorrateo.aplicado == True)
        
        query = query.order_by(Prorrateo.fecha_ingreso.desc())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def listar_por_sede(
        self,
        sede_id: int,
        aplicado: Optional[bool] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> Sequence[Prorrateo]:
        """Listar prorrateos de una sede con filtros."""
        query = select(Prorrateo).where(Prorrateo.sede_id == sede_id)
        
        if aplicado is not None:
            query = query.where(Prorrateo.aplicado == aplicado)
        if fecha_desde:
            query = query.where(Prorrateo.fecha_ingreso >= fecha_desde)
        if fecha_hasta:
            query = query.where(Prorrateo.fecha_ingreso <= fecha_hasta)
        
        query = query.order_by(Prorrateo.fecha_ingreso.desc())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def actualizar(self, id: int, data: dict) -> Optional[Prorrateo]:
        """Actualizar prorrateo."""
        prorrateo = await self.obtener_por_id(id)
        if prorrateo:
            for key, value in data.items():
                setattr(prorrateo, key, value)
            await self.session.commit()
            await self.session.refresh(prorrateo)
        return prorrateo
    
    async def marcar_como_aplicado(
        self, 
        id: int, 
        pago_id: int
    ) -> Optional[Prorrateo]:
        """Marcar prorrateo como aplicado (vinculado a un pago)."""
        return await self.actualizar(id, {
            'aplicado': True,
            'pago_id': pago_id
        })
    
    async def verificar_prorrateo_existente(self, alumno_id: int) -> bool:
        """Verificar si ya existe un prorrateo para un alumno."""
        prorrateo = await self.obtener_por_alumno(alumno_id)
        return prorrateo is not None

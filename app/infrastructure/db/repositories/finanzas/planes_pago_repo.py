# app/infrastructure/db/repositories/finanzas/planes_pago_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import Optional, Sequence
from datetime import date

from app.infrastructure.db.models.finanzas import PlanPagoPersonalizado


class PlanesPagoRepository:
    """Repositorio para gestión de planes de pago personalizados."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def crear(self, data: dict) -> PlanPagoPersonalizado:
        """Crear un nuevo plan de pago."""
        plan = PlanPagoPersonalizado(**data)
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan
    
    async def obtener_por_id(self, id: int) -> Optional[PlanPagoPersonalizado]:
        """Obtener plan de pago por ID."""
        result = await self.session.execute(
            select(PlanPagoPersonalizado).where(PlanPagoPersonalizado.id == id)
        )
        return result.scalar_one_or_none()
    
    async def obtener_por_alumno(self, alumno_id: int) -> Optional[PlanPagoPersonalizado]:
        """Obtener plan de pago de un alumno (solo puede tener uno activo)."""
        result = await self.session.execute(
            select(PlanPagoPersonalizado).where(
                and_(
                    PlanPagoPersonalizado.alumno_id == alumno_id,
                    PlanPagoPersonalizado.estado == 'activo'
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def listar_por_sede(
        self,
        sede_id: int,
        estado: Optional[str] = None
    ) -> Sequence[PlanPagoPersonalizado]:
        """Listar planes de pago de una sede."""
        query = select(PlanPagoPersonalizado).where(
            PlanPagoPersonalizado.sede_id == sede_id
        )
        
        if estado:
            query = query.where(PlanPagoPersonalizado.estado == estado)
        
        query = query.order_by(PlanPagoPersonalizado.fecha_inicio.desc())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def actualizar(self, id: int, data: dict) -> Optional[PlanPagoPersonalizado]:
        """Actualizar plan de pago."""
        plan = await self.obtener_por_id(id)
        if plan:
            for key, value in data.items():
                setattr(plan, key, value)
            await self.session.commit()
            await self.session.refresh(plan)
        return plan
    
    async def cambiar_estado(
        self, 
        id: int, 
        nuevo_estado: str
    ) -> Optional[PlanPagoPersonalizado]:
        """Cambiar estado del plan (activo, completado, cancelado)."""
        return await self.actualizar(id, {'estado': nuevo_estado})
    
    async def verificar_plan_activo(self, alumno_id: int) -> bool:
        """Verificar si un alumno ya tiene un plan activo."""
        plan = await self.obtener_por_alumno(alumno_id)
        return plan is not None

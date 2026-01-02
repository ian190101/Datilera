# app/infrastructure/db/repositories/finanzas/cuotas_plan_pago_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from typing import Optional, Sequence, Dict, Any
from datetime import date

from app.infrastructure.db.models.finanzas import CuotaPlanPago


class CuotasPlanPagoRepository:
    """Repositorio para gestión de cuotas de planes de pago."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def crear(self, data: dict) -> CuotaPlanPago:
        """Crear una nueva cuota."""
        cuota = CuotaPlanPago(**data)
        self.session.add(cuota)
        await self.session.commit()
        await self.session.refresh(cuota)
        return cuota
    
    async def crear_lote(self, cuotas_data: list[dict]) -> Sequence[CuotaPlanPago]:
        """Crear múltiples cuotas en lote (para generar tabla de amortización)."""
        cuotas = [CuotaPlanPago(**data) for data in cuotas_data]
        self.session.add_all(cuotas)
        await self.session.commit()
        
        # Refrescar todas las cuotas
        for cuota in cuotas:
            await self.session.refresh(cuota)
        
        return cuotas
    
    async def obtener_por_id(self, id: int) -> Optional[CuotaPlanPago]:
        """Obtener cuota por ID."""
        result = await self.session.execute(
            select(CuotaPlanPago).where(CuotaPlanPago.id == id)
        )
        return result.scalar_one_or_none()
    
    async def listar_por_plan(
        self, 
        plan_id: int,
        estado: Optional[str] = None
    ) -> Sequence[CuotaPlanPago]:
        """Listar todas las cuotas de un plan (tabla de amortización)."""
        query = select(CuotaPlanPago).where(CuotaPlanPago.plan_id == plan_id)
        
        if estado:
            query = query.where(CuotaPlanPago.estado == estado)
        
        query = query.order_by(CuotaPlanPago.numero_cuota.asc())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def obtener_cuota_por_numero(
        self, 
        plan_id: int, 
        numero_cuota: int
    ) -> Optional[CuotaPlanPago]:
        """Obtener una cuota específica por su número."""
        result = await self.session.execute(
            select(CuotaPlanPago).where(
                and_(
                    CuotaPlanPago.plan_id == plan_id,
                    CuotaPlanPago.numero_cuota == numero_cuota
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def listar_vencidas(
        self,
        fecha_actual: Optional[date] = None
    ) -> Sequence[CuotaPlanPago]:
        """Listar cuotas vencidas no pagadas."""
        if fecha_actual is None:
            fecha_actual = date.today()
        
        result = await self.session.execute(
            select(CuotaPlanPago).where(
                and_(
                    CuotaPlanPago.estado == 'pendiente',
                    CuotaPlanPago.fecha_vencimiento < fecha_actual
                )
            ).order_by(CuotaPlanPago.fecha_vencimiento.asc())
        )
        return result.scalars().all()
    
    async def actualizar(self, id: int, data: dict) -> Optional[CuotaPlanPago]:
        """Actualizar cuota (ej: marcar como pagada)."""
        cuota = await self.obtener_por_id(id)
        if cuota:
            for key, value in data.items():
                setattr(cuota, key, value)
            await self.session.commit()
            await self.session.refresh(cuota)
        return cuota
    
    async def marcar_como_pagada(
        self, 
        id: int, 
        pago_id: int,
        monto_pagado: float,
        fecha_pago: date
    ) -> Optional[CuotaPlanPago]:
        """Marcar cuota como pagada."""
        return await self.actualizar(id, {
            'estado': 'pagada',
            'pago_id': pago_id,
            'monto_pagado': monto_pagado,
            'fecha_pago': fecha_pago
        })
    
    async def obtener_resumen_plan(self, plan_id: int) -> Dict[str, Any]:
        """Obtener resumen de cuotas de un plan.
        
        Retorna totales: pagadas, pendientes, vencidas, monto total, monto pagado.
        """
        result = await self.session.execute(
            select(
                func.count(CuotaPlanPago.id).label('total_cuotas'),
                func.sum(CuotaPlanPago.monto_cuota).label('monto_total'),
                func.sum(CuotaPlanPago.monto_pagado).label('monto_pagado'),
                func.count(
                    CuotaPlanPago.id
                ).filter(CuotaPlanPago.estado == 'pagada').label('cuotas_pagadas'),
                func.count(
                    CuotaPlanPago.id
                ).filter(CuotaPlanPago.estado == 'pendiente').label('cuotas_pendientes'),
                func.count(
                    CuotaPlanPago.id
                ).filter(CuotaPlanPago.estado == 'vencida').label('cuotas_vencidas'),
            ).where(CuotaPlanPago.plan_id == plan_id)
        )
        
        row = result.first()
        
        if not row:
            return {
                'total_cuotas': 0,
                'monto_total': 0.0,
                'monto_pagado': 0.0,
                'cuotas_pagadas': 0,
                'cuotas_pendientes': 0,
                'cuotas_vencidas': 0,
            }
        
        return {
            'total_cuotas': row[0] or 0,
            'monto_total': float(row[1] or 0),
            'monto_pagado': float(row[2] or 0),
            'cuotas_pagadas': row[3] or 0,
            'cuotas_pendientes': row[4] or 0,
            'cuotas_vencidas': row[5] or 0,
        }

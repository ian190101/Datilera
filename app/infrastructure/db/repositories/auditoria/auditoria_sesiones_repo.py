# app/infrastructure/db/repositories/auditoria/auditoria_sesiones_repo.py

"""
Repositorio de infraestructura para Auditoría de Sesiones.
NO depende de entidades de dominio.
"""
from __future__ import annotations
from typing import Sequence, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, insert, update, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.auditoria.auditoria_sesiones import AuditoriaSesion as AuditoriaSesionModel


class AuditoriaSesionesRepository:
    """Repositorio puro de infraestructura para sesiones."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def registrar_inicio(
        self,
        sesion_id: int,
        usuario_id: int,
        sede_id: Optional[int],
        ip: Optional[str],
        user_agent: Optional[str],
        dispositivo_tipo: Optional[str],
    ) -> AuditoriaSesionModel:
        """Registra inicio de sesión."""
        stmt = insert(AuditoriaSesionModel).values(
            sesion_id=sesion_id,
            usuario_id=usuario_id,
            sede_id=sede_id,
            ip=ip,
            user_agent=user_agent,
            dispositivo_tipo=dispositivo_tipo,
            activa=True
        ).returning(AuditoriaSesionModel)
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one()

    async def actualizar_heartbeat(self, sesion_id: int) -> None:
        """Actualiza timestamp de última actividad."""
        stmt = update(AuditoriaSesionModel).where(
            AuditoriaSesionModel.sesion_id == sesion_id
        ).values(ultimo_heartbeat=datetime.utcnow())
        
        await self.session.execute(stmt)
        await self.session.flush()

    async def registrar_cierre(
        self,
        sesion_id: int,
        razon: str = "logout_manual"
    ) -> None:
        """Registra cierre de sesión."""
        stmt = update(AuditoriaSesionModel).where(
            AuditoriaSesionModel.sesion_id == sesion_id
        ).values(
            activa=False,
            fin_sesion=datetime.utcnow(),
            razon_cierre=razon
        )
        
        await self.session.execute(stmt)
        await self.session.flush()

    async def listar_activas(
        self,
        *,
        sede_id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> Sequence[AuditoriaSesionModel]:
        """Lista sesiones activas."""
        conds = [AuditoriaSesionModel.activa == True]
        
        if sede_id:
            conds.append(AuditoriaSesionModel.sede_id == sede_id)
        if usuario_id:
            conds.append(AuditoriaSesionModel.usuario_id == usuario_id)
        
        res = await self.session.execute(
            select(AuditoriaSesionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaSesionModel.ultimo_heartbeat))
        )
        return res.scalars().all()

    async def obtener_por_sesion_id(self, sesion_id: int) -> Optional[AuditoriaSesionModel]:
        """Obtiene una sesión por su sesion_id."""
        res = await self.session.execute(
            select(AuditoriaSesionModel)
            .where(AuditoriaSesionModel.sesion_id == sesion_id)
        )
        return res.scalar_one_or_none()

    async def contar_activas_por_usuario(self, usuario_id: int) -> int:
        """Cuenta sesiones activas de un usuario."""
        res = await self.session.execute(
            select(func.count(AuditoriaSesionModel.id))
            .where(
                and_(
                    AuditoriaSesionModel.usuario_id == usuario_id,
                    AuditoriaSesionModel.activa == True
                )
            )
        )
        return res.scalar_one()

    async def cerrar_inactivas(self, timeout_minutos: int = 30) -> int:
        """Cierra sesiones inactivas."""
        limite = datetime.utcnow() - timedelta(minutes=timeout_minutos)
        
        stmt = update(AuditoriaSesionModel).where(
            and_(
                AuditoriaSesionModel.activa == True,
                AuditoriaSesionModel.ultimo_heartbeat < limite
            )
        ).values(
            activa=False,
            fin_sesion=datetime.utcnow(),
            razon_cierre="timeout"
        )
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def forzar_cierre_usuario(self, usuario_id: int) -> int:
        """Cierra todas las sesiones activas de un usuario."""
        stmt = update(AuditoriaSesionModel).where(
            and_(
                AuditoriaSesionModel.usuario_id == usuario_id,
                AuditoriaSesionModel.activa == True
            )
        ).values(
            activa=False,
            fin_sesion=datetime.utcnow(),
            razon_cierre="forzado_admin"
        )
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def obtener_duracion_promedio_sesiones(
        self,
        *,
        usuario_id: Optional[int] = None,
        desde: Optional[datetime] = None
    ) -> Optional[float]:
        """Calcula duración promedio de sesiones (en minutos)."""
        conds = [AuditoriaSesionModel.fin_sesion.isnot(None)]
        
        if usuario_id:
            conds.append(AuditoriaSesionModel.usuario_id == usuario_id)
        if desde:
            conds.append(AuditoriaSesionModel.inicio_sesion >= desde)
        
        duracion_segundos = func.extract(
            'epoch',
            AuditoriaSesionModel.fin_sesion - AuditoriaSesionModel.inicio_sesion
        )
        
        stmt = select(func.avg(duracion_segundos) / 60).where(and_(*conds))
        
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

# app/infrastructure/db/repositories/auditoria/auditoria_cambios_repo.py

"""
Repositorio de infraestructura para Auditoría de Cambios.
NO depende de entidades de dominio.
"""
from __future__ import annotations
from typing import Sequence, Optional, List, Dict, Any
from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.auditoria.auditoria_cambios import AuditoriaCambio as AuditoriaCambioModel


class AuditoriaCambiosRepository:
    """Repositorio puro de infraestructura para cambios."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def registrar(
        self,
        auditoria_accion_id: int,
        campo: str,
        valor_anterior: Optional[str],
        valor_nuevo: Optional[str],
        tipo_dato: Optional[str],
    ) -> AuditoriaCambioModel:
        """Registra un cambio individual."""
        stmt = insert(AuditoriaCambioModel).values(
            auditoria_accion_id=auditoria_accion_id,
            campo=campo,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            tipo_dato=tipo_dato
        ).returning(AuditoriaCambioModel)
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one()

    async def registrar_multiples(
        self,
        cambios: List[Dict[str, Any]]
    ) -> None:
        """Registra múltiples cambios (bulk insert)."""
        if not cambios:
            return
        
        stmt = insert(AuditoriaCambioModel).values(cambios)
        await self.session.execute(stmt)
        await self.session.flush()

    async def listar_por_accion(
        self,
        auditoria_accion_id: int
    ) -> Sequence[AuditoriaCambioModel]:
        """Lista todos los cambios de una acción."""
        res = await self.session.execute(
            select(AuditoriaCambioModel)
            .where(AuditoriaCambioModel.auditoria_accion_id == auditoria_accion_id)
            .order_by(AuditoriaCambioModel.campo)
        )
        return res.scalars().all()

    async def listar_por_campo(
        self,
        auditoria_accion_id: int,
        campo: str
    ) -> Optional[AuditoriaCambioModel]:
        """Obtiene el cambio de un campo específico."""
        res = await self.session.execute(
            select(AuditoriaCambioModel)
            .where(
                and_(
                    AuditoriaCambioModel.auditoria_accion_id == auditoria_accion_id,
                    AuditoriaCambioModel.campo == campo
                )
            )
        )
        return res.scalar_one_or_none()

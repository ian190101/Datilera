# app/infrastructure/db/repositories/auditoria/auditoria_exportaciones_repo.py

"""
Repositorio de infraestructura para Auditoría de Exportaciones.
NO depende de entidades de dominio.
"""
from __future__ import annotations
from typing import Sequence, Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, insert, update, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.auditoria.auditoria_exportaciones import AuditoriaExportacion as AuditoriaExportacionModel


class AuditoriaExportacionesRepository:
    """Repositorio puro de infraestructura para exportaciones."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def registrar(
        self,
        usuario_id: Optional[int],
        sede_id: Optional[int],
        tipo: str,
        formato: str,
        total_registros: int,
        *,
        filtros: Optional[Dict[str, Any]] = None,
        columnas: Optional[List[str]] = None,
        ruta_archivo: Optional[str] = None,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
    ) -> AuditoriaExportacionModel:
        """Registra una nueva exportación."""
        stmt = insert(AuditoriaExportacionModel).values(
            usuario_id=usuario_id,
            sede_id=sede_id,
            tipo=tipo,
            formato=formato,
            filtros=filtros,
            total_registros=total_registros,
            columnas=columnas,
            ruta_archivo=ruta_archivo,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
        ).returning(AuditoriaExportacionModel)
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one()

    async def marcar_descargado(self, exportacion_id: int) -> None:
        """Marca una exportación como descargada."""
        stmt = update(AuditoriaExportacionModel).where(
            AuditoriaExportacionModel.id == exportacion_id
        ).values(descargado_en=datetime.utcnow())
        
        await self.session.execute(stmt)
        await self.session.flush()

    async def obtener_por_id(self, exportacion_id: int) -> Optional[AuditoriaExportacionModel]:
        """Obtiene una exportación por su ID."""
        res = await self.session.execute(
            select(AuditoriaExportacionModel)
            .where(AuditoriaExportacionModel.id == exportacion_id)
        )
        return res.scalar_one_or_none()

    async def listar_por_usuario(
        self,
        usuario_id: int,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        tipo: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Sequence[AuditoriaExportacionModel]:
        """Lista exportaciones de un usuario."""
        conds = [AuditoriaExportacionModel.usuario_id == usuario_id]
        
        if desde:
            conds.append(AuditoriaExportacionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaExportacionModel.creado_en <= hasta)
        if tipo:
            conds.append(AuditoriaExportacionModel.tipo == tipo)
        
        res = await self.session.execute(
            select(AuditoriaExportacionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaExportacionModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def listar_por_sede(
        self,
        sede_id: int,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Sequence[AuditoriaExportacionModel]:
        """Lista exportaciones de una sede."""
        conds = [AuditoriaExportacionModel.sede_id == sede_id]
        
        if desde:
            conds.append(AuditoriaExportacionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaExportacionModel.creado_en <= hasta)
        
        res = await self.session.execute(
            select(AuditoriaExportacionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaExportacionModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def listar_por_tipo(
        self,
        tipo: str,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Sequence[AuditoriaExportacionModel]:
        """Lista exportaciones por tipo."""
        conds = [AuditoriaExportacionModel.tipo == tipo]
        
        if desde:
            conds.append(AuditoriaExportacionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaExportacionModel.creado_en <= hasta)
        
        res = await self.session.execute(
            select(AuditoriaExportacionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaExportacionModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def listar_fallidas(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        limit: int = 50
    ) -> Sequence[AuditoriaExportacionModel]:
        """Lista exportaciones fallidas."""
        conds = [AuditoriaExportacionModel.exitoso == False]
        
        if sede_id:
            conds.append(AuditoriaExportacionModel.sede_id == sede_id)
        if desde:
            conds.append(AuditoriaExportacionModel.creado_en >= desde)
        
        res = await self.session.execute(
            select(AuditoriaExportacionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaExportacionModel.creado_en))
            .limit(limit)
        )
        return res.scalars().all()

    async def contar_por_tipo(
        self,
        *,
        usuario_id: Optional[int] = None,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta exportaciones agrupadas por tipo."""
        conds = []
        
        if usuario_id:
            conds.append(AuditoriaExportacionModel.usuario_id == usuario_id)
        if sede_id:
            conds.append(AuditoriaExportacionModel.sede_id == sede_id)
        if desde:
            conds.append(AuditoriaExportacionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaExportacionModel.creado_en <= hasta)
        
        stmt = select(
            AuditoriaExportacionModel.tipo,
            func.count(AuditoriaExportacionModel.id).label("total")
        )
        
        if conds:
            stmt = stmt.where(and_(*conds))
        
        stmt = stmt.group_by(AuditoriaExportacionModel.tipo)
        
        res = await self.session.execute(stmt)
        return {row.tipo: row.total for row in res.all()}

    async def contar_por_formato(
        self,
        *,
        tipo: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta exportaciones agrupadas por formato."""
        conds = []
        
        if tipo:
            conds.append(AuditoriaExportacionModel.tipo == tipo)
        if desde:
            conds.append(AuditoriaExportacionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaExportacionModel.creado_en <= hasta)
        
        stmt = select(
            AuditoriaExportacionModel.formato,
            func.count(AuditoriaExportacionModel.id).label("total")
        )
        
        if conds:
            stmt = stmt.where(and_(*conds))
        
        stmt = stmt.group_by(AuditoriaExportacionModel.formato)
        
        res = await self.session.execute(stmt)
        return {row.formato: row.total for row in res.all()}

    async def obtener_total_registros_exportados(
        self,
        *,
        usuario_id: Optional[int] = None,
        tipo: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> int:
        """Suma total de registros exportados."""
        conds = [AuditoriaExportacionModel.exitoso == True]
        
        if usuario_id:
            conds.append(AuditoriaExportacionModel.usuario_id == usuario_id)
        if tipo:
            conds.append(AuditoriaExportacionModel.tipo == tipo)
        if desde:
            conds.append(AuditoriaExportacionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaExportacionModel.creado_en <= hasta)
        
        stmt = select(
            func.sum(AuditoriaExportacionModel.total_registros)
        ).where(and_(*conds))
        
        res = await self.session.execute(stmt)
        total = res.scalar_one_or_none()
        return total if total else 0

    async def detectar_exportaciones_masivas(
        self,
        umbral_registros: int = 1000,
        ventana_horas: int = 1
    ) -> Sequence[AuditoriaExportacionModel]:
        """Detecta exportaciones masivas sospechosas."""
        desde = datetime.utcnow() - timedelta(hours=ventana_horas)
        
        res = await self.session.execute(
            select(AuditoriaExportacionModel)
            .where(
                and_(
                    AuditoriaExportacionModel.total_registros >= umbral_registros,
                    AuditoriaExportacionModel.creado_en >= desde,
                    AuditoriaExportacionModel.exitoso == True
                )
            )
            .order_by(desc(AuditoriaExportacionModel.total_registros))
        )
        return res.scalars().all()

    async def obtener_exportaciones_por_usuario_periodo(
        self,
        usuario_id: int,
        ventana_horas: int = 24
    ) -> Sequence[AuditoriaExportacionModel]:
        """Obtiene exportaciones de un usuario en las últimas N horas."""
        desde = datetime.utcnow() - timedelta(hours=ventana_horas)
        
        res = await self.session.execute(
            select(AuditoriaExportacionModel)
            .where(
                and_(
                    AuditoriaExportacionModel.usuario_id == usuario_id,
                    AuditoriaExportacionModel.creado_en >= desde
                )
            )
            .order_by(desc(AuditoriaExportacionModel.creado_en))
        )
        return res.scalars().all()

    async def limpiar_archivos_antiguos(self, dias: int = 7) -> int:
        """Marca para limpieza archivos antiguos."""
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        
        stmt = update(AuditoriaExportacionModel).where(
            and_(
                AuditoriaExportacionModel.creado_en < fecha_limite,
                AuditoriaExportacionModel.ruta_archivo.isnot(None)
            )
        ).values(ruta_archivo=None)
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

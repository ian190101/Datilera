# app/infrastructure/db/repositories/auditoria/auditoria_acciones_repo.py

"""
Repositorio de infraestructura para Auditoría de Acciones.

NO depende de entidades de dominio.
Trabaja solo con modelos SQLAlchemy y datos primitivos.
"""

from __future__ import annotations

from typing import Sequence, Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select, and_, func, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.auditoria.auditoria_acciones import (
    AuditoriaAccion as AuditoriaAccionModel,
)


class AuditoriaAccionesRepository:
    """
    Repositorio puro de infraestructura.
    Retorna modelos SQLAlchemy o datos primitivos.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========================================================================
    # MÉTODOS DE ESCRITURA
    # ========================================================================

    async def registrar(
        self,
        usuario_id: Optional[int],
        sede_id: Optional[int],
        entidad: str,
        accion: str,
        *,
        entidad_id: Optional[str] = None,
        datos_antes: Optional[Dict[str, Any]] = None,
        datos_despues: Optional[Dict[str, Any]] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        sesion_id: Optional[int] = None,
        nivel: str = "info",
        metodo_http: Optional[str] = None,
        endpoint: Optional[str] = None,
        codigo_respuesta: Optional[int] = None,
        duracion_ms: Optional[int] = None,
        descripcion: Optional[str] = None,
        tags: Optional[List[str]] = None,
        contexto: Optional[Dict[str, Any]] = None,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        stack_trace: Optional[str] = None,
        dispositivo_info: Optional[Dict[str, Any]] = None,
        geolocalizacion: Optional[Dict[str, Any]] = None,
    ) -> AuditoriaAccionModel:
        """
        Registra un evento de auditoría.

        Importante: para MySQL/MariaDB NO usamos INSERT..RETURNING.
        Se usa session.add + flush para obtener el id.
        """
        obj = AuditoriaAccionModel(
            usuario_id=usuario_id,
            sede_id=sede_id,
            entidad=entidad,
            entidad_id=entidad_id,
            accion=accion,
            datos_antes=datos_antes,
            datos_despues=datos_despues,
            ip=ip,
            user_agent=user_agent,
            sesion_id=sesion_id,
            nivel=nivel,
            metodo_http=metodo_http,
            endpoint=endpoint,
            codigo_respuesta=codigo_respuesta,
            duracion_ms=duracion_ms,
            descripcion=descripcion,
            tags=tags,
            contexto=contexto,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
            stack_trace=stack_trace,
            dispositivo_info=dispositivo_info,
            geolocalizacion=geolocalizacion,
        )
        self.session.add(obj)
        await self.session.flush()  # obj.id disponible aquí
        return obj

    # ========================================================================
    # MÉTODOS DE CONSULTA
    # ========================================================================

    async def listar_por_usuario(
        self,
        usuario_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AuditoriaAccionModel]:
        res = await self.session.execute(
            select(AuditoriaAccionModel)
            .where(AuditoriaAccionModel.usuario_id == usuario_id)
            .order_by(desc(AuditoriaAccionModel.creado_en))
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
        offset: int = 0,
    ) -> Sequence[AuditoriaAccionModel]:
        conds = [AuditoriaAccionModel.sede_id == sede_id]
        if desde:
            conds.append(AuditoriaAccionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaAccionModel.creado_en <= hasta)

        res = await self.session.execute(
            select(AuditoriaAccionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaAccionModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def listar_por_entidad(
        self,
        entidad: str,
        *,
        entidad_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AuditoriaAccionModel]:
        conds = [AuditoriaAccionModel.entidad == entidad]
        if entidad_id:
            conds.append(AuditoriaAccionModel.entidad_id == entidad_id)

        res = await self.session.execute(
            select(AuditoriaAccionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaAccionModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def listar_por_accion(
        self,
        accion: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AuditoriaAccionModel]:
        res = await self.session.execute(
            select(AuditoriaAccionModel)
            .where(AuditoriaAccionModel.accion == accion)
            .order_by(desc(AuditoriaAccionModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def listar_por_nivel(
        self,
        nivel: str,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AuditoriaAccionModel]:
        conds = [AuditoriaAccionModel.nivel == nivel]
        if desde:
            conds.append(AuditoriaAccionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaAccionModel.creado_en <= hasta)

        res = await self.session.execute(
            select(AuditoriaAccionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaAccionModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def listar_errores(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AuditoriaAccionModel]:
        conds = [AuditoriaAccionModel.exitoso == False]  # noqa: E712
        if sede_id:
            conds.append(AuditoriaAccionModel.sede_id == sede_id)
        if desde:
            conds.append(AuditoriaAccionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaAccionModel.creado_en <= hasta)

        res = await self.session.execute(
            select(AuditoriaAccionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaAccionModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def buscar_por_descripcion(
        self,
        termino: str,
        *,
        sede_id: Optional[int] = None,
        limit: int = 50,
    ) -> Sequence[AuditoriaAccionModel]:
        conds = [AuditoriaAccionModel.descripcion.ilike(f"%{termino}%")]
        if sede_id:
            conds.append(AuditoriaAccionModel.sede_id == sede_id)

        res = await self.session.execute(
            select(AuditoriaAccionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaAccionModel.creado_en))
            .limit(limit)
        )
        return res.scalars().all()

    async def listar_por_endpoint(
        self,
        endpoint: str,
        *,
        metodo_http: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AuditoriaAccionModel]:
        conds = [AuditoriaAccionModel.endpoint == endpoint]
        if metodo_http:
            conds.append(AuditoriaAccionModel.metodo_http == metodo_http)

        res = await self.session.execute(
            select(AuditoriaAccionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaAccionModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def listar_por_ip(
        self,
        ip: str,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AuditoriaAccionModel]:
        conds = [AuditoriaAccionModel.ip == ip]
        if desde:
            conds.append(AuditoriaAccionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaAccionModel.creado_en <= hasta)

        res = await self.session.execute(
            select(AuditoriaAccionModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaAccionModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def obtener_por_id(self, auditoria_id: int) -> Optional[AuditoriaAccionModel]:
        res = await self.session.execute(
            select(AuditoriaAccionModel).where(AuditoriaAccionModel.id == auditoria_id)
        )
        return res.scalar_one_or_none()

    # ========================================================================
    # ESTADÍSTICAS Y AGREGACIONES
    # ========================================================================

    async def contar_por_accion(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
    ) -> Dict[str, int]:
        conds: list[Any] = []
        if sede_id:
            conds.append(AuditoriaAccionModel.sede_id == sede_id)
        if desde:
            conds.append(AuditoriaAccionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaAccionModel.creado_en <= hasta)

        stmt = select(
            AuditoriaAccionModel.accion,
            func.count(AuditoriaAccionModel.id).label("total"),
        )
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.group_by(AuditoriaAccionModel.accion)

        res = await self.session.execute(stmt)
        return {row.accion: int(row.total) for row in res.all()}

    async def contar_por_entidad(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
    ) -> Dict[str, int]:
        conds: list[Any] = []
        if sede_id:
            conds.append(AuditoriaAccionModel.sede_id == sede_id)
        if desde:
            conds.append(AuditoriaAccionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaAccionModel.creado_en <= hasta)

        stmt = select(
            AuditoriaAccionModel.entidad,
            func.count(AuditoriaAccionModel.id).label("total"),
        )
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.group_by(AuditoriaAccionModel.entidad)

        res = await self.session.execute(stmt)
        return {row.entidad: int(row.total) for row in res.all()}

    async def contar_errores_por_endpoint(
        self,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        conds = [AuditoriaAccionModel.exitoso == False]  # noqa: E712
        if desde:
            conds.append(AuditoriaAccionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaAccionModel.creado_en <= hasta)

        stmt = (
            select(
                AuditoriaAccionModel.endpoint,
                AuditoriaAccionModel.metodo_http,
                func.count(AuditoriaAccionModel.id).label("total_errores"),
            )
            .where(and_(*conds))
            .group_by(AuditoriaAccionModel.endpoint, AuditoriaAccionModel.metodo_http)
            .order_by(desc("total_errores"))
            .limit(limit)
        )

        res = await self.session.execute(stmt)
        return [
            {
                "endpoint": row.endpoint,
                "metodo": row.metodo_http,
                "total_errores": int(row.total_errores),
            }
            for row in res.all()
        ]

    async def obtener_duracion_promedio_por_endpoint(
        self,
        endpoint: str,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
    ) -> Optional[float]:
        conds: list[Any] = [
            AuditoriaAccionModel.endpoint == endpoint,
            AuditoriaAccionModel.duracion_ms.isnot(None),
        ]
        if desde:
            conds.append(AuditoriaAccionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaAccionModel.creado_en <= hasta)

        stmt = select(func.avg(AuditoriaAccionModel.duracion_ms)).where(and_(*conds))
        res = await self.session.execute(stmt)
        val = res.scalar_one_or_none()
        return float(val) if val is not None else None

    async def obtener_actividad_por_hora(
        self,
        *,
        sede_id: Optional[int] = None,
        fecha: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        conds: list[Any] = []
        if sede_id:
            conds.append(AuditoriaAccionModel.sede_id == sede_id)
        if fecha:
            inicio_dia = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
            fin_dia = inicio_dia + timedelta(days=1)
            conds.append(AuditoriaAccionModel.creado_en >= inicio_dia)
            conds.append(AuditoriaAccionModel.creado_en < fin_dia)

        stmt = select(
            func.extract("hour", AuditoriaAccionModel.creado_en).label("hora"),
            func.count(AuditoriaAccionModel.id).label("total"),
        )
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.group_by("hora").order_by("hora")

        res = await self.session.execute(stmt)
        return [{"hora": int(row.hora), "total": int(row.total)} for row in res.all()]

    async def obtener_usuarios_mas_activos(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        conds: list[Any] = [AuditoriaAccionModel.usuario_id.isnot(None)]
        if sede_id:
            conds.append(AuditoriaAccionModel.sede_id == sede_id)
        if desde:
            conds.append(AuditoriaAccionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaAccionModel.creado_en <= hasta)

        stmt = (
            select(
                AuditoriaAccionModel.usuario_id,
                func.count(AuditoriaAccionModel.id).label("total_acciones"),
            )
            .where(and_(*conds))
            .group_by(AuditoriaAccionModel.usuario_id)
            .order_by(desc("total_acciones"))
            .limit(limit)
        )

        res = await self.session.execute(stmt)
        return [
            {"usuario_id": int(row.usuario_id), "total_acciones": int(row.total_acciones)}
            for row in res.all()
        ]

    async def limpiar_antiguos(self, dias: int = 90) -> int:
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        stmt = delete(AuditoriaAccionModel).where(AuditoriaAccionModel.creado_en < fecha_limite)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return int(result.rowcount or 0)

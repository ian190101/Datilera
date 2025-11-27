# app/infrastructure/db/repositories/ia/ia_consultas_repo.py

"""
Repositorio de infraestructura para IAConsultas.
NO depende de entidades de dominio (Enfoque 1).
"""
from __future__ import annotations
from typing import Sequence, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.ia.ia_consultas import IAConsulta as IAConsultaModel


class IAConsultasRepository:
    """Repositorio puro de infraestructura para consultas IA."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def registrar(
        self,
        usuario_id: Optional[int],
        sede_id: Optional[int],
        proveedor: str,
        modelo: str,
        prompt: str,
        *,
        prompt_sanitizado: Optional[str] = None,
        respuesta: Optional[str] = None,
        tokens_prompt: Optional[int] = None,
        tokens_respuesta: Optional[int] = None,
        tokens_total: Optional[int] = None,
        costo_usd: Optional[str] = None,
        categoria: Optional[str] = None,
        contexto: Optional[Dict[str, Any]] = None,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        duracion_segundos: Optional[int] = None,
        tiene_datos_sensibles: bool = False,
    ) -> IAConsultaModel:
        """Registra una consulta a IA."""
        consulta = IAConsultaModel(
            usuario_id=usuario_id,
            sede_id=sede_id,
            proveedor=proveedor,
            modelo=modelo,
            prompt=prompt,
            prompt_sanitizado=prompt_sanitizado,
            respuesta=respuesta,
            tokens_prompt=tokens_prompt,
            tokens_respuesta=tokens_respuesta,
            tokens_total=tokens_total,
            costo_usd=costo_usd,
            categoria=categoria,
            contexto=contexto,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
            duracion_segundos=duracion_segundos,
            tiene_datos_sensibles=tiene_datos_sensibles,
        )
        
        self.session.add(consulta)
        await self.session.flush()
        await self.session.refresh(consulta)
        return consulta
    
    async def obtener_por_id(self, consulta_id: int) -> Optional[IAConsultaModel]:
        """Obtiene una consulta por ID."""
        res = await self.session.execute(
            select(IAConsultaModel).where(IAConsultaModel.id == consulta_id)
        )
        return res.scalar_one_or_none()
    
    async def listar_por_usuario(
        self,
        usuario_id: int,
        *,
        proveedor: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Sequence[IAConsultaModel]:
        """Lista consultas de un usuario."""
        conds = [IAConsultaModel.usuario_id == usuario_id]
        
        if proveedor:
            conds.append(IAConsultaModel.proveedor == proveedor)
        if desde:
            conds.append(IAConsultaModel.creado_en >= desde)
        if hasta:
            conds.append(IAConsultaModel.creado_en <= hasta)
        
        res = await self.session.execute(
            select(IAConsultaModel)
            .where(and_(*conds))
            .order_by(desc(IAConsultaModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()
    
    async def listar_por_proveedor(
        self,
        proveedor: str,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100
    ) -> Sequence[IAConsultaModel]:
        """Lista consultas por proveedor."""
        conds = [IAConsultaModel.proveedor == proveedor]
        
        if desde:
            conds.append(IAConsultaModel.creado_en >= desde)
        if hasta:
            conds.append(IAConsultaModel.creado_en <= hasta)
        
        res = await self.session.execute(
            select(IAConsultaModel)
            .where(and_(*conds))
            .order_by(desc(IAConsultaModel.creado_en))
            .limit(limit)
        )
        return res.scalars().all()
    
    async def calcular_consumo(
        self,
        *,
        usuario_id: Optional[int] = None,
        proveedor: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calcula consumo de tokens y costos."""
        conds = [IAConsultaModel.exitoso == True]
        
        if usuario_id:
            conds.append(IAConsultaModel.usuario_id == usuario_id)
        if proveedor:
            conds.append(IAConsultaModel.proveedor == proveedor)
        if desde:
            conds.append(IAConsultaModel.creado_en >= desde)
        if hasta:
            conds.append(IAConsultaModel.creado_en <= hasta)
        
        stmt = select(
            func.sum(IAConsultaModel.tokens_prompt).label("total_tokens_prompt"),
            func.sum(IAConsultaModel.tokens_respuesta).label("total_tokens_respuesta"),
            func.sum(IAConsultaModel.tokens_total).label("total_tokens"),
            func.sum(func.cast(IAConsultaModel.costo_usd, func.Numeric)).label("costo_total"),
            func.count(IAConsultaModel.id).label("total_consultas")
        ).where(and_(*conds))
        
        res = await self.session.execute(stmt)
        row = res.one()
        
        # ✅ SOLUCIÓN: Acceso con cast explícito
        return {
            "total_tokens_prompt": int(row[0]) if row[0] is not None else 0,
            "total_tokens_respuesta": int(row[1]) if row[1] is not None else 0,
            "total_tokens": int(row[2]) if row[2] is not None else 0,
            "costo_total_usd": float(row[3]) if row[3] is not None else 0.0,
            "total_consultas": int(row[4]) if row[4] is not None else 0
        }
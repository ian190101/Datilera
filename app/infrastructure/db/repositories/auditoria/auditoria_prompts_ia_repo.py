# app/infrastructure/db/repositories/auditoria/auditoria_prompts_ia_repo.py

"""
Repositorio de infraestructura para Auditoría de Prompts IA.
NO depende de entidades de dominio.
"""
from __future__ import annotations
from typing import Sequence, Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import select, insert, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.auditoria.auditoria_prompts_ia import AuditoriaPromptIA as AuditoriaPromptIAModel


class AuditoriaPromptsIARepository:
    """Repositorio puro de infraestructura para prompts IA."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def registrar(
        self,
        usuario_id: Optional[int],
        sede_id: Optional[int],
        prompt_original: str,
        *,
        prompt_sanitizado: Optional[str] = None,
        respuesta: Optional[str] = None,
        tokens_prompt: Optional[int] = None,
        tokens_respuesta: Optional[int] = None,
        tokens_total: Optional[int] = None,
        modelo: Optional[str] = None,
        costo_usd: Optional[str] = None,
        categoria: Optional[str] = None,
        tiene_datos_sensibles: bool = False,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        duracion_segundos: Optional[int] = None,
    ) -> AuditoriaPromptIAModel:
        """Registra una consulta a IA."""
        stmt = insert(AuditoriaPromptIAModel).values(
            usuario_id=usuario_id,
            sede_id=sede_id,
            prompt_original=prompt_original,
            prompt_sanitizado=prompt_sanitizado,
            respuesta=respuesta,
            tokens_prompt=tokens_prompt,
            tokens_respuesta=tokens_respuesta,
            tokens_total=tokens_total,
            modelo=modelo,
            costo_usd=costo_usd,
            categoria=categoria,
            tiene_datos_sensibles=tiene_datos_sensibles,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
            duracion_segundos=duracion_segundos,
        ).returning(AuditoriaPromptIAModel)
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one()

    async def obtener_por_id(self, prompt_id: int) -> Optional[AuditoriaPromptIAModel]:
        """Obtiene un prompt por su ID."""
        res = await self.session.execute(
            select(AuditoriaPromptIAModel)
            .where(AuditoriaPromptIAModel.id == prompt_id)
        )
        return res.scalar_one_or_none()

    async def listar_por_usuario(
        self,
        usuario_id: int,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        categoria: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Sequence[AuditoriaPromptIAModel]:
        """Lista prompts de un usuario."""
        conds = [AuditoriaPromptIAModel.usuario_id == usuario_id]
        
        if desde:
            conds.append(AuditoriaPromptIAModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaPromptIAModel.creado_en <= hasta)
        if categoria:
            conds.append(AuditoriaPromptIAModel.categoria == categoria)
        
        res = await self.session.execute(
            select(AuditoriaPromptIAModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaPromptIAModel.creado_en))
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
    ) -> Sequence[AuditoriaPromptIAModel]:
        """Lista prompts de una sede."""
        conds = [AuditoriaPromptIAModel.sede_id == sede_id]
        
        if desde:
            conds.append(AuditoriaPromptIAModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaPromptIAModel.creado_en <= hasta)
        
        res = await self.session.execute(
            select(AuditoriaPromptIAModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaPromptIAModel.creado_en))
            .limit(limit)
            .offset(offset)
        )
        return res.scalars().all()

    async def listar_con_datos_sensibles(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        limit: int = 50
    ) -> Sequence[AuditoriaPromptIAModel]:
        """Lista prompts con datos sensibles."""
        conds = [AuditoriaPromptIAModel.tiene_datos_sensibles == True]
        
        if sede_id:
            conds.append(AuditoriaPromptIAModel.sede_id == sede_id)
        if desde:
            conds.append(AuditoriaPromptIAModel.creado_en >= desde)
        
        res = await self.session.execute(
            select(AuditoriaPromptIAModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaPromptIAModel.creado_en))
            .limit(limit)
        )
        return res.scalars().all()

    async def listar_fallidos(
        self,
        *,
        usuario_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        limit: int = 50
    ) -> Sequence[AuditoriaPromptIAModel]:
        """Lista prompts fallidos."""
        conds = [AuditoriaPromptIAModel.exitoso == False]
        
        if usuario_id:
            conds.append(AuditoriaPromptIAModel.usuario_id == usuario_id)
        if desde:
            conds.append(AuditoriaPromptIAModel.creado_en >= desde)
        
        res = await self.session.execute(
            select(AuditoriaPromptIAModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaPromptIAModel.creado_en))
            .limit(limit)
        )
        return res.scalars().all()

    async def calcular_tokens_consumidos(
        self,
        *,
        usuario_id: Optional[int] = None,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Calcula total de tokens consumidos."""
        conds = [AuditoriaPromptIAModel.exitoso == True]
        
        if usuario_id:
            conds.append(AuditoriaPromptIAModel.usuario_id == usuario_id)
        if sede_id:
            conds.append(AuditoriaPromptIAModel.sede_id == sede_id)
        if desde:
            conds.append(AuditoriaPromptIAModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaPromptIAModel.creado_en <= hasta)
        
        stmt = select(
            func.sum(AuditoriaPromptIAModel.tokens_prompt).label("total_prompt"),
            func.sum(AuditoriaPromptIAModel.tokens_respuesta).label("total_respuesta"),
            func.sum(AuditoriaPromptIAModel.tokens_total).label("total_total")
        ).where(and_(*conds))
        
        res = await self.session.execute(stmt)
        row = res.one()
        
        return {
            "tokens_prompt": row.total_prompt or 0,
            "tokens_respuesta": row.total_respuesta or 0,
            "tokens_total": row.total_total or 0
        }

    async def calcular_costo_total(
        self,
        *,
        usuario_id: Optional[int] = None,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> float:
        """Calcula costo total en USD."""
        conds = [
            AuditoriaPromptIAModel.exitoso == True,
            AuditoriaPromptIAModel.costo_usd.isnot(None)
        ]
        
        if usuario_id:
            conds.append(AuditoriaPromptIAModel.usuario_id == usuario_id)
        if sede_id:
            conds.append(AuditoriaPromptIAModel.sede_id == sede_id)
        if desde:
            conds.append(AuditoriaPromptIAModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaPromptIAModel.creado_en <= hasta)
        
        stmt = select(
            func.sum(func.cast(AuditoriaPromptIAModel.costo_usd, func.Numeric))
        ).where(and_(*conds))
        
        res = await self.session.execute(stmt)
        total = res.scalar_one_or_none()
        return float(total) if total else 0.0

    async def contar_por_categoria(
        self,
        *,
        usuario_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta prompts por categoría."""
        conds = []
        
        if usuario_id:
            conds.append(AuditoriaPromptIAModel.usuario_id == usuario_id)
        if desde:
            conds.append(AuditoriaPromptIAModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaPromptIAModel.creado_en <= hasta)
        
        stmt = select(
            AuditoriaPromptIAModel.categoria,
            func.count(AuditoriaPromptIAModel.id).label("total")
        )
        
        if conds:
            stmt = stmt.where(and_(*conds))
        
        stmt = stmt.group_by(AuditoriaPromptIAModel.categoria)
        
        res = await self.session.execute(stmt)
        return {row.categoria or "sin_categoria": row.total for row in res.all()}

    async def contar_por_modelo(
        self,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta prompts por modelo."""
        conds = []
        
        if desde:
            conds.append(AuditoriaPromptIAModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaPromptIAModel.creado_en <= hasta)
        
        stmt = select(
            AuditoriaPromptIAModel.modelo,
            func.count(AuditoriaPromptIAModel.id).label("total")
        )
        
        if conds:
            stmt = stmt.where(and_(*conds))
        
        stmt = stmt.group_by(AuditoriaPromptIAModel.modelo)
        
        res = await self.session.execute(stmt)
        return {row.modelo or "desconocido": row.total for row in res.all()}

    async def obtener_duracion_promedio(
        self,
        *,
        categoria: Optional[str] = None,
        modelo: Optional[str] = None
    ) -> Optional[float]:
        """Calcula duración promedio en segundos."""
        conds = [
            AuditoriaPromptIAModel.exitoso == True,
            AuditoriaPromptIAModel.duracion_segundos.isnot(None)
        ]
        
        if categoria:
            conds.append(AuditoriaPromptIAModel.categoria == categoria)
        if modelo:
            conds.append(AuditoriaPromptIAModel.modelo == modelo)
        
        stmt = select(
            func.avg(AuditoriaPromptIAModel.duracion_segundos)
        ).where(and_(*conds))
        
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def obtener_usuarios_mas_activos(
        self,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Top N usuarios con más consultas."""
        conds = [AuditoriaPromptIAModel.usuario_id.isnot(None)]
        
        if desde:
            conds.append(AuditoriaPromptIAModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaPromptIAModel.creado_en <= hasta)
        
        stmt = select(
            AuditoriaPromptIAModel.usuario_id,
            func.count(AuditoriaPromptIAModel.id).label("total_consultas"),
            func.sum(AuditoriaPromptIAModel.tokens_total).label("total_tokens")
        ).where(and_(*conds)).group_by(
            AuditoriaPromptIAModel.usuario_id
        ).order_by(desc("total_consultas")).limit(limit)
        
        res = await self.session.execute(stmt)
        return [
            {
                "usuario_id": row.usuario_id,
                "total_consultas": row.total_consultas,
                "total_tokens": row.total_tokens or 0
            }
            for row in res.all()
        ]

    async def buscar_por_contenido(
        self,
        termino: str,
        *,
        sede_id: Optional[int] = None,
        limit: int = 20
    ) -> Sequence[AuditoriaPromptIAModel]:
        """Búsqueda de texto en prompts."""
        conds = [
            AuditoriaPromptIAModel.prompt_original.ilike(f"%{termino}%")
        ]
        
        if sede_id:
            conds.append(AuditoriaPromptIAModel.sede_id == sede_id)
        
        res = await self.session.execute(
            select(AuditoriaPromptIAModel)
            .where(and_(*conds))
            .order_by(desc(AuditoriaPromptIAModel.creado_en))
            .limit(limit)
        )
        return res.scalars().all()

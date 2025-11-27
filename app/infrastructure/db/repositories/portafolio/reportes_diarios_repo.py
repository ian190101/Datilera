# app/infrastructure/db/repositories/portafolio/reportes_diarios_repo.py

from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.portafolio.reportes_diarios import (
    ReporteDiario,
)  # modelo SQLAlchemy de reportes_diarios [attached_file:356372ef-9574-4bbc-9a5d-3aecec5e6ba0]


class ReportesDiariosRepository(BaseRepository[ReporteDiario]):
    """Repositorio de reportes diarios de Portafolio."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ReporteDiario)

    async def crear_o_actualizar(
        self,
        alumno_id: int,
        profesora_id: int,
        fecha: date,
        resumen: Optional[str],
    ) -> ReporteDiario:
        """Crea o actualiza el reporte diario de un alumno para una fecha dada."""
        stmt = (
            select(ReporteDiario)
            .where(ReporteDiario.alumno_id == alumno_id)
            .where(ReporteDiario.fecha == fecha)
        )
        result = await self.session.execute(stmt)
        reporte: Optional[ReporteDiario] = result.scalar_one_or_none()

        if reporte is None:
            reporte = ReporteDiario(
                alumno_id=alumno_id,
                profesora_id=profesora_id,
                fecha=fecha,
                contenido=resumen if resumen else "",
                enviado=False, 
                confirmado=False
            )
            return await self.create(reporte)

        # actualizar existente solo si no se ha enviado todavía
        if not reporte.enviado:
            reporte.contenido = resumen if resumen else reporte.contenido
            reporte.profesora_id = profesora_id
            await self.session.flush()
        return reporte

    async def obtener_por_id(self, reporte_id: int) -> Optional[ReporteDiario]:
        stmt = select(ReporteDiario).where(ReporteDiario.id == reporte_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def listar_por_alumno(
        self,
        alumno_id: int,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
    ) -> List[ReporteDiario]:
        stmt = select(ReporteDiario).where(ReporteDiario.alumno_id == alumno_id)
        if desde is not None:
            stmt = stmt.where(ReporteDiario.fecha >= desde)
        if hasta is not None:
            stmt = stmt.where(ReporteDiario.fecha <= hasta)
        stmt = stmt.order_by(ReporteDiario.fecha.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def marcar_enviado(self, reporte_id: int, enviado_en) -> None:
        stmt = (
            update(ReporteDiario)
            .where(ReporteDiario.id == reporte_id)
            .values(enviado=True, enviado_en=enviado_en)
        )
        await self.session.execute(stmt)

    async def marcar_confirmado(self, reporte_id: int, confirmado_en) -> None:
        stmt = (
            update(ReporteDiario)
            .where(ReporteDiario.id == reporte_id)
            .values(confirmado=True, confirmado_en=confirmado_en)
        )
        await self.session.execute(stmt)

    async def listar_no_enviados_hasta_fecha(self, fecha: date) -> List[ReporteDiario]:
        """Para autoenvío: reportes del día que aún no están enviados."""
        stmt = (
            select(ReporteDiario)
            .where(ReporteDiario.fecha == fecha)
            .where(ReporteDiario.enviado.is_(False))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

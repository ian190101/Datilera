# app/infrastructure/db/repositories/portafolio/reporte_lecturas_tutores_repo.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.portafolio.reporte_lecturas_tutores import (
    ReporteLecturaTutor,
)  # modelo SQLAlchemy de lecturas [attached_file:5243b050-7f8d-41da-a168-d1fe59fb671e]


class ReporteLecturasTutoresRepository(BaseRepository[ReporteLecturaTutor]):
    """Repositorio de lecturas de tutores de reportes diarios."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ReporteLecturaTutor)

    async def registrar_lectura(self, reporte_id: int, tutor_id: int) -> ReporteLecturaTutor:
        """Idempotente: si ya existe una lectura, la devuelve; si no, la crea."""
        stmt = select(ReporteLecturaTutor).where(
            and_(ReporteLecturaTutor.reporte_diario_id == reporte_id, ReporteLecturaTutor.tutor_id == tutor_id)
        )
        result = await self.session.execute(stmt)
        lectura: Optional[ReporteLecturaTutor] = result.scalar_one_or_none()

        if lectura is not None:
            return lectura

        lectura = ReporteLecturaTutor(reporte_diario_id=reporte_id, tutor_id=tutor_id)
        return await self.create(lectura)

    async def listar_por_reporte(self, reporte_id: int) -> List[ReporteLecturaTutor]:
        stmt = select(ReporteLecturaTutor).where(ReporteLecturaTutor.reporte_diario_id == reporte_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

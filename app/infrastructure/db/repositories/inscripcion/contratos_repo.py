# app/infrastructure/db/repositories/inscripcion/contratos_repo.py
from typing import Dict  # <-- esto es nuevo
from sqlalchemy import select, func  # <-- esto es nuevo
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inscripcion import Contrato


class ContratoRepository(BaseRepository[Contrato]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Contrato)
    async def reservar_numeracion(self, sede_id: int) -> int:  # <-- esto es nuevo
        res = await self.session.execute(  # <-- esto es nuevo
            select(func.coalesce(func.max(Contrato.numeracion_sede), 0)).where(Contrato.sede_id == sede_id)  # <-- esto es nuevo
        )  # <-- esto es nuevo
        return int(res.scalar_one()) + 1  # <-- esto es nuevo

    async def crear_con_variables(self, formulario_id: int, sede_id: int, codigo_contrato: str, numeracion_sede: int, variables: Dict) -> Contrato:  # <-- esto es nuevo
        contrato = Contrato(  # <-- esto es nuevo
            formulario_id=formulario_id,  # <-- esto es nuevo
            sede_id=sede_id,  # <-- esto es nuevo
            codigo_contrato=codigo_contrato,  # <-- esto es nuevo
            numeracion_sede=numeracion_sede,  # <-- esto es nuevo
            variables_json=variables,  # <-- esto es nuevo
            fecha_emision=func.current_date()  # <-- esto es nuevo
        )  # <-- esto es nuevo
        self.session.add(contrato)  # <-- esto es nuevo
        await self.session.flush()  # <-- esto es nuevo
        await self.session.refresh(contrato)  # <-- esto es nuevo
        return contrato  # <-- esto es nuevo

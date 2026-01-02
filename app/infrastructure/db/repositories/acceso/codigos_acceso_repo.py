# app/infrastructure/db/repositories/acceso/codigos_acceso_repo.py
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models.acceso import CodigoAcceso, CodigoAccesoUso, EstadoCodigo
from app.infrastructure.db.repositories.base import BaseRepository
from app.kernel.domain.acceso.errors import (
    CodigoNoEncontrado,
    CodigoExpirado,
    CodigoRevocado,
    CodigoAgotado,
    VerificacionNoPermitida,
)


class CodigosAccesoRepository(BaseRepository[CodigoAcceso]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CodigoAcceso)

    async def guardar(self, codigo: CodigoAcceso) -> None:
        """
        Agrega el código a la sesión.
        IMPORTANTE: No hace commit, eso lo hace el UoW al final.
        """
        self.session.add(codigo)

    async def existe_valor(self, valor: str) -> bool:
        """Verifica si el código (ej: 'A1B2C3') ya existe en la BD."""
        stmt = select(func.count(CodigoAcceso.id)).where(CodigoAcceso.codigo == valor)
        count = await self.session.scalar(stmt)
        return count > 0

    async def _by_codigo(self, codigo: str) -> Optional[CodigoAcceso]:
        stmt = (
            select(CodigoAcceso)
            .options(selectinload(CodigoAcceso.usos))
            .where(CodigoAcceso.codigo == codigo)
            .limit(1)
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def disponible(self, codigo: str) -> bool:
        c = await self._by_codigo(codigo)
        if not c:
            return False
        if c.estado in {EstadoCodigo.expirado, EstadoCodigo.revocado}:
            return False
        if c.expira_en and c.expira_en < date.today():
            return False
        return c.cuentas_creadas < c.max_cuentas

    async def marcar_enviado(self, codigo_id: int, message_id: str | None = None) -> None:
        await self.update(codigo_id, {"enviado": True, "whatsapp_message_id": message_id})

    async def registrar_uso(self, codigo: str, usuario_id: int, rol_id: int) -> None:
        """
        Registra el consumo exitoso del código:
        - Valida estado y vigencia.
        - Inserta un uso.
        - Incrementa contador y, si corresponde, marca consumido.
        Requiere transacción externa (UoW) para commit/rollback.
        """
        c = await self._by_codigo(codigo)
        if not c:
            raise CodigoNoEncontrado("Código no encontrado")

        if c.estado == EstadoCodigo.revocado:
            raise CodigoRevocado("Código revocado")

        if c.expira_en and c.expira_en < date.today():
            raise CodigoExpirado("Código expirado")

        if c.cuentas_creadas >= c.max_cuentas:
            raise CodigoAgotado("Límite de usos alcanzado")

        # Idempotencia simple: evita doble consumo mismo usuario/código en el mismo instante
        uso = CodigoAccesoUso(codigo_id=c.id, usuario_id=usuario_id, rol_id=rol_id)
        self.session.add(uso)

        c.cuentas_creadas += 1
        if c.cuentas_creadas >= c.max_cuentas:
            c.estado = EstadoCodigo.consumido

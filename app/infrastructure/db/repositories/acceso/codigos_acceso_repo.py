# app/infrastructure/db/repositories/acceso/codigos_acceso_repo.py
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.acceso import CodigoAcceso, CodigoAccesoUso, EstadoCodigo
from app.infrastructure.db.repositories.base import BaseRepository

class CodigosAccesoRepository(BaseRepository[CodigoAcceso]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CodigoAcceso)

    async def _by_codigo(self, codigo: str) -> CodigoAcceso | None:
        stmt = select(CodigoAcceso).where(CodigoAcceso.codigo == codigo)
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

    async def marcar_enviado(self, codigo_id: int, message_id: str | None = None):
        await self.update(codigo_id, {"enviado": True, "whatsapp_message_id": message_id})

    async def registrar_uso(self, codigo: str, usuario_id: int, rol_id: int):
        c = await self._by_codigo(codigo)
        if not c:
            raise ValueError("Código inválido")
        if not await self.disponible(codigo):
            raise ValueError("Código no disponible")
        uso = CodigoAccesoUso(codigo_id=c.id, usuario_id=usuario_id, rol_id=rol_id)
        self.session.add(uso)
        c.cuentas_creadas += 1
        if c.cuentas_creadas >= c.max_cuentas:
            c.estado = EstadoCodigo.consumido

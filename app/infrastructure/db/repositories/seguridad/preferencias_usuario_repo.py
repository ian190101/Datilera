# app/infrastructure/db/repositories/seguridad/preferencias_usuario_repo.py
from __future__ import annotations
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import PreferenciaUsuario

class PreferenciasUsuarioRepository(BaseRepository[PreferenciaUsuario]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PreferenciaUsuario)

    async def actualizar_por_usuario(self, usuario_id: int, data: dict) -> None:
        await self.session.execute(update(PreferenciaUsuario).where(PreferenciaUsuario.usuario_id == usuario_id).values(**data))

# app/infrastructure/db/repositories/seguridad/preferencias_usuario_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import PreferenciaUsuario

class PreferenciasUsuarioRepository(BaseRepository[PreferenciaUsuario]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PreferenciaUsuario)

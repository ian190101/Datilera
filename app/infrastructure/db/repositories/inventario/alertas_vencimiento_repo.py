# app/infrastructure/db/repositories/inventario/alertas_vencimiento_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inventario import AlertaVencimiento

class AlertasVencimientoRepository(BaseRepository[AlertaVencimiento]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AlertaVencimiento)

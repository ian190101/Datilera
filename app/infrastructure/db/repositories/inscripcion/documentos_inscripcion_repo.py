# app/infrastructure/db/repositories/inscripcion/documentos_inscripcion_repo.py 
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional  # <-- esto es nuevo
from sqlalchemy import select, update  # <-- esto es nuevo
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inscripcion import DocumentoInscripcion


class DocumentoInscripcionRepository(BaseRepository[DocumentoInscripcion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DocumentoInscripcion)
    async def actualizar_estado(self, doc_id: int, estado: str, error: Optional[str] = None, watermark_url: Optional[str] = None) -> None:  # <-- esto es nuevo
        values = {"estado_procesamiento": estado}  # <-- esto es nuevo
        if error is not None:  # <-- esto es nuevo
            values["error_ultima"] = error  # <-- esto es nuevo
        if watermark_url is not None:  # <-- esto es nuevo
            values["watermark_url"] = watermark_url  # <-- esto es nuevo
        await self.session.execute(  # <-- esto es nuevo
            update(DocumentoInscripcion)  # <-- esto es nuevo
            .where(DocumentoInscripcion.id == doc_id)  # <-- esto es nuevo
            .values(**values)  # <-- esto es nuevo
        )  # <-- esto es nuevo

    async def listar_pendientes(self, limit: int = 100) -> List[DocumentoInscripcion]:  # <-- esto es nuevo
        res = await self.session.execute(  # <-- esto es nuevo
            select(DocumentoInscripcion)  # <-- esto es nuevo
            .where(DocumentoInscripcion.estado_procesamiento == "pendiente")  # <-- esto es nuevo
            .limit(limit)  # <-- esto es nuevo
        )  # <-- esto es nuevo
        return res.scalars().all()  # <-- esto es nuevo

    async def obtener_por_hash(self, hash_archivo: str) -> Optional[DocumentoInscripcion]:  # <-- esto es nuevo
        res = await self.session.execute(  # <-- esto es nuevo
            select(DocumentoInscripcion).where(DocumentoInscripcion.hash_archivo == hash_archivo)  # <-- esto es nuevo
        )  # <-- esto es nuevo
        return res.scalar_one_or_none()  # <-- esto es nuevo

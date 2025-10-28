# app/infrastructure/db/repositories/inscripcion/formularios_repo.py
import json
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inscripcion import (
    FormularioInscripcion, FormularioRespuesta, EstadoFormulario
)

class FormulariosRepository(BaseRepository[FormularioInscripcion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, FormularioInscripcion)

    async def crear_formulario(self, alumno_id: int, sede_id: int, gestion: int) -> FormularioInscripcion:
        form = FormularioInscripcion(alumno_id=alumno_id, sede_id=sede_id, gestion=gestion, estado=EstadoFormulario.borrador)
        return await self.create(form)

    async def upsert_respuestas(self, formulario_id: int, datos: dict[str, object]):
        await self.session.execute(delete(FormularioRespuesta).where(FormularioRespuesta.formulario_id == formulario_id))
        rows = []
        for k, v in datos.items():
            valor = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
            rows.append(FormularioRespuesta(formulario_id=formulario_id, campo=k, valor=valor))
        self.session.add_all(rows)

    async def cargar_dict(self, formulario_id: int) -> dict:
        res = await self.session.execute(select(FormularioRespuesta).where(FormularioRespuesta.formulario_id == formulario_id))
        out: dict[str, object] = {}
        for r in res.scalars().all():
            try:
                out[r.campo] = json.loads(r.valor)
            except Exception:
                out[r.campo] = r.valor
        return out

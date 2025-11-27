#app/kernel/application/acceso/revocar_codigo.py
from __future__ import annotations
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.kernel.domain.acceso.errors import CodigoNoEncontrado
from app.kernel.domain.acceso.estado_codigo_entidad import EstadoCodigo
from app.kernel.domain.acceso.ports import UnitOfWork

from app.kernel.domain.auditoria.ports import  AuditoriaAccionRepositoryPort # type: ignore
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion  # type: ignore


class RevocarCodigoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo_id: int
    motivo: Optional[str] = None
    actor_id: Optional[int] = None
    sede_id: Optional[int] = None

class RevocarCodigo:
    def __init__(self, uow: UnitOfWork, auditoria: Optional["AuditoriaAccionRepositoryPort"] = None):
        self.uow = uow
        self.auditoria = auditoria

    async def execute(self, req: RevocarCodigoRequest) -> None:
        async with self.uow:
            cod = await self.uow.codigos.obtener(req.codigo_id)
            if not cod:
                raise CodigoNoEncontrado()
            await self.uow.codigos.revocar(req.codigo_id, motivo=req.motivo)
            await self.uow.commit()

        if self.auditoria and AuditoriaAccion:
            await self.auditoria.registrar(AuditoriaAccion(
                usuario_id=req.actor_id,
                sede_id=req.sede_id or cod.sede_id,
                entidad="codigos_acceso",
                entidad_id=str(req.codigo_id),
                accion="reject",
                datos_despues={"motivo": req.motivo},
            ))

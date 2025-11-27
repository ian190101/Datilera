#app/kernel/application/acceso/consumir_codigo.py
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.kernel.domain.acceso.codigo_acceso_entidad import CodigoAcceso
from app.kernel.domain.acceso.codigo_acceso_uso_entidad import CodigoAccesoUso
from app.kernel.domain.acceso.estado_codigo_entidad import EstadoCodigo
from app.kernel.domain.acceso.errors import (
    CodigoNoEncontrado,
    CodigoExpirado,
    CodigoRevocado,
    CodigoAgotado,
)
from app.kernel.domain.acceso.ports import UnitOfWork


from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort  # type: ignore
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion  # type: ignore

class ConsumirCodigoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    valor: str = Field(min_length=6, max_length=6)
    usuario_id: int
    rol_id: int

class ConsumirCodigo:
    def __init__(self, uow: UnitOfWork, auditoria: Optional["AuditoriaAccionRepositoryPort"] = None):
        self.uow = uow
        self.auditoria = auditoria

    async def execute(self, req: ConsumirCodigoRequest) -> None:
        async with self.uow:
            cod: Optional[CodigoAcceso] = await self.uow.codigos.obtener_por_valor(req.valor.upper())
            if not cod:
                raise CodigoNoEncontrado("Código no encontrado")

            if cod.estado == EstadoCodigo.revocado:
                raise CodigoRevocado("Código revocado")

            if cod.expira_en and cod.expira_en < date.today():
                # también opcionalmente uow.codigos.set_estado(cod.id, EstadoCodigo.expirado)
                raise CodigoExpirado("Código expirado")

            if cod.cuentas_creadas >= cod.max_cuentas:
                raise CodigoAgotado("Límite de usos alcanzado")

            # registrar uso
            uso = CodigoAccesoUso(
                id=None,
                codigo_id=cod.id,
                usuario_id=req.usuario_id,
                rol_id=req.rol_id,
            )
            await self.uow.codigos_usos.registrar(uso)

            # incrementar contador y estado si se agotó
            await self.uow.codigos.incrementar_usos(cod.id)
            if cod.cuentas_creadas + 1 >= cod.max_cuentas:
                await self.uow.codigos.set_estado(cod.id, EstadoCodigo.consumido)

            await self.uow.commit()

        if self.auditoria and AuditoriaAccion:
            ev = AuditoriaAccion(
                usuario_id=req.usuario_id,
                sede_id=cod.sede_id,
                entidad="codigos_acceso",
                entidad_id=str(cod.id),
                accion="approve",
                datos_despues={"cuentas_creadas": cod.cuentas_creadas + 1, "estado": EstadoCodigo.consumido.value if cod.cuentas_creadas + 1 >= cod.max_cuentas else cod.estado.value},
            )
            await self.auditoria.registrar(ev)

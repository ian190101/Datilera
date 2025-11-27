#app/kernel/application/acceso/generar_codigo.py
from __future__ import annotations

from datetime import date
from secrets import choice
from string import ascii_uppercase, digits
from typing import Optional, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.kernel.domain.acceso.codigo_acceso_entidad import CodigoAcceso
from app.kernel.domain.acceso.estado_codigo_entidad import EstadoCodigo
from app.kernel.domain.acceso.errors import CodigoInvalido
from app.kernel.domain.acceso.ports import UnitOfWork


from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort  
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion 


_ALPHANUM = ascii_uppercase + digits

class GenerarCodigoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sede_id: int
    rol_id: int
    alumno_id: Optional[int] = Field(default=None)
    max_cuentas: int = Field(default=1, ge=1, le=10)
    expira_en: Optional[date] = None
    observaciones: Optional[str] = None
    creado_por: Optional[int] = None

    @field_validator("expira_en")
    @classmethod
    def _no_pasado(cls, v: Optional[date]) -> Optional[date]:
        if v and v < date.today():
            raise CodigoInvalido("La fecha de expiración no puede estar en el pasado")
        return v

class GenerarCodigoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    sede_id: int
    rol_id: int
    alumno_id: Optional[int]
    max_cuentas: int
    cuentas_creadas: int
    expira_en: Optional[date]
    estado: EstadoCodigo

class GenerarCodigo:
    def __init__(self, uow: UnitOfWork, auditoria: Optional["AuditoriaAccionRepositoryPort"] = None):
        self.uow = uow
        self.auditoria = auditoria

    async def _generar_unico(self) -> str:
        # hasta 20 intentos para unicidad
        for _ in range(20):
            val = "".join(choice(_ALPHANUM) for _ in range(6))
            if not await self.uow.codigos.existe_valor(val):
                return val
        raise CodigoInvalido("No se pudo generar un código único")

    async def execute(self, req: GenerarCodigoRequest) -> GenerarCodigoResponse:
        async with self.uow:
            valor = await self._generar_unico()
            codigo = CodigoAcceso(
                id=0,
                sede_id=req.sede_id,
                gestion=date.today().year,
                rol_id=req.rol_id,
                usuario_destino_id=None,
                alumno_id=req.alumno_id,
                max_cuentas=req.max_cuentas,
                cuentas_creadas=0,
                codigo=valor,
                expira_en=req.expira_en,
                estado=EstadoCodigo.pendiente,
                whatsapp_numero="",
                whatsapp_message_id=None,
                enviado=False,
                enviado_en=None,
                entregado_a=None,
                observaciones=req.observaciones,
                creado_por=req.creado_por,
                creado_en=None,  # Pydantic/adapter lo setea si corresponde
                actualizado_en=None,
            )
            await self.uow.codigos.guardar(codigo)
            await self.uow.commit()

        # Auditoría (opcional, fuera de la TX principal si no es crítico)
        if self.auditoria and AuditoriaAccion:
            ev = AuditoriaAccion(
                usuario_id=req.creado_por,
                sede_id=req.sede_id,
                entidad="codigos_acceso",
                entidad_id=None,
                accion="create",
                datos_despues={"codigo": valor, "rol_id": req.rol_id, "max_cuentas": req.max_cuentas},
            )
            await self.auditoria.registrar(ev)

        return GenerarCodigoResponse(
            id=codigo.id,
            codigo=codigo.codigo,
            sede_id=codigo.sede_id,
            rol_id=codigo.rol_id,
            alumno_id=codigo.alumno_id,
            max_cuentas=codigo.max_cuentas,
            cuentas_creadas=codigo.cuentas_creadas,
            expira_en=codigo.expira_en,
            estado=codigo.estado,
        )

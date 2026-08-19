# app/kernel/application/acceso/generar_codigo.py
from __future__ import annotations

from datetime import date
from secrets import choice
from string import ascii_uppercase, digits
from typing import Optional, TYPE_CHECKING # <--- Importamos TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Modelo ORM para guardar en BD
from app.infrastructure.db.models.acceso.codigos_acceso import CodigoAcceso, EstadoCodigo

from app.kernel.domain.acceso.errors import CodigoInvalido
from app.kernel.domain.acceso.ports import UnitOfWork

# --- CORRECCIÓN DE IMPORTS ---
# 1. Para tipos (Pylance): Solo se importa si se están chequeando tipos
if TYPE_CHECKING:
    from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort

# 2. Para runtime (Ejecución): Importamos la Entidad que vamos a instanciar
try:
    from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion
except ImportError:
    AuditoriaAccion = None
# -----------------------------


_ALPHANUM = ascii_uppercase + digits

class GenerarCodigoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sede_id: int
    rol_id: int
    alumno_id: Optional[int] = Field(default=None)
    max_cuentas: int = Field(default=1, ge=1, le=10)
    expira_en: Optional[date] = None
    observaciones: Optional[str] = None
    whatsapp_numero: str = ""
    entregado_a: Optional[str] = None
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
    # Usamos comillas en "AuditoriaAccionRepositoryPort" para Forward Reference
    def __init__(self, uow: UnitOfWork, auditoria: Optional["AuditoriaAccionRepositoryPort"] = None):
        self.uow = uow
        self.auditoria = auditoria

    async def _generar_unico(self) -> str:
        for _ in range(20):
            val = "".join(choice(_ALPHANUM) for _ in range(6))
            if not await self.uow.codigos.existe_valor(val):
                return val
        raise CodigoInvalido("No se pudo generar un código único")

    async def execute(self, req: GenerarCodigoRequest) -> GenerarCodigoResponse:
        async with self.uow:
            valor = await self._generar_unico()
            
            codigo = CodigoAcceso(
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
                whatsapp_numero=req.whatsapp_numero,
                whatsapp_message_id=None,
                enviado=False,
                enviado_en=None,
                entregado_a=req.entregado_a,
                observaciones=req.observaciones,
                creado_por=req.creado_por
            )
            
            await self.uow.codigos.guardar(codigo)
            await self.uow.commit()

        if self.auditoria and AuditoriaAccion:
            ev = AuditoriaAccion(
                usuario_id=req.creado_por,
                sede_id=req.sede_id,
                entidad="codigos_acceso",
                entidad_id=str(codigo.id),
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

# app/kernel/application/acceso/enviar_codigo_whatsapp.py
from __future__ import annotations
from urllib.parse import quote_plus
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.kernel.domain.acceso.errors import CodigoNoEncontrado
from app.kernel.domain.acceso.ports import UnitOfWork


from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort  
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion  


class EnviarCodigoWhatsappRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo_id: int
    telefono_e164: str = Field(..., description="Ej.: 591XXXXXXXX (sin '+')")
    plantilla: str | None = Field(default="Tu código de registro es {codigo}.")
    incluir_link: bool = True

class EnviarCodigoWhatsappResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    texto: str
    link: str | None = None

class EnviarCodigoWhatsapp:
    def __init__(self, uow: UnitOfWork, auditoria: Optional["AuditoriaAccionRepositoryPort"] = None):
        self.uow = uow
        self.auditoria = auditoria

    async def execute(self, req: EnviarCodigoWhatsappRequest) -> EnviarCodigoWhatsappResponse:
        async with self.uow:
            c = await self.uow.codigos.obtener(req.codigo_id)
            if not c:
                raise CodigoNoEncontrado("Código no encontrado")
            texto = (req.plantilla or "Tu código de registro es {codigo}.").format(codigo=c.codigo)
            link = None
            if req.incluir_link:
                numero = req.telefono_e164.replace("+", "")
                link = f"https://wa.me/{numero}?text={quote_plus(texto)}"
            await self.uow.commit()
        if self.auditoria and AuditoriaAccion:
            await self.auditoria.registrar(AuditoriaAccion(
                usuario_id=None, sede_id=c.sede_id, entidad="codigos_acceso", entidad_id=str(c.id),
                accion="download", datos_despues={"preview": True}
            ))
        return EnviarCodigoWhatsappResponse(texto=texto, link=link)

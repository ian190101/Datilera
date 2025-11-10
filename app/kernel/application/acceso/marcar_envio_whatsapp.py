#app/kernel/application/acceso/marcar_envio_whatsapp.py
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.kernel.domain.acceso.errors import CodigoNoEncontrado
from app.kernel.domain.acceso.ports import UnitOfWork

class MarcarEnvioWhatsappRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo_id: int
    whatsapp_message_id: Optional[str] = None

class MarcarEnvioWhatsapp:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, req: MarcarEnvioWhatsappRequest) -> None:
        async with self.uow:
            c = await self.uow.codigos.obtener(req.codigo_id)
            if not c:
                raise CodigoNoEncontrado()
            # actualizar campos de envío
            c.enviado = True
            c.whatsapp_message_id = req.whatsapp_message_id
            await self.uow.codigos.guardar(c)
            await self.uow.commit()

# app/application/inscripcion/firmas/registrar_firma.py
from typing import Optional
from pydantic import BaseModel, Field
from app.kernel.domain.inscripcion import Firma, TipoFirmante
from app.kernel.domain.inscripcion.ports import FirmaRepositoryPort
from app.kernel.domain.inscripcion.errors import FirmaDuplicada, TipoFirmanteInvalido

class RegistrarFirmaCommand(BaseModel):
    formulario_id: int
    tipo_firmante: TipoFirmante
    firmante: str = Field(min_length=2, max_length=120)
    firma_url: str
    ip: Optional[str] = Field(default=None, max_length=50)
    user_agent: Optional[str] = None
    reemplazar: bool = True

class RegistrarFirmaUseCase:
    def __init__(self, firma_repo: FirmaRepositoryPort):
        self.firma_repo = firma_repo

    async def execute(self, cmd: RegistrarFirmaCommand) -> Firma:
        if cmd.tipo_firmante not in (TipoFirmante.MADRE, TipoFirmante.PADRE, TipoFirmante.TUTOR):
            raise TipoFirmanteInvalido(cmd.tipo_firmante.value)
        existente = await self.firma_repo.obtener_por_formulario_y_tipo(cmd.formulario_id, cmd.tipo_firmante)
        nueva = Firma(id=0, formulario_id=cmd.formulario_id, tipo_firmante=cmd.tipo_firmante, firmante=cmd.firmante, firma_url=cmd.firma_url, ip=cmd.ip, user_agent=cmd.user_agent)
        if existente and not cmd.reemplazar:
            raise FirmaDuplicada(cmd.formulario_id, cmd.tipo_firmante.value)
        if existente and cmd.reemplazar:
            return await self.firma_repo.reemplazar(nueva)
        return await self.firma_repo.crear(nueva)

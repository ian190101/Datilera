# app/kernel/application/sede/editar_sede.py
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.kernel.domain.seguridad.sede_entidad import Sede as SedeDomain
from app.kernel.domain.seguridad.errors import SedeNoEncontrada, SedeCodigoDuplicado
from app.kernel.domain.seguridad.ports import AbstractSedeRepository


class EditarSedeDTO(BaseModel):
    sede_id: int = Field(..., gt=0)
    codigo: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=120)
    direccion: Optional[str] = Field(None, max_length=250)
    activo: Optional[bool] = None
    config_alerta_vencimiento_dias: Optional[str] = Field(None, max_length=15)

    @field_validator("codigo")
    @classmethod
    def _norm_codigo(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().upper() if isinstance(v, str) else v

    @field_validator("nombre")
    @classmethod
    def _norm_nombre(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v


class EditarSede:
    """
    Caso de uso: Editar una sede utilizando el puerto AbstractSedeRepository.
    Requiere que el puerto exponga get(...), get_by_codigo(...), update(...). 
    """

    def __init__(self, sede_repo: AbstractSedeRepository):
        self.sede_repo = sede_repo

    async def execute(self, dto: EditarSedeDTO) -> SedeDomain:
        # 1) Verificar existencia
        actual = await self.sede_repo.get(dto.sede_id)
        if not actual:
            raise SedeNoEncontrada(f"Sede con ID {dto.sede_id} no encontrada")

        # 2) Unicidad de código global si se solicita cambio
        if dto.codigo:
            nuevo_codigo = dto.codigo.strip().upper()
            if nuevo_codigo != actual.codigo:
                existente = await self.sede_repo.get_by_codigo(nuevo_codigo)
                if existente and getattr(existente, "id", None) != actual.id:
                    raise SedeCodigoDuplicado(f"El código '{nuevo_codigo}' ya existe")

        # 3) Construir payload de actualización
        data = {
            k: v for k, v in dto.model_dump().items()
            if k != "sede_id" and v is not None
        }

        # 4) Persistir y retornar entidad de dominio
        actualizado = await self.sede_repo.update(dto.sede_id, data)
        return SedeDomain.model_validate(actualizado)

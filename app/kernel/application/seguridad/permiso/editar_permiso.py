# app/kernel/application/seguridad/permisos/editar_permiso.py
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.kernel.domain.seguridad.permiso_entidad import Permiso, Accion
from app.kernel.domain.seguridad.errors import PermisoNoEncontrado, PermisoYaExiste
from app.kernel.domain.seguridad.ports import AbstractPermisoRepository


class EditarPermisoDTO(BaseModel):
    permiso_id: int = Field(..., gt=0)
    recurso: Optional[str] = Field(None, max_length=80)
    accion: Optional[Accion] = None
    descripcion: Optional[str] = Field(None, max_length=200)
    activo: Optional[bool] = None

    @field_validator("recurso")
    @classmethod
    def _norm_recurso(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        nv = v.strip().upper()
        if not nv:
            raise ValueError("El recurso no puede estar vacío")
        return nv


class EditarPermiso:
    """Caso de uso: Editar un permiso existente."""
    def __init__(self, permiso_repo: AbstractPermisoRepository):
        self.permiso_repo = permiso_repo

    async def execute(self, dto: EditarPermisoDTO) -> Permiso:
        actual = await self.permiso_repo.get(dto.permiso_id)
        if not actual:
            raise PermisoNoEncontrado(f"Permiso con ID {dto.permiso_id} no encontrado")

        # Si cambia recurso o acción, validar unicidad
        recurso_nuevo = dto.recurso if dto.recurso else actual.recurso
        accion_nueva = dto.accion if dto.accion else actual.accion

        if (dto.recurso and dto.recurso != actual.recurso) or (
            dto.accion and dto.accion != actual.accion
        ):
            colision = await self.permiso_repo.get_by_recurso_y_accion(recurso_nuevo, accion_nueva)
            if colision:
                raise PermisoYaExiste(
                    f"Ya existe un permiso para '{recurso_nuevo}' con acción '{accion_nueva.value}'"
                )

        data = {k: v for k, v in dto.model_dump().items() if k != "permiso_id" and v is not None}
        actualizado = await self.permiso_repo.update(dto.permiso_id, data)
        return actualizado

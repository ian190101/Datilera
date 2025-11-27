# app/kernel/application/seguridad/permisos/crear_permiso.py
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.kernel.domain.seguridad.permiso_entidad import Permiso, Accion
from app.kernel.domain.seguridad.errors import PermisoYaExiste
from app.kernel.domain.seguridad.ports import AbstractPermisoRepository


class CrearPermisoDTO(BaseModel):
    recurso: str = Field(..., max_length=80)
    accion: Accion
    descripcion: Optional[str] = Field(None, max_length=200)
    activo: bool = True

    @field_validator("recurso")
    @classmethod
    def _norm_recurso(cls, v: str) -> str:
        nv = v.strip().upper()
        if not nv:
            raise ValueError("El recurso no puede estar vacío")
        return nv


class CrearPermiso:
    """Caso de uso: Crear un permiso con recurso y acción únicos."""
    def __init__(self, permiso_repo: AbstractPermisoRepository):
        self.permiso_repo = permiso_repo

    async def execute(self, dto: CrearPermisoDTO) -> Permiso:
        # Validar unicidad por recurso + acción
        existente = await self.permiso_repo.get_by_recurso_y_accion(dto.recurso, dto.accion)
        if existente:
            raise PermisoYaExiste(
                f"Ya existe un permiso para '{dto.recurso}' con acción '{dto.accion.value}'"
            )

        permiso = await self.permiso_repo.crear(
            recurso=dto.recurso,
            accion=dto.accion,
            descripcion=dto.descripcion,
            activo=dto.activo,
        )
        return permiso

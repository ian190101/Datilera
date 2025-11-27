# app/kernel/application/academico/grupos/editar_grupo.py
"""Caso de uso: Editar (actualizar) datos de un grupo."""

from __future__ import annotations

from typing import Optional, Mapping, Any

from pydantic import BaseModel, Field, field_validator

from app.kernel.domain.academico.grupos_entidad import Grupo
from app.kernel.domain.academico.errors import GrupoNoEncontrado, GrupoNombreDuplicado
from app.kernel.domain.academico.ports import IGrupoRepository


class EditarGrupoDTO(BaseModel):
    """
    DTO para actualizar un grupo.
    Solo incluye campos realmente editables desde la UI/negocio.
    No permitimos cambiar 'sede_id' ni 'gestion' aquí para mantener la unicidad estable.
    """
    letra: Optional[str] = Field(default=None, max_length=5)    
    nombre: Optional[str] = Field(default=None, max_length=80)
    tutor_id: Optional[int] = None
    activo: Optional[bool] = None

    @field_validator("letra")
    @classmethod
    def _clean_letra(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v2 = v.strip()
        # Normaliza (ej. mayúsculas) si tu dominio lo requiere:
        v2 = v2.upper()
        if not v2:
            return None
        return v2

    @field_validator("nombre")
    @classmethod
    def _clean_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v2 = v.strip()
        return v2 or None

    @field_validator("tutor_id")
    @classmethod
    def _valid_tutor(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v <= 0:
            raise ValueError("tutor_id debe ser un entero positivo")
        return v


class EditarGrupo:
    """Caso de uso: Editar un grupo existente."""

    def __init__(self, grupo_repo: IGrupoRepository):
        self.grupo_repo = grupo_repo

    async def execute(self, grupo_id: int, dto: EditarGrupoDTO) -> Grupo:
        """
        Actualiza campos del grupo.

        Args:
            grupo_id: ID del grupo a actualizar.
            dto: Datos a actualizar (parcial).

        Returns:
            Entidad Grupo actualizada.

        Raises:
            GrupoNoEncontrado: Si el grupo no existe.
            GrupoNombreDuplicado: Si la nueva 'letra' ya está en uso en la misma sede y gestión.
            ValueError: Si los datos no cumplen reglas básicas.
        """

        # 1) Obtener estado actual
        actual = await self.grupo_repo.get(grupo_id)
        if not actual:
            raise GrupoNoEncontrado(f"Grupo con ID {grupo_id} no encontrado")

        # actual es dict (convención). Si fuera entidad, usa getattr.
        sede_id = actual.get("sede_id")
        gestion = actual.get("gestion")

        if sede_id is None or gestion is None:
            # Protección si el repo no provee estos campos
            raise ValueError("El grupo carece de 'sede_id' o 'gestion' necesarios para validar unicidad")

        data_actualizar: dict[str, Any] = {}

        # 2) Validar / preparar 'letra'
        if dto.letra is not None and dto.letra != actual.get("letra"):
            # Validación de unicidad por sede + gestión (case-insensitive)
            existe = await self.grupo_repo.exists_letra_ci(
                sede_id=sede_id,
                gestion=gestion,
                letra=dto.letra,
                excluir_id=grupo_id,
            )
            if existe:
                raise GrupoNombreDuplicado(
                    f"Ya existe un grupo con la letra '{dto.letra}' en la sede {sede_id} para la gestión {gestion}"
                )
            data_actualizar["letra"] = dto.letra

        # 3) 'nombre' (no suele ser único, pero limpiamos y aplicamos)
        if dto.nombre is not None and dto.nombre != actual.get("nombre"):
            data_actualizar["nombre"] = dto.nombre

        # 4) 'tutor_id' (opcional)
        if dto.tutor_id is not None and dto.tutor_id != actual.get("tutor_id"):
            data_actualizar["tutor_id"] = dto.tutor_id

        # 5) 'activo' (soft toggle)
        if dto.activo is not None and dto.activo != actual.get("activo"):
            data_actualizar["activo"] = dto.activo

        # 6) Persistir si hay cambios
        if data_actualizar:
            await self.grupo_repo.update(grupo_id, data_actualizar)

        # 7) Retornar entidad actualizada
        actualizado = await self.grupo_repo.get(grupo_id)
        return Grupo.model_validate(actualizado)
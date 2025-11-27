# app/kernel/application/academico/paralelos/actualizar_paralelo.py
from __future__ import annotations


from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, field_validator


from app.kernel.domain.academico.paralelos_entidad import Paralelo
from app.kernel.domain.academico.ports import IParaleloRepository
from app.kernel.domain.academico.errors import (
    ParaleloNoEncontrado,
    ParaleloNombreDuplicado,
)


class ActualizarParaleloDTO(BaseModel):
    nombre: Optional[str] = Field(None, max_length=50)
    nivel_id: Optional[int] = None  # si es movible entre niveles

    @field_validator("nombre")
    @classmethod
    def _strip_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v2 = v.strip()
        return v2 or None

class ActualizarHorarioDTO(BaseModel):
    """DTO para actualizar un horario."""
    nombre: str | None = Field(None, max_length=50)
    hora_inicio: str | None = None
    hora_fin: str | None = None

class ActualizarParalelo:
    """Caso de uso: Actualizar un paralelo existente."""
    def __init__(self, paralelo_repo: IParaleloRepository):
        self.paralelo_repo = paralelo_repo

    async def execute(self, paralelo_id: int, dto: ActualizarParaleloDTO) -> Paralelo:
        # 1) Verificar existencia
        actual = await self.paralelo_repo.get(paralelo_id)
        if not actual:
            raise ParaleloNoEncontrado(f"Paralelo con ID {paralelo_id} no encontrado")

        data_actualizar: dict = {}

        # 2) Validar nombre duplicado si cambia
        if dto.nombre is not None and dto.nombre != actual["nombre"]:
            # Tomar el contexto (nivel_id) actual o el nuevo si viene en DTO
            nivel_id = dto.nivel_id if dto.nivel_id is not None else actual.get("nivel_id")
            if await self.paralelo_repo.exists_nombre_ci(
                nombre=dto.nombre,
                nivel_id=nivel_id,
                excluir_id=paralelo_id
            ):
                raise ParaleloNombreDuplicado(
                    f"Ya existe un paralelo con el nombre '{dto.nombre}'"
                )
            data_actualizar["nombre"] = dto.nombre

        # 3) Si se mueve de nivel (opcional)
        if dto.nivel_id is not None and dto.nivel_id != actual.get("nivel_id"):
            data_actualizar["nivel_id"] = dto.nivel_id

        # 4) Persistir cambios si los hay
        if data_actualizar:
            await self.paralelo_repo.update(paralelo_id, data_actualizar)

        actualizado = await self.paralelo_repo.get(paralelo_id)
        return Paralelo.model_validate(actualizado)
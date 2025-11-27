# app/kernel/application/academico/horarios/crear_horario.py
"""Caso de uso: Crear un horario."""
from datetime import time
from pydantic import BaseModel, Field, field_validator

from app.kernel.domain.academico.horarios_entidad import Horario
from app.kernel.domain.academico.ports import IHorarioRepository
from app.kernel.domain.academico.errors import HorarioNombreDuplicado


class CrearHorarioDTO(BaseModel):
    """DTO para crear un horario."""
    nombre: str = Field(..., max_length=50, description="Nombre del horario")
    hora_inicio: time = Field(..., description="Hora de inicio (HH:MM)")
    hora_fin: time = Field(..., description="Hora de fin (HH:MM)")

    @field_validator("nombre")
    @classmethod
    def _strip_nombre(cls, v: str) -> str:
        nv = v.strip()
        if not nv:
            raise ValueError("El nombre no puede estar vacío")
        return nv

    @field_validator("hora_fin")
    @classmethod
    def _validar_rango(cls, v: time, values):
        hi = values.get("hora_inicio")
        if hi is not None and hi >= v:
            raise ValueError("hora_fin debe ser mayor que hora_inicio")
        return v


class CrearHorario:
    """Caso de uso: Crear un nuevo horario."""
    def __init__(self, horario_repo: IHorarioRepository):
        self.horario_repo = horario_repo

    async def execute(self, dto: CrearHorarioDTO) -> Horario:
        """
        Crea un nuevo horario validando que no exista duplicado.
        """
        # 1) Unicidad por nombre (case-insensitive)
        if await self.horario_repo.exists_nombre_ci(nombre=dto.nombre):
            raise HorarioNombreDuplicado(
                f"Ya existe un horario con el nombre '{dto.nombre}'"
            )


        # 2) Crear
        nuevo = await self.horario_repo.create({
            "nombre": dto.nombre,
            "hora_inicio": dto.hora_inicio,
            "hora_fin": dto.hora_fin,
        })

        # 3) Retornar entidad de dominio
        return Horario.model_validate(nuevo)
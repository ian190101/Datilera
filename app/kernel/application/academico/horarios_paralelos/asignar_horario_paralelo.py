#app/kernel/application/academico/horarios_paralelos/asignar_horario_paralelo.py
"""Caso de uso: Asignar un horario a un paralelo (con validaciones)."""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.kernel.domain.academico.horarios_paralelos_entidad import HorarioParalelo
from app.kernel.domain.academico.ports import (
    IHorarioParaleloRepository,
    IParaleloRepository,
    IHorarioRepository,
)
from app.kernel.domain.academico.errors import (
    ParaleloNoEncontrado,
    HorarioNoEncontrado,
    HorarioParaleloSolapado,
    HorarioParaleloPeriodoInvalido,
)


class AsignarHorarioParaleloDTO(BaseModel):
    """DTO para asignar un horario a un paralelo."""
    paralelo_id: int = Field(..., gt=0)
    horario_id: int = Field(..., gt=0)
    desde: date
    hasta: date

    @field_validator("hasta")
    @classmethod
    def _validar_rango(cls, v: date, values):
        d = values.get("desde")
        if d is not None and v < d:
            raise ValueError("La fecha 'hasta' debe ser posterior o igual a 'desde'")
        return v


class AsignarHorarioParalelo:
    """Caso de uso: Asignar un horario a un paralelo."""

    def __init__(
        self,
        horario_paralelo_repo: IHorarioParaleloRepository,
        paralelo_repo: IParaleloRepository,
        horario_repo: IHorarioRepository,
    ):
        self.horario_paralelo_repo = horario_paralelo_repo
        self.paralelo_repo = paralelo_repo
        self.horario_repo = horario_repo

    async def execute(self, dto: AsignarHorarioParaleloDTO) -> HorarioParalelo:
        """
        Asigna un horario a un paralelo validando existencia y solapes.

        Reglas:
        - El paralelo y horario deben existir.
        - 'hasta' >= 'desde'.
        - No permitir asignaciones solapadas para el mismo paralelo.
        """
        # 1) Validar paralelo
        paralelo = await self.paralelo_repo.get(dto.paralelo_id)
        if not paralelo:
            raise ParaleloNoEncontrado(f"Paralelo con ID {dto.paralelo_id} no encontrado")

        # 2) Validar horario
        horario = await self.horario_repo.get(dto.horario_id)
        if not horario:
            raise HorarioNoEncontrado(f"Horario con ID {dto.horario_id} no encontrado")

        # 3) Validación de periodo
        if dto.hasta < dto.desde:
            raise HorarioParaleloPeriodoInvalido(
                f"La fecha 'hasta' ({dto.hasta}) debe ser posterior o igual a 'desde' ({dto.desde})"
            )

        # 4) Validar solapamiento para el mismo paralelo
        hay_solape = await self.horario_paralelo_repo.existe_solape(
            paralelo_id=dto.paralelo_id,
            desde=dto.desde,
            hasta=dto.hasta,
        )
        if hay_solape:
            raise HorarioParaleloSolapado(
                "Ya existe una asignación de horario que se solapa para este paralelo."
            )

        # 5) Crear la asignación
        nueva_asignacion = await self.horario_paralelo_repo.create({
            "paralelo_id": dto.paralelo_id,
            "horario_id": dto.horario_id,
            "desde": dto.desde,
            "hasta": dto.hasta,
        })

        return HorarioParalelo.model_validate(nueva_asignacion)
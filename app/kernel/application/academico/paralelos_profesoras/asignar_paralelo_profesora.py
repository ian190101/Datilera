#app/kernel/application/academico/paralelos_profesoras/asignar_profesora_paralelo.py
"""Caso de uso: Asignar una profesora a un paralelo (con validaciones robustas)."""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.kernel.domain.academico.paralelos_profesoras_entidad import ParaleloProfesora
from app.kernel.domain.academico.ports import (
    IParaleloProfesorRepository,
    IParaleloRepository,
    # IProfesoraRepository,  # si quieres validar existencia de profesora
)
from app.kernel.domain.academico.errors import (
    ParaleloNoEncontrado,
    ParaleloProfesorSolapado,
    ParaleloProfesorPeriodoInvalido,
    # ProfesoraNoEncontrada,  # si lo manejas
)


class AsignarProfesoraParaleloDTO(BaseModel):
    """DTO para asignar una profesora a un paralelo."""
    paralelo_id: int = Field(..., gt=0)
    profesora_id: int = Field(..., gt=0)  # renombrado a 'profesora_id' para el folder
    gestion: int = Field(..., ge=2020, le=2100)
    desde: date
    hasta: date

    @field_validator("hasta")
    @classmethod
    def _validar_rango(cls, v: date, values):
        d = values.get("desde")
        if d is not None and v < d:
            raise ValueError("La fecha 'hasta' debe ser posterior o igual a 'desde'")
        return v


class AsignarProfesoraParalelo:
    """Caso de uso: Asignar una profesora a un paralelo."""

    def __init__(
        self,
        paralelo_profesora_repo: IParaleloProfesorRepository,
        paralelo_repo: IParaleloRepository,
        # profesoras_repo: IProfesoraRepository | None = None,  # opcional
    ):
        self.paralelo_profesora_repo = paralelo_profesora_repo
        self.paralelo_repo = paralelo_repo
        # self.profesoras_repo = profesoras_repo

    async def execute(self, dto: AsignarProfesoraParaleloDTO) -> ParaleloProfesora:
        """
        Asigna una profesora a un paralelo validando disponibilidad, solapes y duplicados.

        Reglas:
        - El paralelo debe existir.
        - 'hasta' >= 'desde'.
        - No permitir asignaciones solapadas para la misma profesora en la misma gestión.
        - No permitir duplicado exacto (misma profesora, paralelo, gestión y periodo idéntico).
        """
        # 1) Validar que el paralelo existe
        paralelo = await self.paralelo_repo.get(dto.paralelo_id)
        if not paralelo:
            raise ParaleloNoEncontrado(f"Paralelo con ID {dto.paralelo_id} no encontrado")

        # 2) (Opcional) Validar que la profesora exista
        # if self.profesoras_repo:
        #     prof = await self.profesoras_repo.get(dto.profesora_id)
        #     if not prof:
        #         raise ProfesoraNoEncontrada(f"Profesora con ID {dto.profesora_id} no encontrada")

        # 3) Validación de periodo (ya cubierta por el DTO; refuerzo semántico)
        if dto.hasta < dto.desde:
            raise ParaleloProfesorPeriodoInvalido(
                f"La fecha 'hasta' ({dto.hasta}) debe ser posterior o igual a 'desde' ({dto.desde})"
            )

        # 4) Evitar asignación duplicada exacta (mismo paralelo, profesora, gestión y periodo)
        existe_exacta = await self.paralelo_profesora_repo.exists_exacta(
            profesora_id=dto.profesora_id,
            paralelo_id=dto.paralelo_id,
            gestion=dto.gestion,
            desde=dto.desde,
            hasta=dto.hasta,
        )
        if existe_exacta:
            # Puedes usar el mismo error de solape o uno específico (Duplicada)
            raise ParaleloProfesorSolapado(
                "Ya existe una asignación idéntica (misma profesora, paralelo, gestión y periodo)."
            )

        # 5) Validar solapamiento por gestión para la misma profesora
        # Regla: si (nuevo.desde <= existente.hasta) y (nuevo.hasta >= existente.desde) -> solapa (inclusive en bordes)
        # Si quieres bordes no solapados cuando tocan exacto, cambia a (< y > estrictos).
        hay_solape = await self.paralelo_profesora_repo.existe_solape(
            profesora_id=dto.profesora_id,
            gestion=dto.gestion,
            desde=dto.desde,
            hasta=dto.hasta,
        )
        if hay_solape:
            raise ParaleloProfesorSolapado(
                "La profesora ya tiene una asignación que se solapa en la misma gestión."
            )

        # 6) Crear la asignación
        nueva_asignacion = await self.paralelo_profesora_repo.create({
            "paralelo_id": dto.paralelo_id,
            "profesora_id": dto.profesora_id,
            "gestion": dto.gestion,
            "desde": dto.desde,
            "hasta": dto.hasta,
        })

        return ParaleloProfesora.model_validate(nueva_asignacion)
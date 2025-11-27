#app/kernel/application/academico/horarios/actualizar_horario.py
"""Caso de uso: Actualizar un horario."""
from pydantic import BaseModel, Field
from sqlalchemy import func, and_
from app.kernel.domain.academico.horarios_entidad import Horario
from app.kernel.domain.academico.ports import IHorarioRepository
from app.kernel.domain.academico.errors import (
HorarioNoEncontrado,
HorarioNombreDuplicado
)

class ActualizarHorarioDTO(BaseModel):
    """DTO para actualizar un horario."""
    nombre: str | None = Field(None, max_length=50)
    hora_inicio: str | None = None
    hora_fin: str | None = None


class ActualizarHorario:
    def __init__(self, horario_repo: IHorarioRepository):
        self.horario_repo = horario_repo

    async def execute(self, horario_id: int, dto: ActualizarHorarioDTO) -> Horario:
        horario_actual = await self.horario_repo.get(horario_id)
        if not horario_actual:
            raise HorarioNoEncontrado(f"Horario con ID {horario_id} no encontrado")

        data_actualizar: dict = {}

        # nombre
        if dto.nombre and dto.nombre != horario_actual["nombre"]:
            if await self.horario_repo.exists_nombre_ci(nombre=dto.nombre, excluir_id=horario_id):
                raise HorarioNombreDuplicado(
                    f"Ya existe un horario con el nombre '{dto.nombre}'"
                )
            data_actualizar["nombre"] = dto.nombre

        # horas (combina dto + actuales y valida)
        hora_inicio = dto.hora_inicio if dto.hora_inicio is not None else horario_actual["hora_inicio"]
        hora_fin = dto.hora_fin if dto.hora_fin is not None else horario_actual["hora_fin"]
        if hora_inicio is not None and hora_fin is not None and hora_inicio >= hora_fin:
            raise ValueError("La hora de inicio debe ser menor que la hora de fin")

        if dto.hora_inicio is not None:
            data_actualizar["hora_inicio"] = dto.hora_inicio
        if dto.hora_fin is not None:
            data_actualizar["hora_fin"] = dto.hora_fin

        if data_actualizar:
            await self.horario_repo.update(horario_id, data_actualizar)

        actualizado = await self.horario_repo.get(horario_id)
        return Horario.model_validate(actualizado)

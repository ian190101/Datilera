# app/kernel/application/academico/horarios/eliminar_horario.py
"""Caso de uso: Eliminar un horario."""
from app.kernel.domain.academico.ports import IHorarioRepository, IHorarioParaleloRepository
from app.kernel.domain.academico.errors import HorarioNoEncontrado, HorarioEnUso


class EliminarHorario:
    """Caso de uso: Eliminar un horario."""

    def __init__(
        self,
        horario_repo: IHorarioRepository,
        horario_paralelo_repo: IHorarioParaleloRepository
    ):
        self.horario_repo = horario_repo
        self.horario_paralelo_repo = horario_paralelo_repo

    async def execute(self, horario_id: int) -> None:
        """
        Elimina un horario si no está en uso.

        Raises:
            HorarioNoEncontrado: Si el horario no existe
            HorarioEnUso: Si el horario está asignado a algún paralelo
        """
        # 1) Verificar existencia
        horario = await self.horario_repo.get(horario_id)
        if not horario:
            raise HorarioNoEncontrado(f"Horario con ID {horario_id} no encontrado")

        # 2) Verificar que no esté en uso (sin tocar ORM desde la app)
        total_asignaciones = await self.horario_paralelo_repo.count_by_horario(horario_id)
        if total_asignaciones > 0:
            # Ojo: 'horario' es dict (según tu repo). Usa indexación.
            nombre = horario.get("nombre") or f"ID {horario_id}"
            raise HorarioEnUso(
                f"El horario '{nombre}' está asignado a {total_asignaciones} paralelo(s)"
            )

        # 3) Eliminar (hard delete)
        await self.horario_repo.delete(horario_id)
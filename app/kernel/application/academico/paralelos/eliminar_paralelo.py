# app/kernel/application/academico/paralelos/eliminar_paralelo.py
from __future__ import annotations

from app.kernel.domain.academico.ports import IParaleloRepository
from app.kernel.domain.academico.errors import (
    ParaleloNoEncontrado,
    ParaleloConDependencias,
)

class EliminarParalelo:
    """
    Caso de uso: Eliminar un paralelo (hard o soft).
    Si hay dependencias (matrículas, asignaciones), lanza error.
    """

    def __init__(self, paralelo_repo: IParaleloRepository, *, soft: bool = False, validar_dependencias: bool = True):
        self.paralelo_repo = paralelo_repo
        self.soft = soft
        self.validar_dependencias = validar_dependencias

    async def execute(self, paralelo_id: int) -> None:
        existente = await self.paralelo_repo.get(paralelo_id)
        if not existente:
            raise ParaleloNoEncontrado(f"Paralelo con ID {paralelo_id} no encontrado")

        if self.soft:
            # Soft delete
            await self.paralelo_repo.delete(paralelo_id)
        else:
            # Hard delete
            await self.paralelo_repo.delete(paralelo_id)
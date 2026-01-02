# app/application/finanzas/categoria_egreso/actualizar_categoria_egreso.py
"""
CU: Actualizar Categoría de Egreso
"""
from dataclasses import dataclass
from typing import Optional

from app.kernel.domain.finanzas import CategoriaEgreso
from app.kernel.domain.finanzas.ports import ICategoriaEgresoRepository
from app.kernel.domain.finanzas.errors import (
    CategoriaEgresoNoEncontradaError,
    CategoriaEgresoYaExisteError
)


@dataclass
class ActualizarCategoriaEgresoCommand:
    """Comando para actualizar categoría de egreso"""
    categoria_id: int
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None
    usuario_id: int = None


class ActualizarCategoriaEgresoUseCase:
    """Caso de uso: Actualizar categoría de egreso"""

    def __init__(self, categoria_repo: ICategoriaEgresoRepository):
        self.categoria_repo = categoria_repo

    async def execute(self, command: ActualizarCategoriaEgresoCommand) -> CategoriaEgreso:
        """
        Actualiza una categoría de egreso existente
        
        Raises:
            CategoriaEgresoNoEncontrada: Si no existe la categoría
            CategoriaEgresoDuplicada: Si el nuevo nombre ya existe
        """
        # Obtener categoría existente
        categoria = await self.categoria_repo.obtener_por_id(command.categoria_id)
        if not categoria:
            raise CategoriaEgresoNoEncontradaError(command.categoria_id)

        # Validar nombre único si se cambia
        if command.nombre and command.nombre != categoria.nombre:
            existe = await self.categoria_repo.existe_nombre_en_sede(
                sede_id=categoria.sede_id,
                nombre=command.nombre,
                excluir_id=categoria.id
            )
            if existe:
                raise CategoriaEgresoYaExisteError(command.nombre, categoria.sede_id)
            categoria.nombre = command.nombre.strip()

        # Actualizar campos opcionales
        if command.descripcion is not None:
            categoria.descripcion = command.descripcion
        if command.activa is not None:
            if command.activa:
                categoria.activar()
            else:
                categoria.desactivar()

        # Persistir
        return await self.categoria_repo.actualizar(categoria)

# app/application/finanzas/actualizar_categoria_pago.py
"""
CU: Actualizar Categoría de Pago
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.kernel.domain.finanzas import CategoriaPago
from app.kernel.domain.finanzas.ports import ICategoriaPagoRepository
from app.kernel.domain.finanzas.errors import (
    CategoriaPagoNoEncontradaError,
    CategoriaPagoYaExisteError
)


@dataclass
class ActualizarCategoriaPagoCommand:
    """Comando para actualizar categoría de pago"""
    categoria_id: int
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    monto_base: Optional[Decimal] = None
    activa: Optional[bool] = None
    usuario_id: int = None


class ActualizarCategoriaPagoUseCase:
    """Caso de uso: Actualizar categoría de pago"""

    def __init__(self, categoria_repo: ICategoriaPagoRepository):
        self.categoria_repo = categoria_repo

    async def execute(self, command: ActualizarCategoriaPagoCommand) -> CategoriaPago:
        """
        Actualiza una categoría de pago existente
        
        Raises:
            CategoriaPagoNoEncontrada: Si no existe la categoría
            CategoriaPagoDuplicada: Si el nuevo nombre ya existe
        """
        # Obtener categoría existente
        categoria = await self.categoria_repo.obtener_por_id(command.categoria_id)
        if not categoria:
            raise CategoriaPagoNoEncontradaError(command.categoria_id)

        # Validar nombre único si se cambia
        if command.nombre and command.nombre != categoria.nombre:
            existe = await self.categoria_repo.existe_nombre_en_sede(
                sede_id=categoria.sede_id,
                nombre=command.nombre,
                excluir_id=categoria.id
            )
            if existe:
                raise CategoriaPagoYaExisteError(command.nombre, categoria.sede_id)
            categoria.nombre = command.nombre.strip()

        # Actualizar campos opcionales
        if command.descripcion is not None:
            categoria.descripcion = command.descripcion
        if command.monto_base is not None:
            categoria.monto_base = command.monto_base
        if command.activa is not None:
            categoria.activa = command.activa

        # Persistir
        return await self.categoria_repo.actualizar(categoria)

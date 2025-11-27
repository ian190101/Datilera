# app/application/finanzas/categoria_pago/crear_categoria_pago.py
"""
CU: Crear Categoría de Pago
HU: Como administrador/contador, quiero crear categorías de pago dinámicas por sede
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.kernel.domain.finanzas import CategoriaPago
from app.kernel.domain.finanzas.ports import CategoriaPagoRepositoryPort
from app.kernel.domain.finanzas.errors import CategoriaPagoDuplicada


@dataclass
class CrearCategoriaPagoCommand:
    """Comando para crear categoría de pago"""
    sede_id: int
    nombre: str
    descripcion: Optional[str] = None
    monto_base: Optional[Decimal] = None
    usuario_id: int = None  # Para auditoría


class CrearCategoriaPagoUseCase:
    """
    Caso de uso: Crear categoría de pago
    
    Validaciones:
    - Nombre único por sede
    - Monto base >= 0 si se proporciona
    """

    def __init__(self, categoria_repo: CategoriaPagoRepositoryPort):
        self.categoria_repo = categoria_repo

    async def execute(self, command: CrearCategoriaPagoCommand) -> CategoriaPago:
        """
        Crea una nueva categoría de pago
        
        Raises:
            CategoriaPagoDuplicada: Si ya existe una categoría con ese nombre en la sede
            ValueError: Si los datos son inválidos
        """
        # Validar nombre único en sede
        existe = await self.categoria_repo.existe_nombre_en_sede(
            sede_id=command.sede_id,
            nombre=command.nombre
        )
        if existe:
            raise CategoriaPagoDuplicada(command.nombre, command.sede_id)

        # Crear entidad
        categoria = CategoriaPago(
            id=0,  # Se asigna en BD
            sede_id=command.sede_id,
            nombre=command.nombre.strip(),
            descripcion=command.descripcion,
            monto_base=command.monto_base,
            activa=True
        )

        # Persistir
        return await self.categoria_repo.crear(categoria)

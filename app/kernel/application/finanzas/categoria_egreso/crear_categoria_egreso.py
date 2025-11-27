# app/application/finanzas/categoria_egreso/crear_categoria_egreso.py
"""
CU: Crear Categoría de Egreso
HU: Como administrador/contador, quiero crear categorías de egreso dinámicas por sede
"""
from dataclasses import dataclass
from typing import Optional

from app.kernel.domain.finanzas import CategoriaEgreso
from app.kernel.domain.finanzas.ports import CategoriaEgresoRepositoryPort
from app.kernel.domain.finanzas.errors import CategoriaEgresoDuplicada


@dataclass
class CrearCategoriaEgresoCommand:
    """Comando para crear categoría de egreso"""
    sede_id: int
    nombre: str
    descripcion: Optional[str] = None
    usuario_id: int = None


class CrearCategoriaEgresoUseCase:
    """Caso de uso: Crear categoría de egreso"""

    def __init__(self, categoria_repo: CategoriaEgresoRepositoryPort):
        self.categoria_repo = categoria_repo

    async def execute(self, command: CrearCategoriaEgresoCommand) -> CategoriaEgreso:
        """
        Crea una nueva categoría de egreso
        
        Raises:
            CategoriaEgresoDuplicada: Si ya existe una categoría con ese nombre
        """
        # Validar nombre único en sede
        existe = await self.categoria_repo.existe_nombre_en_sede(
            sede_id=command.sede_id,
            nombre=command.nombre
        )
        if existe:
            raise CategoriaEgresoDuplicada(command.nombre, command.sede_id)

        # Crear entidad
        categoria = CategoriaEgreso(
            id=0,
            sede_id=command.sede_id,
            nombre=command.nombre.strip(),
            descripcion=command.descripcion,
            activa=True
        )

        # Persistir
        return await self.categoria_repo.crear(categoria)

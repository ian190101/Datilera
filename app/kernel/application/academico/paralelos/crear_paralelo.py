# app/kernel/application/academico/paralelos/crear_paralelo.py
"""Caso de uso: Crear un paralelo."""

from pydantic import BaseModel, Field
from app.kernel.domain.academico.paralelos_entidad import Paralelo
from app.kernel.domain.academico.ports import IParaleloRepository, IGrupoRepository
from app.kernel.domain.academico.errors import GrupoNoEncontrado, ParaleloDuplicado


class CrearParaleloDTO(BaseModel):
    """DTO para crear un paralelo."""
    grupo_id: int = Field(..., gt=0)
    nombre: str | None = Field(None, max_length=50)  # opcional si tu dominio lo requiere


class CrearParalelo:
    """Caso de uso: Crear un nuevo paralelo."""

    def __init__(self, paralelo_repo: IParaleloRepository, grupo_repo: IGrupoRepository):
        self.paralelo_repo = paralelo_repo
        self.grupo_repo = grupo_repo

    async def execute(self, dto: CrearParaleloDTO) -> Paralelo:
        """
        Crea un nuevo paralelo validando que el grupo existe.

        Args:
            dto: Datos del paralelo a crear

        Returns:
            Paralelo creado

        Raises:
            GrupoNoEncontrado: Si el grupo no existe
            ParaleloDuplicado: Si ya existe un paralelo igual (opcional)
        """
        # 1) Validar que el grupo existe
        grupo = await self.grupo_repo.get(dto.grupo_id)
        if not grupo:
            raise GrupoNoEncontrado(f"Grupo con ID {dto.grupo_id} no encontrado")

        # 2) (Opcional) Validar duplicado
        if dto.nombre:
            existe = await self.paralelo_repo.exists_by_nombre_ci(dto.grupo_id, dto.nombre)
            if existe:
                raise ParaleloDuplicado(f"Ya existe un paralelo con nombre '{dto.nombre}' en el grupo {dto.grupo_id}")

        # 3) Crear el paralelo
        nuevo_paralelo = await self.paralelo_repo.create({
            "grupo_id": dto.grupo_id,
            "nombre": dto.nombre
        })

        return Paralelo.model_validate(nuevo_paralelo)
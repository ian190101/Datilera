# app/kernel/application/academico/grupos/crear_grupo.py
"""Caso de uso: Crear un grupo."""
from pydantic import BaseModel, Field, field_validator
from app.kernel.domain.academico.grupos_entidad import Grupo
from app.kernel.domain.academico.ports import IGrupoRepository
from app.kernel.domain.seguridad.ports import AbstractSedeRepository
from app.kernel.domain.academico.errors import GrupoLetraDuplicada
from app.kernel.domain.seguridad.errors import SedeNoEncontrada


class CrearGrupoDTO(BaseModel):
    """DTO para crear un grupo."""
    sede_id: int = Field(..., gt=0)
    nombre: str = Field(..., max_length=100)
    letra: str = Field(..., max_length=10)
    capacidad: int | None = Field(None, ge=0)
    gestion: int = Field(..., ge=2020, le=2100)

    @field_validator("nombre")
    @classmethod
    def _strip_nombre(cls, v: str) -> str:
        nv = v.strip()
        if not nv:
            raise ValueError("El nombre no puede estar vacío")
        return nv

    @field_validator("letra")
    @classmethod
    def _normalize_letra(cls, v: str) -> str:
        nv = v.strip()
        if not nv:
            raise ValueError("La letra no puede estar vacía")
        return nv.upper()


class CrearGrupo:
    """Caso de uso: Crear un nuevo grupo."""

    def __init__(
        self,
        grupo_repo: IGrupoRepository,
        sede_repo: AbstractSedeRepository
    ):
        self.grupo_repo = grupo_repo
        self.sede_repo = sede_repo

    async def execute(self, dto: CrearGrupoDTO) -> Grupo:
        """
        Crea un nuevo grupo validando sede y unicidad.
        Raises:
            SedeNoEncontrada
            GrupoLetraDuplicada
        """
        # 1) Validar sede existente
        sede = await self.sede_repo.get(dto.sede_id)
        if not sede:
            raise SedeNoEncontrada(f"Sede con ID {dto.sede_id} no encontrada")

        # 2) Unicidad: letra por sede+gestion 
        if await self.grupo_repo.exists_letra_en_sede_gestion(
            sede_id=dto.sede_id, letra=dto.letra, gestion=dto.gestion
        ):
            sede_nombre = sede.nombre if sede and sede.nombre else f"ID {dto.sede_id}"
            raise GrupoLetraDuplicada(
                f"Ya existe el grupo '{dto.letra}' en la sede {sede_nombre} para la gestión {dto.gestion}"
            )

        # 3) Crear
        nuevo_grupo = await self.grupo_repo.create({
            "sede_id": dto.sede_id,
            "nombre": dto.nombre,         
            "letra": dto.letra,           
            "capacidad": dto.capacidad,
            "gestion": dto.gestion,
            "activo": True
        })

        # 4) Retornar entidad de dominio
        return Grupo.model_validate(nuevo_grupo)
# app/kernel/application/sede/crear_sede.py
from pydantic import BaseModel, Field, field_validator
from app.kernel.domain.seguridad.sede_entidad import Sede
from app.kernel.domain.seguridad.errors import SedeCodigoDuplicado
from app.kernel.domain.seguridad.ports import AbstractSedeRepository

class CrearSedeDTO(BaseModel):
    codigo: str = Field(..., max_length=10)
    nombre: str = Field(..., max_length=120)
    direccion: str | None = Field(None, max_length=250)
    config_alerta_vencimiento_dias: str | None = Field(default="5,3,1", max_length=15)

    @field_validator("codigo")
    @classmethod
    def _norm_codigo(cls, v: str) -> str:
        nv = v.strip().upper()
        if not nv:
            raise ValueError("El código no puede estar vacío")
        return nv

    @field_validator("nombre")
    @classmethod
    def _norm_nombre(cls, v: str) -> str:
        nv = v.strip()
        if not nv:
            raise ValueError("El nombre no puede estar vacío")
        return nv

class CrearSede:
    def __init__(self, sede_repo: AbstractSedeRepository):
        self.sede_repo = sede_repo

    async def execute(self, dto: CrearSedeDTO) -> Sede:
        # unicidad por código
        existente = await self.sede_repo.get_by_codigo(dto.codigo)
        if existente:
            raise SedeCodigoDuplicado(f"El código '{dto.codigo}' ya existe")

        nueva = await self.sede_repo.crear({
            "codigo": dto.codigo,
            "nombre": dto.nombre,
            "direccion": dto.direccion,
            "activo": True,
            "config_alerta_vencimiento_dias": dto.config_alerta_vencimiento_dias or "5,3,1",
        })
        return Sede.model_validate(nueva)
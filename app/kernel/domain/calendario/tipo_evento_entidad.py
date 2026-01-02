# app/kernel/domain/calendario/tipo_evento_entidad.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer


class TipoEvento(BaseModel):
    """Entidad de dominio: Tipo de Evento configurable."""

    id: Optional[int] = None
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)

    # Estilo visual
    color: str = Field(
        default="#3B95F6",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Color en formato hexadecimal de 6 dígitos",
    )
    icono: Optional[str] = Field(None, max_length=50)

    # Configuración de visibilidad y aprobación
    requiere_aprobacion: bool = False
    visible_profesoras: bool = True
    visible_tutores: bool = True

    # Relaciones
    sede_id: int

    # Estado
    activo: bool = True

    # Auditoría
    creado_por: int
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Métodos de dominio
    # ------------------------------------------------------------------
    def activar(self) -> None:
        """Activa el tipo de evento."""
        self.activo = True
        self.actualizado_en = datetime.utcnow()

    def desactivar(self) -> None:
        """Desactiva el tipo de evento."""
        self.activo = False
        self.actualizado_en = datetime.utcnow()

    # ------------------------------------------------------------------
    # Serialización de fechas → ISO 8601 (solo en JSON)
    # ------------------------------------------------------------------
    @field_serializer("creado_en", "actualizado_en", when_used="json")
    def serialize_datetimes(self, value: datetime | None) -> str | None:
        """
        Convierte datetime → str en formato ISO solo cuando se serializa a JSON.
        En Python puro sigue siendo datetime (tipado perfecto).
        """
        return value.isoformat() if value is not None else None

    # ------------------------------------------------------------------
    # Configuración del modelo
    # ------------------------------------------------------------------
    model_config = {
        "from_attributes": True,        # permite TipoEvento(**obj_orm.__dict__)
        "validate_assignment": True,    # valida al hacer model.atributo = valor
        "extra": "forbid",              # opcional: rechaza campos extraños
    }
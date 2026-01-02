# app/kernel/domain/calendario/entities/planificacion_actividad.py

from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, field_serializer


class PlanificacionActividad(BaseModel):
    """Entidad de dominio: Planificación detallada de actividad."""

    id: Optional[int] = None
    evento_id: Optional[int] = None

    # Fecha y horarios
    fecha: date
    hora_inicio: time
    hora_fin: time

    # Detalles de la actividad
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    objetivo: Optional[str] = None
    materiales: Optional[str] = None

    # Responsables y grupo
    profesora_id: int
    paralelo_id: Optional[int] = None

    # Ubicación
    sede_id: int
    lugar: Optional[str] = Field(None, max_length=100)

    # Estado de ejecución
    completada: bool = False
    notas_ejecucion: Optional[str] = None

    # Auditoría
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: Optional[datetime] = None

    # ==================================================================
    # Validadores
    # ==================================================================

    @field_validator("hora_fin")
    @classmethod
    def validar_hora_fin(cls, v: time, values: dict) -> time:
        """Valida que hora_fin sea estrictamente mayor a hora_inicio."""
        hora_inicio = values.data.get("hora_inicio")
        if hora_inicio is not None and v <= hora_inicio:
            raise ValueError("hora_fin debe ser posterior a hora_inicio")
        return v

    # ==================================================================
    # Métodos de dominio
    # ==================================================================

    def marcar_completada(self, notas: Optional[str] = None) -> None:
        """Marca la actividad como completada y guarda notas si las hay."""
        self.completada = True
        self.notas_ejecucion = notas
        self.actualizado_en = datetime.utcnow()

    # ==================================================================
    # Serialización automática a ISO (solo en JSON)
    # ==================================================================

    @field_serializer(
        "fecha",
        "hora_inicio",
        "hora_fin",
        "creado_en",
        "actualizado_en",
        when_used="json"
    )
    def serialize_dates_and_times(
        self, value: date | time | datetime | None
    ) -> str | None:
        """
        Convierte date → "YYYY-MM-DD"
                 time → "HH:MM:SS"
             datetime → "YYYY-MM-DDTHH:MM:SS.ssssss"
        Solo cuando se vuelca a JSON.
        """
        if value is None:
            return None
        return value.isoformat()

    # ==================================================================
    # Configuración del modelo
    # ==================================================================

    model_config = {
        "from_attributes": True,        # Reemplaza orm_mode / from_attributes de v1
        "validate_assignment": True,    # Valida al hacer model.atributo = valor
        "extra": "forbid",              # Recomendado en dominio: rechaza campos desconocidos
    }
# app/kernel/domain/calendario/entities/evento_calendario.py

from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, field_serializer


class EventoCalendario(BaseModel):
    """Entidad de dominio: Evento del calendario."""

    id: Optional[int] = None
    titulo: str = Field(..., min_length=1, max_length=150)
    descripcion: Optional[str] = None

    # Tipo
    tipo_evento_id: int

    # Fechas y horas
    fecha: date
    fecha_fin: Optional[date] = None
    todo_el_dia: bool = True
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None

    # Ubicación
    sede_id: int
    lugar: Optional[str] = Field(None, max_length=100)

    # Relacionado (polimórfico)
    relacionado_tipo: Optional[str] = None
    relacionado_id: Optional[int] = None

    # Aprobación
    aprobado: bool = True
    aprobado_por: Optional[int] = None
    aprobado_en: Optional[datetime] = None

    # Recordatorios
    recordatorio_dias_antes: Optional[int] = Field(None, ge=0, le=30)
    recordatorio_enviado: bool = False

    # Auditoría
    creado_por: int
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: Optional[datetime] = None

    # ==================================================================
    # Validadores
    # ==================================================================

    @field_validator("fecha_fin")
    @classmethod
    def validar_fecha_fin(cls, v: Optional[date], values: dict) -> Optional[date]:
        """Valida que fecha_fin >= fecha."""
        fecha = values.data.get("fecha")
        if v and fecha and v < fecha:
            raise ValueError("fecha_fin debe ser mayor o igual a fecha")
        return v

    @field_validator("hora_fin")
    @classmethod
    def validar_hora_fin(cls, v: Optional[time], values: dict) -> Optional[time]:
        """Valida que hora_fin > hora_inicio (solo si no es todo el día)."""
        if not values.data.get("todo_el_dia", True):
            hora_inicio = values.data.get("hora_inicio")
            if v and hora_inicio and v <= hora_inicio:
                raise ValueError("hora_fin debe ser posterior a hora_inicio")
        return v

    # ==================================================================
    # Métodos de dominio
    # ==================================================================

    def aprobar(self, aprobado_por: int) -> None:
        """Aprobar el evento."""
        self.aprobado = True
        self.aprobado_por = aprobado_por
        self.aprobado_en = datetime.utcnow()
        self.actualizado_en = datetime.utcnow()

    def marcar_recordatorio_enviado(self) -> None:
        """Marca el recordatorio como enviado."""
        self.recordatorio_enviado = True
        self.actualizado_en = datetime.utcnow()
    

    # ==================================================================
    # Serialización automática de fechas/horas a ISO (solo en JSON)
    # ==================================================================

    @field_serializer("fecha", "fecha_fin", "hora_inicio", "hora_fin", "aprobado_en", "creado_en", "actualizado_en", when_used="json")
    def serialize_date_time(self, value: date | time | datetime | None) -> str | None:
        """
        Serializa date, time y datetime a su representación ISO 8601.
        Solo se aplica cuando se vuelca a JSON.
        """
        if value is None:
            return None
        if isinstance(value, (date, datetime)):
            return value.isoformat()[:10] if isinstance(value, date) and not isinstance(value, datetime) else value.isoformat()
        if isinstance(value, time):
            return value.isoformat()
        return str(value)  # fallback (nunca debería llegar aquí)

    # ==================================================================
    # Configuración del modelo
    # ==================================================================

    model_config = {
        "from_attributes": True,        # Equivale a orm_mode = True en v1
        "validate_assignment": True,    # Valida al hacer model.atributo = valor
        "extra": "forbid",              # Opcional: rechaza campos no declarados
    }
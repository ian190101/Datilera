# app/kernel/domain/finanzas/turno_entidad.py
from __future__ import annotations
from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class Turno(BaseModel):
    id: int
    sede_id: int
    nombre: str
    hora_inicio: time
    hora_fin: time
    descripcion: Optional[str] = None
    activo: bool = True
    orden: Optional[int] = None
    
    # Se genera automáticamente al instanciar
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: Optional[datetime] = None

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        """Asegura que el nombre no esté vacío o sea solo espacios."""
        if not (v or "").strip():
            raise ValueError("El nombre del turno es obligatorio.")
        return v.strip()

    @model_validator(mode='after')
    def validar_horario(self) -> Turno:
        """Valida que la hora de inicio sea anterior a la de fin."""
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser menor a la hora de fin.")
        return self

    # --- Comportamiento de dominio ---

    def cambiar_horario(self, nueva_inicio: time, nueva_fin: time) -> None:
        """
        Actualiza el horario del turno.
        Lanza ValueError si el rango es inválido.
        """
        if nueva_inicio >= nueva_fin:
            raise ValueError("La hora de inicio debe ser menor a la hora de fin.")
        
        self.hora_inicio = nueva_inicio
        self.hora_fin = nueva_fin
        self.actualizado_en = datetime.utcnow()

    def desactivar(self) -> None:
        """Desactiva el turno y actualiza la fecha de modificación."""
        if not self.activo:
            return
        self.activo = False
        self.actualizado_en = datetime.utcnow()

    def activar(self) -> None:
        """Activa el turno y actualiza la fecha de modificación."""
        if self.activo:
            return
        self.activo = True
        self.actualizado_en = datetime.utcnow()
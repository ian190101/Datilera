# app/kernel/domain/cursosextra/inscripcion_curso_extra_entidad.py

"""
Entidad de dominio: InscripcionCursoExtra
"""
from __future__ import annotations
from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TipoAlumnoCursoExtra(str, Enum):
    """Tipo de alumno inscrito."""
    INTERNO = "interno"  # Alumno regular del jardín
    EXTERNO = "externo"  # Alumno externo (no inscrito al centro)


class EstadoInscripcionCursoExtra(str, Enum):
    """Estado de la inscripción."""
    ACTIVO = "activo"
    COMPLETADO = "completado"
    RETIRADO = "retirado"


class InscripcionCursoExtra(BaseModel):
    """
    Entidad **InscripcionCursoExtra**.
    
    Gestiona la inscripción de alumnos (internos y externos) a cursos extra.
    
    Reglas:
    - Un alumno (interno o externo) puede inscribirse en múltiples cursos
    - Solo un tipo de alumno debe estar presente (interno XOR externo)
    - El estado controla el ciclo de vida de la inscripción
    """
    id: int
    curso_extra_id: int
    tipo_alumno: TipoAlumnoCursoExtra
    
    # Referencias (uno debe ser NULL, el otro NOT NULL)
    alumno_id: Optional[int] = None  # Alumno interno
    alumno_externo_id: Optional[int] = None  # Alumno externo
    
    # Datos de tutor (solo para externos, internos lo tienen en su tabla)
    tutor_nombre: Optional[str] = None
    tutor_celular: Optional[str] = None
    
    # Fechas y estado
    fecha_inscripcion: date = Field(default_factory=date.today)
    estado: EstadoInscripcionCursoExtra = EstadoInscripcionCursoExtra.ACTIVO
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )
    
    def model_post_init(self, __context) -> None:
        """Valida integridad: exactamente un tipo de alumno."""
        tiene_interno = self.alumno_id is not None
        tiene_externo = self.alumno_externo_id is not None
        
        if tiene_interno == tiene_externo:  # Ambos o ninguno
            raise ValueError(
                "Debe especificarse exactamente un tipo de alumno (interno XOR externo)."
            )
    
    # --- Comportamiento ---
    
    def es_alumno_interno(self) -> bool:
        """Verifica si es un alumno interno."""
        return self.tipo_alumno == TipoAlumnoCursoExtra.INTERNO
    
    def es_alumno_externo(self) -> bool:
        """Verifica si es un alumno externo."""
        return self.tipo_alumno == TipoAlumnoCursoExtra.EXTERNO
    
    def esta_activo(self) -> bool:
        """Verifica si la inscripción está activa."""
        return self.estado == EstadoInscripcionCursoExtra.ACTIVO
    
    def completar(self) -> None:
        """Marca la inscripción como completada."""
        if self.estado != EstadoInscripcionCursoExtra.ACTIVO:
            raise ValueError("Solo se puede completar una inscripción activa.")
        self.estado = EstadoInscripcionCursoExtra.COMPLETADO
    
    def retirar(self) -> None:
        """Marca al alumno como retirado."""
        if self.estado == EstadoInscripcionCursoExtra.RETIRADO:
            return
        self.estado = EstadoInscripcionCursoExtra.RETIRADO
    
    def reactivar(self) -> None:
        """Reactiva una inscripción retirada."""
        if self.estado == EstadoInscripcionCursoExtra.ACTIVO:
            return
        self.estado = EstadoInscripcionCursoExtra.ACTIVO

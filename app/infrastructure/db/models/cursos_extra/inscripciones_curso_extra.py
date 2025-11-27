from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, String, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
import enum


class TipoAlumnoCursoExtra(enum.Enum):
    """Tipo de alumno inscrito en curso extra"""
    INTERNO = "interno"  # Alumno regular del jardín
    EXTERNO = "externo"  # Alumno externo (no inscrito al centro)


class EstadoInscripcionCursoExtra(enum.Enum):
    """Estado de la inscripción del alumno"""
    ACTIVO = "activo"
    COMPLETADO = "completado"
    RETIRADO = "retirado"


class InscripcionCursoExtra(Base):
    """
    Modelo para gestionar inscripciones de alumnos (internos y externos) a cursos extra.
    Permite diferenciar entre niños del centro y externos, con datos de contacto del tutor.
    """
    __tablename__ = "inscripciones_curso_extra"

    # ============ Campos Primarios ============
    id = Column(Integer, primary_key=True, autoincrement=True)
    curso_extra_id = Column(
        Integer, 
        ForeignKey("cursos_extra.id", ondelete="RESTRICT"), 
        nullable=False, 
        index=True
    )
    
    # ============ Tipo de Alumno ============
    tipo_alumno = Column(
        SQLEnum(TipoAlumnoCursoExtra), 
        nullable=False, 
        default=TipoAlumnoCursoExtra.INTERNO,
        index=True,
        comment="Si es alumno interno del jardín o externo"
    )
    
    # ============ Referencias a Alumnos ============
    alumno_id = Column(
        Integer, 
        ForeignKey("alumnos.id", ondelete="RESTRICT"), 
        nullable=True,  # NULL si es externo
        index=True,
        comment="ID del alumno interno (NULL si es externo)"
    )
    alumno_externo_id = Column(
        Integer, 
        ForeignKey("alumnos_externos.id", ondelete="RESTRICT"), 
        nullable=True,  # NULL si es interno
        index=True,
        comment="ID del alumno externo (NULL si es interno)"
    )
    
    # ============ Datos del Tutor (solo para externos) ============
    tutor_nombre = Column(
        String(200), 
        nullable=True,
        comment="Nombre completo del tutor (solo para externos, internos lo tienen en su tabla)"
    )
    tutor_celular = Column(
        String(15), 
        nullable=True,
        comment="Celular del tutor (solo para externos)"
    )
    
    # ============ Fechas y Estado ============
    fecha_inscripcion = Column(Date, nullable=False, index=True, server_default=func.current_date())
    estado = Column(
        SQLEnum(EstadoInscripcionCursoExtra), 
        nullable=False, 
        default=EstadoInscripcionCursoExtra.ACTIVO,
        server_default="activo",
        index=True
    )
    
    # ============ Auditoría ============
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    inscrito_por_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    
    # ============ Relaciones ============
    curso = relationship("CursoExtra", back_populates="inscripciones")
    alumno = relationship("Alumno", foreign_keys=[alumno_id])
    alumno_externo = relationship("AlumnoExterno", foreign_keys=[alumno_externo_id])
    balance = relationship("BalanceCursoExtra", uselist=False, back_populates="inscripcion")
    inscrito_por = relationship("Usuario")

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Enum as SQLEnum, UniqueConstraint
from app.infrastructure.db.base import Base
import enum
from sqlalchemy.orm import relationship


class EstadoFormulario(enum.Enum):
    borrador = "borrador"
    enviado = "enviado"
    aprobado = "aprobado"
    rechazado = "rechazado"

class FormularioInscripcion(Base):
    __tablename__ = "formularios_inscripcion"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    gestion = Column(Integer, nullable=False, index=True)
    estado = Column(SQLEnum(EstadoFormulario), nullable=False, default=EstadoFormulario.borrador, server_default="borrador", index=True)
    observaciones = Column(Text, nullable=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    # Selección de turno y ciclo de revisión/aprobación
    turno_id = Column(Integer, ForeignKey("turnos.id", ondelete="RESTRICT"), nullable=True, index=True)  # <-- esto es nuevo
    revisado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True, index=True)  # <-- esto es nuevo
    revisado_en = Column(DateTime, nullable=True)  # <-- esto es nuevo
    aprobado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True, index=True)  # <-- esto es nuevo
    aprobado_en = Column(DateTime, nullable=True)  # <-- esto es nuevo


    alumno = relationship("Alumno", back_populates="formularios_inscripcion")
    sede = relationship("Sede", back_populates="formularios_inscripcion")
    turno = relationship("Turno", back_populates="formularios_inscripcion")
    revisado_por_usuario = relationship("Usuario", foreign_keys=[revisado_por], back_populates="formularios_revisados")
    aprobado_por_usuario = relationship("Usuario", foreign_keys=[aprobado_por], back_populates="formularios_aprobados")
    contratos = relationship("Contrato", back_populates="formulario", cascade="all, delete-orphan")
    firmas = relationship("Firma", back_populates="formulario", cascade="all, delete-orphan")
    documentos = relationship("DocumentoInscripcion", back_populates="formulario", cascade="all, delete-orphan")
    respuestas = relationship("FormularioRespuesta", back_populates="formulario", cascade="all, delete-orphan")
    

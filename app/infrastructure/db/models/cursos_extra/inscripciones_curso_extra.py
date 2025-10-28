from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
import enum

class EstadoInscripcionCursoExtra(enum.Enum):
    activo = "activo"
    completado = "completado"
    retirado = "retirado"

class InscripcionCursoExtra(Base):
    __tablename__ = "inscripciones_curso_extra"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=False, index=True)
    curso_extra_id = Column(Integer, ForeignKey("cursos_extra.id", ondelete="RESTRICT"), nullable=False, index=True)
    fecha_inscripcion = Column(Date, nullable=False, index=True)
    estado = Column(SQLEnum(EstadoInscripcionCursoExtra), nullable=False, default=EstadoInscripcionCursoExtra.activo, server_default="activo", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

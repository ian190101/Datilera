from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Enum as SQLEnum, Text, func
from app.infrastructure.db.base import Base
import enum

class EstadoAsistenciaAlumno(enum.Enum):
    presente = "presente"
    ausente = "ausente"
    tardanza = "tardanza"
    permiso = "permiso"

class AsistenciaAlumno(Base):
    __tablename__ = "asistencia_alumnos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"), nullable=False, index=True)
    paralelo_id = Column(Integer, ForeignKey("paralelos.id", ondelete="RESTRICT"), nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    estado = Column(SQLEnum(EstadoAsistenciaAlumno), nullable=False, default=EstadoAsistenciaAlumno.presente, server_default="presente", index=True)
    observaciones = Column(Text, nullable=True)
    registrado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)

    registrado_en = Column(DateTime, nullable=False, server_default=func.now())

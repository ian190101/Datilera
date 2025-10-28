from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Boolean, Enum as SQLEnum, func
from app.infrastructure.db.base import Base
import enum

class EstadoAsistenciaPersonal(enum.Enum):
    presente = "presente"
    ausente = "ausente"
    tardanza = "tardanza"
    permiso = "permiso"

class AsistenciaPersonal(Base):
    __tablename__ = "asistencia_personal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)

    fecha = Column(Date, nullable=False, index=True)
    estado = Column(SQLEnum(EstadoAsistenciaPersonal), nullable=False, default=EstadoAsistenciaPersonal.presente, server_default="presente", index=True)

    entrada_en = Column(DateTime, nullable=True, index=True)
    salida_en = Column(DateTime, nullable=True, index=True)
    justificado = Column(Boolean, nullable=False, default=False, server_default="0", index=True)

    registrado_en = Column(DateTime, nullable=False, server_default=func.now())

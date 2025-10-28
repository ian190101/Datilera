from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Boolean, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
import enum

class EstadoPermiso(enum.Enum):
    pendiente = "pendiente"
    aprobado = "aprobado"
    rechazado = "rechazado"

class PermisoPersonal(Base):
    __tablename__ = "permisos_personal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)

    tipo = Column(String(80), nullable=False, index=True)  # p.ej. "enfermedad", "trámite", "vacación"
    motivo = Column(Text, nullable=True)

    fecha_inicio = Column(Date, nullable=False, index=True)
    fecha_fin = Column(Date, nullable=False, index=True)
    estado = Column(SQLEnum(EstadoPermiso), nullable=False, default=EstadoPermiso.pendiente, server_default="pendiente", index=True)

    aprobado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    aprobado_en = Column(DateTime, nullable=True, index=True)

    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

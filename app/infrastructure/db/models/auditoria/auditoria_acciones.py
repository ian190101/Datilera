from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, func
from app.infrastructure.db.base import Base

class AuditoriaAccion(Base):
    __tablename__ = "auditoria_acciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)

    entidad = Column(String(120), nullable=False, index=True)     # p.ej. "pagos", "alumnos", "items"
    entidad_id = Column(String(64), nullable=True, index=True)    # id de la fila afectada (string por flexibilidad)
    accion = Column(String(30), nullable=False, index=True)       # "create", "update", "delete", "login", etc.

    datos_antes = Column(JSON, nullable=True)                     # snapshot previo
    datos_despues = Column(JSON, nullable=True)                   # snapshot posterior

    ip = Column(String(50), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    sesion_id = Column(Integer, ForeignKey("sesiones.id", ondelete="SET NULL"), nullable=True, index=True)

    creado_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)

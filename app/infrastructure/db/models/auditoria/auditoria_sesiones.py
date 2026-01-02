# app/infrastructure/db/models/auditoria/auditoria_sesiones.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, func, Index
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship


class AuditoriaSesion(Base):
    """
    Tracking de sesiones activas para:
    - Ver quiénes están conectados (HU: servicio técnico)
    - Forzar logout de sesiones (HU)
    - Detectar sesiones duplicadas/sospechosas
    """
    __tablename__ = "auditoria_sesiones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sesion_id = Column(Integer, ForeignKey("sesiones.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Datos de conexión
    ip = Column(String(50), nullable=True, index=True)
    user_agent = Column(String(500), nullable=True)
    dispositivo_tipo = Column(String(20), nullable=True)  # "web", "mobile"
    
    # Timestamps
    inicio_sesion = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    ultimo_heartbeat = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), index=True)
    fin_sesion = Column(DateTime, nullable=True, index=True)
    
    # Estado
    activa = Column(Boolean, nullable=False, default=True, index=True)
    
    # Razón de cierre
    razon_cierre = Column(String(50), nullable=True)
    # Valores: "logout_manual", "timeout", "forzado_admin", "token_expirado"

    __table_args__ = (
        Index('idx_sesion_usuario_activa', 'usuario_id', 'activa'),
        Index('idx_sesion_sede_activa', 'sede_id', 'activa'),
    )


    usuario = relationship("Usuario", back_populates="auditoria_sesiones")
    sede = relationship("Sede", back_populates="auditoria_sesiones")
    #sesion = relationship("Sesion", back_populates="auditoria_sesion", uselist=False)
    #acciones = relationship("AuditoriaAccion", back_populates="sesion", lazy="select")
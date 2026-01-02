from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class Sesion(Base):
    __tablename__ = "sesiones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    expira_en = Column(DateTime, nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    #auditoria_sesion = relationship("AuditoriaSesion", back_populates="sesion", uselist=False)
    usuario = relationship("Usuario", back_populates="sesiones")

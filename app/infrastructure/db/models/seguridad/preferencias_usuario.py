from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from app.infrastructure.db.base import Base

class PreferenciaUsuario(Base):
    __tablename__ = "preferencias_usuario"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    tema = Column(String(20), nullable=False, default="claro", server_default="claro")
    notificaciones_push = Column(Boolean, nullable=False, default=True, server_default="1")
    notificaciones_email = Column(Boolean, nullable=False, default=False, server_default="0")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

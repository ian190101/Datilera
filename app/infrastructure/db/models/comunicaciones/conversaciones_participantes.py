# conversaciones_participantes.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, func
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class ConversacionParticipante(Base):
    __tablename__ = "conversaciones_participantes"
    __table_args__ = (
        UniqueConstraint("conversacion_id", "usuario_id", name="uq_conversacion_usuario"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversacion_id = Column(Integer, ForeignKey("conversaciones.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    rol = Column(String(30), nullable=False, index=True)  # 'profesora', 'tutor', 'directora'
    archivado = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    unido_en = Column(DateTime, nullable=False, server_default=func.now())

    conversacion = relationship("Conversacion", back_populates="participantes")
    usuario = relationship("Usuario", back_populates="conversaciones_participa") 

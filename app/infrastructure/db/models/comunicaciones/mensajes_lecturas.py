# mensajes_lecturas.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class MensajeLeido(Base):
    __tablename__ = "mensajes_lecturas"
    __table_args__ = (
        UniqueConstraint("mensaje_id", "usuario_id", name="uq_mensaje_usuario_lectura"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mensaje_id = Column(Integer, ForeignKey("mensajes.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    leido_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    mensaje = relationship("Mensaje", back_populates="lecturas")
    usuario = relationship("Usuario", back_populates="lecturas_mensajes")

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum, func
from app.infrastructure.db.base import Base
import enum
from sqlalchemy.orm import relationship

class TipoMensaje(enum.Enum):
    texto = "texto"
    sistema = "sistema"

class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversacion_id = Column(Integer, ForeignKey("conversaciones.id", ondelete="CASCADE"), nullable=False, index=True)
    remitente_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    tipo = Column(SQLEnum(TipoMensaje), nullable=False, default=TipoMensaje.texto, server_default="texto", index=True)
    contenido = Column(Text, nullable=False)
    reply_a_id = Column(Integer, ForeignKey("mensajes.id", ondelete="SET NULL"), nullable=True, index=True)
    enviado_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)


    conversacion = relationship("Conversacion", back_populates="mensajes")
    remitente = relationship("Usuario", back_populates="mensajes_enviados", foreign_keys="[Mensaje.remitente_id]")
    respuesta_a = relationship("Mensaje", remote_side="[Mensaje.id]", backref="respuestas")
    adjuntos = relationship("MensajeAdjunto", back_populates="mensaje", cascade="all, delete-orphan", lazy="select")
    lecturas = relationship("MensajeLeido", back_populates="mensaje", cascade="all, delete-orphan", lazy="select")
    notificaciones = relationship("Notificacion", back_populates="mensaje_relacionado", foreign_keys="[Notificacion.relacionado_mensaje_id]")
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum, func
from app.infrastructure.db.base import Base
import enum

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

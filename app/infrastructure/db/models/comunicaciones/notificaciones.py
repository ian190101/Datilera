from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, func
from app.infrastructure.db.base import Base
import enum

class CanalNotificacion(enum.Enum):
    app = "app"
    email = "email"
    sms = "sms"

class EstadoNotificacion(enum.Enum):
    pendiente = "pendiente"
    enviada = "enviada"
    fallida = "fallida"

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    destinatario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    titulo = Column(String(140), nullable=False)
    cuerpo = Column(Text, nullable=True)
    canal = Column(SQLEnum(CanalNotificacion), nullable=False, default=CanalNotificacion.app, server_default="app", index=True)
    estado = Column(SQLEnum(EstadoNotificacion), nullable=False, default=EstadoNotificacion.pendiente, server_default="pendiente", index=True)
    relacionado_mensaje_id = Column(Integer, ForeignKey("mensajes.id", ondelete="SET NULL"), nullable=True, index=True)
    enviado = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    enviado_en = Column(DateTime, nullable=True, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

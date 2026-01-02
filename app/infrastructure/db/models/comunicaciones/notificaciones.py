from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, JSON, func
from app.infrastructure.db.base import Base
import enum
from sqlalchemy.orm import relationship

class CanalNotificacion(enum.Enum):
    app = "app"
    email = "email"
    sms = "sms"

class EstadoNotificacion(enum.Enum):
    pendiente = "pendiente"
    enviada = "enviada"
    fallida = "fallida"

class PrioridadNotificacion(enum.Enum):  # ← AÑADIR
    baja = "baja"
    media = "media"
    alta = "alta"

class Notificacion(Base):
    __tablename__ = "notificaciones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)  # ← Renombrar de destinatario_id
    
    titulo = Column(String(120), nullable=False)  # ← Reducir de 140 a 120 (según entidad dominio)
    cuerpo = Column(Text, nullable=False)  # ← Cambiar a NOT NULL (según entidad dominio)
    tipo = Column(String(50), nullable=False, index=True)  # ← AÑADIR (ej: 'pago_vencimiento', 'nuevo_mensaje', 'alerta_stock')
    
    # AÑADIR campos relacionados genéricos:
    relacionado_tipo = Column(String(50), nullable=True, index=True)  # ← 'pago', 'mensaje', 'actividad', etc.
    relacionado_id = Column(Integer, nullable=True, index=True)  # ← ID del recurso relacionado
    relacionado_mensaje_id = Column(Integer, ForeignKey("mensajes.id", ondelete="SET NULL"), nullable=True, index=True)  # ← Mantener por compatibilidad
    
    canal = Column(SQLEnum(CanalNotificacion), nullable=False, default=CanalNotificacion.app, server_default="app", index=True)
    estado = Column(SQLEnum(EstadoNotificacion), nullable=False, default=EstadoNotificacion.pendiente, server_default="pendiente", index=True)
    prioridad = Column(SQLEnum(PrioridadNotificacion), nullable=False, default=PrioridadNotificacion.media, server_default="media", index=True)  # ← AÑADIR
    
    programada_para = Column(DateTime, nullable=True, index=True)  # ← AÑADIR
    enviado = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    enviado_en = Column(DateTime, nullable=True, index=True)
    leido_en = Column(DateTime, nullable=True, index=True)  # ← AÑADIR
    
    metadatos = Column(JSON, nullable=True)  # ← AÑADIR
    
    creado_en = Column(DateTime, nullable=False, server_default=func.now())


    usuario = relationship("Usuario", back_populates="notificaciones")
    mensaje_relacionado = relationship("Mensaje", back_populates="notificaciones", foreign_keys="[Notificacion.relacionado_mensaje_id]")
    #vistas = relationship("NotificacionVista", back_populates="notificacion", cascade="all, delete-orphan", lazy="select")
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, func
from app.infrastructure.db.base import Base
import enum

class TipoAdjunto(enum.Enum):
    imagen = "imagen"
    video = "video"
    audio = "audio"
    documento = "documento"

class MensajeAdjunto(Base):
    __tablename__ = "mensajes_adjuntos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mensaje_id = Column(Integer, ForeignKey("mensajes.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(SQLEnum(TipoAdjunto), nullable=False, index=True)
    url = Column(String(255), nullable=False)
    nombre_archivo = Column(String(160), nullable=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

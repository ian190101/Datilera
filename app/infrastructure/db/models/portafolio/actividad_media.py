from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
import enum

class TipoMedia(enum.Enum):
    imagen = "imagen"
    video = "video"
    audio = "audio"
    documento = "documento"

class ActividadMedia(Base):
    __tablename__ = "actividad_media"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    actividad_id = Column(Integer, ForeignKey("actividades.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(SQLEnum(TipoMedia), nullable=False)
    url = Column(String(255), nullable=False)
    titulo = Column(String(120), nullable=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

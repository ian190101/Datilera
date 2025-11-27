from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
import enum

class TipoMedia(str, enum.Enum):
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
    url_marcada = Column(String(255), nullable=True,)
    estado = Column(String(20), nullable=False, server_default="pendiente", index=True)
    titulo = Column(String(120), nullable=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    fecha_descarga = Column(DateTime, nullable=True, index=True,)  # <-- se rellena al descargar
    fecha_eliminacion_programada = Column(DateTime, nullable=True, index=True,)
    nombre_archivo = Column(String(120), nullable=False)  # OK
    mime = Column(String(80), nullable=True,)  # OK
    tamano_bytes = Column(Integer, nullable=True,)  # OK
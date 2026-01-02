from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Enum as SQLEnum, Text
from app.infrastructure.db.base import Base
import enum
from sqlalchemy.orm import relationship

class TipoMedia(str, enum.Enum):
    imagen = "imagen"
    video = "video"
    audio = "audio"
    documento = "documento"

class EstadoProcesamientoWatermark(str, enum.Enum):
    pendiente = "pendiente"
    procesando = "procesando"
    completado = "completado"
    error = "error"
    no_aplica = "no_aplica"

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
    # Campos de control de procesamiento de marca de agua
    estado_procesamiento = Column(SQLEnum(EstadoProcesamientoWatermark), nullable=False, server_default="pendiente",index=True)
    cola_id = Column(String(100), nullable=True, index=True)
    intentos_procesamiento = Column(Integer, nullable=False, server_default="0")
    error_procesamiento = Column(Text, nullable=True)
    procesado_en = Column(DateTime, nullable=True)

    actividad = relationship("Actividad", back_populates="media")




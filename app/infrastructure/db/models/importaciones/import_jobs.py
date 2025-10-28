from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
import enum

class EstadoImportacion(enum.Enum):
    pendiente = "pendiente"
    procesando = "procesando"
    completado = "completado"
    error = "error"

class ImportJob(Base):
    __tablename__ = "import_jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    nombre_archivo = Column(String(200), nullable=False)
    tipo_importacion = Column(String(80), nullable=False, index=True)
    archivo_url = Column(String(255), nullable=False)
    estado = Column(SQLEnum(EstadoImportacion), nullable=False, default=EstadoImportacion.pendiente, server_default="pendiente", index=True)
    registros_procesados = Column(Integer, nullable=False, default=0)
    registros_fallidos = Column(Integer, nullable=False, default=0)
    log_errores = Column(Text, nullable=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    completado_en = Column(DateTime, nullable=True)

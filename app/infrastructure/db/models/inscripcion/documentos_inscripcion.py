from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, SmallInteger, Text 
from app.infrastructure.db.base import Base

class DocumentoInscripcion(Base):
    __tablename__ = "documentos_inscripcion"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formulario_id = Column(Integer, ForeignKey("formularios_inscripcion.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_documento = Column(String(80), nullable=False, index=True)
    url = Column(String(255), nullable=False)
    nombre_archivo = Column(String(120), nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    mime = Column(String(50), nullable=True)  # <-- esto es nuevo
    hash_archivo = Column(String(64), nullable=True, index=True)  # <-- esto es nuevo
    tamano_bytes = Column(Integer, nullable=True)  # <-- esto es nuevo

    # Estados: pendiente | procesando | marcado | error
    estado_procesamiento = Column(String(20), nullable=False, server_default="pendiente", index=True)  # <-- esto es nuevo
    procesado_en = Column(DateTime, nullable=True)  # <-- esto es nuevo
    intentos = Column(SmallInteger, nullable=False, server_default="0")  # <-- esto es nuevo
    error_ultima = Column(Text, nullable=True)  # <-- esto es nuevo

    watermark_url = Column(String(255), nullable=True)  # <-- esto es nuevo
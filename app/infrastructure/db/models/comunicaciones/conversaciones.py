from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, func
from app.infrastructure.db.base import Base
import enum

class TipoConversacion(enum.Enum):
    directo = "directo"       # 1 a 1
    grupo = "grupo"           # múltiples participantes
    sistema = "sistema"       # mensajes automáticos

class Conversacion(Base):
    __tablename__ = "conversaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    creado_por_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    titulo = Column(String(150), nullable=True, index=True)
    descripcion = Column(Text, nullable=True)
    tipo = Column(SQLEnum(TipoConversacion), nullable=False, default=TipoConversacion.directo, server_default="directo", index=True)
    cerrado = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

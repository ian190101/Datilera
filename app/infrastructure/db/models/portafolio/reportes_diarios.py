from sqlalchemy import Column, Integer, Text, Date, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base

class ReporteDiario(Base):
    __tablename__ = "reportes_diarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    paralelo_id = Column(Integer, ForeignKey("paralelos.id", ondelete="RESTRICT"), nullable=False, index=True)
    profesora_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    contenido = Column(Text, nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

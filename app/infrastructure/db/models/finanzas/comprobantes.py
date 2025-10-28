from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base

class Comprobante(Base):
    __tablename__ = "comprobantes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pago_id = Column(Integer, ForeignKey("pagos.id", ondelete="RESTRICT"), nullable=False, index=True)
    url = Column(String(255), nullable=False)
    nombre_archivo = Column(String(120), nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean, func
from app.infrastructure.db.base import Base

class AlertaStock(Base):
    __tablename__ = "alertas_stock"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="CASCADE"), nullable=False, index=True)
    mensaje = Column(Text, nullable=False)
    resuelta = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    resuelta_en = Column(DateTime, nullable=True)

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, func
from app.infrastructure.db.base import Base

class AlertaVencimiento(Base):
    __tablename__ = "alertas_vencimiento"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="CASCADE"), nullable=False, index=True)
    lote = Column(String(50), nullable=True)
    fecha_vencimiento = Column(Date, nullable=False, index=True)
    notificada = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

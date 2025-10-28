from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func, UniqueConstraint
from app.infrastructure.db.base import Base

class StockSede(Base):
    __tablename__ = "stock_sede"
    __table_args__ = (
        UniqueConstraint("item_id", "sede_id", name="uq_item_sede"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    cantidad_disponible = Column(Numeric(10, 2), nullable=False, default=0)
    stock_minimo = Column(Numeric(10, 2), nullable=False, default=0)
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

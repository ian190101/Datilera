from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class ItemAtributo(Base):
    __tablename__ = "items_atributos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre_atributo = Column(String(60), nullable=False)
    valor_atributo = Column(String(120), nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    item = relationship("Item", back_populates="atributos")

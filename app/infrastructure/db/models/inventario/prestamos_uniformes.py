from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Boolean, func
from app.infrastructure.db.base import Base

class PrestamoUniforme(Base):
    __tablename__ = "prestamos_uniformes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True)
    fecha_prestamo = Column(Date, nullable=False, index=True)
    fecha_devolucion = Column(Date, nullable=True, index=True)
    devuelto = Column(Boolean, nullable=False, default=False, server_default="0")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

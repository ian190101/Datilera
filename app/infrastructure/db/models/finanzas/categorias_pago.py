# app/infrastructure/db/models/finanzas/categorias_pago.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, ForeignKey, func
from app.infrastructure.db.base import Base


class CategoriaPago(Base):
    __tablename__ = "categorias_pago"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    monto_base = Column(Numeric(10, 2), nullable=True, comment="Monto sugerido por defecto")
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

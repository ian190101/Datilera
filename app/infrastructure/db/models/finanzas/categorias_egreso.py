# app/infrastructure/db/models/finanzas/categorias_egreso.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base


class CategoriaEgreso(Base):
    __tablename__ = "categorias_egreso"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base

class Pago(Base):
    __tablename__ = "pagos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=False, index=True)
    categoria_pago_id = Column(Integer, ForeignKey("categorias_pago.id", ondelete="RESTRICT"), nullable=False, index=True)
    monto_pagado = Column(Numeric(10, 2), nullable=False)
    fecha_pago = Column(Date, nullable=False, index=True)
    metodo_pago = Column(String(50), nullable=False, index=True)
    numero_comprobante = Column(String(80), nullable=True, index=True)
    registrado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

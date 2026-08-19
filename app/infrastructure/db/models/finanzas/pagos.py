from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, func, Boolean, Text
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

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
    anulado = Column(Boolean, nullable=False, default=False, server_default="0")
    anulado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True)
    anulado_en = Column(DateTime, nullable=True)
    motivo_anulacion = Column(Text, nullable=True)


    cuotas = relationship("CuotaPlanPago", back_populates="pago")
    asignaciones_cuotas = relationship("PagoCuota", back_populates="pago")
    alumno = relationship("Alumno", back_populates="pagos")
    categoria = relationship("CategoriaPago", back_populates="pagos", foreign_keys=[categoria_pago_id])
    usuario_registro = relationship("Usuario", back_populates="pagos_registrados", foreign_keys="[Pago.registrado_por]")
    #libro_caja_items = relationship("LibroCaja", back_populates="pago", uselist=False, cascade="all, delete-orphan")

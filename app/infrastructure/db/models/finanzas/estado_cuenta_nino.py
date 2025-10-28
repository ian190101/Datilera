from sqlalchemy import Column, Integer, Numeric, Date, DateTime, ForeignKey, String, func
from app.infrastructure.db.base import Base

class EstadoCuentaNino(Base):
    __tablename__ = "estado_cuenta_nino"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=False, index=True)
    mes = Column(Integer, nullable=False, index=True)
    anio = Column(Integer, nullable=False, index=True)
    saldo_anterior = Column(Numeric(10, 2), nullable=False, default=0)
    total_cargos = Column(Numeric(10, 2), nullable=False, default=0)
    total_pagos = Column(Numeric(10, 2), nullable=False, default=0)
    saldo_actual = Column(Numeric(10, 2), nullable=False, default=0)
    pdf_url = Column(String(255), nullable=True)
    generado_en = Column(DateTime, nullable=False, server_default=func.now())

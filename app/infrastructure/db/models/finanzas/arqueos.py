from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base

class Arqueo(Base):
    __tablename__ = "arqueos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    mes = Column(Integer, nullable=False, index=True)
    anio = Column(Integer, nullable=False, index=True)
    saldo_inicial = Column(Numeric(10, 2), nullable=False)
    total_ingresos = Column(Numeric(10, 2), nullable=False)
    total_egresos = Column(Numeric(10, 2), nullable=False)
    saldo_final = Column(Numeric(10, 2), nullable=False)
    observaciones = Column(Text, nullable=True)
    pdf_url = Column(String(255), nullable=True)
    elaborado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

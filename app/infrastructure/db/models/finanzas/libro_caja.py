from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
import enum

class TipoMovimiento(enum.Enum):
    ingreso = "ingreso"
    egreso = "egreso"

class LibroCaja(Base):
    __tablename__ = "libro_caja"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    tipo = Column(SQLEnum(TipoMovimiento), nullable=False, index=True)
    monto = Column(Numeric(10, 2), nullable=False)
    concepto = Column(String(200), nullable=False)
    referencia = Column(String(100), nullable=True)
    fecha = Column(Date, nullable=False, index=True)
    registrado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

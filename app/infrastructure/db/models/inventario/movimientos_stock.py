from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
import enum

class TipoMovimiento(enum.Enum):
    entrada = "entrada"
    salida = "salida"
    transferencia = "transferencia"
    ajuste = "ajuste"

class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="RESTRICT"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    tipo = Column(SQLEnum(TipoMovimiento), nullable=False, index=True)
    cantidad = Column(Numeric(10, 2), nullable=False)
    motivo = Column(String(200), nullable=True)
    referencia = Column(String(100), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    fecha_movimiento = Column(Date, nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

# app/infrastructure/db/models/finanzas/libro_caja.py
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey, Enum, func, Index
from app.infrastructure.db.base import Base
import enum
from sqlalchemy.orm import relationship


class TipoMovimientoEnum(str, enum.Enum):
    INGRESO = "ingreso"
    EGRESO = "egreso"


class LibroCaja(Base):
    """
    Registro consolidado de movimientos de caja (ingresos y egresos) por sede.
    Usado para arqueos mensuales y reportes financieros.
    """
    __tablename__ = "libro_caja"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    tipo = Column(Enum(TipoMovimientoEnum), nullable=False, index=True)
    
    # FKs a categorías (solo una activa según tipo)
    categoria_pago_id = Column(
        Integer, 
        ForeignKey("categorias_pago.id", ondelete="RESTRICT"), 
        nullable=True, 
        index=True,
        comment="Si tipo=INGRESO"
    )
    categoria_egreso_id = Column(
        Integer, 
        ForeignKey("categorias_egreso.id", ondelete="RESTRICT"), 
        nullable=True, 
        index=True,
        comment="Si tipo=EGRESO"
    )
    
    # FK opcional a pago (si el ingreso viene de tabla pagos)
    pago_id = Column(
        Integer, 
        ForeignKey("pagos.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True,
        comment="Referencia a pago si aplica"
    )

    egreso_id = Column(
        Integer, 
        ForeignKey("egresos.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True,
        comment="Referencia a egreso si aplica"
    )
    
    monto = Column(Numeric(10, 2), nullable=False)
    saldo_acumulado = Column(
        Numeric(12, 2), 
        nullable=True,
        comment="Saldo calculado al momento del registro"
    )
    
    # Concepto libre (opcional si ya hay categoría)
    concepto = Column(String(200), nullable=True, comment="Descripción adicional")
    referencia = Column(String(100), nullable=True, comment="Código de referencia externo")
    observaciones = Column(Text, nullable=True, comment="Notas adicionales para auditoría")
    
    usuario_registro_id = Column(
        Integer, 
        ForeignKey("usuarios.id", ondelete="RESTRICT"), 
        nullable=False,
        comment="Quién registró el movimiento"
    )
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    # Índice compuesto para consultas por sede y fecha
    __table_args__ = (
        Index('ix_libro_caja_sede_fecha', 'sede_id', 'fecha'),
        Index('ix_libro_caja_sede_tipo', 'sede_id', 'tipo'),
    )


    sede = relationship("Sede", back_populates="movimientos_caja")
    categoria_pago = relationship("CategoriaPago", back_populates="movimientos_ingreso")
    #categoria_egreso = relationship("CategoriaEgreso", back_populates="movimientos_egreso")
    usuario_registro = relationship("Usuario", back_populates="movimientos_caja_registrados")
    egreso = relationship("Egreso", back_populates="libro_caja_item", uselist=False)
    #pagos = relationship("Pago", back_populates="libro_caja_item", uselist=False)
    
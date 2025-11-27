from sqlalchemy import Column, Integer, Numeric, Date, DateTime, String, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
import enum


class MetodoPagoCursoExtra(enum.Enum):
    """Método de pago utilizado"""
    EFECTIVO = "efectivo"
    QR = "qr"
    TRANSFERENCIA = "transferencia"


class PagoCursoExtra(Base):
    """
    Modelo para registrar pagos recibidos por inscripciones a cursos extra.
    Cada pago se asocia a un balance y actualiza el saldo pendiente.
    """
    __tablename__ = "pagos_curso_extra"

    # ============ Campos Primarios ============
    id = Column(Integer, primary_key=True, autoincrement=True)
    balance_curso_extra_id = Column(
        Integer, 
        ForeignKey("balance_curso_extra.id", ondelete="RESTRICT"), 
        nullable=False, 
        index=True
    )
    
    # ============ Información del Pago ============
    monto = Column(Numeric(10, 2), nullable=False, comment="Monto del pago")
    fecha_pago = Column(Date, nullable=False, index=True, server_default=func.current_date())
    metodo_pago = Column(
        SQLEnum(MetodoPagoCursoExtra), 
        nullable=False, 
        default=MetodoPagoCursoExtra.EFECTIVO
    )
    
    # ============ Comprobante (futuro módulo) ============
    comprobante_url = Column(String(500), nullable=True, comment="URL del comprobante (imagen/PDF)")
    numero_transaccion = Column(String(100), nullable=True, comment="Número de transacción (QR/transferencia)")
    
    # ============ Observaciones ============
    observaciones = Column(String(500), nullable=True, comment="Notas adicionales sobre el pago")
    
    # ============ Auditoría ============
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    
    # ============ Relaciones ============
    balance = relationship("BalanceCursoExtra", back_populates="pagos")
    registrado_por = relationship("Usuario")

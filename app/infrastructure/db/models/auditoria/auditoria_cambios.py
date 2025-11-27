# app/infrastructure/db/models/auditoria/auditoria_cambios.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, func, Index
from app.infrastructure.db.base import Base


class AuditoriaCambio(Base):
    """
    Historial de cambios campo por campo (HU: historial de cambios para todo).
    
    Permite rastrear:
    - Qué campo cambió
    - Valor anterior vs nuevo
    - Quién lo cambió y cuándo
    """
    __tablename__ = "auditoria_cambios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con auditoría de acción
    auditoria_accion_id = Column(Integer, ForeignKey("auditoria_acciones.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Datos del cambio
    campo = Column(String(100), nullable=False, index=True)
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)
    tipo_dato = Column(String(50), nullable=True)  # "string", "number", "boolean", "date", "json"
    
    # Metadata
    creado_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    __table_args__ = (
        Index('idx_cambio_accion_campo', 'auditoria_accion_id', 'campo'),
    )

from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class CostoCursoExtra(Base):
    """
    Modelo para registrar costos/gastos reales incurridos en un curso extra.
    Cada costo pertenece a una categoría definida previamente.
    """
    __tablename__ = "costos_curso_extra"

    # ============ Campos Primarios ============
    id = Column(Integer, primary_key=True, autoincrement=True)
    curso_extra_id = Column(
        Integer, 
        ForeignKey("cursos_extra.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    categoria_costo_id = Column(
        Integer, 
        ForeignKey("categorias_costo_curso_extra.id", ondelete="RESTRICT"), 
        nullable=False,
        index=True,
        comment="Referencia a la categoría de costo (materiales, instructor, etc.)"
    )
    
    # ============ Información del Costo ============
    descripcion = Column(Text, nullable=True, comment="Descripción detallada del gasto")
    monto = Column(Numeric(10, 2), nullable=False, comment="Monto del gasto")
    fecha_gasto = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    
    # ============ Comprobante (opcional - futuro módulo) ============
    comprobante_url = Column(String(500), nullable=True, comment="URL del comprobante (imagen/PDF)")
    
    # ============ Auditoría ============
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    
    # ============ Relaciones ============
    curso = relationship("CursoExtra", back_populates="costos")
    categoria = relationship("CategoriaCostoCursoExtra", back_populates="costos")
    registrado_por = relationship("Usuario")

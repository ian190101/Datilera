from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class CategoriaCostoCursoExtra(Base):
    """
    Modelo para categorías dinámicas de costos/gastos de cursos extra.
    Permite a la directora definir categorías personalizadas por curso/sede
    (ej. Materiales, Instructor, Publicidad, Transporte, etc.).
    """
    __tablename__ = "categorias_costo_curso_extra"

    # ============ Campos Primarios ============
    id = Column(Integer, primary_key=True, autoincrement=True)
    curso_extra_id = Column(
        Integer, 
        ForeignKey("cursos_extra.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True,
        comment="Curso al que pertenece esta categoría"
    )
    
    # ============ Información de la Categoría ============
    nombre = Column(String(100), nullable=False, index=True, comment="Nombre de la categoría (ej. Materiales)")
    descripcion = Column(Text, nullable=True, comment="Descripción opcional de la categoría")
    
    # ============ Estado ============
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    
    # ============ Auditoría ============
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    creado_por_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    
    # ============ Relaciones ============
    curso = relationship("CursoExtra", back_populates="categorias_costo")
    costos = relationship("CostoCursoExtra", back_populates="categoria")
    creado_por = relationship("Usuario")

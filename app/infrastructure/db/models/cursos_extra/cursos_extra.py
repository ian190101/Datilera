from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, Numeric, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class CursoExtra(Base):
    """
    Modelo para gestionar cursos extra por sede con precios diferenciados,
    límite de cupos, fechas y porcentaje de ganancia institucional.
    """
    __tablename__ = "cursos_extra"

    # ============ Campos Primarios ============
    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # ============ Información del Curso ============
    nombre = Column(String(120), nullable=False, index=True, comment="Nombre del curso (ej. Natación, Robótica)")
    descripcion = Column(Text, nullable=True, comment="Descripción detallada del curso")
    instructor = Column(String(120), nullable=False, comment="Nombre del instructor/profesor")
    gestion = Column(Integer, nullable=False, index=True, comment="Año/Gestión del curso (ej. 2025)")
    
    # ============ Fechas y Duración ============
    fecha_inicio = Column(Date, nullable=False, index=True, comment="Fecha de inicio del curso")
    fecha_fin = Column(Date, nullable=True, index=True, comment="Fecha de fin del curso (opcional/editable)")
    
    # ============ Cupos y Control ============
    cupo_maximo = Column(Integer, nullable=False, default=20, comment="Límite de cupos para inscripciones")
    inscritos_actuales = Column(Integer, nullable=False, default=0, comment="Contador en tiempo real de inscritos activos")
    
    # ============ Precios Diferenciados ============
    precio_interno = Column(
        Numeric(10, 2), 
        nullable=False, 
        comment="Precio para alumnos regulares del jardín"
    )
    precio_externo = Column(
        Numeric(10, 2), 
        nullable=False, 
        comment="Precio para alumnos externos (no inscritos al centro)"
    )
    
    # ============ Reparto de Ganancias ============
    porcentaje_institucion = Column(
        Numeric(5, 2), 
        nullable=False, 
        default=50.00,
        comment="Porcentaje de ganancia para la institución (0-100). El resto va al instructor."
    )
    
    # ============ Estado y Auditoría ============
    activo = Column(Boolean, nullable=False, default=True, server_default="1", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    creado_por_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    
    # ============ Relaciones ============
    sede = relationship("Sede", back_populates="cursos_extra")
    inscripciones = relationship("InscripcionCursoExtra", back_populates="curso", cascade="all, delete-orphan")
    costos = relationship("CostoCursoExtra", back_populates="curso", cascade="all, delete-orphan")
    categorias_costo = relationship("CategoriaCostoCursoExtra", back_populates="curso", cascade="all, delete-orphan")
    creado_por = relationship("Usuario")

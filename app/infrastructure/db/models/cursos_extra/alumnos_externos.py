from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class AlumnoExterno(Base):
    """
    Modelo para alumnos externos (no inscritos al centro) que solo participan en cursos extra.
    Almacena datos básicos del niño y su tutor para gestionar inscripciones.
    """
    __tablename__ = "alumnos_externos"

    # ============ Campos Primarios ============
    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(
        Integer, 
        ForeignKey("sedes.id", ondelete="RESTRICT"), 
        nullable=False, 
        index=True,
        comment="Sede donde se gestiona el alumno externo"
    )
    
    # ============ Datos del Alumno ============
    nombre_completo = Column(String(200), nullable=False, index=True, comment="Nombre completo del niño")
    fecha_nacimiento = Column(Date, nullable=True, comment="Fecha de nacimiento (para calcular edad)")
    edad_anios = Column(Integer, nullable=True, comment="Edad en años (calculada o ingresada)")
    
    # ============ Datos del Tutor Responsable ============
    tutor_nombre = Column(String(200), nullable=False, comment="Nombre del padre/madre/tutor responsable")
    tutor_celular = Column(String(15), nullable=False, index=True, comment="Celular del tutor (contacto principal)")
    tutor_email = Column(String(150), nullable=True, comment="Email del tutor (opcional)")
    
    # ============ Auditoría ============
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    
    # ============ Relaciones ============
    sede = relationship("Sede", back_populates="alumnos_externos")
    inscripciones = relationship("InscripcionCursoExtra", back_populates="alumno_externo")
    registrado_por = relationship("Usuario")

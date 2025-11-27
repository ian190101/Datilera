# app/infrastructure/db/models/alumnos/alumnos.py

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, DECIMAL, DateTime, Time  # NUEVO: DateTime, Time
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime


class Alumno(Base):
    __tablename__ = "alumnos"

    # ==================== CAMPOS EXISTENTES ====================
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=False)
    apellido_materno = Column(String(100))
    fecha_nacimiento = Column(Date, nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    
    # ==================== CAMPOS NUEVOS ====================
    
    # Identificación única
    codigo_unico = Column(String(6), unique=True, nullable=False, index=True)  # NUEVO: 6 caracteres alfanuméricos para registro tutores
    
    # Datos personales adicionales
    nombres_completos = Column(String(200))  # NUEVO: nombres completos (puede diferir de "nombre")
    lugar_nacimiento = Column(String(150))  # NUEVO
    genero = Column(String(1))  # NUEVO: M/F
    foto_url = Column(String(500))  # NUEVO
    
    # Datos de nacimiento (formulario inscripción)
    peso_nacer = Column(DECIMAL(5, 2))  # NUEVO: kg
    talla_nacer = Column(DECIMAL(5, 2))  # NUEVO: cm
    parto_normal = Column(Boolean, default=True)  # NUEVO
    parto_complicaciones = Column(Text)  # NUEVO
    embarazo_normal = Column(Boolean, default=True)  # NUEVO
    embarazo_complicaciones = Column(Text)  # NUEVO
    
    # Salud (formulario)
    tiene_alergias = Column(Boolean, default=False)  # NUEVO
    alergias_detalle = Column(Text)  # NUEVO
    medicacion_actual = Column(Text)  # NUEVO
    tratamiento_actual = Column(Text)  # NUEVO
    enfermedades_previas = Column(Text)  # NUEVO: JSON con [{enfermedad, edad}]
    problemas_salud = Column(Text)  # NUEVO: JSON: {auditivo, visual, respiratorio, digestivo, motriz, lenguaje, cerebral, alergico, otros}
    traumatismos_caidas = Column(Text)  # NUEVO
    
    # Carnet de asegurado
    carnet_asegurado = Column(String(50))  # NUEVO
    aseguradora = Column(String(100))  # NUEVO
    
    # Documentos de identidad
    ci_numero = Column(String(20))  # NUEVO
    ci_complemento = Column(String(5))  # NUEVO
    ci_expedido = Column(String(5))  # NUEVO: CBBA, LP, SC, etc.
    certificado_nacimiento_url = Column(String(500))  # NUEVO: documento adjunto
    libreta_vacunas_url = Column(String(500))  # NUEVO: documento adjunto
    
    # Desarrollo evolutivo (hitos del formulario)
    edad_control_cabeza_meses = Column(Integer)  # NUEVO
    edad_sentarse_meses = Column(Integer)  # NUEVO
    edad_gatear_meses = Column(Integer)  # NUEVO
    edad_caminar_meses = Column(Integer)  # NUEVO
    edad_primeras_palabras_meses = Column(Integer)  # NUEVO
    edad_balbuceo_meses = Column(Integer)  # NUEVO
    edad_primeros_dientes_meses = Column(Integer)  # NUEVO
    problemas_marcha = Column(Text)  # NUEVO
    
    # Alimentación (formulario)
    lactancia_materna_meses = Column(Integer)  # NUEVO
    uso_biberon_desde_meses = Column(Integer)  # NUEVO
    alimentos_rechaza = Column(Text)  # NUEVO
    alimentos_prefiere = Column(Text)  # NUEVO
    intolerancias_alimenticias = Column(Text)  # NUEVO
    dieta_actual = Column(Text)  # NUEVO: JSON {leche, zumos, fruta, verduras, cereales, carnes, otros}
    problemas_alimentacion = Column(Text)  # NUEVO
    alimentos_en_pure = Column(Boolean, default=False)  # NUEVO
    
    # Sueño (formulario)
    horario_sueno_nocturno = Column(String(50))  # NUEVO: "20:00-07:00"
    horario_sueno_diurno = Column(String(100))  # NUEVO: "14:00-16:00"
    problemas_sueno = Column(Text)  # NUEVO
    duerme_con = Column(String(50))  # NUEVO: "solo", "papá", "mamá", "hermanos", "ambos"
    usa_chupete = Column(Boolean, default=False)  # NUEVO
    postura_sueno = Column(String(50))  # NUEVO
    se_duerme_como = Column(Text)  # NUEVO: brazos, canciones, acunado
    pesadillas_frecuencia = Column(String(50))  # NUEVO
    
    # Relación afectivo-social (formulario)
    quien_atiende = Column(String(100))  # NUEVO
    actividades_con_padres = Column(Text)  # NUEVO
    sentimientos_mas_expresados = Column(Text)  # NUEVO
    llora_habitualmente = Column(Boolean, default=False)  # NUEVO
    circunstancias_llanto = Column(Text)  # NUEVO
    objeto_afectivo = Column(String(100))  # NUEVO: mantita, peluche, etc.
    con_quien_juega = Column(Text)  # NUEVO
    juguetes_preferidos = Column(Text)  # NUEVO
    relacion_con_desconocidos = Column(Text)  # NUEVO
    
    # Estado académico
    estado = Column(String(20), default="preinscrito")  # NUEVO: preinscrito, inscrito, activo, baja, egresado
    fecha_inscripcion = Column(Date)  # EXISTENTE (mantener)
    fecha_primera_asistencia = Column(Date)  # NUEVO: para cálculo de prorrateo
    fecha_baja = Column(Date)  # NUEVO
    motivo_baja = Column(Text)  # NUEVO
    
    # Turno del alumno
    turno_id = Column(Integer, ForeignKey("turnos.id"))  # NUEVO: relación con tabla turnos
    
    # Auditoría
    creado_en = Column(DateTime, default=datetime.utcnow)  # EXISTENTE (mantener)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # EXISTENTE (mantener)
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"))  # NUEVO
    
    # ==================== RELACIONES ====================
    sede = relationship("Sede", back_populates="alumnos")  # EXISTENTE
    turno = relationship("Turno", back_populates="alumnos")  # NUEVO
    tutores = relationship("Tutor", secondary="alumnos_tutores", back_populates="alumnos")  # NUEVO
    hermanos = relationship("AlumnoHermano", foreign_keys="AlumnoHermano.alumno_id", back_populates="alumno")  # NUEVO
    paralelos = relationship("AlumnoParalelo", back_populates="alumno")  # EXISTENTE (mantener)
    asistencias = relationship("AsistenciaAlumno", back_populates="alumno")  # EXISTENTE (mantener)
    consentimientos = relationship("Consentimiento", back_populates="alumno")  # EXISTENTE (mantener)
    autorizaciones_retiro = relationship("AutorizacionRetiro", back_populates="alumno")  # NUEVO
    # pagos = relationship("Pago", back_populates="alumno")  # NUEVO (si ya tienes modelo Pago)
    # reportes_diarios = relationship("ReporteDiario", back_populates="alumno")  # NUEVO (si módulo portafolio)

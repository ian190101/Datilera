# app/infrastructure/db/models/alumnos/alumnos.py

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, DECIMAL, DateTime, Time
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
    
    # ==================== CAMPOS NUEVOS (Completos) ====================
    
    # Identificación única
    codigo_unico = Column(String(6), unique=True, nullable=False, index=True)
    
    # Datos personales adicionales
    nombres_completos = Column(String(200))
    lugar_nacimiento = Column(String(150))
    genero = Column(String(1))  # M/F
    foto_url = Column(String(500))
    direccion_domicilio = Column(Text) # --- FALTABA: Dirección Familiar
    
    # Contacto de Emergencia y Familia
    contacto_emergencia_nombre = Column(String(150)) # --- FALTABA
    contacto_emergencia_telefono = Column(String(20)) # --- FALTABA
    familiares_autorizados_recogo = Column(Text) # --- FALTABA: JSON/Texto de quiénes pueden recogerlo
    familiares_en_casa = Column(Text) # --- FALTABA: Quiénes viven en casa
    familiar_mas_apego = Column(String(100)) # --- FALTABA: Con quién se relaciona más
    
    # Datos de nacimiento
    peso_nacer = Column(DECIMAL(5, 2))
    talla_nacer = Column(DECIMAL(5, 2))
    parto_normal = Column(Boolean, default=True)
    parto_complicaciones = Column(Text)
    embarazo_normal = Column(Boolean, default=True)
    embarazo_complicaciones = Column(Text)
    
    # Salud
    tiene_alergias = Column(Boolean, default=False)
    alergias_detalle = Column(Text)
    medicacion_actual = Column(Text)
    tratamiento_actual = Column(Text)
    enfermedades_previas = Column(Text)
    problemas_salud = Column(Text)
    traumatismos_caidas = Column(Text)
    
    # Documentos
    carnet_asegurado = Column(String(50))
    aseguradora = Column(String(100))
    ci_numero = Column(String(20))
    ci_complemento = Column(String(5))
    ci_expedido = Column(String(5))
    certificado_nacimiento_url = Column(String(500))
    libreta_vacunas_url = Column(String(500))
    
    # Desarrollo evolutivo
    edad_control_cabeza_meses = Column(Integer)
    edad_sentarse_meses = Column(Integer)
    edad_gatear_meses = Column(Integer)
    edad_levantarse_meses = Column(Integer) # --- FALTABA: Sostenerse de pie
    edad_caminar_meses = Column(Integer)
    problemas_marcha = Column(Text)
    
    edad_balbuceo_meses = Column(Integer)
    edad_primeras_palabras_meses = Column(Integer)
    
    edad_primeros_dientes_meses = Column(Integer)
    sintomas_denticion = Column(Text) # --- FALTABA: Síntomas al salir dientes
    
    # Alimentación
    lactancia_materna_meses = Column(Integer)
    uso_biberon_desde_meses = Column(Integer)
    problemas_succion_masticacion = Column(Text) # --- FALTABA: Problemas al tragar/masticar
    
    dieta_actual = Column(Text)
    alimentos_en_pure = Column(Boolean, default=False)
    transicion_alimentacion_solida = Column(Text) # --- FALTABA: ¿Le costó pasar a sólida?
    
    intolerancias_alimenticias = Column(Text)
    alimentos_rechaza = Column(Text)
    alimentos_prefiere = Column(Text)
    
    problemas_alimentacion = Column(Text)
    respuesta_problemas_comer = Column(Text) # --- FALTABA: ¿Cómo responden los padres ante problemas?
    
    # Sueño
    horario_sueno_nocturno = Column(String(50))
    horario_sueno_diurno = Column(String(100))
    lugar_sueno = Column(String(100)) # --- FALTABA: ¿Dónde duerme? (Cuna, cama, etc)
    duerme_con = Column(String(50))   # Con quién
    
    co_sleeping_bebe_edad = Column(String(100)) # --- FALTABA: De bebé con quién dormía y hasta qué edad
    
    problemas_sueno = Column(Text)
    momento_problemas_sueno = Column(String(50)) # --- FALTABA: Antes/Durante/Después
    respuesta_problemas_sueno = Column(Text) # --- FALTABA: ¿Cómo responden los padres?
    
    usa_chupete = Column(Boolean, default=False)
    postura_sueno = Column(String(50))
    se_duerme_como = Column(Text)
    pesadillas_frecuencia = Column(String(50))
    otros_habitos_sueno = Column(Text) # --- FALTABA
    
    # Relación afectivo-social
    quien_atiende = Column(String(100))
    actividades_con_padres = Column(Text)
    sentimientos_mas_expresados = Column(Text)
    llora_habitualmente = Column(Boolean, default=False)
    circunstancias_llanto = Column(Text)
    objeto_afectivo = Column(String(100))
    con_quien_juega = Column(Text)
    juguetes_preferidos = Column(Text)
    relacion_con_desconocidos = Column(Text)
    
    # Estado académico
    estado = Column(String(20), default="preinscrito")
    fecha_inscripcion = Column(Date)
    fecha_primera_asistencia = Column(Date)
    fecha_baja = Column(Date)
    motivo_baja = Column(Text)
    
    # Turno
    turno_id = Column(Integer, ForeignKey("turnos.id"))
    
    # Auditoría
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # ==================== RELACIONES ====================
    sede = relationship("Sede", back_populates="alumnos")
    turno = relationship("Turno", back_populates="alumnos")
    tutores = relationship("Tutor", secondary="alumnos_tutores", back_populates="alumnos")
    hermanos = relationship("AlumnoHermano", foreign_keys="AlumnoHermano.alumno_id", back_populates="alumno")
    paralelos = relationship("AlumnoParalelo", back_populates="alumno")
    asistencias = relationship("AsistenciaAlumno", back_populates="alumno")
    consentimientos = relationship("Consentimiento", back_populates="alumno")
    autorizaciones_retiro = relationship("AutorizacionRetiro", back_populates="alumno")
    descuentos = relationship("Descuento", back_populates="alumno")
    plan_pago = relationship("PlanPagoPersonalizado", back_populates="alumno", uselist=False)
    prorrateos = relationship("Prorrateo", back_populates="alumno")
    pagos = relationship("Pago", back_populates="alumno")
    codigos_acceso = relationship("CodigoAcceso", back_populates="alumno", lazy="select")
    alumnos_tutores = relationship("AlumnoTutor", back_populates="alumno")
    planes_pago = relationship("PlanPago", back_populates="alumno")
    formularios_inscripcion = relationship("FormularioInscripcion", back_populates="alumno", lazy="select")
    prestamos_uniformes = relationship("PrestamoUniforme", back_populates="alumno", lazy="select")
    actividades_portafolio = relationship("Actividad", back_populates="alumno", lazy="select")
    reportes_diarios = relationship("ReporteDiario", back_populates="alumno", lazy="select")
# app/infrastructure/db/models/seguridad/usuarios.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship  # ← AGREGAR si no está
from app.infrastructure.db.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hash_password = Column(String(255), nullable=False)
    nombres = Column(String(160), nullable=False)
    apellidos = Column(String(160), nullable=False)
    email = Column(String(120), nullable=True, index=True)
    telefono = Column(String(20), nullable=True)
    foto_perfil_url = Column(String(255), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    ci_numero = Column(String(20))  # NUEVO
    direccion = Column(Text)  # NUEVO
    codigo_acceso = Column(String(6), unique=True, index=True)  # NUEVO
    codigo_usado = Column(Boolean, default=False)  # NUEVO
    codigo_expira_en = Column(DateTime)  # NUEVO
    
    # ==================== AGREGAR ESTA RELACIÓN ====================
    tutor = relationship("Tutor", back_populates="usuario", uselist=False)  # ← NUEVO: relación con tutores
    asistencias_personal = relationship("AsistenciaPersonal", foreign_keys="[AsistenciaPersonal.personal_id]", back_populates="personal", lazy="select")
    asistencias_registradas = relationship("AsistenciaPersonal", foreign_keys="[AsistenciaPersonal.registrado_por_id]", back_populates="registrado_por", lazy="select")
    permisos_personales = relationship("PermisoPersonal", foreign_keys="[PermisoPersonal.personal_id]", back_populates="personal", lazy="select")
    permisos_aprobados = relationship("PermisoPersonal", foreign_keys="[PermisoPersonal.aprobado_por_id]", back_populates="aprobado_por", lazy="select")
    autorizaciones_retiro_creadas = relationship("AutorizacionRetiro", foreign_keys="[AutorizacionRetiro.creado_por_id]", back_populates="creado_por", lazy="select")
    paralelos_asignados = relationship(
    "ParaleloProfesora",
    back_populates="profesora",
    lazy="select",
    )
    # Códigos que este usuario puede consumir (usos)
    codigos_acceso_usados = relationship(
        "CodigoAccesoUso",
        back_populates="usuario",
        lazy="select",
    )

    # Códigos creados por este usuario (admin/directora)
    codigos_acceso_creados = relationship(
        "CodigoAcceso",
        foreign_keys="[CodigoAcceso.creado_por]",
        back_populates="creador",
        lazy="select",
    )

    # Códigos donde es destino explícito (profesora)
    codigos_acceso_asignados = relationship(
        "CodigoAcceso",
        foreign_keys="[CodigoAcceso.usuario_destino_id]",
        back_populates="usuario_destino",
        lazy="select",
    )

    auditoria_acciones = relationship("AuditoriaAccion", back_populates="usuario", lazy="select")
    auditoria_sesiones = relationship("AuditoriaSesion", back_populates="usuario", lazy="select")
    auditoria_exportaciones = relationship("AuditoriaExportacion", back_populates="usuario", lazy="select")
    auditoria_prompts_ia = relationship("AuditoriaPromptIA", back_populates="usuario", lazy="select")
    tipos_eventos_creados = relationship("TipoEvento", foreign_keys="[TipoEvento.creado_por]", back_populates="creador", lazy="select")
    eventos_creados = relationship("EventoCalendario", foreign_keys="[EventoCalendario.creado_por]", back_populates="creador", lazy="select")
    eventos_aprobados = relationship("EventoCalendario", foreign_keys="[EventoCalendario.aprobado_por]", back_populates="aprobador", lazy="select")
    planificaciones_creadas = relationship("PlanificacionActividad", foreign_keys="[PlanificacionActividad.profesora_id]", back_populates="profesora", lazy="select")
    conversaciones_creadas = relationship("Conversacion", back_populates="creador", foreign_keys="[Conversacion.creado_por_id]", lazy="select")
    conversaciones_participa = relationship("ConversacionParticipante", back_populates="usuario", lazy="select")
    mensajes_enviados = relationship("Mensaje", back_populates="remitente", foreign_keys="[Mensaje.remitente_id]", lazy="select")
    lecturas_mensajes = relationship("MensajeLeido", back_populates="usuario", lazy="select")
    notificaciones = relationship("Notificacion", back_populates="usuario", lazy="select")
    #notificaciones_vistas = relationship("NotificacionVista", back_populates="usuario", lazy="select")
    cursos_extra_creados = relationship("CursoExtra", back_populates="creado_por", foreign_keys="[CursoExtra.creado_por_id]", lazy="select")
    inscripciones_cursos_extra = relationship("InscripcionCursoExtra", back_populates="inscrito_por", foreign_keys="[InscripcionCursoExtra.inscrito_por_id]", lazy="select")
    pagos_cursos_extra_registrados = relationship("PagoCursoExtra", back_populates="registrado_por", foreign_keys="[PagoCursoExtra.registrado_por_id]", lazy="select")
    costos_cursos_extra_registrados = relationship("CostoCursoExtra", back_populates="registrado_por", foreign_keys="[CostoCursoExtra.registrado_por_id]", lazy="select")
    categorias_costo_curso_extra_creadas = relationship("CategoriaCostoCursoExtra", back_populates="creado_por", foreign_keys="[CategoriaCostoCursoExtra.creado_por_id]", lazy="select")
    alumnos_externos_registrados = relationship("AlumnoExterno", back_populates="registrado_por", foreign_keys="[AlumnoExterno.registrado_por_id]", lazy="select")
    pagos_registrados = relationship("Pago", back_populates="usuario_registro", foreign_keys="[Pago.registrado_por]", lazy="select")
    movimientos_caja_registrados = relationship("LibroCaja", back_populates="usuario_registro", foreign_keys="[LibroCaja.usuario_registro_id]", lazy="select")
    planes_pago_personalizados_creados = relationship("PlanPagoPersonalizado", back_populates="creador", foreign_keys="[PlanPagoPersonalizado.creado_por]", lazy="select")
    ia_consultas = relationship("IAConsulta", back_populates="usuario", lazy="select")
    formularios_revisados = relationship("FormularioInscripcion", back_populates="revisado_por_usuario", foreign_keys="[FormularioInscripcion.revisado_por]", lazy="select")
    formularios_aprobados = relationship("FormularioInscripcion", back_populates="aprobado_por_usuario", foreign_keys="[FormularioInscripcion.aprobado_por]", lazy="select")
    movimientos_stock = relationship("MovimientoStock", back_populates="usuario", lazy="select")
    actividades_portafolio = relationship("Actividad", back_populates="profesora", lazy="select")
    reportes_diarios = relationship("ReporteDiario", back_populates="profesora", lazy="select")
    lecturas_reportes_diarios = relationship("ReporteLecturaTutor", back_populates="tutor", lazy="select")
    sede = relationship("Sede", back_populates="usuarios")
    sesiones = relationship("Sesion", back_populates="usuario", lazy="select", cascade="all, delete-orphan")
    preferencias = relationship("PreferenciaUsuario", back_populates="usuario", uselist=False, lazy="select")
    #roles = relationship("UsuarioRol", back_populates="usuario", lazy="select", cascade="all, delete-orphan")
    egresos_registrados = relationship(
        "Egreso",
        foreign_keys="Egreso.registrado_por",
        back_populates="usuario_registro"
    )

    # Quién anuló egresos
    egresos_anulados = relationship(
        "Egreso",
        foreign_keys="Egreso.anulado_por",
        back_populates="usuario_anulacion"
    )
    arqueos_elaborados = relationship("Arqueo", back_populates="elaborador", foreign_keys="Arqueo.elaborado_por")
    # 1. ESTA ES LA QUE USAS PARA LOGIN (Many-to-Many directa)
    roles = relationship(
        "Rol",
        secondary="usuarios_roles",
        back_populates="usuarios",
        lazy="select",
        viewonly=True, # Recomendado: usa viewonly=True para evitar ambigüedad al guardar
    )

    # 2. ESTA ES LA NUEVA (Para manejar la tabla intermedia)
    # Se conecta con el archivo que acabamos de corregir
    roles_asociados = relationship(
        "UsuarioRol",
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy="noload"
    )
            # ===============================================================

    @property
    def nombre_usuario(self) -> str:
        return self.username

    @property
    def nombre_completo(self) -> str:
        return f"{(self.nombres or '').strip()} {(self.apellidos or '').strip()}".strip()

    @property
    def sede_nombre(self) -> str:
        # sidebar usa currentuser.sede_nombre [file:2]
        return getattr(self.sede, "nombre", "") or ""

    @property
    def lista_permisos(self) -> list[str]:
        # sidebar usa currentuser.lista_permisos [file:2]
        perms: set[str] = set()
        for rol in (self.roles or []):
            # En tu modelo Rol, la relación directa es rol.permisos [file:24]
            for p in (getattr(rol, "permisos", None) or []):
                # En tu Permiso los campos son vista y accion [file:26]
                vista = (p.vista or "").strip()
                accion = (p.accion or "").strip()
                if vista and accion:
                    perms.add(f"{vista}{accion}")   # ejemplo: "AcademicoVer"
        return sorted(perms)

# app/interfaces/web/routes.py
from fastapi import APIRouter, Request, Depends, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile, Form, Body, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import random
import json
import string
from datetime import datetime, timedelta, date
from sqlalchemy import select, or_, desc, func, update, case, exists, extract, distinct, and_
from contextlib import asynccontextmanager
from sqlalchemy.orm import selectinload, aliased
import shutil
from pathlib import Path
from fastapi.responses import StreamingResponse
import csv
import io
import os
import uuid
from decimal import Decimal
import calendar
from typing import List, Dict, Any, Optional
from typing import Literal
from pydantic import BaseModel
from sqlalchemy.orm.attributes import flag_modified # Importante para actualizar JSONs






# Imports de Configuración y Templates
from app.config.settings import get_settings
from app.main import templates
from app.infrastructure.db.base import Base

# Imports de Infraestructura Real
from app.infrastructure.db.session import get_session
from app.infrastructure.auth.auth_utils import PyJWTTokenService
from app.infrastructure.db.repositories.seguridad.usuarios_repo import UsuariosRepository
from app.infrastructure.db.repositories.dashboard.dashboard_repo import DashboardRepository

# --- IMPORTS PARA PRE-INSCRIPCIÓN REAL ---
from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.db.repositories.academico.grupos_repo import GruposRepository
from app.infrastructure.db.repositories.alumnos.alumnos_repo import AlumnosRepository
from app.infrastructure.db.models.alumnos.alumnos import Alumno
from app.infrastructure.db.models.seguridad.roles import Rol
from app.kernel.application.acceso.generar_codigo import GenerarCodigo, GenerarCodigoRequest
from app.infrastructure.db.models.acceso.codigos_acceso import CodigoAcceso
from app.infrastructure.db.models.alumnos.tutores import Tutor
from app.infrastructure.db.models.seguridad.usuarios import Usuario
from app.infrastructure.db.models.acceso.codigos_acceso import EstadoCodigo, CodigoAcceso
from app.infrastructure.db.models.alumnos.alumnos_tutores import AlumnoTutor
from app.infrastructure.auth.auth_utils import PasslibHasher
from app.infrastructure.db.models.seguridad.usuarios_roles import UsuarioRol
from app.infrastructure.db.models.alumnos.alumnos_paralelos import AlumnoParalelo
from app.infrastructure.db.models.academico.paralelos import Paralelo
from app.infrastructure.db.models.academico.grupos import Grupo
from app.infrastructure.db.models.finanzas.turnos import Turno

from app.infrastructure.db.models.portafolio.actividades import Actividad, TipoActividad
from app.infrastructure.db.models.alumnos.asistencia_alumnos import AsistenciaAlumno
from app.infrastructure.db.models.academico.paralelos_profesoras import ParaleloProfesora
from app.infrastructure.db.models.portafolio.reportes_diarios import ReporteDiario
from app.infrastructure.db.models.portafolio.reporte_lecturas_tutores import ReporteLecturaTutor
from app.infrastructure.db.models.portafolio.actividad_media import ActividadMedia, TipoMedia
from app.infrastructure.db.models.portafolio.planificacion_profesora import PlanificacionProfesora, DuracionPlanificacion
from app.infrastructure.db.models.comunicaciones.conversaciones import Conversacion, TipoConversacion
from app.infrastructure.db.models.comunicaciones.conversaciones_participantes import ConversacionParticipante
from app.infrastructure.db.models.comunicaciones.mensajes import Mensaje, TipoMensaje
from app.infrastructure.db.models.comunicaciones.mensajes_lecturas import MensajeLeido
from app.infrastructure.db.models.comunicaciones.notificaciones import Notificacion, CanalNotificacion, PrioridadNotificacion
from app.infrastructure.db.models.comunicaciones.notificacion_vistas import NotificacionVista
from app.infrastructure.db.models.academico.paralelos_profesoras import ParaleloProfesora
from app.kernel.application.services.ia_chat_service import IAChatService
from app.kernel.application.services.finanzas_service import FinanzasService
from app.kernel.application.services.ingresos_service import IngresosService
from app.kernel.application.services.arqueo_service import ArqueoService
from app.kernel.application.services.categoria_service import CategoriasService
from fastapi.responses import StreamingResponse
from app.kernel.application.services.recibo_service import ReciboService
from app.infrastructure.db.models.finanzas.pagos import Pago
from app.kernel.application.services.deudas_service import DeudasService
from app.infrastructure.db.models.finanzas.cuota_plan_pago import CuotaPlanPago
from app.infrastructure.db.models.finanzas.plan_pago_personalizado import PlanPagoPersonalizado
from app.infrastructure.db.models.finanzas.categorias_pago import CategoriaPago
from app.infrastructure.db.models.finanzas.categorias_egreso import CategoriaEgreso
from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum
from app.infrastructure.db.models.finanzas.egresos import Egreso
from app.infrastructure.db.models.inventario.items import Item
from app.infrastructure.db.models.inventario.familias import Familia
from app.infrastructure.db.models.inventario.categorias import Categoria
from app.infrastructure.db.models.inventario.items_atributos import ItemAtributo
from app.infrastructure.db.models.inventario.stock_sede import StockSede
from app.infrastructure.db.models.inventario.movimientos_stock import MovimientoStock, TipoMovimiento
from app.infrastructure.db.models.inventario.prestamos_uniformes import PrestamoUniforme
from app.infrastructure.db.models.cursos_extra.cursos_extra import CursoExtra
from app.infrastructure.db.models.cursos_extra.inscripciones_curso_extra import InscripcionCursoExtra, TipoAlumnoCursoExtra, EstadoInscripcionCursoExtra
from app.infrastructure.db.models.cursos_extra.alumnos_externos import AlumnoExterno
from app.infrastructure.db.models.cursos_extra.balance_curso_extra import BalanceCursoExtra, EstadoBalance
from app.infrastructure.db.models.cursos_extra.pagos_curso_extra import PagoCursoExtra, MetodoPagoCursoExtra
from app.infrastructure.db.models.cursos_extra.ingresos_curso_extra import IngresoCursoExtra
from app.infrastructure.db.models.cursos_extra.costos_curso_extra import CostoCursoExtra
from app.infrastructure.db.models.cursos_extra.categorias_costo_curso_extra import CategoriaCostoCursoExtra
from app.infrastructure.db.models.seguridad.preferencias_usuario import PreferenciaUsuario


from app.infrastructure.ws.events import (
    WSEventType, 
    WSBaseEvent, 
    WSChatMessagePayload, 
    WSNotificationNewPayload
)
from app.infrastructure.ws.manager import ws_manager, ConnectionInfo




settings = get_settings()
hasher = PasslibHasher()

# Router principal del frontend
web_router = APIRouter(tags=["Frontend Web"])


# ============================================================
# 🔐 DEPENDENCIAS DE AUTENTICACIÓN REAL
# ============================================================

from typing import Optional

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

#from app.infrastructure.auth.authutils import PyJWTTokenService
from app.infrastructure.db.session import get_session
from app.infrastructure.db.models.seguridad.usuarios import Usuario
from app.infrastructure.db.models.seguridad.roles import Rol  # para selectinload(Rol.permisos)


async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> Optional[Usuario]:
    print("\n🔍 --- DEBUG AUTH START ---")

    # 1) Cookie / Header
    print(f"🍪 Cookies recibidas: {request.cookies}")
    token = request.cookies.get("accesstoken") or request.cookies.get("access_token")


    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            print(f"headers: {auth_header}")
            token = auth_header.split(" ")[1] if "Bearer" in auth_header else None

    if not token:
        print("❌ FALLO: No hay token en cookie ni en header.")
        print("🔍 --- DEBUG AUTH END ---\n")
        return None

    try:
        # 2) Decode JWT
        print(f"🔑 Token encontrado (primeros 10 chars): {token[:10]}...")
        token_service = PyJWTTokenService()
        payload = token_service.decode_token(token)
        user_id = int(payload.get("sub"))
        print(f"👤 ID en token: {user_id}")

        # 3) Cargar usuario SQLAlchemy + roles + permisos + sede
        stmt = (
            select(Usuario)
            .options(
                selectinload(Usuario.roles).selectinload(Rol.permisos),  # necesario por lazy="noload" [file:24]
                selectinload(Usuario.sede),  # para sede_nombre en sidebar [file:2]
            )
            .where(Usuario.id == user_id)
            .limit(1)
        )
        res = await db.execute(stmt)
        user = res.scalars().first()

        if not user:
            print("❌ FALLO: Usuario no encontrado en BD.")
            print("🔍 --- DEBUG AUTH END ---\n")
            return None

        # 4) Debug útil
        print(f"✅ ÉXITO: Usuario autenticado: {user.username}")
        print("Roles:", [r.nombre for r in (user.roles or [])])
        # lista_permisos ya sale de tu @property en Usuario [file:25]
        print("Permisos (vista+accion):", user.lista_permisos)
        print("Sede:", user.sede_nombre)

        print("🔍 --- DEBUG AUTH END ---\n")
        return user

    except Exception as e:
        print(f"❌ ERROR EXCEPCIÓN: {e}")
        print("🔍 --- DEBUG AUTH END ---\n")
        return None



def get_home_url_for_user(user) -> str:
    roles = [r.nombre.upper() for r in (user.roles or [])]

    if any(r in {"ADMINISTRADOR","ADMIN","DIRECTORA","SISTEMAS","SUPERADMIN"} for r in roles):
        return "/dashboard"

    if any(r in {"PROFESORA","DOCENTE"} for r in roles):
        return "/academico"

    if "TUTOR" in roles:
        return "/academico"  # o el que estés usando

    if any(r in {"DUENO","DUEÑO","DUENA","DUEÑA"} for r in roles):
        return "/dueno/sedes"  # o el que estés usando

    return "/dashboard"



def check_auth_redirect(user):
    """Helper para verificar autenticación y retornar redirect si es necesario"""
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    return None


# ============================================================
# 🌐 RUTAS PÚBLICAS Y LOGIN
# ============================================================

@web_router.get("/", response_class=RedirectResponse)
async def root_redirect():
    return RedirectResponse(url="/login", status_code=303)


@web_router.get("/login", response_class=HTMLResponse, name="login_page")
async def login_page(request: Request, user = Depends(get_current_user_optional)):
    """Página de inicio de sesión"""
    # Si el usuario ya tiene sesión válida (cookie), lo mandamos dependiendo del usuario como en la funcion gethomeurlforuser
    if user:
        return RedirectResponse(url=get_home_url_for_user(user), status_code=303)
    
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "page_title": f"Iniciar Sesión - {settings.app_name}",
        "ENV": settings.environment
    })

@web_router.get("/logout", response_class=RedirectResponse, name="logout")
async def logout():
    """Cierra la sesión eliminando la cookie"""
    response = RedirectResponse(url="/login", status_code=303)
    
    # Eliminamos la cookie 'access_token'
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth/refresh")

    
    return response



# ============================================================
# ENDPOINTS - PORTAL DE TUTORES
# ============================================================

@web_router.get("/registro", response_class=HTMLResponse, name="registro_tutores")
async def registro_tutores_page(request: Request):
    """Página pública de registro de tutores (sin autenticación)"""
    return templates.TemplateResponse("tutores/registro.html", {
        "request": request,
        "page_title": f"Registro de Tutores - {settings.app_name}"
    })


# ============================================================
# REGISTRO REAL DE TUTORES (COMPLETO)
# ============================================================

@web_router.post("/api/v1/tutores/validar-codigo", tags=["Tutores"])
async def validar_codigo_tutor(
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """Valida código y retorna datos básicos del niño."""
    data = await request.json()
    codigo_str = data.get('codigo', '').strip().upper()
    
    # Buscamos el código y cargamos al alumno
    stmt = select(CodigoAcceso).options(selectinload(CodigoAcceso.alumno)).where(CodigoAcceso.codigo == codigo_str)
    result = await db.execute(stmt)
    codigo_obj = result.scalars().first()
    
    if not codigo_obj:
        return {"valido": False, "mensaje": "Código no encontrado"}
    if codigo_obj.estado in [EstadoCodigo.revocado, EstadoCodigo.expirado]:
        return {"valido": False, "mensaje": "El código ha expirado"}
    if codigo_obj.cuentas_creadas >= codigo_obj.max_cuentas:
        return {"valido": False, "mensaje": "Este código ya alcanzó su límite de uso"}

    alumno = codigo_obj.alumno
    return {
        "valido": True,
        "mensaje": "Código válido",
        "preinscripcion": {
            "id": alumno.id,
            "nombres": alumno.nombre,
            "apellidos": f"{alumno.apellido_paterno} {alumno.apellido_materno or ''}".strip()
        }
    }


@web_router.post("/api/v1/tutores/completar-registro", tags=["Tutores"])
async def completar_registro_tutor(
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """Procesa el formulario gigante de inscripción."""
    form = await request.form()
    codigo_str = form.get('codigo_validado')
    
    # --- Helper para guardar archivos en C:/Users/... ---
    async def guardar_archivo(upload_file, subcarpeta):
        if not upload_file or isinstance(upload_file, str) or upload_file.filename == '': 
            return None
        try:
            # Limpiar nombre
            safe_filename = f"{datetime.now().timestamp()}_{upload_file.filename.replace(' ', '_')}"
            
            # Usar ruta absoluta definida en .env (MEDIA_DIR)
            # Ej: C:/Users/Ian/Desktop/datilera_media/documentos
            ruta_destino = Path(settings.MEDIA_DIR) / subcarpeta
            ruta_destino.mkdir(parents=True, exist_ok=True)
            
            file_path = ruta_destino / safe_filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
                
            # Retornar URL relativa para la BD (/media/documentos/foto.jpg)
            return f"/media/{subcarpeta}/{safe_filename}"
        except Exception as e:
            print(f"❌ Error guardando archivo {upload_file.filename}: {e}")
            return None

    # Helpers de conversión
    def get_bool(key): return form.get(key) == 'SI'
    def get_int(key): 
        v = form.get(key)
        return int(v) if v and v.isdigit() else None
    def get_float(key):
        try: return float(form.get(key))
        except: return None

    try:
        async with db.begin():
            # 1. Verificar Código (Bloqueo pesimista para evitar doble uso simultáneo)
            stmt = select(CodigoAcceso).where(CodigoAcceso.codigo == codigo_str).with_for_update()
            res = await db.execute(stmt)
            codigo_db = res.scalars().first()
            
            if not codigo_db or codigo_db.cuentas_creadas >= codigo_db.max_cuentas:
                raise HTTPException(400, "El código no es válido o ya fue usado.")

            # Recuperar al Alumno
            stmt_alu = select(Alumno).where(Alumno.id == codigo_db.alumno_id)
            res_alu = await db.execute(stmt_alu)
            alumno = res_alu.scalars().first()

            # 2. Actualizar Datos del Alumno (FICHA COMPLETA)
            alumno.lugar_nacimiento = form.get('lugar_nacimiento')
            alumno.direccion_domicilio = form.get('direccion_familiar') # Dirección del niño
            alumno.estado = 'inscrito' 
            
            # Nacimiento
            alumno.peso_nacer = get_float('peso_nacer')
            alumno.talla_nacer = get_float('talla_nacer')
            alumno.embarazo_normal = (form.get('tipo_embarazo') == 'NORMAL')
            alumno.embarazo_complicaciones = form.get('embarazo_complicaciones')
            alumno.parto_normal = (form.get('tipo_parto') == 'NORMAL')
            alumno.parto_complicaciones = form.get('parto_complicaciones')
            
            # Salud
            alumno.tiene_alergias = get_bool('tiene_alergias')
            alumno.alergias_detalle = form.get('alergias')
            alumno.medicacion_actual = form.get('medicacion')
            # Checkboxes múltiples se reciben como lista si usas getlist, aquí asumimos string concatenado o ajustamos en JS
            # Para simplificar, guardamos lo que llegue en el campo de texto
            alumno.problemas_salud = form.get('problemas_salud_otros') 
            alumno.traumatismos_caidas = form.get('traumatismos')
            
            # Sueño
            alumno.horario_sueno_nocturno = form.get('sueno_nocturno')
            alumno.horario_sueno_diurno = form.get('sueno_diurno')
            alumno.lugar_sueno = form.get('donde_duerme')
            alumno.duerme_con = form.get('con_quien_duerme')
            alumno.co_sleeping_bebe_edad = form.get('co_sleeping')
            alumno.usa_chupete = get_bool('usa_chupete')
            alumno.postura_sueno = form.get('postura_sueno')
            alumno.se_duerme_como = form.get('como_duerme') # brazos, cuna...
            alumno.pesadillas_frecuencia = form.get('pesadillas')
            alumno.problemas_sueno = form.get('problemas_sueno')
            alumno.respuesta_problemas_sueno = form.get('respuesta_sueno')

            # Alimentación
            alumno.lactancia_materna_meses = get_int('lactancia_meses')
            alumno.uso_biberon_desde_meses = get_int('biberon_desde')
            alumno.problemas_succion_masticacion = form.get('problemas_comer')
            alumno.alimentos_en_pure = (form.get('tipo_comida') == 'PURE')
            alumno.alimentos_rechaza = form.get('alimentos_rechaza')
            alumno.alimentos_prefiere = form.get('alimentos_prefiere')
            alumno.intolerancias_alimenticias = form.get('intolerancias')
            alumno.transicion_alimentacion_solida = form.get('costo_solidos') # ¿Le costó pasar a sólidos?
            
            # Desarrollo
            alumno.edad_control_cabeza_meses = get_int('edad_cabeza')
            alumno.edad_sentarse_meses = get_int('edad_sentarse')
            alumno.edad_gatear_meses = get_int('edad_gatear')
            alumno.edad_levantarse_meses = get_int('edad_pararse')
            alumno.edad_caminar_meses = get_int('edad_caminar')
            alumno.edad_primeras_palabras_meses = get_int('edad_palabras')
            alumno.edad_primeros_dientes_meses = get_int('edad_dientes')
            alumno.sintomas_denticion = form.get('sintomas_dientes')
            alumno.problemas_marcha = form.get('problemas_marcha')
            
            # Social / Familiar
            alumno.quien_atiende = form.get('quien_atiende')
            alumno.familiares_en_casa = form.get('quien_vive_casa')
            alumno.actividades_con_padres = form.get('actividades_padres')
            alumno.sentimientos_mas_expresados = form.get('emociones')
            alumno.llora_habitualmente = get_bool('llora_mucho')
            alumno.circunstancias_llanto = form.get('motivo_llanto')
            alumno.objeto_afectivo = form.get('objeto_apego')
            alumno.con_quien_juega = form.get('con_quien_juega')
            alumno.relacion_con_desconocidos = form.get('relacion_extraños')
            
            # Emergencia
            alumno.contacto_emergencia_nombre = form.get('emergencia_nombre')
            # Nota: usamos el mismo campo para relación o teléfono según tu modelo, aquí asumí nombre completo
            alumno.familiares_autorizados_recogo = form.get('autorizados_recoger')

            # Guardar Archivos
            url_nac = await guardar_archivo(form.get('doc_certificado_nacimiento'), "documentos_alumnos")
            if url_nac: alumno.certificado_nacimiento_url = url_nac
            
            url_vac = await guardar_archivo(form.get('doc_carnet_vacunas'), "documentos_alumnos")
            if url_vac: alumno.libreta_vacunas_url = url_vac

            # 3. Crear USUARIO (Login)
            nuevo_usuario = Usuario(
                sede_id=codigo_db.sede_id,
                username=form.get('nombre_usuario'),
                hash_password=hasher.hash_password(form.get('password')),
                nombres=form.get('tutor1_nombres'),
                apellidos="", # Se guarda completo en nombres por ahora
                email=form.get('tutor1_email'),
                telefono=form.get('tutor1_celular'),
                activo=True
            )
            db.add(nuevo_usuario)
            await db.flush() # Obtener ID


            # Buscamos el ID del rol "TUTOR" (usamos ilike para ignorar mayúsculas)
            rol_tutor = await db.scalar(select(Rol).where(Rol.nombre.ilike("TUTOR")))
            
            if rol_tutor:
                # Creamos la relación en la tabla intermedia
                usuario_rol_rel = UsuarioRol(
                    usuario_id=nuevo_usuario.id,
                    rol_id=rol_tutor.id
                )
                db.add(usuario_rol_rel)
            else:
                # Fallback por si no existe el rol en la BD (opcional: lanzar error)
                print("⚠️ ALERTA: No se encontró el rol 'TUTOR' en la base de datos.")
            # =================================================================


            # 4. Crear TUTOR 1 (Principal)
            tutor1 = Tutor(
                usuario_id=nuevo_usuario.id,
                nombres=form.get('tutor1_nombres'),
                apellidos="", 
                ci_numero=form.get('tutor1_ci'),
                ci_expedido=form.get('tutor1_expedido'),
                celular=form.get('tutor1_celular'),
                email=form.get('tutor1_email'),
                direccion=form.get('tutor1_direccion'), # Dirección trabajo
                lugar_trabajo=form.get('tutor1_lugar_trabajo'),
                profesion=form.get('tutor1_profesion'),
                codigo_acceso=codigo_str,
                codigo_usado=True
            )
            db.add(tutor1)
            await db.flush()

            # Vincular Tutor 1 - Alumno
            from sqlalchemy import text
            # Crear el objeto de relación usando tu modelo
            relacion_tutor = AlumnoTutor(
                alumno_id=alumno.id,
                tutor_id=tutor1.id,
                tipo_relacion="MADRE/PADRE",  # O lo que venga del form: form.get('tutor1_relacion')
                tiene_custodia=True,          # El 1er '1' que tenías
                es_principal=True,            # El 2do '1' que tenías (asumiendo que era para principal)
                #vive_con_alumno=True,         # Puedes agregar más campos explícitos si quieres
                autorizado_retirar=True
            )

            # Guardarlo
            db.add(relacion_tutor) # O tomar del form si existe campo relación

           # 5. Crear TUTOR 2 (Opcional)
            if form.get('tutor2_nombres'):
                tutor2 = Tutor(
                    nombres=form.get('tutor2_nombres'),
                    apellidos="",
                    ci_numero=form.get('tutor2_ci') or "S/N",
                    celular=form.get('tutor2_celular') or "S/N",
                    profesion=form.get('tutor2_profesion'),
                    lugar_trabajo=form.get('tutor2_lugar_trabajo'),
                    email=form.get('tutor2_email')
                )
                db.add(tutor2)
                await db.flush()

                relacion2 = AlumnoTutor(
                    alumno_id=alumno.id,
                    tutor_id=tutor2.id,
                    tipo_relacion="PADRE/MADRE",  # o form.get('tutor2_relacion')
                    es_principal=False,
                    autorizado_retirar=True,
                    # completa los demás flags si tu modelo los requiere
                )
                db.add(relacion2)


            # 6. Consumir Código
            codigo_db.cuentas_creadas += 1
            if codigo_db.cuentas_creadas >= codigo_db.max_cuentas:
                codigo_db.estado = EstadoCodigo.consumido

        return {
            "success": True, 
            "mensaje": "¡Inscripción completada exitosamente!", 
            "usuario": form.get('nombre_usuario')
        }

    except Exception as e:
        print(f"❌ Error Registro: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar: {str(e)}")



# ============================================================
# REGISTRO DE PROFESORAS
# ============================================================

@web_router.get("/registro-profesoras", response_class=HTMLResponse, name="registro_profesoras")
async def registro_profesoras_page(request: Request):
    """Página pública de registro de profesoras"""
    return templates.TemplateResponse("profesoras/registro.html", {
        "request": request,
        "page_title": f"Registro de Personal - {settings.app_name}"
    })

@web_router.post("/api/v1/profesoras/validar-codigo", tags=["Profesores"])
async def validar_codigo_profesora(
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    data = await request.json()
    codigo_str = data.get('codigo', '').strip().upper()
    
    # Buscar código (Asumiendo que el rol para profes tiene ID específico o se valida por lógica de negocio)
    stmt = select(CodigoAcceso).where(CodigoAcceso.codigo == codigo_str)
    result = await db.execute(stmt)
    codigo_obj = result.scalars().first()
    
    if not codigo_obj:
        return {"valido": False, "mensaje": "Código no encontrado"}
    
    # Validar que sea un código destinado a STAFF/PROFESORA (opcional, si manejas roles en códigos)
    # if codigo_obj.rol_id != ID_ROL_PROFESORA: ...

    if codigo_obj.estado in [EstadoCodigo.revocado, EstadoCodigo.expirado, EstadoCodigo.consumido]:
        return {"valido": False, "mensaje": "El código ya fue utilizado o ha expirado"}

    return {
        "valido": True,
        "mensaje": "Código válido"
    }

@web_router.post("/api/v1/profesoras/completar-registro", tags=["Profesores"])
async def completar_registro_profesora(
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    form = await request.form()
    codigo_str = form.get('codigo_validado')
    
    try:
        async with db.begin():
            # 1. Verificar Código
            stmt = select(CodigoAcceso).where(CodigoAcceso.codigo == codigo_str).with_for_update()
            res = await db.execute(stmt)
            codigo_db = res.scalars().first()
            
            if not codigo_db or codigo_db.estado == EstadoCodigo.consumido:
                raise HTTPException(400, "Código inválido o ya usado")

            # 2. Crear USUARIO
            nuevo_usuario = Usuario(
                sede_id=codigo_db.sede_id,
                username=form.get('nombre_usuario'),
                hash_password=hasher.hash_password(form.get('password')),
                nombres=form.get('nombres_completos'),
                apellidos="", 
                email=None,   
                telefono=form.get('celular'),
                ci_numero=form.get('ci'),
                direccion=form.get('direccion'),
                activo=True
            )
            db.add(nuevo_usuario)
            await db.flush() # Importante: Obtenemos el ID del nuevo usuario
            
            # 3. Asignar Rol (Método Explícito: Igual que Tutores)
            # Buscamos el ID del rol "PROFESORA"
            rol_profe = await db.scalar(select(Rol).where(Rol.nombre.ilike("PROFESORA")))
            
            if rol_profe:
                # Creamos la relación manualmente en la tabla intermedia
                nueva_relacion = UsuarioRol(
                    usuario_id=nuevo_usuario.id, 
                    rol_id=rol_profe.id
                )
                db.add(nueva_relacion)
            else:
                print("⚠️ ADVERTENCIA: No se encontró el rol 'PROFESORA' en la BD. El usuario se creó sin rol.")

            # 4. Consumir Código
            codigo_db.estado = EstadoCodigo.consumido
            codigo_db.cuentas_creadas += 1
            codigo_db.usuario_destino_id = nuevo_usuario.id 

        return {
            "success": True,
            "mensaje": "Cuenta de profesora creada exitosamente",
            "usuario": form.get('nombre_usuario')
        }

    except Exception as e:
        print(f"❌ Error Registro Profesora: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar: {str(e)}")

# ============================================================
# 🛡️ RUTAS PROTEGIDAS (DASHBOARD & MÓDULOS)
# ============================================================

@web_router.get("/dashboard", response_class=HTMLResponse, name="dashboard")
async def dashboard_page(request: Request, user = Depends(get_current_user_optional)):
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    return templates.TemplateResponse("dashboard/index.html", {
        "request": request,
        "current_user": user,
        "page_title": f"Panel General - {settings.app_name}",
        "active_menu": "dashboard"
    })



# ============================================================
# DICCIONARIOS DE TRADUCCIÓN (Helpers)
# ============================================================
MESES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

DIAS = {
    0: "Lun", 1: "Mar", 2: "Mié", 3: "Jue", 4: "Vie", 5: "Sáb", 6: "Dom"
}


# ============================================================
# 📊 DASHBOARD REAL (CON FILTROS DINÁMICOS)
# ============================================================

@web_router.get("/api/v1/reportes/dashboard/metricas", tags=["Dashboard"])
async def get_dashboard_metrics(
    period: str = "month",  # week, month, year
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Calcula métricas filtradas por el periodo seleccionado."""
    if not user: return {}
    
    # Imports locales
    from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum
    from app.infrastructure.db.models.finanzas.cuota_plan_pago import CuotaPlanPago
    from app.infrastructure.db.models.finanzas.plan_pago_personalizado import PlanPagoPersonalizado
    
    hoy = datetime.now().date()
    start_date = hoy
    
    # Definir rango de fechas según filtro
    if period == 'week':
        # Lunes de esta semana
        start_date = hoy - timedelta(days=hoy.weekday())
    elif period == 'year':
        start_date = date(hoy.year, 1, 1)
    else: # Default: month
        start_date = date(hoy.year, hoy.month, 1)

    # 1. Total Inscritos (Siempre es el total histórico activo, no depende del periodo)
    stmt_total = select(func.count(Alumno.id)).where(
        Alumno.sede_id == user.sede_id,
        Alumno.estado == 'inscrito'
    )
    total_inscritos = await db.scalar(stmt_total) or 0
    
    # 2. Nuevos en el periodo seleccionado
    stmt_nuevos = select(func.count(Alumno.id)).where(
        Alumno.sede_id == user.sede_id,
        Alumno.creado_en >= start_date
    )
    nuevos_total = await db.scalar(stmt_nuevos) or 0
    
    # 3. Ingresos en el periodo seleccionado
    stmt_ingresos = select(func.sum(LibroCaja.monto)).where(
        LibroCaja.sede_id == user.sede_id,
        LibroCaja.tipo == TipoMovimientoEnum.INGRESO,
        LibroCaja.fecha >= start_date
    )
    ingresos_total = await db.scalar(stmt_ingresos) or 0.0
    
    # 4. Mora (Deuda acumulada histórica, no depende del periodo, es estado actual)
    stmt_mora = (
        select(
            func.count(CuotaPlanPago.id),
            func.sum(CuotaPlanPago.monto_cuota - CuotaPlanPago.monto_pagado)
        )
        .join(PlanPagoPersonalizado, CuotaPlanPago.plan_id == PlanPagoPersonalizado.id)
        .join(Alumno, PlanPagoPersonalizado.alumno_id == Alumno.id)
        .where(
            Alumno.sede_id == user.sede_id,
            CuotaPlanPago.estado == 'pendiente',
            CuotaPlanPago.fecha_vencimiento < hoy 
        )
    )
    row_mora = (await db.execute(stmt_mora)).first()
    
    return {
        "total_inscritos": total_inscritos,
        "inscritos_cambio_porcentaje": 0, 
        "ingresos_total": float(ingresos_total),
        "ingresos_objetivo_porcentaje": 0,
        "pagos_pendientes_cantidad": row_mora[0] or 0,
        "pagos_pendientes_monto": float(row_mora[1] or 0.0),
        "nuevos_total": nuevos_total
    }

@web_router.get("/api/v1/reportes/dashboard/crecimiento-inscripciones", tags=["Dashboard"])
async def get_dashboard_chart_inscripciones(
    period: str = "month",
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Gráfico de inscripciones. 
    """
    if not user: return {"labels": [], "valores": []}
    
    hoy = datetime.now().date()
    labels = []
    valores = []
    
    if period == 'year':
        # Mostrar ultimos 12 meses
        for i in range(11, -1, -1):
            d = hoy.replace(day=1) - timedelta(days=30*i)
            
            stmt = select(func.count(Alumno.id)).where(
                Alumno.sede_id == user.sede_id,
                extract('month', Alumno.creado_en) == d.month,
                extract('year', Alumno.creado_en) == d.year
            )
            count = await db.scalar(stmt) or 0
            
            # ✅ CORREGIDO: Usar diccionario MESES
            labels.append(MESES[d.month]) 
            valores.append(count)
            
        # Invertir para que sea cronológico
        labels.reverse()
        valores.reverse()

    elif period == 'month':
        # Mostrar por semanas del mes actual
        inicio_mes = date(hoy.year, hoy.month, 1)
        for i in range(5):
            inicio_sem = inicio_mes + timedelta(weeks=i)
            fin_sem = inicio_sem + timedelta(days=6)
            if inicio_sem.month != hoy.month: break 
            
            stmt = select(func.count(Alumno.id)).where(
                Alumno.sede_id == user.sede_id,
                Alumno.creado_en >= inicio_sem,
                Alumno.creado_en <= fin_sem
            )
            count = await db.scalar(stmt) or 0
            
            # ✅ CORREGIDO: Texto simple "Sem 1", "Sem 2"...
            labels.append(f"Sem {i+1}")
            valores.append(count)
            
    else: # week (Diario)
        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)
            stmt = select(func.count(Alumno.id)).where(
                Alumno.sede_id == user.sede_id,
                func.date(Alumno.creado_en) == dia
            )
            count = await db.scalar(stmt) or 0
            
            # ✅ CORREGIDO: Usar diccionario DIAS
            label_dia = f"{DIAS[dia.weekday()]} {dia.day}" # Ej: "Lun 12"
            labels.append(label_dia)
            valores.append(count)

    return {"labels": labels, "valores": valores}

@web_router.get("/api/v1/reportes/dashboard/flujo-ingresos", tags=["Dashboard"])
async def get_dashboard_chart_ingresos(
    period: str = "month",
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Ingresos (Barras).
    """
    if not user: return {"labels": [], "valores": []}
    
    from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum
    
    hoy = datetime.now().date()
    labels = []
    valores = []
    
    if period == 'year':
        # Agrupar por mes
        for i in range(5, -1, -1): # Últimos 6 meses
            mes_calc = (hoy.month - i)
            anio_calc = hoy.year
            if mes_calc <= 0:
                mes_calc += 12
                anio_calc -= 1
                
            stmt = select(func.sum(LibroCaja.monto)).where(
                LibroCaja.sede_id == user.sede_id,
                LibroCaja.tipo == TipoMovimientoEnum.INGRESO,
                extract('month', LibroCaja.fecha) == mes_calc,
                extract('year', LibroCaja.fecha) == anio_calc
            )
            total = await db.scalar(stmt) or 0.0
            
            # ✅ CORREGIDO: Usar diccionario MESES
            labels.append(MESES[mes_calc])
            valores.append(float(total))

    elif period == 'week':
        # Diario
        start_week = hoy - timedelta(days=hoy.weekday()) # Lunes
        for i in range(7):
            dia = start_week + timedelta(days=i)
            stmt = select(func.sum(LibroCaja.monto)).where(
                LibroCaja.sede_id == user.sede_id,
                LibroCaja.tipo == TipoMovimientoEnum.INGRESO,
                LibroCaja.fecha == dia
            )
            total = await db.scalar(stmt) or 0.0
            
            # ✅ CORREGIDO: Usar diccionario DIAS
            label_dia = f"{DIAS[dia.weekday()]} {dia.day}" # Ej: "Lun 12"
            labels.append(label_dia)
            valores.append(float(total))
            
    else: # Default: 'month' (Mostrar 4 semanas atrás)
        for i in range(3, -1, -1):
            fin_sem = hoy - timedelta(weeks=i)
            # Ajustar al domingo
            fin_sem = fin_sem + timedelta(days=(6 - fin_sem.weekday()))
            inicio_sem = fin_sem - timedelta(days=6)
            
            stmt = select(func.sum(LibroCaja.monto)).where(
                LibroCaja.sede_id == user.sede_id,
                LibroCaja.tipo == TipoMovimientoEnum.INGRESO,
                LibroCaja.fecha >= inicio_sem,
                LibroCaja.fecha <= fin_sem
            )
            total = await db.scalar(stmt) or 0.0
            
            # ✅ CORREGIDO: Usar diccionario MESES con la fecha de inicio de semana
            # Esto evita el error de "NameError: variable 'dia' is not defined"
            label = f"{inicio_sem.day} {MESES[inicio_sem.month]}" # Ej: "25 Dic"
            labels.append(label)
            valores.append(float(total))
        
    return {"labels": labels, "valores": valores}


@web_router.get("/inscripciones", response_class=HTMLResponse, name="inscripciones_list")
async def inscripciones_list_page(request: Request, user = Depends(get_current_user_optional)):
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    return templates.TemplateResponse("inscripciones/list.html", {
        "request": request,
        "current_user": user,
        "page_title": f"Inscripciones - {settings.app_name}",
        "active_menu": "inscripciones"
    })


@web_router.get("/inscripciones/nueva", response_class=HTMLResponse, name="inscripciones_create")
async def inscripciones_create_page(request: Request, user = Depends(get_current_user_optional)):
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    return templates.TemplateResponse("inscripciones/create.html", {
        "request": request,
        "current_user": user,
        "page_title": f"Nueva Inscripción - {settings.app_name}",
        "active_menu": "inscripciones"
    })


@web_router.get("/academico", response_class=HTMLResponse, name="academico")
async def academico_page(request: Request, user = Depends(get_current_user_optional)):
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    return templates.TemplateResponse("academico/index.html", {
        "request": request,
        "current_user": user,
        "page_title": f"Gestión Académica - {settings.app_name}",
        "active_menu": "academico"
    })


@web_router.get("/finanzas", response_class=HTMLResponse, name="finanzas")
async def finanzas_page(request: Request, user = Depends(get_current_user_optional)):
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    return templates.TemplateResponse("finanzas/index.html", {
        "request": request,
        "current_user": user,
        "page_title": f"Finanzas & Pagos - {settings.app_name}",
        "active_menu": "finanzas",
        "now": datetime.now()
    })


# ============================================================
# 📋 LISTADO REAL DE INSCRIPCIONES
# ============================================================

@web_router.get("/api/v1/inscripciones", tags=["Inscripciones"])
async def listar_inscripciones_endpoint(
    page: int = 1,
    per_page: int = 10,
    search: str = "",
    estado: str = "",
    grupo: str = "", 
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: return {"items": [], "total": 0}

    # 1. Query Base con Eager Loading (Carga Ansiosa)
    # Cargamos todas las relaciones necesarias para pintar la tabla rápido
    stmt = (
        select(Alumno)
        .options(
            selectinload(Alumno.tutores),
            selectinload(Alumno.codigos_acceso),
            selectinload(Alumno.turno),
            # Carga anidada: Alumno -> Lista[AlumnoParalelo] -> Paralelo -> Grupo
            selectinload(Alumno.paralelos).selectinload(AlumnoParalelo.paralelo).selectinload(Paralelo.grupo)
        )
        .where(Alumno.sede_id == user.sede_id)
        .order_by(desc(Alumno.creado_en))
    )

    # 2. Filtros Dinámicos
    if estado:
        # Mapeo Front -> BD
        estado_map = {
            "ACTIVO": "inscrito", 
            "PENDIENTE": "preinscrito", 
            "INACTIVO": "baja"
        }
        val = estado_map.get(estado, estado.lower())
        stmt = stmt.where(Alumno.estado == val)

    if grupo:
        # Filtro de Grupo (Relación Muchos a Muchos)
        # Buscamos alumnos que tengan AL MENOS un paralelo asociado a este grupo
        stmt = stmt.join(Alumno.paralelos).join(AlumnoParalelo.paralelo).where(Paralelo.grupo_id == int(grupo))

    if search:
        term = f"%{search}%"
        stmt = stmt.where(or_(
            Alumno.nombre.ilike(term),
            Alumno.apellido_paterno.ilike(term),
            Alumno.nombres_completos.ilike(term),
            Alumno.codigo_unico.ilike(term)
        ))

    count_query = select(func.count()).select_from(stmt.subquery())
    total_real = await db.scalar(count_query) or 0

    # 3. Contadores en Tiempo Real (Stats)
    stat_stmt = select(
        func.count().label('total'),
        func.sum(case((Alumno.estado == 'inscrito', 1), else_=0)).label('activos'),
        func.sum(case((Alumno.estado == 'preinscrito', 1), else_=0)).label('pendientes')
    ).where(Alumno.sede_id == user.sede_id)
    
    stat_res = await db.execute(stat_stmt)
    stat = stat_res.one()
    
    # 4. Ejecución con Paginación
    # Contar total filtrado (usando distinct por si el join duplica filas)
    count_stmt = select(func.count(distinct(Alumno.id))).select_from(stmt.subquery())
    # Nota: Si el subquery es complejo, a veces es mejor contar simple. 
    # Para simplificar aquí usamos count del query filtrado:
    # (Si da error, simplificar a select(func.count(Alumno.id))... con los mismos wheres)
    
    # Paginacion
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    alumnos = result.scalars().all() # .unique() a veces necesario en relaciones M2M

    
    # 5. Formateo de Datos para el Frontend
    items = []
    hoy = datetime.now().date()
    for alu in alumnos:
        # A) Tutor
        nombre_tutor = "Sin tutor"
        telefono_tutor = "--"
        if alu.tutores:
            t = alu.tutores[0]
            nombre_tutor = f"{t.nombres} {t.apellidos}"
            telefono_tutor = t.celular
        elif alu.codigos_acceso:
            c = alu.codigos_acceso[-1]
            nombre_tutor = "Pre-registro"
            telefono_tutor = c.whatsapp_numero

        # B) Grupo, Paralelo y Turno
        grupo_str = "Sin Asignar"
        paralelo_str = "-"
        
        # Lógica: Tomamos el último paralelo asignado (o el activo)
        if alu.paralelos:
            # Ordenamos o filtramos si fuera necesario, aquí tomamos el último de la lista
            ap = alu.paralelos[-1] 
            if ap.paralelo:
                paralelo_str = ap.paralelo.letra
                if ap.paralelo.grupo:
                    grupo_str = ap.paralelo.grupo.nombre
        
        turno_str = alu.turno.nombre if alu.turno else "Sin Turno"

        # C) Estado Visual
        estado_front = "PENDIENTE"
        if alu.estado == 'inscrito': estado_front = "ACTIVO"
        elif alu.estado == 'baja': estado_front = "INACTIVO"

        # D) CÁLCULO DE EDAD DETALLADA (Años, Meses, Días)
        edad_str = "--"
        if alu.fecha_nacimiento:
            nac = alu.fecha_nacimiento
            # Calcular diferencia
            anos = hoy.year - nac.year
            meses = hoy.month - nac.month
            dias = hoy.day - nac.day

            # Ajuste de meses/días negativos
            if dias < 0:
                meses -= 1
                # Días del mes anterior
                import calendar
                prev_month = (hoy.month - 1) if hoy.month > 1 else 12
                prev_year = hoy.year if hoy.month > 1 else hoy.year - 1
                _, dias_mes_ant = calendar.monthrange(prev_year, prev_month)
                dias += dias_mes_ant
            
            if meses < 0:
                anos -= 1
                meses += 12
            
            # Construir texto amigable (singular/plural)
            txt_a = f"{anos} año{'s' if anos != 1 else ''}"
            txt_m = f"{meses} mes{'es' if meses != 1 else ''}"
            txt_d = f"{dias} día{'s' if dias != 1 else ''}"
            
            # Formato corto: "1 año, 2 meses" o "5 meses, 3 días" (si es bebé)
            if anos > 0:
                edad_str = f"{txt_a}, {txt_m}"
            elif meses > 0:
                edad_str = f"{txt_m}, {txt_d}"
            else:
                edad_str = f"{txt_d}"

        items.append({
            "id": alu.id,
            "nombre_alumno": alu.nombres_completos or f"{alu.nombre} {alu.apellido_paterno}",
            "foto_url": alu.foto_url if alu.foto_url else None,
            "codigo_inscripcion": alu.codigo_unico,
            "grupo": grupo_str,
            "paralelo": paralelo_str,
            "turno": turno_str,
            "edad_detalle": edad_str,
            "nombre_tutor_1": nombre_tutor,
            "telefono_tutor_1": telefono_tutor,
            "estado": estado_front,
            "fecha_inscripcion": alu.creado_en.strftime("%d/%m/%Y") if alu.creado_en else ""
        })

    # Si count_stmt es muy complejo, usamos len por ahora (en producción usar count real)
    total_filtered = len(alumnos) if not search and not grupo else len(alumnos) # Placeholder simple

    return {
        "items": items, 
        "total": total_real, # Ajustar con count real
        "page": page, 
        "per_page": per_page, 
        "stats": {
            "total": stat.total or 0, 
            "activos": stat.activos or 0, 
            "pendientes": stat.pendientes or 0
        }
    }


#Lista simple de alumnos

@web_router.get("/api/v1/alumnos-select/lista", tags=["Alumnos"])
async def listar_alumnos_simple(
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Devuelve ID y Nombre para llenar el <select> de cobros"""
    if not user: 
        raise HTTPException(401, "No autenticado")
    
    try:
        stmt = select(
            Alumno.id,
            Alumno.nombre,
            Alumno.apellido_paterno,
            Alumno.apellido_materno
        ).where(
            and_(
                Alumno.sede_id == user.sede_id,
                Alumno.estado == 'inscrito'
            )
        ).order_by(Alumno.apellido_paterno)
        
        result = await db.execute(stmt)
        rows = result.all()
        
        # ✅ Devolver lista de diccionarios directamente
        return [
            {
                "id": r.id,
                "nombre": f"{r.apellido_paterno} {r.apellido_materno or ''} {r.nombre}".strip()
            }
            for r in rows
        ]
    
    except Exception as e:
        print(f"❌ ERROR en lista-simple: {e}")
        raise HTTPException(500, f"Error interno: {str(e)}")


# ============================================================
# GESTIÓN DE FOTOS Y FICHA TÉCNICA
# ============================================================

@web_router.post("/api/v1/inscripciones/{alumno_id}/foto", tags=["Inscripciones"])
async def subir_foto_alumno(
    alumno_id: int,
    file: UploadFile = File(...),
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: 
        raise HTTPException(401)

    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "El archivo debe ser una imagen")

    try:
        # Guardar archivo en disco
        safe_filename = f"foto_{alumno_id}_{datetime.now().timestamp()}.jpg"
        ruta_carpeta = Path(settings.MEDIA_DIR) / "fotos_alumnos"
        ruta_carpeta.mkdir(parents=True, exist_ok=True)
        
        ruta_completa = ruta_carpeta / safe_filename
        
        with open(ruta_completa, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        url_publica = f"/media/fotos_alumnos/{safe_filename}"
        
        # --- CORRECCIÓN AQUÍ ---
        alumno = await db.get(Alumno, alumno_id)
        if not alumno: 
            raise HTTPException(404, "Alumno no encontrado")
        
        # 1. Asignar valor
        alumno.foto_url = url_publica
        
        # 2. Agregar a la sesión (para asegurar que SQLAlchemy lo rastree)
        db.add(alumno)
        
        # 3. CONFIRMAR CAMBIOS (Esto es lo que faltaba)
        await db.commit()
        
        # 4. Refrescar objeto (opcional, para asegurar que tenemos el dato guardado)
        await db.refresh(alumno)
        
        return {"success": True, "url": alumno.foto_url}
    
    except Exception as e:
        await db.rollback() # Importante: rollback si falla algo
        print(f"Error subiendo foto: {e}")
        raise HTTPException(500, "Error al guardar la imagen")

@web_router.get("/api/v1/inscripciones/{alumno_id}/ficha", tags=["Inscripciones"])
async def obtener_ficha_alumno(
    alumno_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Devuelve TODOS los datos para el File Personal"""
    if not user: raise HTTPException(401)
    
    stmt = (
        select(Alumno)
        .options(selectinload(Alumno.tutores)) # Cargar tutores
        .where(Alumno.id == alumno_id)
    )
    res = await db.execute(stmt)
    alu = res.scalars().first()
    
    if not alu: raise HTTPException(404)
    
    # Calcular edad exacta
    edad_str = ""
    meses_totales = 0
    if alu.fecha_nacimiento:
        hoy = datetime.now().date()
        nac = alu.fecha_nacimiento
        anos = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
        meses = (hoy.year - nac.year) * 12 + hoy.month - nac.month
        meses_totales = meses
        edad_str = f"{anos} años"

    # Organizar Tutores (Mamá / Papá)
    mama = {}
    papa = {}
    
    for t in alu.tutores:
        # Lógica simple para distinguir, puedes mejorarla según tu campo 'relacion'
        # Aquí asumimos que si el nombre termina en 'a' es mujer (muy básico, mejor usar campo género o relación)
        # O simplemente enviamos tutor 1 y tutor 2
        datos_tutor = {
            "nombre": f"{t.nombres} {t.apellidos}",
            "ci": f"{t.ci_numero} {t.ci_expedido or ''}",
            "celular": t.celular,
            "email": t.email,
            "profesion": t.profesion,
            "lugar_trabajo": t.lugar_trabajo,
            "direccion_trabajo": t.direccion, # Usamos dirección como dirección trabajo
            "horario": "08:00 - 18:00" # Placeholder o campo real si existe
        }
        # Asignar a mamá o papá según orden o lógica
        if not mama: mama = datos_tutor
        else: papa = datos_tutor

    return {
        "alumno": {
            "nombre_completo": alu.nombres_completos,
            "fecha_nacimiento": alu.fecha_nacimiento.strftime("%d/%m/%Y") if alu.fecha_nacimiento else "-",
            "edad_texto": edad_str,
            "edad_meses": meses_totales,
            "foto_url": alu.foto_url,
            "direccion": alu.direccion_domicilio,
            "telefono_fijo": "--", # Agregar a modelo si falta
            "celulares": f"{mama.get('celular', '')} / {papa.get('celular', '')}"
        },
        "mama": mama,
        "papa": papa,
        "emergencia": {
            "nombre": alu.contacto_emergencia_nombre,
            "parentesco": "--", 
            "telefono": "--" # Ajustar si tienes el campo
        },
        "recojo": {
            "nombre": alu.familiares_autorizados_recogo,
            "parentesco": "--",
            "telefono": "--"
        }
    }


# ============================================================
# ASIGNACIÓN ACADÉMICA (GRUPO, PARALELO, TURNO)
# ============================================================



@web_router.post("/api/v1/inscripciones/{alumno_id}/asignacion", tags=["Inscripciones"])
async def guardar_asignacion_alumno(
    alumno_id: int,
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    data = await request.json()
    
    nuevo_paralelo_id = int(data.get('paralelo_id')) if data.get('paralelo_id') else None
    nuevo_turno_id = int(data.get('turno_id')) if data.get('turno_id') else None
    
    try:
        # --- CORRECCIÓN: Eliminamos 'async with db.begin():' para evitar doble transacción ---
        
        # 1. Actualizar Turno en Alumno
        alumno = await db.get(Alumno, alumno_id)
        if not alumno: raise HTTPException(404, "Alumno no encontrado")
        
        alumno.turno_id = nuevo_turno_id
        
        # 2. Gestionar Paralelo (Historial)
        if nuevo_paralelo_id:
            # A) Desactivar asignaciones anteriores
            stmt_update = (
                update(AlumnoParalelo)
                .where(AlumnoParalelo.alumno_id == alumno_id)
                .where(AlumnoParalelo.activo == True)
                .values(activo=False)
            )
            await db.execute(stmt_update)
            
            # B) Crear nueva asignación
            nueva_asignacion = AlumnoParalelo(
                alumno_id=alumno_id,
                paralelo_id=nuevo_paralelo_id,
                fecha_asignacion=datetime.now().date(),
                activo=True
            )
            db.add(nueva_asignacion)
            
        # 3. Confirmar cambios manualmente
        await db.commit()
        return {"success": True, "mensaje": "Asignación guardada correctamente"}

    except Exception as e:
        await db.rollback()
        print(f"Error asignando curso: {e}")
        # Si es HTTPException lo relanzamos tal cual
        if isinstance(e, HTTPException): raise e
        raise HTTPException(500, detail=f"Error interno: {str(e)}")

# ============================================================
# ACCIONES: DESACTIVAR Y EXPORTAR (Directo)
# ============================================================

@web_router.patch("/api/v1/inscripciones/{alumno_id}/desactivar", tags=["Inscripciones"])
async def desactivar_alumno_endpoint(
    alumno_id: int, 
    user = Depends(get_current_user_optional), 
    db: AsyncSession = Depends(get_session)
):
    """Cambia el estado a 'baja' (Desactivar)"""
    if not user: raise HTTPException(401)
    
    try:
        # --- CORRECCIÓN: Quitamos 'async with db.begin():' ---
        
        stmt = select(Alumno).where(Alumno.id == alumno_id)
        res = await db.execute(stmt)
        alumno = res.scalars().first()
        
        if not alumno:
            raise HTTPException(404, "Alumno no encontrado")
            
        alumno.estado = 'baja' 
        alumno.fecha_baja = datetime.now().date()
        
        # Confirmamos manualmente
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        print(f"Error desactivando alumno: {e}")
        # Si ya es HTTPException, la relanzamos
        if isinstance(e, HTTPException): raise e
        raise HTTPException(500, detail=str(e))
        
    return {"success": True, "mensaje": "Alumno dado de baja correctamente"}
@web_router.get("/api/v1/exportaciones/inscripciones/excel", tags=["Inscripciones"])
async def exportar_inscripciones_excel(user = Depends(get_current_user_optional), db: AsyncSession = Depends(get_session)):
    if not user: raise HTTPException(401)
    
    stmt = select(Alumno).where(Alumno.sede_id == user.sede_id).order_by(Alumno.apellido_paterno)
    alumnos = (await db.execute(stmt)).scalars().all()
    
    output = io.StringIO()
    # Escribir BOM para que Excel reconozca UTF-8 (Tildes y Ñ)
    output.write('\ufeff') 
    writer = csv.writer(output, delimiter=';')
    
    writer.writerow(['ID', 'Código', 'Nombres', 'Apellidos', 'Grupo', 'Paralelo', 'Turno', 'Tutor' 'Estado', 'Fecha Nacimiento'])
    for a in alumnos:
        writer.writerow([
            a.id, a.codigo_unico, a.nombre, f"{a.apellido_paterno} {a.apellido_materno or ''}",
            a.estado, a.fecha_nacimiento
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=inscripciones_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

@web_router.get("/api/v1/exportaciones/inscripciones/pdf", response_class=HTMLResponse, tags=["Inscripciones"])
async def exportar_inscripciones_pdf_view(request: Request, user = Depends(get_current_user_optional), db: AsyncSession = Depends(get_session)):
    """Genera una vista HTML limpia lista para Imprimir a PDF"""
    if not user: return RedirectResponse("/login")
    
    stmt = select(Alumno).where(Alumno.sede_id == user.sede_id).order_by(Alumno.apellido_paterno)
    alumnos = (await db.execute(stmt)).scalars().all()
    
    # HTML simple para imprimir
    html_content = f"""
    <html>
    <head>
        <title>Reporte de Inscripciones</title>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            h1 {{ text-align: center; color: #333; }}
            .header {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="header">
            <h1>Reporte de Alumnos - {settings.app_name}</h1>
            <p>Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p>Total Registros: {len(alumnos)}</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Código</th>
                    <th>Apellidos</th>
                    <th>Nombres</th>
                    <th>Estado</th>
                    <th>Fecha Nac.</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td>{a.codigo_unico}</td><td>{a.apellido_paterno} {a.apellido_materno or ''}</td><td>{a.nombre}</td><td>{a.estado}</td><td>{a.fecha_nacimiento}</td></tr>" for a in alumnos])}
            </tbody>
        </table>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ============================================================
# PRE-INSCRIPCIÓN REAL
# ============================================================





@web_router.post("/api/v1/inscripciones/preinscripcion", tags=["Inscripciones"])
async def crear_preinscripcion_endpoint(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user:
        raise HTTPException(status_code=401, detail="No autorizado")

    data = await request.json()
    
    # Generar código único interno para el alumno
    codigo_unico_alumno = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Helper para reutilizar la sesión de FastAPI en el UoW
    @asynccontextmanager
    async def session_wrapper():
        yield db

    try:
        uow = UnitOfWork(session_factory=session_wrapper)
        
        async with uow:
            # 1. Obtener ID del Rol "TUTOR"
            stmt_rol = select(Rol).where(Rol.nombre.ilike("TUTOR"))
            res_rol = await uow.session.execute(stmt_rol) 
            rol_tutor_obj = res_rol.scalars().first()
            rol_id = rol_tutor_obj.id if rol_tutor_obj else 2

            # --- NUEVA LÓGICA: SEPARAR APELLIDOS ---
            raw_apellidos = data.get('apellidos', '').strip()
            partes_apellido = raw_apellidos.split() # Separa por espacios
            
            if not partes_apellido:
                paterno = "-"
                materno = None
            elif len(partes_apellido) == 1:
                paterno = partes_apellido[0]
                materno = None
            else:
                paterno = partes_apellido[0] # El primero es paterno
                materno = ' '.join(partes_apellido[1:]) # El resto es materno
            # ---------------------------------------

            # A. Crear Alumno
            nuevo_alumno = Alumno(
                nombre=data.get('nombres'),
                apellido_paterno=paterno, # <--- USAMOS EL DATO SEPARADO
                apellido_materno=materno, # <--- USAMOS EL DATO SEPARADO
                fecha_nacimiento=datetime.strptime(data.get('fecha_nacimiento'), "%Y-%m-%d").date(),
                genero=data.get('genero'),
                sede_id=user.sede_id,
                codigo_unico=codigo_unico_alumno,
                estado='preinscrito',
                nombres_completos=f"{data.get('nombres')} {raw_apellidos}",
                creado_por_id=user.id,
            )
            uow.alumnos.add(nuevo_alumno)
            await uow.session.flush()

            # B. Generar Código de Acceso
            caso_uso = GenerarCodigo(uow)
            
            grupo_id = data.get('grupo')
            obs_texto = f"Tutor: {data.get('tutor_nombre')} ({data.get('tutor_parentesco')}) - Tel: {data.get('tutor_telefono')}"
            if grupo_id:
                obs_texto += f" - Grupo Pre-seleccionado ID: {grupo_id}"

            req_codigo = GenerarCodigoRequest(
                sede_id=user.sede_id,
                rol_id=rol_id,
                alumno_id=nuevo_alumno.id,
                max_cuentas=2,
                whatsapp_numero=data.get('tutor_telefono'),
                observaciones=obs_texto,
                creado_por=user.id
            )
            
            resp_codigo = await caso_uso.execute(req_codigo)
            
            # C. Confirmar todo
            # El caso de uso llama a uow.commit() internamente
            
            return {
                "success": True,
                "codigo_tutor": resp_codigo.codigo, # <--- ESTO ES LO QUE EL JS RECIBE
                "alumno_id": nuevo_alumno.id,
                "mensaje": "Pre-inscripción creada exitosamente"
            }

    except Exception as e:
        print(f"Error Pre-inscripción: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# API ENDPOINTS: LISTADOS COMPLETOS (CRUD)
# ============================================================

# ============================================================
# API GRUPOS (CRUD COMPLETO)
# ============================================================

@web_router.get("/api/v1/grupos", tags=["Academico"])
async def listar_grupos_endpoint(
    search: str = "",
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Retorna lista completa para Tablas y Selects"""
    if not user: return {"items": []}
    
    # Traer todos los campos necesarios
    stmt = select(Grupo).where(Grupo.sede_id == user.sede_id).order_by(desc(Grupo.activo), Grupo.nombre)
    
    if search:
        stmt = stmt.where(Grupo.nombre.ilike(f"%{search}%"))
        
    result = await db.execute(stmt)
    grupos = result.scalars().all()
    
    return {
        "items": [
            {
                "id": g.id,
                "nombre": g.nombre,
                "gestion": g.gestion,
                "activo": g.activo,
                "creado_en": g.creado_en.strftime("%Y-%m-%d") if g.creado_en else ""
            } for g in grupos
        ]
    }

@web_router.get("/api/v1/grupos/{grupo_id}", tags=["Academico"])
async def obtener_grupo_endpoint(
    grupo_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    grupo = await db.get(Grupo, grupo_id)
    if not grupo or grupo.sede_id != user.sede_id:
        raise HTTPException(404, "Grupo no encontrado")
    
    return {
        "id": grupo.id,
        "nombre": grupo.nombre,
        "gestion": grupo.gestion,
        "activo": grupo.activo
    }

@web_router.put("/api/v1/grupos/{grupo_id}", tags=["Academico"])
async def actualizar_grupo_endpoint(
    grupo_id: int,
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    data = await request.json()
    
    try:
        # --- CORRECCIÓN: Eliminado 'async with db.begin():' ---
        grupo = await db.get(Grupo, grupo_id)
        
        # Validación de seguridad: el grupo debe pertenecer a la sede del usuario
        if not grupo or grupo.sede_id != user.sede_id:
            raise HTTPException(404, "Grupo no encontrado")
            
        grupo.nombre = data.get('nombre')
        grupo.gestion = data.get('gestion')
        grupo.activo = bool(data.get('activo'))
        
        # Confirmar cambios manualmente
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        # Si ya es un error HTTP, lo relanzamos
        if isinstance(e, HTTPException): raise e
        raise HTTPException(500, detail=str(e))
        
    return {"success": True, "mensaje": "Grupo actualizado correctamente"}

@web_router.get("/api/v1/paralelos", tags=["Academico"])
async def listar_paralelos_endpoint(
    page: int = 1, 
    per_page: int = 10, 
    search: str = "",
    grupo_id: int = None, # <--- NUEVO PARÁMETRO
    user = Depends(get_current_user_optional), 
    db: AsyncSession = Depends(get_session)
):
    if not user: return {"items": [], "total": 0}
    
    # Query Base
    stmt = select(Paralelo).options(selectinload(Paralelo.grupo)).where(Paralelo.sede_id == user.sede_id).order_by(Paralelo.grupo_id, Paralelo.letra)
    
    # Filtro eficiente por ID de Grupo (Directo a la BD)
    if grupo_id:
        stmt = stmt.where(Paralelo.grupo_id == grupo_id)

    # Filtro de búsqueda (Search)
    if search:
        stmt = stmt.join(Grupo).where(or_(
            Paralelo.letra.ilike(f"%{search}%"),
            Grupo.nombre.ilike(f"%{search}%")
        ))
        
    total = len((await db.execute(stmt)).scalars().all())
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    items = (await db.execute(stmt)).scalars().all()
    
    return {
        "items": [
            {
                "id": p.id,
                "letra": p.letra,
                "capacidad": p.capacidad,
                "grupo": p.grupo.nombre if p.grupo else "Sin Grupo",
                "grupo_id": p.grupo_id, # Enviamos el ID por si acaso
                "activo": p.activo
            } for p in items
        ],
        "total": total, "page": page, "per_page": per_page
    }

@web_router.get("/api/v1/paralelos/{paralelo_id}", tags=["Academico"])
async def obtener_paralelo_endpoint(
    paralelo_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    paralelo = await db.get(Paralelo, paralelo_id)
    if not paralelo or paralelo.sede_id != user.sede_id:
        raise HTTPException(404, "Paralelo no encontrado")
    
    return {
        "id": paralelo.id,
        "grupo_id": paralelo.grupo_id,
        "letra": paralelo.letra,
        "capacidad": paralelo.capacidad,
        "activo": paralelo.activo
    }

@web_router.put("/api/v1/paralelos/{paralelo_id}", tags=["Academico"])
async def actualizar_paralelo_endpoint(
    paralelo_id: int,
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    data = await request.json()
    
    try:
        # --- CORRECCIÓN ---
        paralelo = await db.get(Paralelo, paralelo_id)
        if not paralelo or paralelo.sede_id != user.sede_id:
            raise HTTPException(404, "Paralelo no encontrado")
            
        paralelo.grupo_id = int(data.get('grupo_id'))
        paralelo.letra = data.get('letra')
        paralelo.capacidad = int(data.get('capacidad'))
        paralelo.activo = bool(data.get('activo'))
        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(500, detail=str(e))
        
    return {"success": True, "mensaje": "Paralelo actualizado correctamente"}
# --- TURNOS ---
@web_router.get("/api/v1/turnos", tags=["Finanzas"])
async def listar_turnos_endpoint(
    page: int = 1, per_page: int = 10, search: str = "",
    user = Depends(get_current_user_optional), db: AsyncSession = Depends(get_session)
):
    if not user: return {"items": [], "total": 0}
    
    stmt = select(Turno).where(Turno.sede_id == user.sede_id).order_by(Turno.hora_inicio)
    
    if search:
        stmt = stmt.where(Turno.nombre.ilike(f"%{search}%"))
        
    total = len((await db.execute(stmt)).scalars().all())
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    items = (await db.execute(stmt)).scalars().all()
    
    return {
        "items": [
            {
                "id": t.id,
                "nombre": t.nombre,
                "hora_inicio": t.hora_inicio.strftime("%H:%M"),
                "hora_fin": t.hora_fin.strftime("%H:%M"),
                "activo": t.activo
            } for t in items
        ],
        "total": total
    }

@web_router.get("/api/v1/turnos/{turno_id}", tags=["Finanzas"])
async def obtener_turno_endpoint(
    turno_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    turno = await db.get(Turno, turno_id)
    if not turno or turno.sede_id != user.sede_id:
        raise HTTPException(404, "Turno no encontrado")
    
    return {
        "id": turno.id,
        "nombre": turno.nombre,
        "hora_inicio": turno.hora_inicio.strftime("%H:%M"),
        "hora_fin": turno.hora_fin.strftime("%H:%M"),
        "activo": turno.activo
    }

@web_router.put("/api/v1/turnos/{turno_id}", tags=["Finanzas"])
async def actualizar_turno_endpoint(
    turno_id: int,
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    data = await request.json()
    
    try:
        # --- CORRECCIÓN ---
        turno = await db.get(Turno, turno_id)
        if not turno or turno.sede_id != user.sede_id:
            raise HTTPException(404, "Turno no encontrado")
            
        turno.nombre = data.get('nombre')
        # Convertir hora string a objeto time
        turno.hora_inicio = datetime.strptime(data.get('hora_inicio'), '%H:%M').time()
        turno.hora_fin = datetime.strptime(data.get('hora_fin'), '%H:%M').time()
        turno.activo = bool(data.get('activo'))
        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException): raise e
        raise HTTPException(500, detail=str(e))
        
    return {"success": True, "mensaje": "Turno actualizado correctamente"}





# ============================================================
# DASHBOARD DEL TUTOR (PROTEGIDO)
# ============================================================

@web_router.get("/tutor/dashboard", response_class=HTMLResponse, name="tutor_dashboard")
async def tutor_dashboard_page(request: Request, user = Depends(get_current_user_optional)):
    """Dashboard del tutor (requiere autenticación)"""
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    # Verificar que sea un tutor
    if user.role not in ['TUTOR', 'SUPERADMIN']:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return templates.TemplateResponse("tutores/dashboard.html", {
        "request": request,
        "current_user": user,
        "page_title": f"Mi Dashboard - {settings.app_name}",
        "active_menu": "dashboard"
    })




# ============================================================
# 📬 API COMUNICACIONES (REAL & CORREGIDO)
# ============================================================

# ============================================================
# VISTA HTML: COMUNICACIONES
# ============================================================

@web_router.get("/comunicaciones", response_class=HTMLResponse, name="comunicaciones")
async def comunicaciones_page(request: Request, user = Depends(get_current_user_optional)):
    """Página principal del módulo de comunicaciones"""
    
    # 1. Verificar sesión
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    # 2. Renderizar el template
    # Asegúrate de que el archivo index.html que subiste esté en:
    # templates/comunicaciones/index.html
    return templates.TemplateResponse("comunicaciones/index.html", {
        "request": request,
        "current_user": user,
        "page_title": f"Comunicaciones - {settings.app_name}",
        "active_menu": "comunicaciones" # Para resaltar el menú lateral
    })

# --- 1. LISTAR CONVERSACIONES (Bandeja de Entrada) ---
@web_router.get("/api/v1/comunicaciones/conversaciones", tags=["Comunicaciones"])
async def listar_conversaciones_real(
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)

    # 1. Obtener IDs de conversaciones donde participo
    subq_mis_convs = select(ConversacionParticipante.conversacion_id).where(
        ConversacionParticipante.usuario_id == user.id
    )

    # 2. Consultar conversaciones activas
    stmt = select(Conversacion).options(
        selectinload(Conversacion.participantes).selectinload(ConversacionParticipante.usuario),
        selectinload(Conversacion.mensajes)
    ).where(
        Conversacion.id.in_(subq_mis_convs),
        Conversacion.cerrado == False
    ).order_by(desc(Conversacion.ultima_actividad_en))

    result = await db.execute(stmt)
    conversaciones = result.scalars().all()

    items = []
    for conv in conversaciones:
        # Determinar Nombre e Imagen
        titulo = conv.titulo
        foto_url = None
        # avatar = None # (Implementar si tienes campo avatar)
        
        if conv.tipo == TipoConversacion.directo:
            otro = next((p.usuario for p in conv.participantes if p.usuario_id != user.id), None)
            if otro:
                titulo = f"{otro.nombres} {otro.apellidos or ''}".strip()
                foto_url = otro.foto_perfil_url
            else:
                titulo = "Chat Personal"
                foto_url = user.foto_perfil_url
        
        # --- NUEVA VALIDACIÓN DE SEGURIDAD (BACKEND) ---
        # Si la "foto" son solo iniciales (ej: "CP") o texto corto sin formato de ruta, lo descartamos.
        if foto_url and (len(foto_url) < 5 or "/" not in foto_url):
            foto_url = None
        
        # Último mensaje
        ultimo_msg = "Sin mensajes"
        fecha_msg = conv.ultima_actividad_en
        
        # Ordenar mensajes en memoria (o hacer subquery para optimizar)
        msgs_ordenados = sorted(conv.mensajes, key=lambda m: m.enviado_en, reverse=True)
        if msgs_ordenados:
            ultimo_msg = msgs_ordenados[0].contenido
            fecha_msg = msgs_ordenados[0].enviado_en

        # Contar no leídos (Simplificado: Mensajes que no son míos)
        # TODO: Cruzar con tabla MensajeLeido para precisión exacta
        no_leidos = 0 

        items.append({
            "id": conv.id,
            "usuario_nombre": titulo,
            "usuario_avatar": foto_url,
            "usuario_rol": "Participante", 
            "ultimo_mensaje": ultimo_msg[:50],
            "ultimo_mensaje_fecha": fecha_msg.isoformat(),
            "no_leidos": no_leidos
        })

    return {"items": items}

# --- ENDPOINT FALTANTE: BANDEJA DE ENTRADA (SOLUCIONA ERROR 405) ---
@web_router.get("/api/v1/comunicaciones/mensajes", tags=["Comunicaciones"])
async def listar_mensajes_inbox(
    filter: str = "all",
    page: int = 1,
    per_page: int = 20,
    search: str = "",
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Bandeja de entrada de mensajes individuales"""
    if not user: raise HTTPException(401)

    # 1. Buscar mensajes donde participo
    # (Simplificado: Traemos mensajes de mis conversaciones)
    subq_mis_convs = select(ConversacionParticipante.conversacion_id).where(
        ConversacionParticipante.usuario_id == user.id
    )

    stmt = (
        select(Mensaje, Conversacion.asunto, Usuario.nombres, Usuario.apellidos, MensajeLeido.leido_en)
        .join(Conversacion, Mensaje.conversacion_id == Conversacion.id)
        .join(Usuario, Mensaje.remitente_id == Usuario.id)
        .outerjoin(MensajeLeido, and_(
            MensajeLeido.mensaje_id == Mensaje.id,
            MensajeLeido.usuario_id == user.id
        ))
        .where(Mensaje.conversacion_id.in_(subq_mis_convs))
        .order_by(desc(Mensaje.enviado_en))
    )

    if search:
        stmt = stmt.where(Mensaje.contenido.ilike(f"%{search}%"))

    # Paginación manual simple
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for row in rows:
        msg, asunto, nom, ape, leido_fecha = row
        
        # Es mío?
        es_mio = (msg.remitente_id == user.id)
        
        # Está leído? (Si es mío, siempre es true. Si no, ver fecha lectura)
        leido = True if es_mio else (leido_fecha is not None)

        items.append({
            "id": msg.id,
            "asunto": asunto,
            "mensaje": msg.contenido,
            "emisor_nombre": f"{nom} {ape or ''}".strip(),
            "emisor_id": msg.remitente_id,
            "prioridad": "NORMAL",
            "fecha_envio": msg.enviado_en.isoformat(),
            "leido": leido,
            "es_mio": es_mio
        })

    return {
        "items": items,
        "total": 100, # TODO: Implementar count real si deseas
        "pagination": {"current_page": page, "total_pages": 5}
    }

# --- 2. DETALLE DE CONVERSACIÓN ---
@web_router.get("/api/v1/comunicaciones/conversaciones/{conv_id}", tags=["Comunicaciones"])
async def get_conversacion_detalle(
    conv_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    
    stmt = select(Conversacion).options(
        selectinload(Conversacion.participantes).selectinload(ConversacionParticipante.usuario)
    ).where(Conversacion.id == conv_id)
    
    conv = (await db.execute(stmt)).scalars().first()
    if not conv: raise HTTPException(404)
    
    if not any(p.usuario_id == user.id for p in conv.participantes):
        raise HTTPException(403, "No perteneces a este chat")

    titulo = conv.titulo
    foto_url = None
    if conv.tipo == TipoConversacion.directo:
        # Buscamos al "otro" participante
        otro = next((p.usuario for p in conv.participantes if p.usuario_id != user.id), None)
        
        if otro:
            # CASO 1: Chat con otra persona
            titulo = f"{otro.nombres} {otro.apellidos or ''}".strip()
            foto_url = otro.foto_perfil_url
        else:
            # CASO 2: Chat Personal (conmigo mismo)
            # Aquí 'otro' es None, por eso fallaba antes al intentar leer otro.nombres
            titulo = f"{user.nombres} {user.apellidos or ''} (Tú)".strip()
            foto_url = user.foto_perfil_url

    # Validación de seguridad (Igual que en la lista)
    if foto_url and (len(foto_url) < 5 or "/" not in foto_url):
        foto_url = None


    return {
        "id": conv.id,
        "usuario_nombre": titulo,
        "usuario_avatar": foto_url,
        "usuario_rol": "Miembro" if conv.tipo == TipoConversacion.grupo else "",
        "tipo": conv.tipo.value
    }

# --- 3. LISTAR MENSAJES ---
@web_router.get("/api/v1/comunicaciones/conversaciones/{conv_id}/mensajes", tags=["Comunicaciones"])
async def listar_mensajes_chat(
    conv_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)

    stmt = select(Mensaje).options(selectinload(Mensaje.remitente)).where(
        Mensaje.conversacion_id == conv_id
    ).order_by(Mensaje.enviado_en.asc())
    
    msgs = (await db.execute(stmt)).scalars().all()
    
    items = []
    for m in msgs:
        items.append({
            "id": m.id,
            "contenido": m.contenido,
            "emisor_id": m.remitente_id,
            "emisor_nombre": f"{m.remitente.nombres} {m.remitente.apellidos or ''}".strip(),
            "fecha_envio": m.enviado_en.isoformat(),
            "es_mio": (m.remitente_id == user.id),
            "leido": True # TODO: Chequear MensajeLeido
        })
        
    return {"items": items}

# --- 4. ENVIAR MENSAJE (CHAT EXISTENTE) ---
@web_router.post("/api/v1/comunicaciones/conversaciones/{conv_id}/mensajes", tags=["Comunicaciones"])
async def enviar_mensaje_chat(
    conv_id: int,
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    data = await request.json()
    contenido = data.get("contenido")
    if not contenido: raise HTTPException(400, "Mensaje vacío")

    # A. Guardar en BD
    nuevo_msg = Mensaje(
        conversacion_id=conv_id,
        remitente_id=user.id,
        contenido=contenido,
        tipo=TipoMensaje.texto
    )
    db.add(nuevo_msg)
    
    stmt_update = update(Conversacion).where(Conversacion.id == conv_id).values(ultima_actividad_en=func.now())
    await db.execute(stmt_update)
    
    await db.commit()
    await db.refresh(nuevo_msg)

    # B. Notificar WS (CORREGIDO PARA USAR CLASES PYDANTIC)
    stmt_part = select(ConversacionParticipante.usuario_id).where(ConversacionParticipante.conversacion_id == conv_id)
    participantes_ids = (await db.execute(stmt_part)).scalars().all()

    # 1. Crear el Payload tipado
    payload_data = WSChatMessagePayload(
        mensaje_id=nuevo_msg.id,
        conversacion_id=conv_id,
        remitente_id=user.id,
        texto=contenido,
        enviado_en=nuevo_msg.enviado_en.isoformat()
    )
    
    # 2. Crear el Evento Wrapper
    event = WSBaseEvent(
        type=WSEventType.CHAT_MESSAGE_NEW,
        data=payload_data.model_dump()
    )

    # 3. Enviar el OBJETO (no dict) al manager
    for pid in participantes_ids:
        await ws_manager.send_to_user(pid, event)

    return {"success": True}

# --- 5. CREAR NUEVO MENSAJE (MODAL) ---
@web_router.post("/api/v1/comunicaciones/mensajes", tags=["Comunicaciones"])
async def crear_conversacion_mensaje(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    data = await request.json()
    destinatarios = data.get("destinatarios", []) 
    asunto = data.get("asunto", "Sin asunto")
    contenido = data.get("mensaje", "")
    
    if not destinatarios or not contenido:
        raise HTTPException(400, "Faltan datos")

    conv_id = None

    # Reutilizar chat directo si es 1 a 1
    if len(destinatarios) == 1:
        target_id = int(destinatarios[0])
        stmt = select(Conversacion).join(ConversacionParticipante).where(
            Conversacion.tipo == TipoConversacion.directo,
            ConversacionParticipante.usuario_id == user.id
        )
        mis_directos = (await db.execute(stmt)).scalars().all()
        
        for c in mis_directos:
            subq = select(ConversacionParticipante).where(
                ConversacionParticipante.conversacion_id == c.id,
                ConversacionParticipante.usuario_id == target_id
            )
            if (await db.execute(subq)).scalars().first():
                conv_id = c.id
                break
    
    # Crear nueva si no existe
    if not conv_id:
        tipo = TipoConversacion.grupo if len(destinatarios) > 1 else TipoConversacion.directo
        titulo_chat = asunto if tipo == TipoConversacion.grupo else None
        
        nueva_conv = Conversacion(
            sede_id=user.sede_id,
            creado_por_id=user.id,
            titulo=titulo_chat,
            asunto=asunto,
            tipo=tipo
        )
        db.add(nueva_conv)
        await db.flush()
        conv_id = nueva_conv.id
        
        parts = set(destinatarios)
        parts.add(user.id)
        
        for pid in parts:
            db.add(ConversacionParticipante(conversacion_id=conv_id, usuario_id=pid, rol="miembro"))

    nuevo_msg = Mensaje(
        conversacion_id=conv_id,
        remitente_id=user.id,
        contenido=contenido,
        tipo=TipoMensaje.texto
    )
    db.add(nuevo_msg)
    
    # Actualizar fecha actividad
    await db.execute(update(Conversacion).where(Conversacion.id == conv_id).values(ultima_actividad_en=func.now()))
    
    await db.commit()
    await db.refresh(nuevo_msg)
    
    # Notificar WS (Misma lógica corregida)
    stmt_part = select(ConversacionParticipante.usuario_id).where(ConversacionParticipante.conversacion_id == conv_id)
    participantes_ids = (await db.execute(stmt_part)).scalars().all()

    payload_data = WSChatMessagePayload(
        mensaje_id=nuevo_msg.id,
        conversacion_id=conv_id,
        remitente_id=user.id,
        texto=contenido,
        enviado_en=nuevo_msg.enviado_en.isoformat()
    )
    event = WSBaseEvent(type=WSEventType.CHAT_MESSAGE_NEW, data=payload_data.model_dump())

    for pid in participantes_ids:
        await ws_manager.send_to_user(pid, event)

    return {"success": True, "conversacion_id": conv_id}

# --- 6. ENDPOINTS FALTANTES (LEER / ARCHIVAR) ---

@web_router.patch("/api/v1/comunicaciones/mensajes/{mensaje_id}/leer", tags=["Comunicaciones"])
async def marcar_mensaje_leido(
    mensaje_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Marca un mensaje específico como leído"""
    if not user: raise HTTPException(401)
    
    # Verificar si ya existe la lectura
    stmt = select(MensajeLeido).where(
        MensajeLeido.mensaje_id == mensaje_id,
        MensajeLeido.usuario_id == user.id
    )
    existe = (await db.execute(stmt)).scalars().first()
    
    if not existe:
        nuevo = MensajeLeido(mensaje_id=mensaje_id, usuario_id=user.id)
        db.add(nuevo)
        await db.commit()
        
    return {"success": True}

@web_router.patch("/api/v1/comunicaciones/conversaciones/{conv_id}/marcar-leido", tags=["Comunicaciones"])
async def marcar_conversacion_leida(
    conv_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Marca todos los mensajes de una conversación como leídos"""
    if not user: raise HTTPException(401)
    
    # Lógica simplificada: Insertar lecturas para mensajes no leídos
    # (Para producción: usar una query INSERT ... SELECT left join)
    return {"success": True} 

@web_router.patch("/api/v1/comunicaciones/conversaciones/{conv_id}/archivar", tags=["Comunicaciones"])
async def archivar_conversacion(
    conv_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Archiva una conversación (Soft delete o flag)"""
    if not user: raise HTTPException(401)
    
    # Si la tabla conversaciones_participantes tuviera campo 'archivado', lo actualizamos ahí.
    # Por ahora, simulamos éxito.
    return {"success": True}

# --- 7. COMUNICADOS & NOTIFICACIONES ---

@web_router.get("/api/v1/comunicaciones/comunicados", tags=["Comunicaciones"])
async def listar_comunicados(user = Depends(get_current_user_optional), db: AsyncSession = Depends(get_session)):
    if not user: raise HTTPException(401)
    
    stmt = select(Notificacion).where(Notificacion.usuario_id == user.id).order_by(desc(Notificacion.creado_en))
    result = (await db.execute(stmt)).scalars().all()
    
    items = []
    for n in result:
        items.append({
            "id": n.id,
            "titulo": n.titulo,
            "contenido": n.cuerpo,
            "tipo": n.tipo or "INFORMATIVO",
            "fecha_publicacion": n.creado_en.isoformat(),
            "autor_nombre": "Sistema",
            "vigencia_hasta": None
        })
    return {"items": items}

@web_router.post("/api/v1/comunicaciones/comunicados", tags=["Comunicaciones"])
async def crear_comunicado(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    data = await request.json()
    titulo = data.get("titulo")
    contenido = data.get("contenido")
    tipo = data.get("tipo", "INFORMATIVO")
    
    # Enviar a TODOS los usuarios de la sede
    stmt = select(Usuario.id).where(Usuario.sede_id == user.sede_id, Usuario.activo == True)
    usuarios_ids = (await db.execute(stmt)).scalars().all()
    
    notificaciones = []
    for uid in usuarios_ids:
        n = Notificacion(
            usuario_id=uid,
            titulo=titulo,
            cuerpo=contenido,
            tipo=tipo,
            canal=CanalNotificacion.app,
            prioridad=PrioridadNotificacion.media
        )
        db.add(n)
        notificaciones.append(n)
        
    await db.commit()
    
    # Notificar WebSocket (Masivo)
    for n in notificaciones:
        payload_data = WSNotificationNewPayload(
            notificacion_id=n.id,
            titulo=n.titulo,
            mensaje=n.cuerpo,
            tipo=n.tipo,
            creado_en=n.creado_en.isoformat() if n.creado_en else "",
            leida=False,
            sede_id=user.sede_id
        )
        event = WSBaseEvent(type=WSEventType.NOTIFICATION_NEW, data=payload_data.model_dump())
        await ws_manager.send_to_user(n.usuario_id, event)

    return {"success": True, "count": len(usuarios_ids)}

# Helper simple
def get_initials(name):
    if not name: return "??"
    parts = name.split()
    if len(parts) >= 2: return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper()


# ============================================================
# 🔔 NOTIFICACIONES (SOLUCIÓN ERRORES 404 Y NUEVO MODAL)
# ============================================================

@web_router.get("/api/v1/notificaciones", tags=["Comunicaciones"])
async def listar_notificaciones_usuario(
    leida: bool | None = None,
    page: int = 1, 
    per_page: int = 20,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Lista las notificaciones DEL USUARIO ACTUAL.
    Soluciona el error 404 que tienes en consola.
    """
    if not user: raise HTTPException(401)

    stmt = select(Notificacion).where(Notificacion.usuario_id == user.id)

    # Filtro ?leida=false
    if leida is False:
        stmt = stmt.where(Notificacion.leido_en.is_(None))
    elif leida is True:
        stmt = stmt.where(Notificacion.leido_en.is_not(None))

    # Ordenar por fecha (más recientes primero)
    stmt = stmt.order_by(desc(Notificacion.creado_en))

    # Total para paginación (simple)
    total = 0 # Puedes implementar count real si quieres
    
    # Paginación
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    notificaciones = result.scalars().all()

    items = []
    for n in notificaciones:
        items.append({
            "id": n.id,
            "titulo": n.titulo,
            "mensaje": n.cuerpo,
            "tipo": n.tipo, # PAGO, ACADEMICO, etc.
            "leida": n.leido_en is not None,
            "fecha_creacion": n.creado_en.isoformat(),
            "prioridad": n.prioridad.value if hasattr(n.prioridad, 'value') else "media"
        })

    # Calcular total no leídas para el badge
    stmt_count = select(func.count(Notificacion.id)).where(
        Notificacion.usuario_id == user.id,
        Notificacion.leido_en.is_(None)
    )
    total_no_leidas = await db.scalar(stmt_count)

    return {
        "items": items,
        "total": total_no_leidas, # Usado para el badge
        "page": page,
        "per_page": per_page
    }

@web_router.patch("/api/v1/notificaciones/{notif_id}/leer", tags=["Comunicaciones"])
async def marcar_notificacion_leida(
    notif_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Marca una notificación como leída"""
    if not user: raise HTTPException(401)
    
    notif = await db.get(Notificacion, notif_id)
    if not notif or notif.usuario_id != user.id:
        raise HTTPException(404, "Notificación no encontrada")
    
    if not notif.leido_en:
        notif.leido_en = datetime.now()
        await db.commit()
        
    return {"success": True}

@web_router.post("/api/v1/notificaciones/enviar", tags=["Comunicaciones"])
async def enviar_notificacion_masiva(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Endpoint para el NUEVO MODAL.
    Crea notificaciones para múltiples usuarios seleccionados.
    """
    if not user: raise HTTPException(401)
    
    data = await request.json()
    destinatarios = data.get("destinatarios", []) # Lista de IDs
    titulo = data.get("titulo")
    mensaje = data.get("mensaje")
    tipo = data.get("tipo", "SISTEMA") # INFO, ALERTA, etc.
    prioridad_str = data.get("prioridad", "media").lower()
    
    if not destinatarios or not titulo or not mensaje:
        raise HTTPException(400, "Faltan datos requeridos")

    # Mapear prioridad
    prioridad_map = {
        "baja": PrioridadNotificacion.baja,
        "media": PrioridadNotificacion.media,
        "alta": PrioridadNotificacion.alta
    }
    prioridad_enum = prioridad_map.get(prioridad_str, PrioridadNotificacion.media)

    notificaciones_creadas = []

    try:
        for uid in destinatarios:
            nueva_notif = Notificacion(
                usuario_id=uid,
                titulo=titulo,
                cuerpo=mensaje,
                tipo=tipo,
                prioridad=prioridad_enum,
                canal=CanalNotificacion.app,
                creado_en=datetime.now()
            )
            db.add(nueva_notif)
            notificaciones_creadas.append(nueva_notif) # Guardamos ref para WS
        
        await db.commit()

        # Enviar WebSocket a cada usuario
        for n in notificaciones_creadas:
            payload = WSNotificationNewPayload(
                notificacion_id=n.id,
                titulo=n.titulo,
                mensaje=n.cuerpo,
                tipo=n.tipo,
                creado_en=n.creado_en.isoformat(),
                leida=False,
                sede_id=user.sede_id
            )
            # Construir evento usando el helper de events.py
            # Nota: Asegúrate de importar build_notification_new_event arriba
            from app.infrastructure.ws.events import build_notification_new_event 
            event = build_notification_new_event(payload)
            
            await ws_manager.send_to_user(n.usuario_id, event)

        return {"success": True, "enviados": len(destinatarios)}

    except Exception as e:
        await db.rollback()
        print(f"Error enviando notificaciones: {e}")
        raise HTTPException(500, str(e))

# ============================================================
# WEBSOCKET UNIFICADO (CHAT + NOTIFICACIONES)
# ============================================================

# Escuchamos en ambas rutas para compatibilidad con main.js y comunicaciones.js
@web_router.websocket("/api/v1/ws/chat")
@web_router.websocket("/api/v1/ws/notifications")
async def websocket_unified_endpoint(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_session)
):
    """
    Endpoint único para WebSockets. 
    Maneja tanto el chat como las notificaciones globales.
    Soporta autenticación por Cookie (seguro) y por URL (legacy main.js).
    """
    # 1. Autenticación Híbrida
    # Primero intentamos leer cookie segura (comunicaciones.js)
    token = websocket.cookies.get("access_token") or websocket.cookies.get("accesstoken")
    
    # Si no hay cookie, intentamos leer de la URL ?token=... (main.js)
    if not token:
        token = websocket.query_params.get("token") 

    user = None
    if token:
        try:
            token_service = PyJWTTokenService()
            payload = token_service.decode_token(token)
            user_id = int(payload.get("sub"))
            
            repo = UsuariosRepository(db)
            user = await repo.get_by_id(user_id)
        except Exception as e:
            print(f"⚠️ WS Auth Error: {e}")

    # Si falló la autenticación, cerramos con código 1008 (Policy Violation)
    if not user:
        await websocket.close(code=1008)
        return

    # 2. Conectar al Manager Global
    # El manager agrupa por ID de usuario, así que no importa si vienes
    # de /chat o /notifications, te trata como el mismo usuario.
    info = ConnectionInfo(user_id=user.id, sede_id=user.sede_id)
    await ws_manager.connect(info, websocket)

    # En routes.py -> websocket_unified_endpoint

    try:
        while True:
            # 3. Escuchar mensajes del cliente
            try:
                data = await websocket.receive_json()
                msg_type = data.get('type')
                
                # Manejo de "Escribiendo..." (Typing)
                if msg_type == 'typing':
                    target_user_id = data.get('target_user_id')
                    if target_user_id:
                        # CORRECCIÓN: Enviar objeto WSBaseEvent, no diccionario
                        event = WSBaseEvent(
                            type=WSEventType.CHAT_TYPING,
                            data={
                                "conversation_id": data.get('conversation_id'),
                                "user_id": user.id,
                                "user_name": f"{user.nombres} {user.apellidos or ''}".strip()
                            }
                        )
                        await ws_manager.send_to_user(target_user_id, event)
                
                elif msg_type == 'stop_typing':
                    target_user_id = data.get('target_user_id')
                    if target_user_id:
                        # CORRECCIÓN: Enviar objeto WSBaseEvent
                        event = WSBaseEvent(
                            type=WSEventType.CHAT_STOP_TYPING,
                            data={
                                "conversation_id": data.get('conversation_id'),
                                "user_id": user.id
                            }
                        )
                        await ws_manager.send_to_user(target_user_id, event)

            except RuntimeError:
                break # Cliente desconectado
                
    except WebSocketDisconnect:
        ws_manager.disconnect(info, websocket)
    except Exception as e:
        print(f"🔴 WS Error Crítico: {e}")
        ws_manager.disconnect(info, websocket)


# ============================================================
# USUARIOS (para destinatarios en mensajes)
# ============================================================




# ============================================================
# INVENTARIO - MÓDULO COMPLETO
# ============================================================

@web_router.get("/inventario", response_class=HTMLResponse, name="inventario")
async def inventario_page(request: Request, user = Depends(get_current_user_optional)):
    """Página de gestión de inventarios (requiere autenticación)"""
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    return templates.TemplateResponse("inventario/index.html", {
        "request": request,
        "current_user": user,
        "page_title": f"Inventarios - {settings.app_name}",
        "active_menu": "inventario"
    })


# ============================================================
# API: SEGUIMIENTO DIARIO (TABLA DE ICONOS CON ROLES)
# ============================================================

# app/interfaces/web/routes.py

# --- IMPORTS NECESARIOS (Asegúrate de tenerlos) ---
# --- IMPORTS CORREGIDOS ---
# Eliminamos la línea de 'profesores' que daba error
from app.infrastructure.db.models.academico.paralelos_profesoras import ParaleloProfesora
from app.infrastructure.db.models.alumnos.tutores import Tutor
from app.infrastructure.db.models.alumnos.alumnos_tutores import AlumnoTutor
from app.infrastructure.db.models.alumnos.alumnos_paralelos import AlumnoParalelo
from app.infrastructure.db.models.academico.paralelos import Paralelo

@web_router.get("/api/v1/academico/diario", tags=["Academico"])
async def get_seguimiento_diario(
    fecha: str,
    grupo_id: int = None,
    paralelo_id: int = None, 
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Retorna la sábana de actividades diaria filtrada por permisos.
    """
    if not user: raise HTTPException(401)
    
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        fecha_dt = datetime.now().date()

    # 1. DETECCIÓN DE ROLES
    roles_names = []
    if hasattr(user, 'roles') and user.roles:
        roles_names = [r.nombre.upper() for r in user.roles]
    elif hasattr(user, 'rol') and user.rol:
        roles_names = [user.rol.nombre.upper()]
        
    es_admin = any(r in ["ADMIN", "ADMINISTRADOR", "DIRECTORA", "DIRECTOR", "SECRETARIA"] for r in roles_names)
    es_profesora = any(r in ["PROFESOR", "PROFESORA", "DOCENTE"] for r in roles_names)
    es_tutor = any(r in ["TUTOR", "PADRE", "FAMILIAR"] for r in roles_names)

    # 2. QUERY BASE
    stmt = select(Alumno).where(
        Alumno.sede_id == user.sede_id,
        Alumno.estado == 'inscrito'
    )

    # 3. FILTROS OPCIONALES
    if paralelo_id:
        stmt = stmt.join(Alumno.paralelos).where(
            and_(AlumnoParalelo.activo == True, AlumnoParalelo.paralelo_id == paralelo_id)
        )
    elif grupo_id:
        stmt = stmt.join(Alumno.paralelos).join(AlumnoParalelo.paralelo).where(
            and_(AlumnoParalelo.activo == True, Paralelo.grupo_id == grupo_id)
        )

    # 4. SEGURIDAD CASCADA

    # A) CASO PROFESORA: Usamos user.id DIRECTAMENTE
    if not es_admin and es_profesora:
        anio_actual = datetime.now().year
        
        # ✅ CORRECCIÓN: Usamos user.id en lugar de buscar un perfil de profesor
        subq_mis_paralelos = select(ParaleloProfesora.paralelo_id).where(
            ParaleloProfesora.profesora_id == user.id,  # Vinculación directa Usuario -> Paralelo
            ParaleloProfesora.gestion == anio_actual
        )

        stmt = stmt.where(
            select(AlumnoParalelo).where(
                and_(
                    AlumnoParalelo.alumno_id == Alumno.id,
                    AlumnoParalelo.activo == True,
                    AlumnoParalelo.paralelo_id.in_(subq_mis_paralelos)
                )
            ).exists()
        )

    # B) CASO TUTOR
    elif not es_admin and es_tutor:
        tutor = await db.scalar(select(Tutor).where(Tutor.usuario_id == user.id))
        
        if not tutor:
            return {"items": []} 

        stmt = stmt.join(AlumnoTutor, AlumnoTutor.alumno_id == Alumno.id)\
                   .where(AlumnoTutor.tutor_id == tutor.id)

    # 5. EJECUCIÓN
    stmt = stmt.distinct().order_by(Alumno.apellido_paterno)
    alumnos = (await db.execute(stmt)).scalars().all()
    
    if not alumnos:
        return {"items": []}

    # 6. CARGAR ACTIVIDADES Y REPORTES (Igual que antes)
    alumnos_ids = [a.id for a in alumnos]
    
    stmt_act = select(
        Actividad.alumno_id,
        Actividad.tipo,
        func.count(Actividad.id)
    ).where(
        and_(
            Actividad.fecha_actividad == fecha_dt,
            Actividad.alumno_id.in_(alumnos_ids)
        )
    ).group_by(Actividad.alumno_id, Actividad.tipo)
    
    res_act = await db.execute(stmt_act)
    
    actividades_map = {}
    for aid, tipo_enum, count in res_act:
        if aid not in actividades_map: actividades_map[aid] = {}
        tipo_str = tipo_enum.name if hasattr(tipo_enum, 'name') else str(tipo_enum)
        actividades_map[aid][tipo_str] = count

    stmt_rep = select(ReporteDiario).options(selectinload(ReporteDiario.lecturas_tutores)).where(
        and_(ReporteDiario.fecha == fecha_dt, ReporteDiario.alumno_id.in_(alumnos_ids))
    )
    res_rep = (await db.execute(stmt_rep)).scalars().all()
    reportes_map = {r.alumno_id: r for r in res_rep}

    items = []
    for alu in alumnos:
        acts = actividades_map.get(alu.id, {})
        r = reportes_map.get(alu.id)
        
        estado = "Sin abrir"
        color = "bg-gray-100 text-gray-500"
        total_acts = sum(acts.values())
        
        if r:
            if r.confirmado:
                estado = "Confirmado"; color = "bg-green-100 text-green-700"
            elif r.lecturas_tutores and any(l.leido for l in r.lecturas_tutores):
                estado = "Leído"; color = "bg-blue-100 text-blue-700"
            else:
                estado = "Enviado"; color = "bg-yellow-100 text-yellow-800"
        elif total_acts > 0:
             estado = "En curso"; color = "bg-indigo-50 text-indigo-600"

        items.append({
            "id": alu.id,
            "nombre_completo": f"{alu.apellido_paterno} {alu.apellido_materno or ''} {alu.nombre}".strip(),
            "foto_url": alu.foto_url,
            "actividades": acts, 
            "estado_reporte": estado,
            "badge_color": color,
            "reporte_id": r.id if r else None
        })

    return {"items": items}

# ============================================================
# API: CREAR ACTIVIDAD (NUEVA)
# ============================================================


@web_router.post("/api/v1/academico/actividades", tags=["Academico"])
async def crear_actividad_endpoint(
    alumno_id: int = Form(...),
    tipo: str = Form(...),
    fecha: str = Form(...),
    titulo: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    valor: Optional[str] = Form(None),
    hora: Optional[str] = Form(None),
    archivo: Optional[UploadFile] = File(None), # <--- Nuevo campo archivo
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Registra actividad. Soporta subida de archivos para FOTO/VIDEO
    y guarda el estado de ánimo en 'valor'.
    """
    if not user: raise HTTPException(401)

    try:
        # 1. Crear la Actividad
        fecha_act = datetime.strptime(fecha, "%Y-%m-%d").date()
        
        nueva_actividad = Actividad(
            alumno_id=alumno_id,
            profesora_id=user.id,
            tipo=tipo, 
            titulo=titulo or tipo.capitalize(),
            descripcion=descripcion,
            valor=valor, # Aquí se guardará "FELIZ", "TRISTE", etc.
            hora=hora or datetime.now().strftime("%H:%M"),
            fecha_actividad=fecha_act
        )
        
        db.add(nueva_actividad)
        await db.flush() # Para obtener el ID de la actividad antes de guardar el archivo

        # 2. Si hay archivo (FOTO o VIDEO), guardarlo
        if archivo and archivo.filename:
            # Definir carpeta y tipo media
            tipo_media = TipoMedia.imagen
            subcarpeta = "fotos_actividades"
            
            if tipo == "VIDEO":
                tipo_media = TipoMedia.video
                subcarpeta = "videos_actividades"
            elif tipo == "FOTO":
                tipo_media = TipoMedia.imagen
                subcarpeta = "fotos_actividades"

            # Guardar en disco
            safe_filename = f"{nueva_actividad.id}_{int(datetime.now().timestamp())}_{archivo.filename.replace(' ', '_')}"
            ruta_carpeta = Path(settings.MEDIA_DIR) / subcarpeta
            ruta_carpeta.mkdir(parents=True, exist_ok=True)
            ruta_final = ruta_carpeta / safe_filename
            
            with open(ruta_final, "wb") as buffer:
                shutil.copyfileobj(archivo.file, buffer)
            
            url_publica = f"/media/{subcarpeta}/{safe_filename}"

            # Crear registro en ActividadMedia
            media = ActividadMedia(
                actividad_id=nueva_actividad.id,
                tipo=tipo_media,
                url=url_publica,
                nombre_archivo=archivo.filename,
                estado="completado" # O pendiente si usas watermark
            )
            db.add(media)

        await db.commit()
        return {"success": True, "mensaje": "Actividad registrada correctamente"}
        
    except Exception as e:
        await db.rollback()
        print(f"Error creando actividad: {e}")
        raise HTTPException(500, detail=str(e))
    

# ============================================================
# API: PLANIFICACIONES
# ============================================================

@web_router.post("/api/v1/academico/planificaciones", tags=["Academico"])
async def subir_planificacion_endpoint(
    duracion: str = Form(...),
    titulo: Optional[str] = Form(None),
    archivo: UploadFile = File(...),
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Sube un PDF de planificación"""
    if not user: raise HTTPException(401)
    
    if archivo.content_type != "application/pdf":
        raise HTTPException(400, "El archivo debe ser un PDF")

    try:
        # 1. Guardar PDF en disco
        safe_filename = f"PLAN_{user.id}_{int(datetime.now().timestamp())}_{archivo.filename.replace(' ', '_')}"
        ruta_carpeta = Path(settings.MEDIA_DIR) / "planificaciones"
        ruta_carpeta.mkdir(parents=True, exist_ok=True)
        ruta_final = ruta_carpeta / safe_filename
        
        with open(ruta_final, "wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)
            
        url_publica = f"/media/planificaciones/{safe_filename}"

        # 2. Guardar en BD
        nueva_plan = PlanificacionProfesora(
            profesora_id=user.id,
            duracion=duracion, # Debe coincidir con los valores del Enum (ej: "1 Mes")
            titulo=titulo or f"Planificación {duracion}",
            archivo_url=url_publica
        )
        
        db.add(nueva_plan)
        await db.commit()
        
        return {"success": True, "mensaje": "Planificación subida correctamente"}

    except Exception as e:
        await db.rollback()
        print(f"Error subiendo planificación: {e}")
        raise HTTPException(500, detail=str(e))

# ============================================================
# API: DETALLE DEL ALUMNO (MODAL ROJO)
# ============================================================

@web_router.get("/api/v1/academico/diario/{alumno_id}/detalle", tags=["Academico"])
async def get_detalle_diario_alumno(
    alumno_id: int,
    fecha: str,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Devuelve el detalle cronológico para el modal rojo"""
    if not user: raise HTTPException(401)
    
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    
    # 1. Datos Alumno
    alumno = await db.get(Alumno, alumno_id)
    if not alumno: raise HTTPException(404)

    # 2. Actividades del día (Cargamos 'profesora' y 'media')
    stmt = select(Actividad).options(
        selectinload(Actividad.profesora),
        selectinload(Actividad.media)  # <--- IMPORTANTE: Cargar fotos/videos
    ).where(
        and_(
            Actividad.alumno_id == alumno_id,
            Actividad.fecha_actividad == fecha_dt
        )
    ).order_by(desc(Actividad.creado_en))
    
    actividades = (await db.execute(stmt)).scalars().all()
    
    lista = []
    for act in actividades:
        creador = f"{act.profesora.nombres}{" "}{act.profesora.apellidos}" if act.profesora else "Staff"
        
        # Obtener URL del archivo si existe
        media_url = None
        media_tipo = None
        if act.media:
            # Tomamos el primero (generalmente es uno por actividad)
            m = act.media[0]
            media_url = m.url
            media_tipo = m.tipo # imagen, video

        lista.append({
            "id": act.id,
            "tipo": act.tipo.name if hasattr(act.tipo, 'name') else str(act.tipo),
            "titulo": act.titulo,
            "descripcion": act.descripcion,
            "valor": act.valor, # Aquí viene "FELIZ", "TRISTE" o "38°C"
            "hora": act.hora or act.creado_en.strftime("%H:%M"),
            "fecha_creacion": act.creado_en.strftime("%d/%m/%Y"), # Fecha real de creación
            "creador": creador,
            "media_url": media_url,
            "media_tipo": media_tipo
        })


    return {
        "alumno": {
            "nombre": alumno.nombres_completos,
            "foto_url": alumno.foto_url
        },
        "fecha_str": fecha_dt.strftime("%d de %B de %Y"),
        "actividades": lista
    }

# ============================================================
# CRUD PLANIFICACIONES (NUEVO)
# ============================================================

# 1. Vista HTML
@web_router.get("/academico/planificaciones", response_class=HTMLResponse)
async def planificaciones_page(request: Request, user = Depends(get_current_user_optional)):
    if not user: return RedirectResponse("/login")
    return templates.TemplateResponse("academico/planificaciones/index.html", {
        "request": request,
        "current_user": user,
        "page_title": f"Planificaciones - {settings.app_name}",
        "active_menu": "academico"
    })

# 2. API Listar
@web_router.get("/api/v1/academico/planificaciones", tags=["Academico"])
async def listar_planificaciones(
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Lista las planificaciones. Profesora ve las suyas, Admin ve todas."""
    if not user: raise HTTPException(401)

    stmt = select(PlanificacionProfesora).options(selectinload(PlanificacionProfesora.profesora)).order_by(desc(PlanificacionProfesora.creado_en))
    
    # Filtro por rol (si no es admin, solo ve las suyas)
    roles = [r.nombre.upper() for r in user.roles] if user.roles else []
    es_admin = any(r in ["ADMINISTRADOR", "DIRECTOR", "SUPERADMIN"] for r in roles)
    
    if not es_admin:
        stmt = stmt.where(PlanificacionProfesora.profesora_id == user.id)

    result = await db.execute(stmt)
    planes = result.scalars().all()

    return {
        "items": [
            {
                "id": p.id,
                "titulo": p.titulo,
                "duracion": p.duracion.value if hasattr(p.duracion, 'value') else str(p.duracion),
                "archivo_url": p.archivo_url,
                "fecha_creacion": p.creado_en.strftime("%d/%m/%Y"),
                "profesora": f"{p.profesora.nombres} {p.profesora.apellidos or ''}".strip() if p.profesora else "Desconocido"
            } for p in planes
        ]
    }

# 3. API Eliminar
@web_router.delete("/api/v1/academico/planificaciones/{plan_id}", tags=["Academico"])
async def eliminar_planificacion(
    plan_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    
    plan = await db.get(PlanificacionProfesora, plan_id)
    if not plan: raise HTTPException(404, "Planificación no encontrada")

    # Verificar permisos (solo dueño o admin)
    roles = [r.nombre.upper() for r in user.roles] if user.roles else []
    es_admin = any(r in ["ADMINISTRADOR", "DIRECTOR", "SUPERADMIN"] for r in roles)
    
    if not es_admin and plan.profesora_id != user.id:
        raise HTTPException(403, "No tienes permiso para eliminar esto")

    try:
        # Opcional: Eliminar archivo físico
        # if os.path.exists(plan.archivo_url): os.remove(...)
        
        await db.delete(plan)
        await db.commit()
        return {"success": True, "mensaje": "Eliminado correctamente"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, str(e))

# ============================================================
# API: ASISTENCIA (LISTA Y GUARDADO)
# ============================================================

# --- IMPORTS NECESARIOS (Asegúrate de tenerlos arriba) ---
from app.infrastructure.db.models.alumnos.tutores import Tutor
from app.infrastructure.db.models.alumnos.alumnos_tutores import AlumnoTutor
from app.infrastructure.db.models.academico.paralelos_profesoras import ParaleloProfesora
from app.infrastructure.db.models.alumnos.alumnos_paralelos import AlumnoParalelo
from app.infrastructure.db.models.academico.paralelos import Paralelo
from app.infrastructure.db.models.alumnos.asistencia_alumnos import AsistenciaAlumno # Asumo que este es tu modelo

@web_router.get("/api/v1/academico/asistencia", tags=["Academico"])
async def get_asistencia_dia(
    fecha: str,
    grupo_id: Optional[int] = None,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: 
        raise HTTPException(401)
    
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()

    # 1. DETECCIÓN DE ROLES ROBUSTA
    roles_names = []
    if hasattr(user, 'roles') and user.roles:
        roles_names = [r.nombre.upper() for r in user.roles]
    elif hasattr(user, 'rol') and user.rol:
        roles_names = [user.rol.nombre.upper()]

    es_admin = any(r in ["ADMINISTRADOR", "DIRECTOR", "SUPERADMIN", "ADMIN"] for r in roles_names)
    es_profesora = any(r in ["PROFESOR", "PROFESORA", "DOCENTE"] for r in roles_names)
    es_tutor = any(r in ["TUTOR", "PADRE", "FAMILIAR"] for r in roles_names) # <--- NUEVO

    # 2. QUERY BASE
    stmt = select(Alumno).where(
        Alumno.sede_id == user.sede_id,
        Alumno.estado == 'inscrito'
    )

    # 3. SEGURIDAD (CASCADA) 

    # A) CASO PROFESORA: Filtra por sus paralelos asignados
    if not es_admin and es_profesora:
        anio_actual = datetime.now().year
        
        # Subconsulta: Paralelos de la profesora
        subq_mis_paralelos = select(ParaleloProfesora.paralelo_id).where(
            ParaleloProfesora.profesora_id == user.id,
            ParaleloProfesora.gestion == anio_actual
        )
        
        # Filtramos alumnos que estén en esos paralelos
        stmt = stmt.where(
            select(AlumnoParalelo).where(
                and_(
                    AlumnoParalelo.alumno_id == Alumno.id,
                    AlumnoParalelo.activo == True,
                    AlumnoParalelo.paralelo_id.in_(subq_mis_paralelos)
                )
            ).exists()
        )

    # B) CASO TUTOR: Filtra solo a sus hijos
    elif not es_admin and es_tutor:
        # Buscar perfil de Tutor
        tutor = await db.scalar(select(Tutor).where(Tutor.usuario_id == user.id))
        
        if not tutor:
            return {"items": []} # Es tutor pero sin perfil enlazado

        # Filtramos por la relación Alumno-Tutor
        stmt = stmt.join(AlumnoTutor, AlumnoTutor.alumno_id == Alumno.id)\
                   .where(AlumnoTutor.tutor_id == tutor.id)

    # 4. FILTRO OPCIONAL POR GRUPO (Si mandan grupo_id)
    # Nota: Esto aplica para Admin o si la Profesora/Tutor filtra dentro de sus permitidos
    if grupo_id:
        stmt = stmt.where(
            select(AlumnoParalelo).join(Paralelo).where(
                and_(
                    AlumnoParalelo.alumno_id == Alumno.id,
                    AlumnoParalelo.activo == True,
                    Paralelo.grupo_id == grupo_id
                )
            ).exists()
        )

    # 5. EJECUCIÓN CONSULTA ALUMNOS
    stmt = stmt.distinct().order_by(Alumno.apellido_paterno)
    result = await db.execute(stmt)
    alumnos = result.scalars().all()
    
    if not alumnos:
        return {"items": []}

    # 6. OBTENER ASISTENCIAS (Misma lógica que tenías)
    alumnos_ids = [a.id for a in alumnos]
    asistencias_map = {}
    
    if alumnos_ids:
        stmt_asis = select(AsistenciaAlumno).where(
            and_(
                AsistenciaAlumno.fecha == fecha_dt,
                AsistenciaAlumno.alumno_id.in_(alumnos_ids)
            )
        )
        res_asis = (await db.execute(stmt_asis)).scalars().all()
        
        for a in res_asis:
            asistencias_map[a.alumno_id] = {
                "estado": a.estado, # P.ej: PRESENTE, FALTA, ATRASO
                "hora_retraso": a.hora_retraso.strftime("%H:%M") if a.hora_retraso else "",
                "observacion": a.observaciones or ""
            }

    # 7. CONSTRUIR RESPUESTA
    items = []
    for alu in alumnos:
        # Estado por defecto si no hay registro
        asis = asistencias_map.get(alu.id, {
            "estado": "PENDIENTE", 
            "hora_retraso": "", 
            "observacion": ""
        })
        
        items.append({
            "id": alu.id,
            "nombre": f"{alu.apellido_paterno} {alu.apellido_materno or ''} {alu.nombre}".strip(),
            "foto_url": alu.foto_url,
            "asistencia": asis
        })
    
    return {"items": items}

@web_router.post("/api/v1/academico/asistencia", tags=["Academico"])
async def guardar_asistencia_lote(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Guarda o actualiza asistencia masiva"""
    if not user: raise HTTPException(401)
    
    data = await request.json()
    fecha = datetime.strptime(data.get('fecha'), "%Y-%m-%d").date()
    lista = data.get('asistencias', []) # [{id: 1, estado: 'PRESENTE', ...}]
    
    try:
        # Usamos transacción única para todo el lote
        # (db.begin() no es necesario si controlamos commit al final en modo autocommit=False)
        
        for item in lista:
            alumno_id = item['id']
            estado = item['estado']
            
            # Buscar registro existente
            stmt = select(AsistenciaAlumno).where(
                and_(AsistenciaAlumno.fecha == fecha, AsistenciaAlumno.alumno_id == alumno_id)
            )
            existing = (await db.execute(stmt)).scalars().first()
            
            # Procesar hora
            hora_obj = None
            if estado == 'RETRASO' and item.get('hora_retraso'):
                try:
                    hora_obj = datetime.strptime(item['hora_retraso'], "%H:%M").time()
                except: pass

            if existing:
                existing.estado = estado
                existing.hora_retraso = hora_obj
                existing.observaciones = item.get('observacion')
                existing.registrado_por_id = user.id
            else:
                new_asis = AsistenciaAlumno(
                    alumno_id=alumno_id,
                    fecha=fecha,
                    estado=estado,
                    hora_retraso=hora_obj,
                    observaciones=item.get('observacion'),
                    sede_id=user.sede_id,
                    registrado_por_id=user.id
                )
                db.add(new_asis)
        
        await db.commit()
        return {"success": True, "mensaje": "Asistencia guardada"}
        
    except Exception as e:
        await db.rollback()
        print(f"Error guardando asistencia: {e}")
        raise HTTPException(500, detail=str(e))


# ============================================================
# USUARIOS - FRONTEND WEB (REAL)
# ============================================================

@web_router.get("/usuarios", response_class=HTMLResponse, name="usuarios_list")
async def usuarios_list_page(request: Request, user = Depends(get_current_user_optional)):
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    # Verificar permisos (Solo Admin/Dueño/Superadmin)
    # if user.role not in ['ADMIN', 'DUENO', 'SUPERADMIN']: ...
    
    return templates.TemplateResponse(
        "usuarios/list.html",
        {
            "request": request,
            "current_user": user,
            "page_title": f"Usuarios - {settings.app_name}",
            "active_menu": "usuarios",
        },
    )

# =========================
# API USUARIOS (REAL)
# =========================

@web_router.get("/api/v1/usuarios", tags=["Usuarios"])
async def get_usuarios_endpoint(
    page: int = 1,
    per_page: int = 10,
    search: str = "",
    rol: str | None = None,
    activo: int | None = None,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    # 1. Construir filtros (CONDICIONES COMUNES)
    conditions = []
    
    if search:
        term = f"%{search}%"
        conditions.append(or_(
            Usuario.nombres.ilike(term),
            Usuario.apellidos.ilike(term),
            Usuario.username.ilike(term),
            Usuario.email.ilike(term)
        ))
    
    if activo is not None:
        conditions.append(Usuario.activo == bool(activo))

    # 2. QUERY PARA CONTAR (OPTIMIZADA)
    # No usamos selectinload aquí, es mucho más rápido
    count_stmt = select(func.count(Usuario.id))
    
    if rol:
        # Solo hacemos join si filtramos por rol
        count_stmt = count_stmt.join(Usuario.roles).where(Rol.nombre.ilike(f"%{rol}%"))
    
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))

    total = await db.scalar(count_stmt) or 0

    # 3. QUERY PARA DATOS (CON RELACIONES)
    # Aquí sí cargamos los roles para mostrarlos
    stmt = select(Usuario).options(selectinload(Usuario.roles)).order_by(desc(Usuario.creado_en))
    
    if rol:
        stmt = stmt.join(Usuario.roles).where(Rol.nombre.ilike(f"%{rol}%"))
    
    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Paginación
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(stmt)
    usuarios = result.scalars().all()

    # 4. Serialización
    items = []
    for u in usuarios:
        rol_nombre = "SIN ROL"
        if u.roles:
            rol_nombre = u.roles[0].nombre

        items.append({
            "id": u.id,
            "username": u.username,
            "nombres": u.nombres,
            "apellidos": u.apellidos,
            # Campo útil para el buscador del frontend
            "nombre_completo": f"{u.nombres} {u.apellidos or ''}".strip(), 
            "email": u.email,
            "telefono": u.telefono,
            "foto_perfil_url": u.foto_perfil_url,
            "rol_nombre": rol_nombre,
            "activo": u.activo,
            "creado_en": u.creado_en.isoformat() if u.creado_en else None
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@web_router.post("/api/v1/usuarios", tags=["Usuarios"])
async def create_usuario_endpoint(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Crear usuario administrativo directamente (Admin, Dueño)"""
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    data = await request.json()
    
    if not data.get("username") or not data.get("password"):
        raise HTTPException(status_code=400, detail="Usuario y contraseña requeridos")

    # Helper UoW (para consistencia)
    from contextlib import asynccontextmanager
    @asynccontextmanager
    async def session_wrapper():
        yield db

    try:
        uow = UnitOfWork(session_factory=session_wrapper)
        
        async with uow:
            # Verificar duplicados
            stmt = select(Usuario).where(Usuario.username == data.get("username"))
            res = await uow.session.execute(stmt)
            if res.scalars().first():
                raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

            # Crear Usuario
            nuevo_usuario = Usuario(
                sede_id=user.sede_id,
                username=data.get("username"),
                hash_password=hasher.hash_password(data.get("password")),
                nombres=data.get("nombres"),
                apellidos=data.get("apellidos", ""),
                email=data.get("email"),
                telefono=data.get("telefono"),
                activo=True
            )
            uow.session.add(nuevo_usuario)
            await uow.session.flush()

            # --- CAMBIO AQUÍ: BUSCAR POR NOMBRE ---
            rol_nombre = data.get("rol") # El front enviará "ADMINISTRADOR", "PROFESORA", etc.
            if rol_nombre:
                # Usamos ilike para que no importen mayúsculas/minúsculas
                rol_obj = await uow.session.scalar(select(Rol).where(Rol.nombre.ilike(rol_nombre)))
                
                if rol_obj:
                    # Crear relación
                    user_rol = UsuarioRol(usuario_id=nuevo_usuario.id, rol_id=rol_obj.id)
                    uow.session.add(user_rol)
                else:
                    raise HTTPException(400, f"Rol '{rol_nombre}' no encontrado")
            
            await uow.commit()

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        print(f"❌ Error creando usuario: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {"success": True, "usuario": {"id": nuevo_usuario.id, "username": nuevo_usuario.username}}


@web_router.post("/api/v1/usuarios/profesora", tags=["Usuarios"])
async def create_invitacion_profesora_endpoint(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Genera código de invitación para profesora"""
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    data = await request.json()
    codigo_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Helper UoW
    @asynccontextmanager
    async def session_wrapper():
        yield db

    try:
        uow = UnitOfWork(session_factory=session_wrapper)
        async with uow:
            # Obtener Rol Profesora
            rol_profe = await uow.session.scalar(select(Rol).where(Rol.nombre.ilike("PROFESORA")))
            rol_id = rol_profe.id if rol_profe else 3 

            # Crear Código
            nuevo_codigo = CodigoAcceso(
                sede_id=user.sede_id,
                gestion=datetime.now().year,
                rol_id=rol_id,
                codigo=codigo_str,
                max_cuentas=1,
                cuentas_creadas=0,
                estado=EstadoCodigo.pendiente,
                whatsapp_numero=data.get("telefono", ""),
                observaciones=f"Invitación para: {data.get('nombres')} {data.get('apellidos')}",
                creado_por=user.id
            )
            uow.session.add(nuevo_codigo)
            await uow.commit()
    
    except Exception as e:
        print(f"❌ Error creando invitación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "success": True,
        "id": nuevo_codigo.id,
        "codigo": codigo_str,
        "nombres": data.get("nombres"),
        "apellidos": data.get("apellidos"),
        "telefono": data.get("telefono"),
        "mensaje": "Código de invitación generado correctamente"
    }


@web_router.post("/api/v1/usuarios/profesora", tags=["Usuarios"])
async def create_invitacion_profesora_endpoint(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Genera un CÓDIGO DE INVITACIÓN para una nueva profesora.
    No crea el usuario todavía; la profesora se registra usando este código.
    """
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    data = await request.json()
    
    # Generar código único
    codigo_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Generar caso de uso o lógica directa
    async with db.begin():
        # Obtener Rol Profesora
        rol_profe = await db.scalar(select(Rol).where(Rol.nombre == "PROFESORA"))
        rol_id = rol_profe.id if rol_profe else 3 # Fallback ID

        # Crear Código de Acceso
        nuevo_codigo = CodigoAcceso(
            sede_id=user.sede_id,
            gestion=datetime.now().year,
            rol_id=rol_id,
            codigo=codigo_str,
            max_cuentas=1, # Solo 1 cuenta por profe
            cuentas_creadas=0,
            estado=EstadoCodigo.pendiente,
            whatsapp_numero=data.get("telefono", ""),
            observaciones=f"Invitación para: {data.get('nombres')} {data.get('apellidos')}",
            creado_por=user.id
        )
        db.add(nuevo_codigo)
    
    # Retornar datos para mostrar (y enviar por WhatsApp si se implementa)
    return {
        "success": True,
        "id": nuevo_codigo.id,
        "codigo": codigo_str,
        "nombres": data.get("nombres"),
        "apellidos": data.get("apellidos"),
        "telefono": data.get("telefono"),
        "mensaje": "Código de invitación generado correctamente"
    }


@web_router.get("/api/v1/roles", tags=["Usuarios"])
async def get_roles_endpoint(
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Lista los roles disponibles para asignar"""
    if not user: return {"items": []}

    # Buscamos todos los roles menos TUTOR
    stmt = select(Rol).where(Rol.nombre != "TUTOR").order_by(Rol.nombre)
    result = await db.execute(stmt)
    roles = result.scalars().all()

    # CAMBIO: Usamos 'nombre' en lugar de 'codigo'
    return {
        "items": [{"codigo": r.nombre, "nombre": r.nombre} for r in roles],
        "total": len(roles)
    }


# --- VISTAS HTML (Páginas completas) ---

@web_router.get("/academico/grupos", response_class=HTMLResponse)
async def grupos_index(request: Request, user = Depends(get_current_user_optional)):
    if not user: return RedirectResponse("/login")
    return templates.TemplateResponse("academico/grupos/index.html", {
        "request": request, "current_user": user, "page_title": "Gestión de Grupos", "active_menu": "academico"
    })

@web_router.get("/academico/paralelos", response_class=HTMLResponse)
async def paralelos_index(request: Request, user = Depends(get_current_user_optional)):
    if not user: return RedirectResponse("/login")
    return templates.TemplateResponse("academico/paralelos/index.html", {
        "request": request, "current_user": user, "page_title": "Gestión de Paralelos", "active_menu": "academico"
    })

@web_router.get("/finanzas/turnos", response_class=HTMLResponse)
async def turnos_index(request: Request, user = Depends(get_current_user_optional)):
    if not user: return RedirectResponse("/login")
    return templates.TemplateResponse("finanzas/turnos/index.html", {
        "request": request, "current_user": user, "page_title": "Gestión de Turnos", "active_menu": "finanzas"
    })

@web_router.get("/academico/horarios", response_class=HTMLResponse)
async def horarios_index(request: Request, user = Depends(get_current_user_optional)):
    if not user: return RedirectResponse("/login")
    return templates.TemplateResponse("academico/horarios/index.html", {
        "request": request, "current_user": user, "page_title": "Gestión de Horarios", "active_menu": "academico"
    })

# --- API ENDPOINTS (CREACIÓN RÁPIDA) ---

@web_router.post("/api/v1/grupos", tags=["Academico"])
async def crear_grupo_endpoint(request: Request, user = Depends(get_current_user_optional), db: AsyncSession = Depends(get_session)):
    if not user: raise HTTPException(401)
    data = await request.json()
    
    @asynccontextmanager
    async def session_wrapper(): yield db
    
    try:
        uow = UnitOfWork(session_factory=session_wrapper)
        async with uow:
            nuevo = Grupo(
                sede_id=user.sede_id,
                nombre=data.get('nombre'),
                gestion=data.get('gestion') or datetime.now().year,
                activo=True
            )
            uow.session.add(nuevo)
            await uow.commit()
            return {"success": True, "id": nuevo.id, "mensaje": "Grupo creado correctamente"}
    except Exception as e:
        raise HTTPException(500, str(e))

@web_router.post("/api/v1/paralelos", tags=["Academico"])
async def crear_paralelo_endpoint(request: Request, user = Depends(get_current_user_optional), db: AsyncSession = Depends(get_session)):
    if not user: raise HTTPException(401)
    data = await request.json()
    
    @asynccontextmanager
    async def session_wrapper(): yield db
    
    try:
        uow = UnitOfWork(session_factory=session_wrapper)
        async with uow:
            nuevo = Paralelo(
                sede_id=user.sede_id,
                grupo_id=int(data.get('grupo_id')),
                letra=data.get('letra'),
                capacidad=int(data.get('capacidad') or 30),
                activo=True
            )
            uow.session.add(nuevo)
            await uow.commit()
            return {"success": True, "id": nuevo.id, "mensaje": "Paralelo creado correctamente"}
    except Exception as e:
        raise HTTPException(500, str(e))

@web_router.post("/api/v1/turnos", tags=["Finanzas"])
async def crear_turno_endpoint(request: Request, user = Depends(get_current_user_optional), db: AsyncSession = Depends(get_session)):
    if not user: raise HTTPException(401)
    data = await request.json()
    
    @asynccontextmanager
    async def session_wrapper(): yield db
    
    try:
        uow = UnitOfWork(session_factory=session_wrapper)
        async with uow:
            # Validar y convertir horas
            h_inicio = datetime.strptime(data.get('hora_inicio'), '%H:%M').time()
            h_fin = datetime.strptime(data.get('hora_fin'), '%H:%M').time()
            
            nuevo = Turno(
                sede_id=user.sede_id,
                nombre=data.get('nombre'),
                descripcion=data.get('descripcion'),
                hora_inicio=h_inicio,
                hora_fin=h_fin,
                activo=True,
                creado_por_id=user.id
            )
            uow.session.add(nuevo)
            await uow.commit()
            return {"success": True, "id": nuevo.id, "mensaje": "Turno creado correctamente"}
    except Exception as e:
        print(f"Error Turno: {e}")
        raise HTTPException(500, str(e))

    

# Ejemplo en routes.py

@web_router.post("/api/v1/ia/chat", tags=["IA"])
async def chat_con_sistema(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    data = await request.json()
    prompt = data.get("message")
    
    # Servicio de Aplicación
    service = IAChatService(db)
    
    # Definir el contexto del sistema (MCP básico)
    # Aquí es donde le dices a la IA cómo comportarse o le pasas esquemas de datos
    system_prompt = """
    Eres un asistente experto del sistema multisede Datilera, entrenado específicamente sobre sus módulos académicos, financieros administrativos, de inventario, comunicaciones y portafolio infantil.​
Rol y objetivo
Tu objetivo es guiar a los usuarios en el uso del sistema Datilera, resolver dudas operativas del día a día y proponerles el flujo más eficiente según su rol (superadmin, director, profesora, tutor, administración, servicio técnico).​
Debes:
Explicar paso a paso cómo realizar tareas frecuentes: inscripciones, generación de contratos, registro de pagos, arqueos, gestión de inventarios, asistencia, reportes diarios, comunicaciones y notificaciones.​
Responder preguntas sobre reglas de negocio (prorrateo, descuentos, cupos por paralelo, políticas de notificaciones, manejo de datos sensibles, permisos por rol, etc.).​
Sugerir al usuario la pantalla, menú o endpoint adecuado dentro de Datilera cuando sea relevante.​
Alcance funcional
Cuando respondas, limítate a la lógica y capacidades del sistema Datilera, incluyendo:
Gestión académica: sedes, grupos, paralelos, horarios, asistencia de alumnos y personal, permisos y bajas médicas, portafolio y reportes diarios.​
Gestión financiera: planes de pago, prorrateo, descuentos, estados de cuenta, conciliaciones, arqueos, libro de caja, cursos extra y sus saldos.​
Inventarios: familias, categorías, stock por sede, mínimos, alertas y movimientos sin evidencias obligatorias.​
Comunicaciones y notificaciones: chat tutor–profesora–directora, notificaciones persistentes, recordatorios configurados y estadísticas básicas.​
Estilo de respuesta
Usa un tono claro, respetuoso y orientado a personal administrativo y docente con distintos niveles de dominio tecnológico.
Prioriza respuestas accionables: “haz clic en…”, “ve al módulo…”, “usa el filtro…”, “verifica que…”.​
Si la pregunta es ambigua, primero pide las aclaraciones mínimas (rol, sede, módulo) y luego indica el flujo recomendado.​
Cuando una operación involucra reglas sensibles (finanzas, datos de niños, permisos), recuerde brevemente la regla de negocio relevante antes de indicar los pasos.​
Comportamiento esperado
Si el usuario pide algo que el sistema Datilera no soporta o contradice una regla de negocio, explícalo claramente y, si es posible, propone una alternativa dentro de las funcionalidades existentes.​
Si la tarea implica coordinación entre roles (por ejemplo, profesora solicita permiso y director aprueba), explique qué hace cada rol y en qué pantalla.​
Mantén las respuestas concisas, enfocadas en el contexto escolar de Datilera y listas para usar como ayuda integrada dentro del sistema.
    """
    
    respuesta = await service.procesar_consulta(
        prompt=prompt,
        usuario_id=user.id,
        sede_id=user.sede_id,
        proveedor_nombre="gemini", # O dejar dinámico
        contexto_sistema=system_prompt
    )
    
    return {"reply": respuesta}




@web_router.get("/api/v1/finanzas/recibo/{pago_id}", tags=["Finanzas"])
async def descargar_recibo(
    pago_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: 
        raise HTTPException(401, "No autenticado")
    
    try:
        # 1. Obtener el pago con todas sus relaciones
        stmt = (
            select(Pago)
            .options(
                selectinload(Pago.alumno).selectinload(Alumno.tutores),
                selectinload(Pago.categoria),
                selectinload(Pago.usuario_registro)
            )
            .where(Pago.id == pago_id)
        )
        
        result = await db.execute(stmt)
        pago = result.scalars().first()
        
        if not pago:
            raise HTTPException(404, "Pago no encontrado")
        
        alumno = pago.alumno
        
        if not alumno:
            raise HTTPException(404, "Alumno no encontrado para este pago")
        
        # 2. Construir nombre completo del alumno (CORREGIDO)
        alumno_nombre = f"{alumno.apellido_paterno or ''} {alumno.apellido_materno or ''} {alumno.nombre or ''}".strip()
        
        # 3. Obtener datos del tutor principal
        tutor_nombre = "N/A"
        tutor_ci = "S/N"
        
        if alumno.tutores and len(alumno.tutores) > 0:
            # Tomar el primer tutor disponible
            tutor = alumno.tutores[0]
            
            # Construir nombre del tutor (ajusta según tu modelo Tutor)
            if hasattr(tutor, 'nombres') and hasattr(tutor, 'apellidos'):
                tutor_nombre = f"{tutor.nombres} {tutor.apellidos}".strip()
            elif hasattr(tutor, 'nombre_completo'):
                tutor_nombre = tutor.nombre_completo
            
            # CI del tutor
            if hasattr(tutor, 'ci_numero'):
                tutor_ci = tutor.ci_numero or "S/N"
            elif hasattr(tutor, 'ci'):
                tutor_ci = tutor.ci or "S/N"
        
        # 4. Obtener nombre del usuario cajero
        usuario_cajero = "Sistema"
        if pago.usuario_registro:
            # Construir nombre del usuario (CORREGIDO)
            if hasattr(pago.usuario_registro, 'nombres'):
                usuario_cajero = f"{pago.usuario_registro.nombres} {getattr(pago.usuario_registro, 'apellidos', '')}".strip()
            elif hasattr(pago.usuario_registro, 'username'):
                usuario_cajero = pago.usuario_registro.username
        
        # 5. Categoría del pago
        categoria_nombre = "Pago"
        if pago.categoria and hasattr(pago.categoria, 'nombre'):
            categoria_nombre = pago.categoria.nombre
        
        # 6. Preparar datos para el PDF
        datos_recibo = {
            "numero_recibo": f"REC-{pago.id:06d}",
            "fecha": pago.fecha_pago,
            "cliente_nombre": tutor_nombre,
            "cliente_ci": tutor_ci,
            "alumno_nombre": alumno_nombre,  # ← Nombre completo del niño
            "detalle": f"{categoria_nombre} - Método: {pago.metodo_pago}",
            "monto_total": float(pago.monto_pagado),
            "usuario_cajero": usuario_cajero,
            "comprobante": pago.numero_comprobante or "N/A"
        }
        
        # 7. Generar PDF
        recibo_service = ReciboService()
        pdf_buffer = recibo_service.generar_recibo_pdf(datos_recibo)
        
        # 8. Retornar como descarga
        filename = f"Recibo_{pago.id:06d}_{pago.fecha_pago.strftime('%Y%m%d')}.pdf"
        return StreamingResponse(
            pdf_buffer, 
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR generando recibo: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Error al generar recibo: {str(e)}")


    # app/interfaces/web/routes.py

@web_router.put("/api/v1/finanzas/pagos/{pago_id}/anular", tags=["Finanzas"])
async def anular_transaccion(
    pago_id: int,
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Anula un pago, revierte la caja y restaura la deuda del alumno.
    """
    if not user: raise HTTPException(401)
    
    # Recibimos el motivo desde el cuerpo JSON
    try:
        data = await request.json()
        motivo = data.get("motivo", "Error de registro")
    except:
        motivo = "Sin motivo especificado"

    service = IngresosService(db)
    
    try:
        resultado = await service.anular_pago(pago_id, user.id, motivo)
        await db.commit()
        return {"status": "success", "message": resultado["mensaje"]}
    
    except ValueError as ve:
        await db.rollback()
        raise HTTPException(400, detail=str(ve))
    except Exception as e:
        await db.rollback()
        print(f"Error anulando: {e}")
        raise HTTPException(500, detail="Error interno al anular la transacción.")
    

# --- MÓDULO DE DEUDAS ---



@web_router.post("/api/v1/finanzas/deudores/notificar", tags=["Finanzas"])
async def notificar_deudor(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Envía una notificación interna (campanita) al tutor del alumno.
    Payload: { "alumno_id": 1, "cuota_numero": 3 }
    """
    if not user: raise HTTPException(401)
    
    data = await request.json()
    service = DeudasService(db)
    
    try:
        resultado = await service.generar_notificacion_automatica(
            alumno_id=data['alumno_id'], 
            cuota_numero=data['cuota_numero'],
            usuario_emisor_id=user.id
        )
        await db.commit()
        return resultado
        
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": str(e)}
    

# --- ENDPOINTS AUXILIARES PARA EL FORMULARIO ---



# --- CRUD CATEGORÍAS (INGRESOS Y EGRESOS) ---

@web_router.get("/api/v1/finanzas/categorias/gestion", tags=["Finanzas"])
async def obtener_todas_categorias(
    tipo: str, # 'ingreso' o 'egreso'
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Lista todas las categorías (activas e inactivas) para gestión"""
    if not user: raise HTTPException(401)
    
    Modelo = CategoriaPago if tipo == 'ingreso' else CategoriaEgreso
    stmt = select(Modelo).where(Modelo.sede_id == user.sede_id).order_by(Modelo.nombre)
    result = await db.execute(stmt)
    categorias = result.scalars().all()
    
    return [{"id": c.id, "nombre": c.nombre, "activo": c.activo} for c in categorias]

@web_router.put("/api/v1/finanzas/categorias/{id}/estado", tags=["Finanzas"])
async def cambiar_estado_categoria(
    id: int,
    tipo: str, # 'ingreso' o 'egreso'
    activo: bool,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Activar o Desactivar una categoría (Soft Delete)"""
    if not user: raise HTTPException(401)
    
    Modelo = CategoriaPago if tipo == 'ingreso' else CategoriaEgreso
    categoria = await db.get(Modelo, id)
    
    if not categoria or categoria.sede_id != user.sede_id:
        raise HTTPException(404, "Categoría no encontrada")
        
    categoria.activo = activo
    await db.commit()
    return {"status": "success", "message": "Estado actualizado"}

@web_router.post("/api/v1/finanzas/categorias/crear", tags=["Finanzas"])
async def crear_nueva_categoria(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    data = await request.json()
    nombre = data.get("nombre").upper() # Guardar siempre en mayúsculas
    tipo = data.get("tipo") # 'ingreso' o 'egreso'
    
    Modelo = CategoriaPago if tipo == 'ingreso' else CategoriaEgreso
    
    # Verificar duplicados
    stmt = select(Modelo).where(and_(Modelo.nombre == nombre, Modelo.sede_id == user.sede_id))
    existe = await db.scalar(stmt)
    if existe:
        raise HTTPException(400, "Ya existe una categoría con este nombre")
        
    nueva = Modelo(nombre=nombre, sede_id=user.sede_id, activo=True)
    db.add(nueva)
    await db.commit()
    
    return {"status": "success", "id": nueva.id, "nombre": nueva.nombre}


    
   # ============================================================
# 💰 MÓDULO DE FINANZAS (CORREGIDO Y UNIFICADO)
# Lógica idéntica al Excel SEPTIEMBRE.xlsx
# ============================================================

# --- UTILS FINANCIEROS ---

def calcular_prorrateo(fecha_ingreso: date, monto_mensual: float) -> float:
    """
    Regla de Negocio: 
    - Se toma 20 días hábiles como referencia mensual.
    - Costo diario = Monto / 20.
    - Si faltan <= 3 días para fin de mes, se cobra desde el siguiente.
    """
    hoy = fecha_ingreso
    ultimo_dia_mes = calendar.monthrange(hoy.year, hoy.month)[1]
    dias_restantes = ultimo_dia_mes - hoy.day
    
    # Regla: Si se inscribe 3 días o menos para que acabe el mes, pasa al siguiente
    if dias_restantes <= 3:
        return 0.0 # No paga este mes, su plan inicia el siguiente
        
    # Costo diario basado en 20 días hábiles promedio
    costo_diario = float(monto_mensual) / 20.0
    
    # Días a cobrar: Días hábiles restantes (Lunes a Viernes)
    dias_a_cobrar = 0
    temp_date = hoy
    while temp_date.month == hoy.month:
        if temp_date.weekday() < 5: # 0=Lunes, 4=Viernes
            dias_a_cobrar += 1
        temp_date = temp_date + timedelta(days=1)
        
    total_prorrateado = dias_a_cobrar * costo_diario
    
    # Redondeo boliviano (hacia x.00 o x.50)
    entero = int(total_prorrateado)
    decimal = total_prorrateado - entero
    if decimal <= 0.49:
        return float(entero) + 0.50 
    elif decimal == 0.50:
        return float(entero) + 0.50
    else:
        return float(entero + 1)

# --- ENDPOINTS FINANZAS ---

@web_router.post("/api/v1/finanzas/planes-pago/generar", tags=["Finanzas"])
async def generarplanpago(
    request: Request,
    user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    """Genera el plan de cuotas (Mensualidad, Material, Merienda)."""
    if not user:
        raise HTTPException(401)

    try:
        data = await request.json()

        alumnoid = int(data.get("alumnoid"))
        mensualidad = float(data.get("mensualidad", 950))
        fechaingreso = datetime.strptime(data.get("fechaingreso"), "%Y-%m-%d").date()
        montomaterial = float(data.get("montomaterial", 0))
        montomerienda = float(data.get("montomerienda", 0))
        tipopagoanual = (data.get("tipopago") or "MENSUAL").upper()

        incluye_material = montomaterial > 0
        incluye_merienda = montomerienda > 0

        # 1) Verificar / limpiar plan anterior
        stmt = select(PlanPagoPersonalizado).where(PlanPagoPersonalizado.alumno_id == alumnoid)
        planexistente = (await db.execute(stmt)).scalars().first()

        if planexistente:
            # Borra cuotas pendientes del plan anterior
            await db.execute(
                CuotaPlanPago.__table__.delete().where(
                    CuotaPlanPago.plan_id == planexistente.id,
                    CuotaPlanPago.estado == "pendiente",
                )
            )
            await db.delete(planexistente)
            await db.flush()

        # 2) Crear nuevo plan (con campos REALES de tu modelo)
        # Nota: monto_total/monto_cuota los recalculamos luego cuando generemos cuotas
        plan = PlanPagoPersonalizado(
            alumno_id=alumnoid,
            monto_base=mensualidad,
            incluye_material=incluye_material,
            monto_material=montomaterial,
            incluye_merienda=incluye_merienda,
            monto_merienda=montomerienda,
            monto_total=0,          # se setea abajo
            numero_cuotas=12,       # por defecto
            monto_cuota=0,          # se setea abajo
            fecha_inicio=fechaingreso,
            sede_id=user.sede_id,
            creado_por=user.id,
            estado="activo",
        )
        db.add(plan)
        await db.flush()  # obtener plan.id

        # 3) Generar cuotas
        mesinicio = fechaingreso.month
        anioactual = fechaingreso.year

        montomes1 = calcular_prorrateo(fechaingreso, mensualidad)
        totalplan = 0.0

        mesesrestantes = 13 - mesinicio
        cuotamaterial = (montomaterial / mesesrestantes) if mesesrestantes > 0 else 0
        cuotamerienda = (montomerienda / mesesrestantes) if mesesrestantes > 0 else 0

        for mes in range(mesinicio, 13):
            esprimermes = (mes == mesinicio)
            montocuota_mes = montomes1 if esprimermes else mensualidad

            # Descuentos
            if tipopagoanual == "ANUAL":
                montocuota_mes = montocuota_mes * 0.94
            elif tipopagoanual == "SEMESTRAL" and (mes - mesinicio) < 6:
                montocuota_mes = montocuota_mes * 0.97

            totalcuota = float(montocuota_mes) + float(cuotamaterial) + float(cuotamerienda)

            db.add(
                CuotaPlanPago(
                    plan_id=plan.id,
                    numero_cuota=mes,
                    monto_cuota=totalcuota,
                    fecha_vencimiento=date(anioactual, mes, 10),
                    estado="pendiente",
                )
            )
            totalplan += totalcuota

        # 4) Actualizar totales del plan (campos reales)
        plan.monto_total = totalplan
        plan.monto_cuota = (totalplan / float(plan.numero_cuotas)) if plan.numero_cuotas else 0

        await db.commit()
        return {"success": True, "mensaje": "Plan generado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Error al generar plan: {str(e)}")







@web_router.get("/api/v1/finanzas/alumno/{alumno_id}/cuotas-pendientes", tags=["Finanzas"])
async def obtener_cuotas_pendientes(
    alumno_id: int, 
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    
    # 1. Cuotas del Plan
    stmt = (
        select(CuotaPlanPago)
        .join(PlanPagoPersonalizado)
        .where(
            PlanPagoPersonalizado.alumno_id == alumno_id,
            CuotaPlanPago.estado == 'pendiente'
        )
        .order_by(CuotaPlanPago.fecha_vencimiento)
    )
    cuotas = (await db.execute(stmt)).scalars().all()
    
    items = []
    meses_str = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    for c in cuotas:
        items.append({
            "id": c.id,
            "tipo": "CUOTA",
            "numero": c.numero_cuota,
            "detalle": f"Mensualidad {meses_str[c.numero_cuota]} (Vence: {c.fecha_vencimiento.strftime('%d/%m')})",
            "monto": float(c.monto_cuota - c.monto_pagado),
            "vencimiento": c.fecha_vencimiento.strftime("%d/%m/%Y")
        })
        
    # 2. Opciones variables (para cobrar almuerzos extra, etc.)
    items.append({"id": "VAR_ALMUERZO", "tipo": "VARIABLE", "detalle": "Pack Almuerzos", "monto": 0, "vencimiento": "-"})
    items.append({"id": "VAR_CUIDADO", "tipo": "VARIABLE", "detalle": "Cuidado por Día", "monto": 0, "vencimiento": "-"})
    items.append({"id": "VAR_INSCRIPCION", "tipo": "VARIABLE", "detalle": "Inscripción", "monto": 0, "vencimiento": "-"})
    
    return items

@web_router.post("/api/v1/ingresos/cobrar", tags=["Finanzas"])
async def registrar_cobro_ingreso(
    request: Request,
    user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    """Registra el Pago, actualiza Cuota y escribe en Libro de Caja."""
    if not user:
        raise HTTPException(401, "No autenticado")

    try:
        form = await request.form()

        alumno_id_raw = form.get("pagoalumnoid")          # select alumno
        monto_raw = form.get("pagomonto")
        metodo = (form.get("pagometodo") or "EFECTIVO").upper()
        categoria_pago_id_raw = form.get("pagocategoriaid")
        cuota_id_raw = form.get("pagocuotaid")            # puede ser int o VARxxxx
        comprobante = form.get("pagocomprobante")
        fecha_raw = form.get("pagofecha")

        if not monto_raw:
            raise HTTPException(400, "Monto es requerido")
        if not categoria_pago_id_raw or not str(categoria_pago_id_raw).isdigit():
            raise HTTPException(400, "Categoría es requerida")

        monto = Decimal(monto_raw)
        categoria_pago_id = int(categoria_pago_id_raw)

        fecha_pago = (
            datetime.strptime(str(fecha_raw), "%Y-%m-%d").date()
            if fecha_raw else datetime.now().date()
        )

        alumno_id = int(alumno_id_raw) if alumno_id_raw and str(alumno_id_raw).isdigit() else None

        # Si se está pagando una cuota real (numérica) y no vino alumno, derivarlo desde la cuota/plan
        cuota_obj: CuotaPlanPago | None = None
        if (not alumno_id) and cuota_id_raw and str(cuota_id_raw).isdigit():
            cuota_obj = await db.get(CuotaPlanPago, int(cuota_id_raw))
            if not cuota_obj:
                raise HTTPException(404, "Cuota no encontrada")

            await db.refresh(cuota_obj, attribute_names=["plan"])
            if not cuota_obj.plan:
                raise HTTPException(400, "La cuota no tiene plan asociado")

            # Seguridad multi-sede (la cuota debe ser de la sede del usuario)
            if cuota_obj.plan.sede_id != user.sede_id:
                raise HTTPException(403, "No tienes permiso para cobrar esta cuota")

            alumno_id = cuota_obj.plan.alumno_id

        if not alumno_id:
            raise HTTPException(400, "Debe seleccionar un alumno")

        # Guardar comprobante (si aplica)
        safefilename = None
        if comprobante and hasattr(comprobante, "filename") and comprobante.filename:
            safefilename = f"{datetime.now().timestamp()}_{comprobante.filename}"
            path = Path(settings.MEDIADIR) / "comprobantes"
            path.mkdir(parents=True, exist_ok=True)
            with open(path / safefilename, "wb") as f:
                shutil.copyfileobj(comprobante.file, f)

        # 1) Crear el Pago (modelo real)
        nuevopago = Pago(
            alumno_id=alumno_id,
            categoria_pago_id=categoria_pago_id,
            monto_pagado=monto,
            fecha_pago=fecha_pago,
            metodo_pago=metodo,
            numero_comprobante=safefilename,
            registrado_por=user.id,
            anulado=False,
        )
        db.add(nuevopago)
        await db.flush()  # ID del pago

        # 2) Actualizar cuota si aplica (solo si cuota_id_raw es numérico)
        concepto = "Ingreso Vario"
        if cuota_id_raw and str(cuota_id_raw).isdigit():
            if cuota_obj is None:
                cuota_obj = await db.get(CuotaPlanPago, int(cuota_id_raw))

            if not cuota_obj:
                raise HTTPException(404, "Cuota no encontrada")

            # saldo restante de cuota
            saldo = (cuota_obj.monto_cuota or 0) - (cuota_obj.monto_pagado or 0)

            if monto >= saldo:
                cuota_obj.monto_pagado = cuota_obj.monto_cuota
                cuota_obj.estado = "pagada"
                cuota_obj.fecha_pago = datetime.now()
            else:
                cuota_obj.monto_pagado = (cuota_obj.monto_pagado or 0) + monto
                cuota_obj.estado = "pendiente"

            cuota_obj.pago_id = nuevopago.id
            concepto = f"Cuota {cuota_obj.numero_cuota} - Alumno {alumno_id}"
        else:
            # Variables (tu mapeo)
            mapavar = {
                "VARALMUERZO": "Almuerzos",
                "VARCUIDADO": "Cuidado Diario",
                "VARINSCRIPCION": "Inscripción",
            }
            concepto = mapavar.get(str(cuota_id_raw), "Pago Extra")

        # 3) Registrar en Libro de Caja (modelo real)
        mov = LibroCaja(
            sede_id=user.sede_id,
            fecha=fecha_pago,
            tipo=TipoMovimientoEnum.INGRESO,
            categoria_pago_id=categoria_pago_id,
            pago_id=nuevopago.id,
            monto=monto,
            concepto=f"{concepto}",
            usuario_registro_id=user.id,
        )
        db.add(mov)

        await db.commit()
        return {"success": True, "mensaje": "Pago registrado correctamente", "pago_id": nuevopago.id}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Error al registrar pago: {str(e)}")



@web_router.post("/api/v1/finanzas/gastos", tags=["Finanzas"])
async def registrar_gasto_egreso(
    request: Request,
    user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    """Registra Egresos (Servicios, Material, Sueldos) directamente en Caja."""
    if not user:
        raise HTTPException(401, "No autenticado")

    try:
        form = await request.form()

        # Datos del form
        monto_raw = form.get("monto")
        categoria_nombre = (form.get("categoria") or "").strip()
        detalle = (form.get("detalle") or "").strip()
        fecha_str = (form.get("fecha") or "").strip()  # opcional si tu form lo manda

        if not monto_raw:
            raise HTTPException(400, "Monto es requerido")
        if not categoria_nombre:
            raise HTTPException(400, "Categoría es requerida")
        if not detalle:
            raise HTTPException(400, "Detalle es requerido")

        monto = Decimal(monto_raw)
        fecha_egreso = (
            datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if fecha_str else datetime.now().date()
        )

        # 1) Buscar categoría (por sede)
        stmt = (
            select(CategoriaEgreso)
            .where(
                CategoriaEgreso.sede_id == user.sede_id,
                CategoriaEgreso.nombre.ilike(categoria_nombre),
            )
        )
        cat_obj = (await db.execute(stmt)).scalars().first()

        # 2) Crear categoría si no existe
        if not cat_obj:
            cat_obj = CategoriaEgreso(
                nombre=categoria_nombre.upper(),
                sede_id=user.sede_id,
                activo=True,
            )
            db.add(cat_obj)
            await db.flush()  # para obtener cat_obj.id

        # 3) Registro detallado egreso + movimiento caja
        from app.infrastructure.db.models.finanzas.egresos import Egreso
        from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum

        nuevo_egreso = Egreso(
            sede_id=user.sede_id,
            categoria_egreso_id=cat_obj.id,
            monto=monto,
            fecha_egreso=fecha_egreso,
            concepto=detalle,
            registrado_por=user.id,
        )
        db.add(nuevo_egreso)
        await db.flush()  # opcional: si luego necesitas nuevo_egreso.id

        mov = LibroCaja(
            sede_id=user.sede_id,
            fecha=fecha_egreso,
            tipo=TipoMovimientoEnum.EGRESO,
            categoria_egreso_id=cat_obj.id,
            monto=monto,
            concepto=detalle,
            usuario_registro_id=user.id,
            egreso_id=getattr(nuevo_egreso, "id", None),  # si tu modelo lo tiene
        )
        db.add(mov)

        await db.commit()

        return {"success": True, "mensaje": "Gasto registrado"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Error al registrar gasto: {str(e)}")

@web_router.post("/api/v1/finanzas/sueldos", tags=["Finanzas"])
async def registrar_pago_sueldo_directo(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Wrapper específico para sueldos que reutiliza la lógica de gastos"""
    # El frontend manda datos de sueldo, los convertimos a formato gasto
    data = await request.json()
    
    # Simulamos un request form para reutilizar la función de arriba
    # O simplemente insertamos directo aquí (más limpio):
    async with db.begin():
        # Buscar/Crear Categoría SUELDOS
        stmt = select(CategoriaEgreso).where(CategoriaEgreso.nombre == "SUELDOS", CategoriaEgreso.sede_id == user.sede_id)
        cat_obj = (await db.execute(stmt)).scalars().first()
        if not cat_obj:
            cat_obj = CategoriaEgreso(nombre="SUELDOS", sede_id=user.sede_id, activo=True)
            db.add(cat_obj)
            await db.flush()
            
        from app.infrastructure.db.models.finanzas.egresos import Egreso
        from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum

        detalle = f"Sueldo: {data.get('nombre')} - Cargo: {data.get('cargo')}"
        monto = Decimal(data.get('liquido_pagable'))

        # Egreso
        egreso = Egreso(
            sede_id=user.sede_id,
            categoria_egreso_id=cat_obj.id,
            monto=monto,
            fecha_egreso=datetime.now().date(),
            concepto=detalle,
            registrado_por=user.id
        )
        db.add(egreso)
        
        # Libro Caja
        mov = LibroCaja(
            sede_id=user.sede_id,
            fecha=datetime.now().date(),
            tipo=TipoMovimientoEnum.EGRESO,
            categoria_egreso_id=cat_obj.id,
            monto=monto,
            concepto=detalle,
            usuario_registro_id=user.id
        )
        db.add(mov)
        
    return {"success": True, "mensaje": "Sueldo registrado"}

@web_router.get("/api/v1/finanzas/arqueo", tags=["Finanzas"])
async def obtener_reporte_arqueo(
    mes: int = None,
    anio: int = None,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Genera el reporte idéntico al Excel 'EEFF' (Estados Financieros).
    """
    if not user: raise HTTPException(401)
    if not mes: mes = datetime.now().month
    if not anio: anio = datetime.now().year
    
    from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum
    
    # 1. Ingresos Reales (Caja)
    stmt_ingresos = (
        select(CategoriaPago.nombre, func.sum(LibroCaja.monto))
        .join(CategoriaPago, LibroCaja.categoria_pago_id == CategoriaPago.id)
        .where(
            LibroCaja.sede_id == user.sede_id,
            extract('month', LibroCaja.fecha) == mes,
            extract('year', LibroCaja.fecha) == anio,
            LibroCaja.tipo == TipoMovimientoEnum.INGRESO
        )
        .group_by(CategoriaPago.nombre)
    )
    ingresos_reales = {row[0]: float(row[1]) for row in (await db.execute(stmt_ingresos)).all()}
    
    # 2. Por Cobrar (Planificado)
    # Suma de todas las cuotas que vencían este mes
    stmt_por_cobrar = (
        select(func.sum(CuotaPlanPago.monto_cuota))
        .where(
            extract('month', CuotaPlanPago.fecha_vencimiento) == mes,
            extract('year', CuotaPlanPago.fecha_vencimiento) == anio
        )
    )
    total_por_cobrar = await db.scalar(stmt_por_cobrar) or 0.0
    
    # 3. Egresos (Gastos + Sueldos)
    stmt_egresos = (
        select(CategoriaEgreso.nombre, func.sum(LibroCaja.monto))
        .join(CategoriaEgreso, LibroCaja.categoria_egreso_id == CategoriaEgreso.id)
        .where(
            LibroCaja.sede_id == user.sede_id,
            extract('month', LibroCaja.fecha) == mes,
            extract('year', LibroCaja.fecha) == anio,
            LibroCaja.tipo == TipoMovimientoEnum.EGRESO
        )
        .group_by(CategoriaEgreso.nombre)
    )
    gastos = [{"categoria": row[0], "monto": float(row[1])} for row in (await db.execute(stmt_egresos)).all()]
    
    total_ingresos = sum(ingresos_reales.values())
    total_gastos = sum(g['monto'] for g in gastos)
    
    return {
        "resumen": {
            "ingreso_real": total_ingresos,
            "por_cobrar_estimado": float(total_por_cobrar),
            "total_gastos": total_gastos,
            "utilidad": total_ingresos - total_gastos
        },
        "detalles_ingreso": ingresos_reales,
        "detalles_gasto": gastos
    }

# --- GESTIÓN DE CATEGORÍAS ---

@web_router.get("/api/v1/finanzas/categorias/gestion", tags=["Finanzas"])
async def obtener_todas_categorias(
    tipo: str, 
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    Modelo = CategoriaPago if tipo == 'ingreso' else CategoriaEgreso
    stmt = select(Modelo).where(Modelo.sede_id == user.sede_id).order_by(Modelo.nombre)
    categorias = (await db.execute(stmt)).scalars().all()
    return [{"id": c.id, "nombre": c.nombre, "activo": c.activo} for c in categorias]

@web_router.put("/api/v1/finanzas/categorias/{id}/estado", tags=["Finanzas"])
async def cambiar_estado_categoria(
    id: int, tipo: str, activo: bool,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    Modelo = CategoriaPago if tipo == 'ingreso' else CategoriaEgreso
    cat = await db.get(Modelo, id)
    if cat:
        cat.activo = activo
        await db.commit()
    return {"success": True}

@web_router.post("/api/v1/finanzas/categorias/crear", tags=["Finanzas"])
async def crear_nueva_categoria(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    data = await request.json()
    tipo = data.get('tipo')
    nombre = data.get('nombre').upper()
    Modelo = CategoriaPago if tipo == 'ingreso' else CategoriaEgreso
    
    async with db.begin():
        nueva = Modelo(nombre=nombre, sede_id=user.sede_id, activo=True)
        db.add(nueva)
    return {"success": True}

@web_router.get("/api/v1/finanzas/pagos/historial", tags=["Finanzas"])
async def obtener_historial_pagos(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Devuelve el historial de pagos para la tabla de finanzas"""
    if not user:
        raise HTTPException(401, "No autenticado")
    
    try:
        # Filtros por fecha (últimos 30 días por defecto)
        hoy = datetime.now().date()
        f_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date() if fecha_desde else hoy - timedelta(days=30)
        f_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date() if fecha_hasta else hoy
        
        # ✅ CORRECCIÓN: Filtrar por sede a través del alumno
        stmt = (
            select(Pago)
            .join(Pago.alumno)  # JOIN con alumno
            .options(
                selectinload(Pago.alumno),
                selectinload(Pago.categoria)
            )
            .where(
                and_(
                    Alumno.sede_id == user.sede_id,  # ← Filtro por sede del alumno
                    Pago.fecha_pago >= f_desde,
                    Pago.fecha_pago <= f_hasta,
                    Pago.anulado == False
                )
            )
            .order_by(desc(Pago.fecha_pago), desc(Pago.id))
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        
        result = await db.execute(stmt)
        pagos = result.scalars().all()
        
        # Contar total (también con JOIN)
        count_stmt = (
            select(func.count(Pago.id))
            .join(Pago.alumno)
            .where(
                and_(
                    Alumno.sede_id == user.sede_id,
                    Pago.fecha_pago >= f_desde,
                    Pago.fecha_pago <= f_hasta,
                    Pago.anulado == False
                )
            )
        )
        total = await db.scalar(count_stmt) or 0
        
        # Construir respuesta
        items = []
        for p in pagos:
            # Nombre del alumno
            alumno_nombre = "N/A"
            if p.alumno:
                alumno_nombre = f"{p.alumno.apellido_paterno} {p.alumno.apellido_materno or ''} {p.alumno.nombre}".strip()
            
            # Nombre de la categoría
            categoria_nombre = "Pago"
            if p.categoria:
                categoria_nombre = p.categoria.nombre
            
            items.append({
                "id": p.id,
                "fecha": p.fecha_pago.strftime("%d/%m/%Y"),
                "tipo": "INGRESO",
                "detalle": f"{categoria_nombre} - {alumno_nombre}",
                "monto": float(p.monto_pagado),
                "metodo": p.metodo_pago or "EFECTIVO",
                "comprobante": p.numero_comprobante or "-"
            })
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "has_more": (page * per_page) < total
        }
    
    except Exception as e:
        print(f"❌ ERROR en historial: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Error: {str(e)}")

# ============================================================
# GESTIÓN DE CATEGORÍAS DE INGRESO/EGRESO
# ============================================================

@web_router.get("/finanzas/categorias/ingresos", response_class=HTMLResponse, name="categorias_ingresos")
async def pagina_categorias_ingresos(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Página de gestión de categorías de ingreso"""
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    return templates.TemplateResponse("finanzas/categorias_ingresos.html", {
        "request": request,
        "current_user": user,  # ✅ CAMBIO: usar current_user en lugar de user
        "page_title": "Categorías de Ingreso"
    })

@web_router.get("/finanzas/categorias/egresos", response_class=HTMLResponse, name="categorias_egresos")
async def pagina_categorias_egresos(
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Página de gestión de categorías de egreso"""
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    return templates.TemplateResponse("finanzas/categorias_egresos.html", {
        "request": request,
        "current_user": user,  # ✅ CAMBIO: usar current_user en lugar de user
        "page_title": "Categorías de Egreso"
    })


@web_router.get("/api/v1/finanzas/categorias/gestion", tags=["Finanzas"])
async def listar_categorias_gestion(
    tipo: str,  # 'ingreso' o 'egreso'
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Lista categorías para gestión (incluye inactivas)"""
    if not user:
        raise HTTPException(401, "No autenticado")
    
    try:
        if tipo.lower() == 'ingreso':
            stmt = select(CategoriaPago).where(
                CategoriaPago.sede_id == user.sede_id
            ).order_by(CategoriaPago.nombre)
            
            result = await db.execute(stmt)
            categorias = result.scalars().all()
            
            return [
                {
                    "id": c.id,
                    "nombre": c.nombre,
                    "activo": c.activo,
                    "creado_en": c.creado_en.strftime("%d/%m/%Y") if c.creado_en else None
                }
                for c in categorias
            ]
        
        elif tipo.lower() == 'egreso':
            stmt = select(CategoriaEgreso).where(
                CategoriaEgreso.sede_id == user.sede_id
            ).order_by(CategoriaEgreso.nombre)
            
            result = await db.execute(stmt)
            categorias = result.scalars().all()
            
            return [
                {
                    "id": c.id,
                    "nombre": c.nombre,
                    "activo": c.activo,
                    "creado_en": c.creado_en.strftime("%d/%m/%Y") if c.creado_en else None
                }
                for c in categorias
            ]
        else:
            raise HTTPException(400, "Tipo debe ser 'ingreso' o 'egreso'")
    
    except Exception as e:
        print(f"❌ Error listando categorías: {e}")
        raise HTTPException(500, str(e))

@web_router.patch("/api/v1/finanzas/categorias/{categoria_id}/toggle", tags=["Finanzas"])
async def toggle_categoria_estado(
    categoria_id: int,
    tipo: str,  # 'ingreso' o 'egreso'
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Activa/desactiva una categoría"""
    if not user:
        raise HTTPException(401)
    
    try:
        if tipo == 'ingreso':
            categoria = await db.get(CategoriaPago, categoria_id)
        else:
            categoria = await db.get(CategoriaEgreso, categoria_id)
        
        if not categoria:
            raise HTTPException(404, "Categoría no encontrada")
        
        if categoria.sede_id != user.sede_id:
            raise HTTPException(403, "No tiene permiso")
        
        # Toggle estado
        categoria.activo = not categoria.activo
        await db.commit()
        
        return {
            "success": True,
            "activo": categoria.activo,
            "mensaje": f"Categoría {'activada' if categoria.activo else 'desactivada'}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"❌ Error: {e}")
        raise HTTPException(500, str(e))

@web_router.put("/api/v1/finanzas/categorias/{categoria_id}/editar", tags=["Finanzas"])
async def editar_categoria(
    categoria_id: int,
    request: Request,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Edita el nombre de una categoría"""
    if not user:
        raise HTTPException(401)
    
    try:
        data = await request.json()
        nuevo_nombre = data.get('nombre', '').strip()
        tipo = data.get('tipo', 'ingreso')
        
        if not nuevo_nombre:
            raise HTTPException(400, "El nombre no puede estar vacío")
        
        # Obtener categoría
        if tipo == 'ingreso':
            categoria = await db.get(CategoriaPago, categoria_id)
        else:
            categoria = await db.get(CategoriaEgreso, categoria_id)
        
        if not categoria:
            raise HTTPException(404, "Categoría no encontrada")
        
        if categoria.sede_id != user.sede_id:
            raise HTTPException(403, "No tiene permiso")
        
        # Verificar duplicados
        if tipo == 'ingreso':
            stmt = select(CategoriaPago).where(
                and_(
                    CategoriaPago.sede_id == user.sede_id,
                    CategoriaPago.nombre == nuevo_nombre,
                    CategoriaPago.id != categoria_id
                )
            )
        else:
            stmt = select(CategoriaEgreso).where(
                and_(
                    CategoriaEgreso.sede_id == user.sede_id,
                    CategoriaEgreso.nombre == nuevo_nombre,
                    CategoriaEgreso.id != categoria_id
                )
            )
        
        existe = await db.scalar(select(func.count()).select_from(stmt.subquery()))
        
        if existe > 0:
            raise HTTPException(400, "Ya existe una categoría con ese nombre")
        
        # Actualizar
        categoria.nombre = nuevo_nombre
        await db.commit()
        
        return {
            "success": True,
            "mensaje": "Categoría actualizada"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"❌ Error: {e}")
        raise HTTPException(500, str(e))


@web_router.put("/api/v1/finanzas/categorias/{categoria_id}/estado", tags=["Finanzas"])
async def actualizar_estado_categoria(
    categoria_id: int,
    tipo: str,
    activo: bool,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Activa o desactiva una categoría"""
    if not user:
        raise HTTPException(401, "No autenticado")
    
    try:
        # Seleccionar modelo según tipo
        if tipo == 'ingreso':
            categoria = await db.get(CategoriaPago, categoria_id)
        elif tipo == 'egreso':
            categoria = await db.get(CategoriaEgreso, categoria_id)
        else:
            raise HTTPException(400, "Tipo debe ser 'ingreso' o 'egreso'")
        
        if not categoria:
            raise HTTPException(404, "Categoría no encontrada")
        
        # Verificar permisos de sede
        if categoria.sede_id != user.sede_id:
            raise HTTPException(403, "No tiene permiso para modificar esta categoría")
        
        # Actualizar estado
        categoria.activo = activo
        await db.commit()
        
        return {
            "success": True,
            "mensaje": f"Categoría {'activada' if activo else 'desactivada'} correctamente"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"❌ Error actualizando estado: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Error: {str(e)}")

# ... (debajo de @web_router.get("/finanzas"...) )

@web_router.get("/finanzas/planes-pago", response_class=HTMLResponse)
async def planes_pago_page(request: Request, user = Depends(get_current_user_optional)):
    """Vista para gestionar los planes de pago"""
    if not user: return RedirectResponse("/login")
    
    # Asegúrate de que el archivo planes_pago.html esté en la carpeta templates/finanzas/
    # Si está en la raíz de templates, usa solo "planes_pago.html"
    return templates.TemplateResponse("finanzas/planes_pago.html", {
        "request": request, 
        "current_user": user, 
        "page_title": "Gestión de Planes de Pago",
        "active_menu": "finanzas"
    })


# --- AGREGAR EN ROUTES.PY (SECCIÓN FINANZAS) ---

@web_router.get("/api/v1/finanzas/planes-pago/alumno/{alumno_id}", tags=["Finanzas"])
async def obtener_detalle_plan_alumno(
    alumno_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Obtiene el plan completo (pagadas y no pagadas) para la vista de gestión"""
    if not user: raise HTTPException(401)

    # 1. Buscar el plan activo
    stmt_plan = select(PlanPagoPersonalizado).where(
        PlanPagoPersonalizado.alumno_id == alumno_id,
        PlanPagoPersonalizado.estado == 'activo' # O el estado que uses por defecto
    )
    plan = (await db.execute(stmt_plan)).scalars().first()

    if not plan:
        return {"tiene_plan": False, "mensaje": "No hay plan activo"}

    # 2. Buscar todas las cuotas (ordenadas por fecha)
    stmt_cuotas = select(CuotaPlanPago).where(
        CuotaPlanPago.plan_id == plan.id
    ).order_by(CuotaPlanPago.fecha_vencimiento)
    
    cuotas_db = (await db.execute(stmt_cuotas)).scalars().all()

    # 3. Formatear para el Frontend
    lista_cuotas = []
    meses_str = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    for c in cuotas_db:
        # Calcular estado visual
        estado_final = c.estado
        # Si está pendiente y la fecha ya pasó, es MORA
        if c.estado == 'pendiente' and c.fecha_vencimiento < datetime.now().date():
            estado_final = 'mora'

        lista_cuotas.append({
            "numero": c.numero_cuota,
            "mes": meses_str[c.numero_cuota] if 1 <= c.numero_cuota <= 12 else "Extra",
            "vencimiento": c.fecha_vencimiento.strftime("%d/%m/%Y"),
            "monto_total": float(c.monto_cuota),
            "monto_pagado": float(c.monto_pagado),
            "saldo": float(c.monto_cuota - c.monto_pagado),
            "estado": estado_final.upper() # PENDIENTE, PAGADO, MORA
        })

    return {
        "tiene_plan": True,
        "resumen": {
            "total_plan": float(plan.monto_total),
            "tipo": "Personalizado" # O derivar de lógica si guardaste el tipo
        },
        "cuotas": lista_cuotas
    }


@web_router.get("/api/v1/finanzas/deudores", tags=["Finanzas"])
async def obtener_reporte_deudores(
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    print(">>> ENTRANDO A ENDPOINT DEUDORES (DEBUG) <<<") # Si no ves esto, no se actualizó el archivo
    if not user: raise HTTPException(401)

    hoy = datetime.now().date()

    try:
        # Consulta simplificada para probar
        print(">>> CONSTRUYENDO QUERY...")
        stmt = (
            select(
                CuotaPlanPago, 
                Alumno.nombre,           # Asegúrate que sea PLURAL si tu tabla es así
                Alumno.apellido_paterno,  
                Alumno.apellido_materno,  
                Alumno.id.label("alumno_id")
            )
            .join(PlanPagoPersonalizado, CuotaPlanPago.plan_id == PlanPagoPersonalizado.id)
            .join(Alumno, PlanPagoPersonalizado.alumno_id == Alumno.id)
            .where(
                CuotaPlanPago.estado == 'pendiente',
                CuotaPlanPago.fecha_vencimiento < hoy,
                Alumno.sede_id == user.sede_id 
            )
            .order_by(CuotaPlanPago.fecha_vencimiento)
        )
        
        print(">>> EJECUTANDO QUERY...")
        resultados = (await db.execute(stmt)).all()
        print(f">>> QUERY EXITOSA. RESULTADOS: {len(resultados)}")

        lista_deudores = []
        for row in resultados:
            cuota = row[0]
            nombres = row[1] 
            paterno = row[2] or ""
            materno = row[3] or ""
            alumno_id = row[4]
            
            nombre_completo = f"{paterno} {materno}, {nombres}".strip().replace("  ", " ")
            dias_atraso = (hoy - cuota.fecha_vencimiento).days
            
            lista_deudores.append({
                "alumnoid": alumno_id,
                "nombrecompleto": nombre_completo,
                "concepto": f"Cuota #{cuota.numero_cuota} (Vencía: {cuota.fecha_vencimiento.strftime('%d/%m')})",
                "cuotanumero": cuota.numero_cuota,
                "diasatraso": dias_atraso,
                "totalexigible": float(cuota.monto_cuota - cuota.monto_pagado)
            })

        return lista_deudores

    except Exception as e:
        print(f"!!! ERROR FATAL EN DEUDORES: {str(e)}")
        import traceback
        traceback.print_exc() # Esto imprimirá el error real en la consola negra
        return []

# app/interfaces/web/routes.py

# --- REEMPLAZAR EN ROUTES.PY (SECCIÓN FINANZAS) ---

# --- REEMPLAZAR EN ROUTES.PY ---

@web_router.get("/api/v1/finanzas/movimientos", tags=["Finanzas"])
async def obtener_movimientos_caja(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    tipo: Optional[str] = None, # 'INGRESO' o 'EGRESO'
    limit: int = 100,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Consulta Libro Caja unificado.
    CORRECCIÓN: Usa outerjoin explícito para evitar error de atributos faltantes.
    """
    if not user: raise HTTPException(401)
    
    # Importamos modelos necesarios
    from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum
    from app.infrastructure.db.models.finanzas.pagos import Pago
    from app.infrastructure.db.models.finanzas.categorias_pago import CategoriaPago
    from app.infrastructure.db.models.finanzas.categorias_egreso import CategoriaEgreso
    
    
    # 1. Filtros
    condiciones = [LibroCaja.sede_id == user.sede_id]
    
    if fecha_desde:
        condiciones.append(LibroCaja.fecha >= datetime.strptime(fecha_desde, "%Y-%m-%d").date())
    if fecha_hasta:
        condiciones.append(LibroCaja.fecha <= datetime.strptime(fecha_hasta, "%Y-%m-%d").date())
        
    if tipo and tipo in ['INGRESO', 'EGRESO']:
        tipo_enum = TipoMovimientoEnum.INGRESO if tipo == 'INGRESO' else TipoMovimientoEnum.EGRESO
        condiciones.append(LibroCaja.tipo == tipo_enum)

    # 2. Query Principal con JOINs Explícitos
    # Traemos el LibroCaja y columnas específicas de las otras tablas
    stmt = (
        select(
            LibroCaja,
            Pago.metodo_pago,
            Pago.numero_comprobante,
            CategoriaPago.nombre.label("nombre_cat_ingreso"),
            CategoriaEgreso.nombre.label("nombre_cat_egreso"),
            #### <--- AGREGAR ESTOS CAMPOS AL SELECT:
            Alumno.nombre,           
            Alumno.apellido_paterno,   
            Alumno.apellido_materno,
            Pago.id.label("pago_id_real") # Necesario para el botón de recibo
        )
        .outerjoin(Pago, LibroCaja.pago_id == Pago.id)
        .outerjoin(CategoriaPago, LibroCaja.categoria_pago_id == CategoriaPago.id)
        .outerjoin(CategoriaEgreso, LibroCaja.categoria_egreso_id == CategoriaEgreso.id)
        .outerjoin(Alumno, Pago.alumno_id == Alumno.id) 
        .where(and_(*condiciones))
        .order_by(desc(LibroCaja.fecha), desc(LibroCaja.id))
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    # 3. Calcular Totales (Resumen)
    stmt_sum = (
        select(LibroCaja.tipo, func.sum(LibroCaja.monto))
        .where(and_(*condiciones))
        .group_by(LibroCaja.tipo)
    )
    res_sum = await db.execute(stmt_sum)
    totales_raw = res_sum.all()
    
    suma_ing = 0.0
    suma_egr = 0.0
    for t, m in totales_raw:
        if t == TipoMovimientoEnum.INGRESO: suma_ing = float(m or 0)
        elif t == TipoMovimientoEnum.EGRESO: suma_egr = float(m or 0)

    # 4. Formatear Items para la Tabla
    lista_items = []
    for row in rows:
        # Desempaquetar la tupla del resultado
        mov = row[0] # Objeto LibroCaja
        metodo = row[1]
        comprobante = row[2]
        cat_ingreso = row[3]
        cat_egreso = row[4]
        #### <--- AGREGAR ESTAS VARIABLES NUEVAS:
        a_nombres = row[5]
        a_paterno = row[6]
        a_materno = row[7]
        pago_id_real = row[8]

        # Determinar nombre de categoría
        nombre_categoria = "-"
        if mov.tipo == TipoMovimientoEnum.INGRESO:
            nombre_categoria = cat_ingreso or "Ingreso General"
        else:
            nombre_categoria = cat_egreso or "Gasto General"
        #### <--- AGREGAR LÓGICA DE NOMBRE:
        detalle_final = mov.concepto
        if a_nombres: # Si hay datos del alumno
            nombre_completo = f"{a_paterno or ''} {a_materno or ''}, {a_nombres}".strip()
            # Lo concatenamos al detalle para que se vea en la tabla
            detalle_final = f"{detalle_final} - {nombre_completo}"

        lista_items.append({
            "id": mov.id,
            "pago_id": pago_id_real,
            "fecha": mov.fecha.strftime("%d/%m/%Y"),
            "tipo": mov.tipo.name if hasattr(mov.tipo, 'name') else str(mov.tipo), 
            "categoria": nombre_categoria,
            "detalle": detalle_final,
            "metodo": metodo or "EFECTIVO",
            "comprobante": comprobante,
            "monto": float(mov.monto)
        })

    return {
        "resumen": {
            "total_ingresos": suma_ing,
            "total_egresos": suma_egr,
            "saldo": suma_ing - suma_egr
        },
        "items": lista_items
    }


# --- REEMPLAZAR EN ROUTES.PY ---

@web_router.get("/api/v1/usuarios/me", tags=["Usuarios"])
async def obtener_usuario_actual(
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Retorna la información del usuario logueado actualmente.
    Carga roles (Muchos a Muchos) y usa los atributos correctos.
    """
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        # Imports locales para garantizar visibilidad
        from app.infrastructure.db.models.seguridad.usuarios import Usuario 
        from sqlalchemy.orm import selectinload

        # 1. Consulta para recargar al usuario con sus ROLES
        stmt = (
            select(Usuario)
            .options(selectinload(Usuario.roles)) # Usamos 'roles' (plural)
            .where(Usuario.id == user.id)
        )
        result = await db.execute(stmt)
        user_full = result.scalars().first()

        if not user_full:
             raise HTTPException(401, "Usuario no encontrado")

        # 2. Procesar Roles (Unir por comas si tiene varios, o 'Usuario' si no tiene)
        rol_nombre = "Usuario"
        if user_full.roles and len(user_full.roles) > 0:
            # Crea un string como: "ADMINISTRADOR, PROFESORA"
            rol_nombre = ", ".join([r.nombre for r in user_full.roles])

        # 3. Retornar Objeto
        return {
            "id": user_full.id,
            "username": user_full.username, # ✅ CORRECTO: Es 'username'
            "nombres": user_full.nombres,
            "apellidos": user_full.apellidos,
            "nombre_completo": f"{user_full.nombres} {user_full.apellidos or ''}".strip(),
            "rol_nombre": rol_nombre,
            "avatar": getattr(user_full, 'avatar', None)
        }

    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN /usuarios/me: {e}")
        import traceback
        traceback.print_exc()
        # Mensaje genérico para no exponer traza al frontend, pero logueado en consola
        raise HTTPException(status_code=500, detail="Error interno al obtener perfil de usuario.")


# --- AGREGAR EN ROUTES.PY ---

@web_router.get("/api/v1/finanzas/reporte-sueldos", tags=["Finanzas"])
async def obtener_reporte_sueldos(
    mes: int,
    anio: int,
    estado: str = "todos", # todos, pagado, pendiente
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Compara usuarios con rol PROFESORA vs Egresos de categoría 'SUELDOS' del mes.
    """
    if not user: raise HTTPException(401)

    # 1. Obtener todas las profesoras activas
    # Asumimos que el rol se llama 'PROFESORA' o similar
    stmt_profes = (
        select(Usuario)
        .join(Usuario.roles)
        .where(
            Usuario.sede_id == user.sede_id,
            Usuario.activo == True,
            Rol.nombre.ilike("%PROFESORA%") 
        )
        .order_by(Usuario.nombres)
    )
    profesoras = (await db.execute(stmt_profes)).scalars().all()

    # 2. Obtener Egresos de categoría "SUELDOS" en ese mes/año
    # Buscamos coincidencias en el detalle o un campo metadata si existiera
    from sqlalchemy import extract
    stmt_pagos = (
        select(Egreso)
        .join(CategoriaEgreso)
        .where(
            Egreso.sede_id == user.sede_id,
            CategoriaEgreso.nombre.ilike("SUELDOS"),
            extract('month', Egreso.fecha_egreso) == mes,
            extract('year', Egreso.fecha_egreso) == anio
        )
    )
    pagos_realizados = (await db.execute(stmt_pagos)).scalars().all()

    # 3. Cruzar información (Matching por nombre en el concepto/detalle)
    # Como no tenemos campo ID en Egreso, buscamos el nombre de la profe dentro del string 'concepto'
    reporte = []
    
    for profe in profesoras:
        nombre_completo = f"{profe.nombres} {profe.apellidos}".strip()
        pago_encontrado = None
        
        # Búsqueda simple: ¿El nombre de la profe está en el detalle del pago?
        for pago in pagos_realizados:
            if nombre_completo.lower() in pago.concepto.lower():
                pago_encontrado = pago
                break
        
        item = {
            "profesora_id": profe.id,
            "nombre": nombre_completo,
            "estado": "PAGADO" if pago_encontrado else "PENDIENTE",
            "monto": float(pago_encontrado.monto) if pago_encontrado else 0.0,
            "fecha_pago": pago_encontrado.fecha_egreso.strftime("%d/%m/%Y") if pago_encontrado else "-"
        }

        # Filtro de backend
        if estado == "pagado" and not pago_encontrado: continue
        if estado == "pendiente" and pago_encontrado: continue
        
        reporte.append(item)

    return reporte

# --------------------------
# 1. FAMILIAS Y CATEGORIAS
# --------------------------

@web_router.get("/api/v1/inventarios/familias", tags=["Inventario"])
async def listar_familias(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Familia).where(Familia.activo == True))
    return result.scalars().all()

@web_router.post("/api/v1/inventarios/familias", tags=["Inventario"])
async def crear_familia(nombre: str = Body(...), descripcion: str = Body(None), db: AsyncSession = Depends(get_session)):
    # Validar duplicados
    existe = await db.execute(select(Familia).where(Familia.nombre == nombre))
    if existe.scalars().first():
        raise HTTPException(400, "Ya existe una familia con este nombre")
    
    nueva = Familia(nombre=nombre, descripcion=descripcion)
    db.add(nueva)
    await db.commit()
    return {"mensaje": "Familia creada", "id": nueva.id, "nombre": nueva.nombre}

@web_router.get("/api/v1/inventarios/categorias", tags=["Inventario"])
async def listar_categorias(familia_id: Optional[int] = None, db: AsyncSession = Depends(get_session)):
    stmt = select(Categoria).where(Categoria.activo == True).options(selectinload(Categoria.familia))
    if familia_id:
        stmt = stmt.where(Categoria.familia_id == familia_id)
    result = await db.execute(stmt)
    categorias = result.scalars().all()
    # Retornamos estructura plana para el frontend
    return [{
        "id": c.id, 
        "nombre": c.nombre, 
        "familia_id": c.familia_id, 
        "familia_nombre": c.familia.nombre if c.familia else "Sin Familia"
    } for c in categorias]

@web_router.post("/api/v1/inventarios/categorias", tags=["Inventario"])
async def crear_categoria(
    nombre: str = Body(...), 
    familia_id: int = Body(...), 
    descripcion: str = Body(None), 
    db: AsyncSession = Depends(get_session)
):
    nueva = Categoria(nombre=nombre, familia_id=familia_id, descripcion=descripcion)
    db.add(nueva)
    await db.commit()
    return {"mensaje": "Categoría creada", "id": nueva.id, "nombre": nueva.nombre}

# --------------------------
# 2. ITEMS (PRODUCTOS)
# --------------------------

@web_router.get("/api/v1/inventarios/items", tags=["Inventario"])
async def listar_items(
    search: Optional[str] = None, 
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    
    # Query compleja: Item + Categoria + Stock en la Sede del Usuario
    stmt = (
        select(Item, StockSede.cantidad_disponible)
        .outerjoin(StockSede, (StockSede.item_id == Item.id) & (StockSede.sede_id == user.sede_id))
        .options(
            selectinload(Item.categoria).selectinload(Categoria.familia),
            selectinload(Item.atributos)
        )
        .where(Item.activo == True)
        .order_by(Item.nombre)
    )
    
    if search:
        stmt = stmt.where(or_(Item.nombre.ilike(f"%{search}%"), Item.codigo.ilike(f"%{search}%")))
        
    result = await db.execute(stmt)
    rows = result.all()
    
    data = []
    for item, stock in rows:
        data.append({
            "id": item.id,
            "codigo": item.codigo,
            "nombre": item.nombre,
            "categoria": item.categoria.nombre if item.categoria else "-",
            "familia": item.categoria.familia.nombre if item.categoria and item.categoria.familia else "-",
            "precio": float(item.precio_unitario),
            "stock": float(stock or 0), # Si no hay registro de stock, es 0
            "unidad": item.unidad_medida,
            "atributos": {attr.nombre_atributo: attr.valor_atributo for attr in item.atributos}
        })
    return data

# En app/interfaces/web/routes.py (Dentro de POST /inventarios/items)

@web_router.post("/api/v1/inventarios/items", tags=["Inventario"])
async def crear_item(
    payload: dict = Body(...),
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Crea Item + Atributos + Stock Inicial y Mínimo configurables
    """
    if not user: raise HTTPException(401)
    
    try:
        # 1. Generar SKU Automático
        cat = await db.get(Categoria, payload['categoria_id'])
        if not cat: raise HTTPException(404, "Categoría no encontrada")
        
        stmt_fam = select(Familia).where(Familia.id == cat.familia_id)
        fam = (await db.execute(stmt_fam)).scalars().first()
        
        prefix_fam = fam.nombre[:3].upper() if fam else "GEN"
        prefix_cat = cat.nombre[:3].upper()
        
        last_item = await db.execute(
            select(Item.codigo)
            .where(Item.codigo.like(f"{prefix_fam}-{prefix_cat}-%"))
            .order_by(desc(Item.id))
            .limit(1)
        )
        last_code = last_item.scalars().first()
        
        new_seq = 1
        if last_code:
            try:
                new_seq = int(last_code.split('-')[-1]) + 1
            except: pass
                
        sku = f"{prefix_fam}-{prefix_cat}-{new_seq:03d}"
        
        # 2. Crear Item
        nuevo_item = Item(
            categoria_id=payload['categoria_id'],
            codigo=sku,
            nombre=payload['nombre'],
            descripcion=payload.get('descripcion'),
            precio_unitario=payload['precio'],
            unidad_medida=payload.get('unidad', 'UNIDAD') # Recibe la unidad personalizada
        )
        db.add(nuevo_item)
        await db.flush()
        
        # 3. Guardar Atributos
        atributos = payload.get('atributos', [])
        for attr in atributos:
            if attr.get('nombre') and attr.get('valor'):
                new_attr = ItemAtributo(
                    item_id=nuevo_item.id,
                    nombre_atributo=attr['nombre'],
                    valor_atributo=attr['valor']
                )
                db.add(new_attr)
        
        # 4. Inicializar Stock (CORREGIDO: Usa los valores del formulario)
        stock_inicial = StockSede(
            item_id=nuevo_item.id,
            sede_id=user.sede_id,
            cantidad_disponible=payload.get('stock_inicial', 0), # <--- Aquí entra lo que escribas
            stock_minimo=payload.get('stock_minimo', 5)          # <--- Aquí entra el mínimo config
        )
        db.add(stock_inicial)
        
        await db.commit()
        return {"mensaje": "Producto creado exitosamente", "codigo": sku}
        
    except Exception as e:
        await db.rollback()
        print(f"Error creando item: {e}")
        raise HTTPException(500, f"Error al crear producto: {str(e)}")
# --------------------------
# 3. MOVIMIENTOS DE STOCK
# --------------------------

@web_router.post("/api/v1/inventarios/movimientos", tags=["Inventario"])
async def registrar_movimiento(
    item_id: int = Body(...),
    tipo: str = Body(...), # 'entrada' o 'salida'
    cantidad: float = Body(...),
    motivo: str = Body(...),
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    
    # Obtener stock actual
    stmt = select(StockSede).where(StockSede.item_id == item_id, StockSede.sede_id == user.sede_id)
    result = await db.execute(stmt)
    stock_record = result.scalars().first()
    
    if not stock_record:
        # Si no existe registro (caso raro si se creó con el item), lo creamos
        stock_record = StockSede(item_id=item_id, sede_id=user.sede_id, cantidad_disponible=0)
        db.add(stock_record)
    
    # Lógica de cálculo
    if tipo == 'salida':
        if stock_record.cantidad_disponible < cantidad:
            raise HTTPException(400, f"Stock insuficiente. Disponible: {stock_record.cantidad_disponible}")
        stock_record.cantidad_disponible -= Decimal(cantidad)
        enum_tipo = TipoMovimiento.salida
    else:
        stock_record.cantidad_disponible += Decimal(cantidad)
        enum_tipo = TipoMovimiento.entrada
        
    # Registrar Historial
    nuevo_mov = MovimientoStock(
        item_id=item_id,
        sede_id=user.sede_id,
        tipo=enum_tipo,
        cantidad=cantidad,
        motivo=motivo,
        usuario_id=user.id,
        fecha_movimiento=datetime.now().date()
    )
    db.add(nuevo_mov)
    await db.commit()
    
    return {"mensaje": "Movimiento registrado", "nuevo_stock": stock_record.cantidad_disponible}

# --------------------------
# 4. PRESTAMOS DE UNIFORMES
# --------------------------

@web_router.get("/api/v1/inventarios/prestamos", tags=["Inventario"])
async def listar_prestamos(user = Depends(get_current_user_optional), db: AsyncSession = Depends(get_session)):
    # Listamos préstamos pendientes
    stmt = (
        select(PrestamoUniforme)
        .options(selectinload(PrestamoUniforme.alumno), selectinload(PrestamoUniforme.item))
        .where(PrestamoUniforme.devuelto == False)
        .order_by(PrestamoUniforme.fecha_prestamo)
    )
    result = await db.execute(stmt)
    prestamos = result.scalars().all()
    
    return [{
        "id": p.id,
        "item": p.item.nombre,
        "beneficiario": f"{p.alumno.nombre} {p.alumno.apellido_paterno}" if p.alumno else "Desconocido", # OJO: Modelo usa Alumno
        "fecha": p.fecha_prestamo,
        "estado": "Pendiente"
    } for p in prestamos]

@web_router.post("/api/v1/inventarios/prestamos", tags=["Inventario"])
async def crear_prestamo(
    item_id: int = Body(...),
    beneficiario_id: int = Body(...), # ID de Alumno (Profesora conceptualmente según HU)
    cantidad: int = Body(1), # Por defecto 1 uniforme
    db: AsyncSession = Depends(get_session)
):
    # Nota: El modelo PrestamoUniforme no tiene campo 'cantidad', se asume 1 registro por item prestado.
    # Si se prestan 2, se deberían crear 2 registros o modificar el modelo. Asumiremos 1 por ahora.
    
    nuevo_prestamo = PrestamoUniforme(
        item_id=item_id,
        alumno_id=beneficiario_id, # Usamos el campo del modelo (alumno_id)
        fecha_prestamo=datetime.now().date(),
        devuelto=False
    )
    db.add(nuevo_prestamo)
    
    # Opcional: ¿El préstamo descuenta stock?
    # Según lógica estándar sí, debería.
    # ... Lógica de descuento de stock aquí si se requiere ...
    
    await db.commit()
    return {"mensaje": "Préstamo registrado"}

@web_router.patch("/api/v1/inventarios/prestamos/{id}/devolver", tags=["Inventario"])
async def devolver_prestamo(id: int, db: AsyncSession = Depends(get_session)):
    prestamo = await db.get(PrestamoUniforme, id)
    if not prestamo: raise HTTPException(404)
    
    prestamo.devuelto = True
    prestamo.fecha_devolucion = datetime.now().date()
    await db.commit()
    return {"mensaje": "Devolución registrada"}


@web_router.get("/api/v1/inventarios/movimientos", tags=["Inventario"])
async def listar_movimientos_stock(
    tipo: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    
    stmt = (
        select(MovimientoStock)
        .options(selectinload(MovimientoStock.item), selectinload(MovimientoStock.usuario))
        .where(MovimientoStock.sede_id == user.sede_id)
        .order_by(desc(MovimientoStock.creado_en))
    )
    
    if tipo:
        try:
            # Importar el Enum si no está disponible en el scope
            from app.infrastructure.db.models.inventario.movimientos_stock import TipoMovimiento
            tipo_enum = TipoMovimiento[tipo.lower()]
            stmt = stmt.where(MovimientoStock.tipo == tipo_enum)
        except: pass
        
    if start_date:
        stmt = stmt.where(MovimientoStock.fecha_movimiento >= start_date)
    if end_date:
        stmt = stmt.where(MovimientoStock.fecha_movimiento <= end_date)
        
    result = await db.execute(stmt)
    movs = result.scalars().all()
    
    return [{
        "id": m.id,
        "fecha": m.fecha_movimiento.strftime("%d/%m/%Y"),
        "tipo": m.tipo.name.upper(),
        "item": m.item.nombre if m.item else "Item eliminado",
        "cantidad": float(m.cantidad),
        "motivo": m.motivo,
        # ✅ CORRECCIÓN AQUÍ: Usar .username en lugar de .nombre_usuario
        "usuario": m.usuario.username if m.usuario else "-" 
    } for m in movs]

    # --- AGREGAR EN ROUTES.PY (Sección Inventario) ---

@web_router.get("/api/v1/inventarios/metricas", tags=["Inventario"])
async def obtener_metricas_inventario(
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Retorna los KPIs principales para el dashboard de inventario.
    """
    if not user: raise HTTPException(401)
    
    try:
        from datetime import date
        from sqlalchemy import func, cast, Numeric
        
        # 1. Total Productos (Activos)
        stmt_total = select(func.count(Item.id)).where(Item.activo == True)
        total_productos = (await db.execute(stmt_total)).scalar() or 0
        
        # 2. Valor Total del Inventario (Precio * Stock Disponible en mi sede)
        # Hacemos JOIN entre StockSede e Item
        stmt_valor = (
            select(func.sum(StockSede.cantidad_disponible * Item.precio_unitario))
            .join(Item, StockSede.item_id == Item.id)
            .where(StockSede.sede_id == user.sede_id)
        )
        valor_total = (await db.execute(stmt_valor)).scalar() or 0.0
        
        # 3. Alertas de Stock Bajo (Disponible <= Minimo)
        stmt_bajo = (
            select(func.count(StockSede.id))
            .where(
                StockSede.sede_id == user.sede_id,
                StockSede.cantidad_disponible <= StockSede.stock_minimo
            )
        )
        stock_bajo = (await db.execute(stmt_bajo)).scalar() or 0
        
        # 4. Movimientos de Hoy
        stmt_movs = (
            select(func.count(MovimientoStock.id))
            .where(
                MovimientoStock.sede_id == user.sede_id,
                MovimientoStock.fecha_movimiento == date.today()
            )
        )
        movimientos_hoy = (await db.execute(stmt_movs)).scalar() or 0
        
        return {
            "total_productos": total_productos,
            "valor_inventario": float(valor_total),
            "stock_bajo": stock_bajo,
            "movimientos_hoy": movimientos_hoy
        }

    except Exception as e:
        print(f"Error calculando métricas: {e}")
        return {
            "total_productos": 0,
            "valor_inventario": 0.0,
            "stock_bajo": 0,
            "movimientos_hoy": 0
        }
    
# --- VISTA HTML PRINCIPAL ---
@web_router.get("/cursos-extra", response_class=HTMLResponse, tags=["Vistas"])
async def vista_cursos_extra(request: Request, user=Depends(get_current_user_optional)):
    if not user: return RedirectResponse("/login")
    return templates.TemplateResponse("cursos_extra/index.html", {
            "request": request, 
            "current_user": user,  # <--- AQUÍ ESTABA EL ERROR
            "user": user,           # Enviamos ambos por seguridad si alguna vista interna usa 'user'
            "active_menu": "cursos_extra"
        })

# --------------------------
# 1. GESTIÓN DE CURSOS
# --------------------------

# --- EN ROUTES.PY (Reemplazar la función 'listarcursosextra' que está fallando) ---

@web_router.get("/api/v1/cursos-extra", tags=["Cursos Extra"])
async def listar_cursos_extra(
    activo: bool = Query(True), 
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Lista los cursos extra de la sede del usuario actual.
    CORREGIDO: Usa los nombres de atributos con guiones bajos (snake_case).
    """
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        # 1. Consulta Principal
        stmt = (
            select(CursoExtra, IngresoCursoExtra)
            .outerjoin(IngresoCursoExtra, IngresoCursoExtra.curso_extra_id == CursoExtra.id) # ✅ curso_extra_id
            .where(
                CursoExtra.sede_id == user.sede_id, # ✅ sede_id
                CursoExtra.activo == activo
            )
            .order_by(desc(CursoExtra.id))
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        data = []
        for curso, finanza in rows:
            # 2. Subconsulta de Inscritos
            stmt_count = select(func.count(InscripcionCursoExtra.id)).where(
                InscripcionCursoExtra.curso_extra_id == curso.id, # ✅ curso_extra_id
                InscripcionCursoExtra.estado != EstadoInscripcionCursoExtra.RETIRADO
            )
            inscritos = (await db.execute(stmt_count)).scalar() or 0
            
            # 3. Construcción del JSON (Usando nombres correctos)
            data.append({
                "id": curso.id,
                "nombre": curso.nombre,
                "instructor": curso.instructor,
                "gestion": curso.gestion,
                # ✅ Fechas con guión bajo
                "fechas": f"{curso.fecha_inicio} al {curso.fecha_fin or 'Indefinido'}",
                "precios": {
                    # ✅ Precios con guión bajo
                    "interno": float(curso.precio_interno), 
                    "externo": float(curso.precio_externo)
                },
                "cupos": {
                    "max": curso.cupo_maximo, # ✅ cupo_maximo
                    "ocupados": inscritos
                },
                "finanzas": {
                    # ✅ Campos de finanzas con guión bajo
                    "ingresos": float(finanza.total_ingresos) if finanza else 0.0,
                    "gastos": float(finanza.total_gastos) if finanza else 0.0,
                    "ganancia_institucion": float(finanza.ganancia_institucion) if finanza else 0.0
                }
            })
            
        return data

    except Exception as e:
        print(f"Error listando cursos: {e}")
        # Importante: Imprimir el error completo para debug si vuelve a fallar
        import traceback
        traceback.print_exc()
        return []

# --------------------------
# 2. INSCRIPCIONES (Lógica Compleja)
# --------------------------

@web_router.post("/api/v1/cursos-extra/inscripcion", tags=["Cursos Extra"])
async def inscribir_alumno_curso(
    payload: dict = Body(...),
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Maneja inscripción de alumno interno o externo y crea su balance de deuda inicial.
    """
    try:
        curso = await db.get(CursoExtra, payload['curso_id'])
        if not curso: raise HTTPException(404, "Curso no encontrado")
        
        tipo_alumno = payload['tipo_alumno'] # 'INTERNO' o 'EXTERNO'
        alumno_id = None
        alumno_externo_id = None
        monto_a_pagar = 0
        
        # A. Lógica Alumno
        if tipo_alumno == 'INTERNO':
            alumno_id = payload['alumno_id']
            monto_a_pagar = curso.precio_interno
            # Validar que no esté inscrito ya
            exists_q = await db.execute(select(InscripcionCursoExtra).where(
                InscripcionCursoExtra.curso_extra_id == curso.id,
                InscripcionCursoExtra.alumno_id == alumno_id,
                InscripcionCursoExtra.estado == EstadoInscripcionCursoExtra.ACTIVO
            ))
            if exists_q.scalar(): raise HTTPException(400, "El alumno ya está inscrito en este curso")
            
        else: # EXTERNO
            monto_a_pagar = curso.precio_externo
            # Crear o Buscar Alumno Externo
            # Si viene ID, es uno existente, si no, creamos
            if payload.get('alumno_externo_id'):
                alumno_externo_id = payload['alumno_externo_id']
            else:
                nuevo_ext = AlumnoExterno(
                    sede_id=user.sede_id,
                    nombre_completo=payload['nombre_completo'],
                    fecha_nacimiento=datetime.strptime(payload['fecha_nacimiento'], "%Y-%m-%d").date() if payload.get('fecha_nacimiento') else None,
                    edad_anios=payload.get('edad'),
                    tutor_nombre=payload['tutor_nombre'],
                    tutor_celular=payload['tutor_celular']
                )
                db.add(nuevo_ext)
                await db.flush()
                alumno_externo_id = nuevo_ext.id

        # B. Crear Inscripción
        inscripcion = InscripcionCursoExtra(
            curso_extra_id=curso.id,
            tipo_alumno=TipoAlumnoCursoExtra[tipo_alumno], # Map to Enum
            alumno_id=alumno_id,
            alumno_externo_id=alumno_externo_id,
            tutor_nombre=payload.get('tutor_nombre') if tipo_alumno == 'EXTERNO' else None,
            tutor_celular=payload.get('tutor_celular') if tipo_alumno == 'EXTERNO' else None,
            inscrito_por_id=user.id
        )
        db.add(inscripcion)
        await db.flush()
        
        # C. Crear Balance (Deuda)
        balance = BalanceCursoExtra(
            inscripcion_curso_extra_id=inscripcion.id,
            monto_total=monto_a_pagar,
            monto_pagado=0,
            saldo=monto_a_pagar,
            estado=EstadoBalance.PENDIENTE
        )
        db.add(balance)
        
        await db.commit()
        return {"mensaje": "Inscripción realizada correctamente"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Error en inscripción: {str(e)}")

# --------------------------
# 3. PAGOS Y FINANZAS
# --------------------------

@web_router.get("/api/v1/cursos-extra/{curso_id}/inscritos", tags=["Cursos Extra"])
async def listar_inscritos_curso(curso_id: int, db: AsyncSession = Depends(get_session)):
    """ Retorna inscritos con su estado de cuenta """
    try:
        # Importamos Alumno explícitamente para el join anidado
        from app.infrastructure.db.models.alumnos.alumnos import Alumno

        stmt = (
            select(InscripcionCursoExtra, BalanceCursoExtra)
            .join(BalanceCursoExtra, BalanceCursoExtra.inscripcion_curso_extra_id == InscripcionCursoExtra.id)
            .options(
                # Carga Ansiosa Anidada: Inscripcion -> Alumno -> Tutores
                # (Esto evita el error de Greenlet)
                selectinload(InscripcionCursoExtra.alumno).selectinload(Alumno.tutores),
                selectinload(InscripcionCursoExtra.alumno_externo)
            )
            .where(InscripcionCursoExtra.curso_extra_id == curso_id)
        )
        result = await db.execute(stmt)
        rows = result.all()
        
        data = []
        for insc, bal in rows:
            nombre_alumno = "Desconocido"
            tutor_info = "-"
            celular_info = "-"

            # Lógica para ALUMNO INTERNO
            if insc.tipo_alumno == TipoAlumnoCursoExtra.INTERNO and insc.alumno:
                # Nombre Alumno
                nombre_alumno = f"{insc.alumno.nombre} {insc.alumno.apellido_paterno or ''}".strip()
                
                # Datos Tutor (Si existe)
                if insc.alumno.tutores and len(insc.alumno.tutores) > 0:
                    t = insc.alumno.tutores[0]
                    # ✅ CORRECCIÓN AQUÍ: Construimos el nombre manualmente usando 'nombres' y 'apellidos'
                    tutor_info = f"{t.nombres} {t.apellidos or ''}".strip()
                    celular_info = t.celular
            
            # Lógica para ALUMNO EXTERNO
            elif insc.tipo_alumno == TipoAlumnoCursoExtra.EXTERNO and insc.alumno_externo:
                nombre_alumno = insc.alumno_externo.nombre_completo
                tutor_info = insc.tutor_nombre or insc.alumno_externo.tutor_nombre
                celular_info = insc.tutor_celular or insc.alumno_externo.tutor_celular
                
            data.append({
                "inscripcion_id": insc.id,
                "balance_id": bal.id,
                "nombre": nombre_alumno,
                "tipo": insc.tipo_alumno.name,
                "tutor": tutor_info,
                "celular": celular_info,
                "deuda_total": float(bal.monto_total),
                "pagado": float(bal.monto_pagado),
                "saldo": float(bal.saldo),
                "estado_pago": bal.estado.name
            })
        return data

    except Exception as e:
        print(f"Error listando inscritos: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener inscritos: {str(e)}")
@web_router.post("/api/v1/cursos-extra/pagos", tags=["Cursos Extra"])
async def registrar_pago_curso(
    payload: dict = Body(...),
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    try:
        # 1. Obtener Balance e Inscripción
        balance = await db.get(BalanceCursoExtra, payload['balance_id'])
        if not balance: raise HTTPException(404, "Balance no encontrado")
        
        inscripcion = await db.get(InscripcionCursoExtra, balance.inscripcion_curso_extra_id)
        curso = await db.get(CursoExtra, inscripcion.curso_extra_id)
        
        monto = Decimal(payload['monto'])
        
        if monto > balance.saldo:
            raise HTTPException(400, f"El monto excede el saldo pendiente ({balance.saldo})")
            
        # 2. Registrar Pago
        nuevo_pago = PagoCursoExtra(
            balance_curso_extra_id=balance.id,
            monto=monto,
            metodo_pago=MetodoPagoCursoExtra[payload.get('metodo', 'EFECTIVO')],
            observaciones=payload.get('observaciones'),
            registrado_por_id=user.id
        )
        db.add(nuevo_pago)
        
        # 3. Actualizar Balance Individual
        balance.monto_pagado += monto
        balance.saldo -= monto
        if balance.saldo == 0:
            balance.estado = EstadoBalance.PAGADO
        else:
            balance.estado = EstadoBalance.PARCIAL
            
        # 4. Actualizar Finanzas Globales del Curso (TRIGGER DE APP)
        # Buscamos el registro de ingresos del curso
        stmt_ing = select(IngresoCursoExtra).where(IngresoCursoExtra.curso_extra_id == curso.id)
        ingreso_global = (await db.execute(stmt_ing)).scalars().first()
        
        if ingreso_global:
            ingreso_global.total_ingresos += monto
            ingreso_global.ganancia_bruta = ingreso_global.total_ingresos - ingreso_global.total_gastos
            
            # Reparto de Ganancias
            pct_inst = curso.porcentaje_institucion / 100
            ingreso_global.ganancia_institucion = ingreso_global.ganancia_bruta * pct_inst
            ingreso_global.ganancia_instructor = ingreso_global.ganancia_bruta * (1 - pct_inst)
            
        await db.commit()
        return {"mensaje": "Pago registrado correctamente"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Error registrando pago: {str(e)}")

# --------------------------
# 4. GASTOS DEL CURSO
# --------------------------

@web_router.post("/api/v1/cursos-extra/gastos", tags=["Cursos Extra"])
async def registrar_gasto_curso(
    payload: dict = Body(...),
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    try:
        # Crear categoría si no existe o usar existente
        # Por simplicidad asumiremos que envían el ID de categoría o un string para crear
        # Aquí asumimos creación directa por nombre de categoría para agilidad
        
        curso_id = payload['curso_id']
        curso = await db.get(CursoExtra, curso_id)
        
        # Verificar si existe categoría de costo, sino crearla
        cat_nombre = payload.get('categoria', 'General')
        stmt_cat = select(CategoriaCostoCursoExtra).where(
            CategoriaCostoCursoExtra.curso_extra_id == curso_id,
            CategoriaCostoCursoExtra.nombre == cat_nombre
        )
        cat_costo = (await db.execute(stmt_cat)).scalars().first()
        
        if not cat_costo:
            cat_costo = CategoriaCostoCursoExtra(curso_extra_id=curso_id, nombre=cat_nombre)
            db.add(cat_costo)
            await db.flush()
            
        # Registrar Costo
        monto = Decimal(payload['monto'])
        nuevo_costo = CostoCursoExtra(
            curso_extra_id=curso_id,
            categoria_costo_id=cat_costo.id,
            descripcion=payload.get('descripcion'),
            monto=monto,
            registrado_por_id=user.id
        )
        db.add(nuevo_costo)
        
        # Actualizar Finanzas Globales
        stmt_ing = select(IngresoCursoExtra).where(IngresoCursoExtra.curso_extra_id == curso_id)
        ingreso_global = (await db.execute(stmt_ing)).scalars().first()
        
        if ingreso_global:
            ingreso_global.total_gastos += monto
            ingreso_global.ganancia_bruta = ingreso_global.total_ingresos - ingreso_global.total_gastos
            
            # Recalcular reparto (sobre la nueva ganancia bruta)
            pct_inst = curso.porcentaje_institucion / 100
            # Nota: Si la ganancia es negativa, esto reflejará pérdida compartida
            ingreso_global.ganancia_institucion = ingreso_global.ganancia_bruta * pct_inst
            ingreso_global.ganancia_instructor = ingreso_global.ganancia_bruta * (1 - pct_inst)
            
        await db.commit()
        return {"mensaje": "Gasto registrado"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Error: {str(e)}")

# --- PEGAR EN ROUTES.PY (Debajo de listar_cursos_extra) ---

# --- EN ROUTES.PY (Reemplazar endpoint crear_curso_extra) ---

@web_router.post("/api/v1/cursos-extra", tags=["Cursos Extra"])
async def crear_curso_extra(
    payload: dict = Body(...),
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Crea un nuevo curso extra con cupo máximo configurable.
    """
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        # 1. Crear el Curso
        nuevo_curso = CursoExtra(
            sede_id=user.sede_id,
            nombre=payload.get('nombre'),
            descripcion=payload.get('descripcion'),
            instructor=payload.get('instructor'),
            gestion=payload.get('gestion', datetime.now().year),
            fecha_inicio=datetime.strptime(payload['fecha_inicio'], "%Y-%m-%d").date(),
            # Fecha fin es opcional
            fecha_fin=datetime.strptime(payload['fecha_fin'], "%Y-%m-%d").date() if payload.get('fecha_fin') else None,
            
            # ✅ NUEVO: Leemos el cupo_maximo del payload (Default 20 si no se envía)
            cupo_maximo=int(payload.get('cupo_maximo', 20)),
            
            precio_interno=Decimal(payload['precio_interno']),
            precio_externo=Decimal(payload['precio_externo']),
            porcentaje_institucion=Decimal(payload.get('porcentaje', 50)),
            activo=True
        )
        db.add(nuevo_curso)
        await db.flush() # Para obtener el ID del nuevo curso
        
        # 2. Inicializar registro financiero
        finanza = IngresoCursoExtra(
            curso_extra_id=nuevo_curso.id,
            total_ingresos=0,
            total_gastos=0,
            ganancia_bruta=0,
            ganancia_institucion=0,
            ganancia_instructor=0
        )
        db.add(finanza)
        
        await db.commit()
        return {"mensaje": "Curso creado exitosamente", "id": nuevo_curso.id}

    except Exception as e:
        await db.rollback()
        print(f"Error creando curso: {e}")
        import traceback
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=f"Error al guardar: {str(e)}")
    

# --- EN ROUTES.PY (Sección de Cursos Extra) ---

@web_router.post("/api/v1/cursos-extra/gastos", tags=["Cursos Extra"])
async def registrar_gasto_curso(
    payload: dict = Body(...),
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Registra un gasto asociado a una categoría. 
    Si la categoría no existe para este curso, la crea automáticamente.
    Actualiza el balance financiero del curso.
    """
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        curso_id = payload.get('curso_id')
        if not curso_id:
            raise HTTPException(400, "ID de curso requerido")

        curso = await db.get(CursoExtra, curso_id)
        if not curso:
            raise HTTPException(404, "Curso no encontrado")

        # 1. Gestionar Categoría (Dinámica)
        cat_nombre = payload.get('categoria', 'General').strip().title() # Ej: "Materiales"
        
        # Buscar si ya existe la categoría en este curso
        stmt_cat = select(CategoriaCostoCursoExtra).where(
            CategoriaCostoCursoExtra.curso_extra_id == curso_id,
            CategoriaCostoCursoExtra.nombre == cat_nombre
        )
        categoria = (await db.execute(stmt_cat)).scalars().first()
        
        # Si no existe, crearla
        if not categoria:
            categoria = CategoriaCostoCursoExtra(
                curso_extra_id=curso_id,
                nombre=cat_nombre,
                descripcion="Categoría creada automáticamente al registrar gasto",
                creado_por_id=user.id
            )
            db.add(categoria)
            await db.flush() # Para obtener ID
            
        # 2. Registrar el Gasto
        monto = Decimal(payload['monto'])
        nuevo_gasto = CostoCursoExtra(
            curso_extra_id=curso_id,
            categoria_costo_id=categoria.id,
            descripcion=payload.get('descripcion'),
            monto=monto,
            registrado_por_id=user.id,
            fecha_gasto=datetime.now()
        )
        db.add(nuevo_gasto)
        
        # 3. Actualizar Finanzas Globales del Curso
        stmt_ing = select(IngresoCursoExtra).where(IngresoCursoExtra.curso_extra_id == curso_id)
        ingreso_global = (await db.execute(stmt_ing)).scalars().first()
        
        if ingreso_global:
            ingreso_global.total_gastos += monto
            ingreso_global.ganancia_bruta = ingreso_global.total_ingresos - ingreso_global.total_gastos
            
            # Recalcular reparto de utilidades
            pct_inst = curso.porcentaje_institucion / 100
            ingreso_global.ganancia_institucion = ingreso_global.ganancia_bruta * pct_inst
            ingreso_global.ganancia_instructor = ingreso_global.ganancia_bruta * (1 - pct_inst)
            
        await db.commit()
        return {"mensaje": "Gasto registrado correctamente"}
        
    except Exception as e:
        await db.rollback()
        print(f"Error registrando gasto: {e}")
        raise HTTPException(status_code=500, detail=f"Error al registrar gasto: {str(e)}")
    
@web_router.get("/academico/tutor", response_class=HTMLResponse, name="academico_tutor")
async def academico_tutor_page(request: Request, user=Depends(get_current_user_optional)):
    redirect = check_auth_redirect(user)
    if redirect:
        return redirect
    if (user.role or "").upper() not in ("TUTOR", "SUPERADMIN"):
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(
        "academico/tutor_index.html",
        {"request": request, "current_user": user, "pagetitle": "Académico - Tutor", "activemenu": "academico"},
    )

#Asignacion

# =============================================================================
#  ENDPOINT 1: PROFESORAS DISPONIBLES (Corregido: profesora_id)
# =============================================================================
@web_router.get("/api/v1/profesoras/disponibles")
async def get_profesoras_disponibles(db: AsyncSession = Depends(get_session)):
    """
    Retorna usuarios con rol PROFESORA/DOCENTE que NO están asignados en la tabla intermedia.
    """
    # 1. Buscar IDs ocupados en la tabla intermedia
    # CORRECCIÓN: Usamos 'profesora_id' en lugar de 'profesor_id'
    stmt_ocupadas = select(ParaleloProfesora.profesora_id)
    result_ocupadas = await db.execute(stmt_ocupadas)
    ids_ocupados = result_ocupadas.scalars().all()
    
    # 2. Buscar usuarios PROFESORA excluyendo los ocupados
    stmt = (
        select(Usuario)
        .join(UsuarioRol)
        .join(Rol)
        .where(
            or_(
                Rol.nombre.ilike("%PROFESORA%"),
                Rol.nombre.ilike("%DOCENTE%")
            )
        )
        .where(Usuario.activo == True)
    )

    if ids_ocupados:
        stmt = stmt.where(Usuario.id.not_in(ids_ocupados))
    
    result = await db.execute(stmt)
    profes = result.scalars().all()
    
    return [
        {"id": p.id, "nombre_completo": f"{p.nombres} {p.apellidos or ''}".strip()} 
        for p in profes
    ]

# =============================================================================
#  ENDPOINT 2: ARBOL DE GRUPOS (Corregido: p.letra)
# =============================================================================
@web_router.get("/api/v1/academico/grupos-paralelos-tree")
async def get_grupos_paralelos_tree(db: AsyncSession = Depends(get_session)):
    """
    Retorna árbol de Grupos -> Paralelos
    CORRECCIÓN: Se usa 'p.letra' porque Paralelo no tiene 'nombre'.
    """
    # Usamos orden por nombre de grupo
    stmt = select(Grupo).options(selectinload(Grupo.paralelos)).order_by(Grupo.nombre)
    result = await db.execute(stmt)
    grupos = result.scalars().all()
    
    # Obtener paralelos ya asignados
    stmt_ocupados = select(ParaleloProfesora.paralelo_id)
    res_ocupados = await db.execute(stmt_ocupados)
    paralelos_ocupados_ids = res_ocupados.scalars().all()

    data = []
    for g in grupos:
        paralelos_list = []
        if g.paralelos:
            for p in g.paralelos:
                # Verificar si el paralelo ya tiene profe asignado
                if p.id not in paralelos_ocupados_ids:
                    # CORRECCIÓN: Usamos p.letra
                    nombre_paralelo = f"{p.letra}" 
                    paralelos_list.append({"id": p.id, "nombre": nombre_paralelo})
        
        data.append({
            "id": g.id,
            "nombre": g.nombre, 
            "paralelos": paralelos_list
        })
    return data

# =============================================================================
#  ENDPOINT 3: ASIGNAR (Corregido: Insert)
# =============================================================================
@web_router.post("/api/v1/asignar-profesor-paralelo")
async def asignar_profesor_paralelo(
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """
    Guarda la asignación en la tabla intermedia ParaleloProfesora
    """
    data = await request.json()
    profesor_id_req = data.get("profesor_id") # Variable del request
    paralelo_id_req = data.get("paralelo_id")
    
    if not profesor_id_req or not paralelo_id_req:
        raise HTTPException(status_code=400, detail="Faltan datos")
        
    async with db.begin():
        # Verificar duplicados
        stmt_check = select(ParaleloProfesora).where(
            and_(
                ParaleloProfesora.paralelo_id == paralelo_id_req,
                # CORRECCIÓN: Campo del modelo es profesora_id
                ParaleloProfesora.profesora_id == profesor_id_req 
            )
        )
        existing = (await db.execute(stmt_check)).first()
        
        if existing:
            return {"success": True, "message": "Esta profesora ya estaba asignada a este paralelo"}

        # Insertar en tabla intermedia
        nueva_asignacion = ParaleloProfesora(
            paralelo_id=paralelo_id_req,
            profesora_id=profesor_id_req, # CORRECCIÓN: Campo modelo = profesora_id
            gestion=datetime.now().year,  # Tu modelo requiere 'gestion', usamos el año actual
            es_titular=True               # Valor por defecto
        )
        db.add(nueva_asignacion)
        
    return {"success": True, "message": "Profesora asignada correctamente"}


# --- 1. RUTA PARA LA VISTA HTML ---
@web_router.get("/usuarios/asignaciones", response_class=HTMLResponse)
async def pagina_asignaciones(request: Request, user=Depends(get_current_user_optional)):
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    return templates.TemplateResponse(
        "usuarios/asignaciones.html", # Crearemos este archivo abajo
        {"request": request, "current_user": user, "page_title": "Asignaciones Profesora-Aula"}
    )

@web_router.get("/api/v1/asignaciones/lista")
async def get_lista_asignaciones(db: AsyncSession = Depends(get_session)):
    """Retorna la lista de asignaciones actuales usando JOINs explícitos"""
    
    # Consulta uniendo tablas manualmente para no depender de relaciones faltantes
    stmt = (
        select(ParaleloProfesora, Usuario, Paralelo, Grupo)
        .join(Usuario, ParaleloProfesora.profesora_id == Usuario.id)
        .join(Paralelo, ParaleloProfesora.paralelo_id == Paralelo.id)
        .outerjoin(Grupo, Paralelo.grupo_id == Grupo.id)
        .order_by(desc(ParaleloProfesora.creado_en))
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    data = []
    # Desempaquetamos los 4 objetos de cada fila
    for asignacion, profe, par, grp in rows:
        nombre_profe = f"{profe.nombres} {profe.apellidos or ''}".strip()
        
        grupo_nombre = "Sin Grupo"
        if grp:
            grupo_nombre = grp.nombre

        paralelo_letra = par.letra if par else "?"

        data.append({
            "id": asignacion.id,
            "profesora_id": asignacion.profesora_id,
            "profesora_nombre": nombre_profe,
            "grupo_nombre": grupo_nombre,
            "paralelo_letra": paralelo_letra,
            "paralelo_id": asignacion.paralelo_id,
            "gestion": asignacion.gestion,
            "es_titular": asignacion.es_titular
        })
    return data

@web_router.get("/api/v1/profesoras/disponibles")
async def get_profesoras_disponibles(
    include_id: Optional[int] = Query(None), # <--- Nuevo parámetro
    db: AsyncSession = Depends(get_session)
):
    """
    Retorna profesoras disponibles. 
    Si se envía include_id, esa profesora también se incluye (para edición).
    """
    # 1. Buscar IDs ocupados
    stmt_ocupadas = select(ParaleloProfesora.profesora_id)
    result_ocupadas = await db.execute(stmt_ocupadas)
    ids_ocupados = result_ocupadas.scalars().all()
    
    # Si tenemos un ID para incluir (edición), lo sacamos de la lista de "ocupados"
    if include_id and include_id in ids_ocupados:
        # Convertimos a lista mutable para remover
        ids_ocupados = [id for id in ids_ocupados if id != include_id]
    
    # 2. Query normal
    stmt = (
        select(Usuario)
        .join(UsuarioRol)
        .join(Rol)
        .where(
            or_(
                Rol.nombre.ilike("%PROFESORA%"),
                Rol.nombre.ilike("%DOCENTE%")
            )
        )
        .where(Usuario.activo == True)
    )

    if ids_ocupados:
        stmt = stmt.where(Usuario.id.not_in(ids_ocupados))
    
    result = await db.execute(stmt)
    profes = result.scalars().all()
    
    return [
        {"id": p.id, "nombre_completo": f"{p.nombres} {p.apellidos or ''}".strip()} 
        for p in profes
    ]

# --- AGREGAR AL FINAL DE routes.py ---

@web_router.delete("/api/v1/asignaciones/{asignacion_id}", tags=["Academico"])
async def eliminar_asignacion_endpoint(
    asignacion_id: int,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """Elimina la asignación de una profesora a un paralelo, liberándola."""
    if not user: raise HTTPException(401)
    
    # 1. Buscar la asignación
    asignacion = await db.get(ParaleloProfesora, asignacion_id)
    if not asignacion:
        raise HTTPException(404, "Asignación no encontrada")
        
    # (Opcional) Verificar permisos si es necesario
    # if user.rol.nombre != 'ADMINISTRADOR': ...

    try:
        await db.delete(asignacion)
        await db.commit()
        return {"success": True, "mensaje": "Asignación eliminada correctamente"}
    except Exception as e:
        await db.rollback()
        print(f"Error eliminando asignación: {e}")
        raise HTTPException(500, "No se pudo eliminar la asignación")


# --- AGREGAR EN routes.py ---

# 1. Ruta para mostrar la página HTML
@web_router.get("/perfil", response_class=HTMLResponse)
async def pagina_perfil(request: Request, user=Depends(get_current_user_optional)):
    redirect = check_auth_redirect(user)
    if redirect: return redirect
    
    return templates.TemplateResponse(
        "/usuarios/perfil.html",
        {"request": request, "current_user": user, "page_title": "Mi Perfil"}
    )

#Actulizar foto
@web_router.post("/api/v1/perfil/foto")
async def update_perfil_foto(
    file: UploadFile = File(...),
    user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    
    # Validar extensión de imagen
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "El archivo debe ser una imagen")

    try:
        # 1. Obtener configuración (ruta absoluta del env)
        settings = get_settings()
        
        # 2. Generar nombre seguro único
        timestamp = int(datetime.now().timestamp())
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        safe_filename = f"profile_{user.id}_{timestamp}.{ext}"
        
        # 3. Definir Rutas
        # RUTA FÍSICA: C:/Users/Ian/Desktop/datilera_media/perfiles/archivo.jpg
        # Usamos Path para manejar las barras / o \ automáticamente en Windows
        ruta_base = Path(settings.MEDIA_DIR)
        directorio_destino = ruta_base / "perfiles"
        archivo_destino = directorio_destino / safe_filename
        
        # Crear carpeta si no existe
        directorio_destino.mkdir(parents=True, exist_ok=True)
        
        # 4. Guardar el archivo físicamente
        with open(archivo_destino, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 5. Actualizar BD con la URL relativa (para el navegador)
        # El navegador pide: http://localhost:8000/media/perfiles/foto.jpg
        ruta_web = f"/media/perfiles/{safe_filename}"
        
        user.foto_perfil_url = ruta_web
        await db.commit()
        
        return {"success": True, "foto_url": ruta_web}
        
    except Exception as e:
        await db.rollback()
        print(f"❌ Error subiendo foto: {e}")
        # Tip: Imprime la ruta intentada para depurar
        print(f"   Intentando guardar en: {settings.MEDIA_DIR}/perfiles") 
        raise HTTPException(500, f"Error al guardar la imagen: {str(e)}")

# 3. API para cambiar Contraseña
@web_router.post("/api/v1/perfil/password")
async def update_perfil_password(
    request: Request,
    user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    if not user: raise HTTPException(401)
    
    data = await request.json()
    actual = data.get('password_actual')
    nueva = data.get('password_nueva')
    
    # Validar contraseña actual
    if not hasher.verify_password(actual, user.hash_password):
        raise HTTPException(400, "La contraseña actual es incorrecta")
        
    # Guardar nueva
    user.hash_password = hasher.hash_password(nueva)
    await db.commit()
    
    return {"success": True, "mensaje": "Contraseña actualizada correctamente"}

# --- ESQUEMA DE DATOS ---
class UserPreferencesRequest(BaseModel):
    # El frontend sigue enviando "light" o "dark"
    theme: Literal["dark", "light"]

# --- RUTA PATCH MODIFICADA ---
@web_router.patch("/api/v1/usuarios/me/preferencias", tags=["Usuarios"])
async def update_user_preferences(
    prefs: UserPreferencesRequest,
    user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_session)
):
    """
    Recibe 'light'/'dark', lo traduce a 'claro'/'oscuro' y lo guarda.
    """
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        # 1. TRADUCCIÓN: Frontend (Inglés) -> Dominio/BD (Español)
        tema_a_guardar = "claro" if prefs.theme == "light" else "oscuro"

        # 2. Buscar si existe
        stmt = select(PreferenciaUsuario).where(PreferenciaUsuario.usuario_id == user.id)
        result = await db.execute(stmt)
        db_prefs = result.scalars().first()

        if db_prefs:
            # Actualizamos con el valor en ESPAÑOL
            db_prefs.tema = tema_a_guardar
        else:
            # Creamos con el valor en ESPAÑOL
            new_prefs = PreferenciaUsuario(
                usuario_id=user.id,
                tema=tema_a_guardar,
                notificaciones_push=True,
                notificaciones_email=False
            )
            db.add(new_prefs)

        await db.commit()
        
        # Retornamos lo que el frontend espera (puedes devolver el mismo 'prefs.theme')
        return {"status": "ok", "theme": prefs.theme}

    except Exception as e:
        await db.rollback()
        print(f"❌ Error guardando preferencias: {e}")
        raise HTTPException(status_code=500, detail="Error interno")
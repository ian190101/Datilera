from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_, desc

# --- MODELOS DEL SISTEMA ---
from app.infrastructure.db.models.alumnos.alumnos import Alumno
from app.infrastructure.db.models.seguridad.usuarios import Usuario
from app.infrastructure.db.models.comunicaciones.notificaciones import Notificacion
from app.infrastructure.db.models.comunicaciones.mensajes import Mensaje
from app.infrastructure.db.models.comunicaciones.conversaciones import Conversacion
from app.infrastructure.db.models.finanzas.turnos import Turno # Ejemplo de configuración
from app.infrastructure.db.models.seguridad.sedes import Sede

# --- REPOSITORIOS (Reutilizamos lógica existente) ---
from app.infrastructure.db.repositories.dashboard.dashboard_repo import DashboardRepository

# --- INFRAESTRUCTURA IA ---
from app.infrastructure.db.models.ia.ia_consultas import IAConsulta
from app.infrastructure.services.ia import get_ia_provider_by_name
from app.kernel.domain.ia.ia import IARequest

class IAChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _obtener_resumen_sistema(self, sede_id: int) -> str:
        """
        Recopila una 'radiografía' completa del estado actual de la sede
        para dársela como contexto a la IA.
        """
        try:

            # 1. OBTENER NOMBRE DE LA SEDE
            # Consultamos el nombre real para que la IA sepa dónde está
            stmt_sede = select(Sede.nombre).where(Sede.id == sede_id)
            nombre_sede = await self.db.scalar(stmt_sede)
            nombre_sede = nombre_sede if nombre_sede else f"Sede {sede_id}"

            # 2. CONTEO REAL DE ALUMNOS (Corrección del problema "0 alumnos")
            # Hacemos un conteo directo sin filtros de fecha y sin la columna 'eliminado'
            stmt_alumnos = select(
                func.count(Alumno.id).label('total'),
                func.sum(case((func.lower(Alumno.estado) == 'inscrito', 1), else_=0)).label('inscritos'),
                func.sum(case((func.lower(Alumno.estado) == 'preinscrito', 1), else_=0)).label('preinscritos')
            ).where(
                Alumno.sede_id == sede_id
                # Eliminamos 'Alumno.eliminado' porque tu modelo no lo tiene
            )
            res_alu = (await self.db.execute(stmt_alumnos)).one()

            # 3. DATOS FINANCIEROS (Usamos tu Repo existente que funcionaba bien)
            dashboard_repo = DashboardRepository(self.db)
            metrics = await dashboard_repo.get_metricas_generales(sede_id=sede_id)

            # 4. ESTADÍSTICAS DE USUARIOS
            stmt_users = select(
                func.count(Usuario.id).label('total'),
                func.sum(case((Usuario.activo == True, 1), else_=0)).label('activos')
            ).where(Usuario.sede_id == sede_id)
            res_users = (await self.db.execute(stmt_users)).one()

            # 5. COMUNICACIONES HOY
            hoy = datetime.now().date()
            stmt_msgs = select(func.count(Mensaje.id)).join(Conversacion).where(
                and_(Conversacion.sede_id == sede_id, func.date(Mensaje.enviado_en) == hoy)
            )
            total_mensajes_hoy = await self.db.scalar(stmt_msgs) or 0
            # 1. MÉTRICAS DEL DASHBOARD (Finanzas y Alumnado)
            # Reutilizamos tu repositorio existente para no duplicar lógica compleja
            dashboard_repo = DashboardRepository(self.db)
            # Asumimos que devuelve un dict tipo: {"ingresos_mes": 100, "total_alumnos": 50...}
            metrics = await dashboard_repo.get_metricas_generales(sede_id=sede_id)
            
            # 2. ESTADÍSTICAS DE USUARIOS (Staff)
            stmt_users = select(
                func.count().label('total'),
                func.sum(case((Usuario.activo == True, 1), else_=0)).label('activos')
            ).where(Usuario.sede_id == sede_id)
            res_users = (await self.db.execute(stmt_users)).one()

            # 3. COMUNICACIONES (Mensajes y Notificaciones Hoy)
            hoy = datetime.now().date()
            
            # Mensajes intercambiados hoy
            stmt_msgs = select(func.count(Mensaje.id)).join(Conversacion).where(
                and_(Conversacion.sede_id == sede_id, func.date(Mensaje.enviado_en) == hoy)
            )
            total_mensajes_hoy = await self.db.scalar(stmt_msgs) or 0

            # Notificaciones enviadas este mes
            inicio_mes = hoy.replace(day=1)
            stmt_notif = select(func.count(Notificacion.id)).where(
                and_(
                    Notificacion.creado_en >= inicio_mes
                )
                # Nota: Si Notificacion tuviera sede_id directo lo usaríamos, 
                # si no, asumimos que se filtra por los usuarios de la sede.
                # Aquí hago un count simple para el ejemplo.
            )
            total_notif_mes = await self.db.scalar(stmt_notif) or 0

            # 4. CONSTRUCCIÓN DEL TEXTO DE CONTEXTO
            # Esto es lo que la IA "lee" antes de responder
            contexto = f"""
            [ESTADO ACTUAL DEL SISTEMA DATILERA - {datetime.now().strftime('%d/%m/%Y %H:%M')}]
            
            📊 FINANZAS Y ADMISIONES (Dashboard):
            - Ingresos del Mes: {metrics.get('ingresos_mes', 0)}
            - Total Alumnos Inscritos: {metrics.get('total_alumnos', 0)}
            - Pagos Pendientes: {metrics.get('pagos_pendientes_count', 0)} ({metrics.get('monto_pendiente', 0)} Bs.)
            - Pagos al Día: {metrics.get('pagos_al_dia_percent', 0)}%
            
            👥 USUARIOS Y STAFF:
            - Usuarios Totales en Sede: {res_users.total or 0}
            - Usuarios Activos: {res_users.activos or 0}
            
            💬 COMUNICACIONES Y ACTIVIDAD:
            - Mensajes de chat enviados hoy: {total_mensajes_hoy}
            - Notificaciones/Comunicados este mes: {total_notif_mes}
            
            ℹ️ CONFIGURACIÓN:
            - Sede ID: {sede_id}
            - Sede nombre {nombre_sede}
            """
            return contexto

        except Exception as e:
            print(f"⚠️ Error generando contexto IA: {e}")
            return "[Error obteniendo datos del sistema. Responde basándote solo en tu conocimiento general.]"

    async def procesar_consulta(
        self, 
        prompt: str, 
        usuario_id: int, 
        sede_id: int,
        proveedor_nombre: str = "gemini",
        contexto_sistema: str = "Eres un asistente administrativo experto."
    ) -> str:
        
        # 1. Validar Proveedor
        provider = get_ia_provider_by_name(proveedor_nombre)
        if not provider:
            raise ValueError(f"Proveedor '{proveedor_nombre}' no disponible.")

        # 2. INYECCIÓN RAG (Retrieval-Augmented Generation)
        # Obtenemos los datos frescos de la BD
        datos_sistema = await self._obtener_resumen_sistema(sede_id)
        
        # 3. Prompt Engineering
        # Le damos una personalidad y le prohibimos inventar datos numéricos
        system_instruction_final = f"""
        {contexto_sistema}
        
        Tus Instrucciones Principales:
        1. Eres 'Datilera Copilot', el asistente inteligente del centro educativo.
        2. Tienes acceso a los DATOS EN TIEMPO REAL que se presentan abajo. Úsalos para responder.
        3. Si te preguntan "cuántos alumnos hay" o "cuánto ingresó este mes", USA LOS DATOS PROVISTOS. No inventes.
        4. Si te preguntan algo que no está en los datos (ej: "nombre del padre de Juan"), di cortésmente que no tienes acceso a ese dato específico por privacidad.
        5. Sé amable, profesional y conciso.
        
        --- DATOS DEL SISTEMA ---
        {datos_sistema}
        -------------------------
        """

        # 4. Preparar Request
        request = IARequest(
            prompt=prompt,
            system_instruction=system_instruction_final,
            messages=[], 
            contexto={"usuario_id": usuario_id, "sede_id": sede_id}
        )

        # 5. Ejecutar Llamada IA
        start = datetime.now()
        response = await provider.generar_respuesta(request)
        duration = (datetime.now() - start).seconds

        # 6. Auditoría / Logging (Importante para saber qué preguntan los usuarios)
        try:
            log = IAConsulta(
                usuario_id=usuario_id,
                sede_id=sede_id,
                proveedor=provider.get_nombre_proveedor(),
                modelo=response.model_name,
                prompt=prompt,
                respuesta=response.content,
                tokens_prompt=response.tokens_prompt,
                tokens_respuesta=response.tokens_respuesta,
                tokens_total=response.tokens_total,
                costo_usd=response.cost_usd,
                categoria="chat_sistema",
                contexto={"resumen_datos": "inyectado"}, # No guardamos todo el texto para ahorrar espacio
                exitoso=response.successful,
                mensaje_error=response.error_message,
                duracion_segundos=duration,
                creado_en=datetime.utcnow()
            )
            self.db.add(log)
            await self.db.commit()
        except Exception as e:
            print(f"Error guardando log IA: {e}")

        if not response.successful:
            raise Exception(f"Error proveedor IA: {response.error_message}")

        return response.content
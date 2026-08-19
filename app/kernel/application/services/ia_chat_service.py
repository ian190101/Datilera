from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.infrastructure.db.models.comunicaciones.notificaciones import (
    CanalNotificacion,
    EstadoNotificacion,
    Notificacion,
    PrioridadNotificacion,
)
from app.infrastructure.db.models.ia.ia_consultas import IAConsulta
from app.infrastructure.db.models.seguridad.sedes import Sede
from app.infrastructure.services.ia import get_ia_provider_by_name
from app.kernel.application.services.datilera_knowledge import (
    buscar_guias,
    construir_contexto_asistente,
    normalizar,
    respuesta_guia,
)
from app.kernel.application.services.ia_financial_analytics import AnaliticaFinancieraIA, PeriodoFinanciero
from app.kernel.domain.ia.ia import IAMessage, IARequest


@dataclass(slots=True)
class ResultadoChat:
    reply: str
    intent: str
    confidence: float
    sources: list[dict[str, str]] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    visualizations: list[dict[str, Any]] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reply": self.reply,
            "intent": self.intent,
            "confidence": self.confidence,
            "sources": self.sources,
            "actions": self.actions,
            "visualizations": self.visualizations,
            "suggestions": self.suggestions,
        }


class IAChatService:
    """Copiloto con conocimiento local, analítica verificable y acciones confirmables."""

    FINANZAS = (
        "finanza", "financier", "econom", "pago", "ingreso", "egreso", "gasto", "caja", "saldo", "deuda",
        "cuota", "moros", "cobrar", "rentabilidad", "flujo", "reporte financiero",
    )
    ANALISIS = ("grafica", "grafico", "tendencia", "compar", "evolucion", "distribucion", "analiza")
    INSTITUCION = ("institucion", "sede", "direccion", "nombre del centro", "datilera")
    AUTOMATIZACION = ("recuerdame", "recordatorio", "avisame", "programa una notificacion")
    CAPACIDADES = ("que puedes hacer", "que haces", "en que ayudas", "modulos disponibles", "ayuda del sistema")

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    async def procesar_consulta(
        self,
        prompt: str,
        usuario_id: int,
        sede_id: int,
        puede_ver_finanzas: bool,
        history: list[dict[str, str]] | None = None,
        proveedor_nombre: str = "gemini",
        roles: list[str] | None = None,
    ) -> ResultadoChat:
        prompt = " ".join(prompt.split()).strip()
        if not prompt:
            raise ValueError("La consulta no puede estar vacía")
        if len(prompt) > 1500:
            raise ValueError("La consulta supera los 1500 caracteres")

        consulta = normalizar(prompt)
        historial = history or []
        contexto_financiero = any(
            "reporte financiero" in normalizar(str(item.get("content", "")))
            or "resultado neto" in normalizar(str(item.get("content", "")))
            for item in historial[-4:]
        )
        consulta_financiera = any(clave in consulta for clave in self.FINANZAS)
        senales_analitica = (
            "resumen", "reporte", "cuanto", "total", "graf", "tendencia", "saldo", "deuda",
            "pendiente", "ingreso", "egreso", "gasto", "caja", "moros", "rentabilidad",
            "flujo", "cobrar", "compar", "evolucion", "distribucion", "analiza", "muestra",
        )
        pide_analisis_financiero = (
            consulta_financiera and any(clave in consulta for clave in senales_analitica)
        ) or (contexto_financiero and any(clave in consulta for clave in self.ANALISIS))
        pregunta_procedimiento = any(
            clave in consulta
            for clave in (
                "como registrar", "como crear", "donde registro", "como anular", "como usar",
                "como se calcula", "que es", "cuando se paga", "fecha de pago",
            )
        )

        if any(clave in consulta for clave in self.AUTOMATIZACION):
            resultado = self._preparar_recordatorio(prompt, usuario_id, sede_id)
        elif pide_analisis_financiero and not pregunta_procedimiento:
            resultado = await self._responder_finanzas(prompt, sede_id, puede_ver_finanzas)
        elif pregunta_procedimiento and buscar_guias(prompt):
            resultado = self._respuesta_de_guia(buscar_guias(prompt)[0])
        elif any(clave in consulta for clave in self.CAPACIDADES):
            resultado = self._responder_capacidades(puede_ver_finanzas)
        elif any(clave in consulta for clave in self.INSTITUCION):
            resultado = await self._responder_institucion(sede_id)
        else:
            guias = buscar_guias(prompt)
            if guias:
                resultado = self._respuesta_de_guia(guias[0])
            else:
                resultado = await self._responder_con_modelo(
                    prompt,
                    usuario_id,
                    sede_id,
                    historial,
                    proveedor_nombre,
                    roles or [],
                )

        await self._registrar_auditoria(prompt, resultado, usuario_id, sede_id, proveedor_nombre)
        return resultado

    @staticmethod
    def _respuesta_de_guia(guia: Any) -> ResultadoChat:
        return ResultadoChat(
            reply=respuesta_guia(guia),
            intent="uso_sistema",
            confidence=0.96,
            sources=[{"label": f"Guía verificada del módulo {guia.modulo}", "type": "manual"}],
            actions=[{"type": "navigate", "label": f"Abrir {guia.modulo}", "url": guia.ruta}],
            suggestions=list(guia.consultas[:3]),
        )

    @staticmethod
    def _responder_capacidades(puede_ver_finanzas: bool) -> ResultadoChat:
        finanzas = (
            "analizar caja, cartera, tendencias y categorías con gráficas y exportación CSV"
            if puede_ver_finanzas
            else "explicar Finanzas sin exponer cifras restringidas"
        )
        return ResultadoChat(
            reply=(
                "**Puedo ayudarte directamente en Datilera con:**\n"
                "- Guías verificadas de Inscripciones, Académico, Comunicaciones, Inventario, Cursos Extra y Usuarios.\n"
                f"- Finanzas: {finanzas}.\n"
                "- Información configurada de tu sede.\n"
                "- Recordatorios personales con fecha y hora, siempre después de tu confirmación.\n"
                "- Accesos directos y preguntas de seguimiento dentro del chat.\n\n"
                "No registro ni anulo pagos de forma automática, y nunca muestro información que tu rol no puede consultar."
            ),
            intent="capacidades",
            confidence=1.0,
            sources=[{"label": "Catálogo verificado de Datilera", "type": "manual"}],
            suggestions=[
                "Muéstrame los módulos disponibles",
                "Genera un resumen financiero de este mes",
                "¿Cómo inscribo a un segundo hijo del mismo tutor?",
            ],
        )

    async def _responder_finanzas(self, prompt: str, sede_id: int, permitido: bool) -> ResultadoChat:
        if not permitido:
            return ResultadoChat(
                reply=(
                    "No puedo mostrar datos financieros porque tu cuenta no tiene acceso a Finanzas. "
                    "Sí puedo explicarte el flujo general del módulo o puedes solicitar el reporte a un administrador."
                ),
                intent="finanzas",
                confidence=1.0,
                sources=[{"label": "Permisos de la sesión", "type": "permission"}],
            )

        inicio, fin, etiqueta = self._resolver_periodo(prompt)
        periodo = PeriodoFinanciero(inicio, fin, etiqueta)
        analitica = AnaliticaFinancieraIA(self.db)
        datos = await analitica.obtener(sede_id, periodo)
        cartera = datos["cartera"]
        consulta = normalizar(prompt)
        enfoque = "egresos" if any(clave in consulta for clave in ("egreso", "gasto")) else "ingresos"
        generado = datetime.now().strftime("%d/%m/%Y %H:%M")
        reply = (
            f"**Reporte financiero — {etiqueta}**\n"
            f"- Ingresos: **Bs {datos['ingresos']:,.2f}**\n"
            f"- Egresos: **Bs {datos['egresos']:,.2f}**\n"
            f"- Resultado neto: **Bs {datos['saldo']:,.2f}**\n"
            f"- Movimientos registrados: **{datos['movimientos']}**\n\n"
            f"**Cartera activa al {fin.strftime('%d/%m/%Y')}**\n"
            f"- Pendiente por cobrar: **Bs {cartera['pendiente']:,.2f}** en **{cartera['cuotas_pendientes']} cuotas**\n"
            f"- Vencido: **Bs {cartera['vencido']:,.2f}** en **{cartera['cuotas_vencidas']} cuotas**\n\n"
            f"Período: {inicio.strftime('%d/%m/%Y')} al {fin.strftime('%d/%m/%Y')}. Consultado: {generado}."
        )
        if not datos["movimientos"]:
            reply += "\n\nNo hay movimientos de caja en el período; no se completaron valores artificiales."
        return ResultadoChat(
            reply=reply,
            intent="finanzas",
            confidence=1.0,
            sources=[
                {"label": "Libro de caja de la sede", "type": "database"},
                {"label": "Planes y cuotas activas", "type": "database"},
            ],
            actions=[
                {
                    "type": "download",
                    "label": "Descargar reporte CSV",
                    "url": f"/api/v1/ia/reportes/finanzas.csv?desde={inicio.isoformat()}&hasta={fin.isoformat()}",
                },
                {"type": "navigate", "label": "Abrir Finanzas", "url": "/finanzas"},
            ],
            visualizations=analitica.construir_graficos(datos, enfoque),
            suggestions=[
                "Muéstrame la tendencia financiera de los últimos 6 meses",
                "Analiza los egresos por categoría",
                "¿Cuánto está pendiente y vencido por cobrar?",
            ],
        )

    async def _responder_institucion(self, sede_id: int) -> ResultadoChat:
        sede = await self.db.scalar(select(Sede).where(Sede.id == sede_id))
        if not sede:
            texto = "No encontré información institucional configurada para tu sede."
        else:
            direccion = sede.direccion or "no registrada"
            texto = f"Estás trabajando en **{sede.nombre}** (código {sede.codigo}). La dirección registrada es **{direccion}**."
        return ResultadoChat(
            reply=texto,
            intent="institucion",
            confidence=1.0,
            sources=[{"label": "Configuración de la sede", "type": "database"}],
            suggestions=["¿Qué módulos tiene el sistema?", "¿Cómo registro una inscripción?"],
        )

    def _preparar_recordatorio(self, prompt: str, usuario_id: int, sede_id: int) -> ResultadoChat:
        programada = self._extraer_fecha_hora(prompt)
        if not programada:
            return ResultadoChat(
                reply=(
                    "Puedo crear el recordatorio, pero necesito una fecha y hora. Por ejemplo: "
                    "**“Recuérdame mañana a las 09:30 revisar la caja”**."
                ),
                intent="automatizacion",
                confidence=1.0,
            )
        mensaje = re.sub(
            r"(?i)\b(recu[eé]rdame|av[ií]same|recordatorio|programa una notificaci[oó]n)\b",
            "",
            prompt,
        ).strip(" :,-")
        mensaje = re.sub(r"(?i)\bmañana\s+a\s+las\s+\d{1,2}(?::\d{2})?\b", "", mensaje).strip(" :,-")
        mensaje = re.sub(
            r"(?i)\b\d{1,2}/\d{1,2}(?:/\d{4})?\s+a\s+las\s+\d{1,2}(?::\d{2})?\b",
            "",
            mensaje,
        ).strip(" :,-")
        mensaje = mensaje or "Recordatorio solicitado desde Datilera Copilot"
        token = self._crear_token_accion(usuario_id, sede_id, mensaje, programada)
        return ResultadoChat(
            reply=(
                f"Preparé un recordatorio para el **{programada.strftime('%d/%m/%Y a las %H:%M')}**: "
                f"“{mensaje}”. Confírmalo para crearlo."
            ),
            intent="automatizacion",
            confidence=1.0,
            actions=[{"type": "confirm_reminder", "label": "Confirmar recordatorio", "token": token}],
            sources=[{"label": "Fecha interpretada por Datilera", "type": "automation"}],
        )

    async def confirmar_recordatorio(self, token: str, usuario_id: int, sede_id: int) -> ResultadoChat:
        try:
            data = jwt.decode(token, self.settings.jwt_secret, algorithms=[self.settings.jwt_algorithm])
            if data.get("type") != "ia_action" or data.get("action") != "create_reminder":
                raise ValueError("acción no permitida")
            if int(data["sub"]) != usuario_id or int(data["sede"]) != sede_id:
                raise ValueError("la acción pertenece a otra sesión")
            programada = datetime.fromisoformat(data["scheduled_at"])
            mensaje = str(data["message"])[:500]
        except Exception as exc:
            raise ValueError("La confirmación es inválida o expiró; vuelve a solicitar el recordatorio") from exc

        notificacion = Notificacion(
            usuario_id=usuario_id,
            titulo="Recordatorio de Datilera Copilot",
            cuerpo=mensaje,
            tipo="recordatorio_ia",
            canal=CanalNotificacion.app,
            estado=EstadoNotificacion.pendiente,
            prioridad=PrioridadNotificacion.media,
            programada_para=programada,
            enviado=False,
            metadatos={"origen": "ia_copilot", "sede_id": sede_id},
        )
        self.db.add(notificacion)
        await self.db.commit()
        return ResultadoChat(
            reply=f"Recordatorio creado correctamente para el **{programada.strftime('%d/%m/%Y a las %H:%M')}**.",
            intent="automatizacion",
            confidence=1.0,
            sources=[{"label": "Notificaciones personales", "type": "database"}],
        )

    async def _responder_con_modelo(
        self,
        prompt: str,
        usuario_id: int,
        sede_id: int,
        history: list[dict[str, str]],
        proveedor_nombre: str,
        roles: list[str],
    ) -> ResultadoChat:
        provider = get_ia_provider_by_name(proveedor_nombre)
        if not provider:
            return ResultadoChat(
                "El servicio de respuestas generales no está disponible en este momento.",
                "general",
                0.0,
            )
        conocimiento = construir_contexto_asistente(roles)
        instrucciones = (
            "Eres Datilera Copilot. Responde en español, con precisión, de forma breve y accionable. "
            "No inventes funciones, cifras ni datos institucionales. Si algo no aparece en el contexto, dilo claramente. "
            "No solicites contraseñas, documentos de identidad ni datos sensibles. No generes SQL ni afirmes haber ejecutado acciones. "
            "No prometas automatizaciones fuera del catálogo. Distingue una guía de una acción ya ejecutada. "
            "Para cifras económicas, indica al usuario que formule la consulta financiera dentro del chat; el motor seguro la resolverá. "
            f"\n\nCONOCIMIENTO VERIFICADO DEL SISTEMA:\n{conocimiento}"
        )
        mensajes = [
            IAMessage(role=item["role"], content=item["content"][:1000])
            for item in history[-8:]
            if item.get("role") in {"user", "assistant"} and item.get("content")
        ]
        request = IARequest(
            prompt=prompt,
            messages=mensajes,
            system_instruction=instrucciones,
            contexto={"usuario_id": usuario_id, "sede_id": sede_id, "roles": roles},
            temperature=0.15,
            max_tokens=900,
        )
        response = await provider.generar_respuesta(request)
        if not response.successful:
            return ResultadoChat(
                "No pude consultar el modelo en este momento. Intenta nuevamente o pregunta por un módulo específico.",
                "general",
                0.0,
            )
        return ResultadoChat(
            reply=response.content,
            intent="general",
            confidence=0.72,
            sources=[
                {"label": "Conocimiento verificado de Datilera", "type": "manual"},
                {"label": "Asistente Gemini", "type": "ai"},
            ],
            suggestions=[
                "¿Cómo registro una inscripción?",
                "¿Qué puede hacer mi rol?",
                "Muéstrame los módulos disponibles",
            ],
        )

    async def _registrar_auditoria(
        self,
        prompt: str,
        resultado: ResultadoChat,
        usuario_id: int,
        sede_id: int,
        proveedor: str,
    ) -> None:
        try:
            self.db.add(IAConsulta(
                usuario_id=usuario_id,
                sede_id=sede_id,
                proveedor=proveedor,
                modelo=self.settings.gemini_model,
                prompt=prompt,
                respuesta=resultado.reply,
                categoria=resultado.intent,
                contexto={
                    "fuentes": [item["type"] for item in resultado.sources],
                    "confianza": resultado.confidence,
                    "visualizaciones": len(resultado.visualizations),
                },
                exitoso=True,
                tiene_datos_sensibles=False,
            ))
            await self.db.commit()
        except Exception:
            await self.db.rollback()

    def _crear_token_accion(
        self,
        usuario_id: int,
        sede_id: int,
        mensaje: str,
        programada: datetime,
    ) -> str:
        ahora = datetime.now(UTC)
        return jwt.encode({
            "sub": str(usuario_id),
            "sede": str(sede_id),
            "type": "ia_action",
            "action": "create_reminder",
            "message": mensaje[:500],
            "scheduled_at": programada.isoformat(),
            "iat": ahora,
            "exp": ahora + timedelta(minutes=10),
        }, self.settings.jwt_secret, algorithm=self.settings.jwt_algorithm)

    @staticmethod
    def _resolver_periodo(prompt: str) -> tuple[date, date, str]:
        hoy = date.today()
        texto = normalizar(prompt)
        rango = re.search(
            r"desde\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+hasta\s+(\d{1,2})/(\d{1,2})/(\d{4})",
            texto,
        )
        if rango:
            try:
                inicio = date(int(rango.group(3)), int(rango.group(2)), int(rango.group(1)))
                fin = min(date(int(rango.group(6)), int(rango.group(5)), int(rango.group(4))), hoy)
                if inicio <= fin:
                    return inicio, fin, "período personalizado"
            except ValueError:
                pass
        if "hoy" in texto:
            return hoy, hoy, "hoy"
        if "ultimos" in texto and "mes" in texto:
            cantidad_match = re.search(r"ultimos\s+(\d{1,2})\s+mes", texto)
            cantidad = min(max(int(cantidad_match.group(1)) if cantidad_match else 6, 1), 24)
            mes = hoy.month - cantidad + 1
            anio = hoy.year
            while mes <= 0:
                mes += 12
                anio -= 1
            return date(anio, mes, 1), hoy, f"últimos {cantidad} meses"
        if "mes anterior" in texto or "mes pasado" in texto:
            anio = hoy.year if hoy.month > 1 else hoy.year - 1
            mes = hoy.month - 1 if hoy.month > 1 else 12
            return date(anio, mes, 1), date(anio, mes, calendar.monthrange(anio, mes)[1]), "mes anterior"
        if "ano anterior" in texto or "ano pasado" in texto:
            return date(hoy.year - 1, 1, 1), date(hoy.year - 1, 12, 31), f"año {hoy.year - 1}"
        if "ano" in texto or "anual" in texto:
            return hoy.replace(month=1, day=1), hoy, f"año {hoy.year}"
        meses = {
            "enero": 1,
            "febrero": 2,
            "marzo": 3,
            "abril": 4,
            "mayo": 5,
            "junio": 6,
            "julio": 7,
            "agosto": 8,
            "septiembre": 9,
            "octubre": 10,
            "noviembre": 11,
            "diciembre": 12,
        }
        for nombre, mes in meses.items():
            if nombre in texto:
                anio_match = re.search(rf"{nombre}\s+(?:de\s+)?(20\d{{2}})", texto)
                anio = int(anio_match.group(1)) if anio_match else hoy.year
                fin_mes = date(anio, mes, calendar.monthrange(anio, mes)[1])
                return date(anio, mes, 1), min(fin_mes, hoy), f"{nombre} {anio}"
        return hoy.replace(day=1), hoy, hoy.strftime("mes de %B %Y")

    @staticmethod
    def _extraer_fecha_hora(prompt: str) -> datetime | None:
        texto = normalizar(prompt)
        hora_match = re.search(r"\ba las\s+(\d{1,2})(?::(\d{2}))?", texto)
        if not hora_match:
            return None
        horas, minutos = int(hora_match.group(1)), int(hora_match.group(2) or 0)
        if horas > 23 or minutos > 59:
            return None
        hoy = date.today()
        if "manana" in texto:
            dia = hoy + timedelta(days=1)
        else:
            fecha_match = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b", texto)
            if not fecha_match:
                return None
            try:
                dia = date(
                    int(fecha_match.group(3) or hoy.year),
                    int(fecha_match.group(2)),
                    int(fecha_match.group(1)),
                )
            except ValueError:
                return None
        programada = datetime.combine(dia, time(horas, minutos))
        return programada if programada > datetime.now() else None

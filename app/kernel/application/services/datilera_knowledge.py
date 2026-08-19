from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GuiaSistema:
    modulo: str
    ruta: str
    palabras_clave: tuple[str, ...]
    descripcion: str
    pasos: tuple[str, ...]
    reglas: tuple[str, ...] = ()
    consultas: tuple[str, ...] = ()


GUIAS_SISTEMA: tuple[GuiaSistema, ...] = (
    GuiaSistema(
        "Dashboard",
        "/dashboard",
        ("dashboard", "inicio", "indicadores", "resumen general", "metricas"),
        "Muestra indicadores recientes de la sede y accesos rápidos según el rol.",
        (
            "Abre Dashboard en el menú lateral.",
            "Revisa inscritos, ingresos, pagos pendientes y actividad reciente.",
            "Usa el acceso rápido correspondiente para consultar el detalle.",
        ),
        ("Los indicadores siempre se filtran por la sede de la sesión.",),
        ("¿Qué significan los indicadores?", "Muéstrame un resumen financiero", "¿Cómo reviso pagos pendientes?"),
    ),
    GuiaSistema(
        "Inscripciones",
        "/inscripciones",
        ("inscribir", "inscripcion", "preinscripcion", "contrato", "alumno", "tutor", "ficha personal"),
        "Administra alumnos, tutores, documentación, asignación académica y ficha imprimible.",
        (
            "Abre Inscripciones y selecciona Nueva inscripción.",
            "Busca o registra al tutor; los datos de preinscripción se reutilizan cuando existen.",
            "Completa los datos del alumno y verifica sede, grupo, paralelo y turno.",
            "Revisa la ficha y el contrato antes de finalizar.",
        ),
        (
            "Un tutor existente puede vincularse a más de un alumno.",
            "La ficha debe conservar toda la información registrada y su encabezado al imprimir varias hojas.",
        ),
        ("¿Cómo asigno un tutor existente?", "¿Cómo imprimo la ficha completa?", "¿Cómo inscribo a dos hermanos?"),
    ),
    GuiaSistema(
        "Académico",
        "/academico",
        ("academico", "paralelo", "grupo", "asistencia", "horario", "profesora", "reporte diario", "portafolio", "planificacion"),
        "Gestiona grupos, paralelos, asistencia, planificación, actividades y reportes diarios.",
        (
            "Abre Académico.",
            "Elige el grupo o paralelo asignado.",
            "Selecciona asistencia, planificación, actividad o reporte diario.",
            "Verifica fecha y alumnos antes de guardar.",
        ),
        ("Profesoras y tutores sólo ven los grupos y alumnos autorizados para su cuenta.",),
        ("¿Cómo registro asistencia?", "¿Cómo creo un reporte diario?", "¿Dónde veo los paralelos asignados?"),
    ),
    GuiaSistema(
        "Finanzas & Pagos",
        "/finanzas",
        ("finanza", "pago", "ingreso", "egreso", "caja", "arqueo", "deuda", "cuota", "recibo", "descuento", "prorrateo", "morosidad"),
        "Registra pagos y egresos; consulta cuotas, deudores, recibos, libro de caja y reportes.",
        (
            "Abre Finanzas & Pagos.",
            "Selecciona pagos, deudores, caja, egresos, planes o reportes.",
            "Aplica el período y verifica alumno, categoría y monto.",
            "Confirma la operación y comprueba el recibo o movimiento generado.",
        ),
        (
            "El prorrateo usa hasta 20 días hábiles; si quedan tres días calendario o menos, el cobro inicia el mes siguiente.",
            "Los importes prorrateados se redondean a múltiplos de Bs 0,50.",
            "El resultado neto del chat proviene del libro de caja; la cartera pendiente proviene de cuotas activas.",
            "Una anulación financiera requiere permiso y debe conservar auditoría.",
        ),
        ("Genera una gráfica financiera", "¿Cuánto está pendiente por cobrar?", "¿Cómo se calcula el prorrateo?"),
    ),
    GuiaSistema(
        "Comunicaciones",
        "/comunicaciones",
        ("comunicacion", "chat", "mensaje", "notificacion", "comunicado", "destinatario", "prioridad"),
        "Permite conversaciones entre roles autorizados, comunicados y notificaciones persistentes.",
        (
            "Abre Comunicaciones.",
            "Selecciona una conversación o inicia una con un destinatario permitido.",
            "Escribe el mensaje o comunicado, define prioridad cuando corresponda y confirma.",
            "Comprueba su aparición en la conversación o bandeja.",
        ),
        (
            "Tutor puede escribir a profesoras y administración; profesora puede escribir a tutores y administración.",
            "El tutor no crea notificaciones generales.",
            "Las prioridades alta, media y baja afectan orden y presentación de notificaciones.",
        ),
        ("¿A quién puedo enviar mensajes?", "¿Cómo funcionan las prioridades?", "¿Cómo envío un comunicado?"),
    ),
    GuiaSistema(
        "Inventario",
        "/inventario",
        ("inventario", "stock", "item", "producto", "prestamo", "uniforme", "movimiento", "familia"),
        "Controla artículos, categorías, stock por sede, movimientos y préstamos.",
        (
            "Abre Inventarios.",
            "Busca el artículo o créalo con familia y categoría.",
            "Registra entrada, salida o préstamo indicando cantidad y motivo.",
            "Verifica el stock resultante y sus alertas de mínimo.",
        ),
        ("El stock y sus movimientos están separados por sede.",),
        ("¿Cómo registro una entrada?", "¿Cómo presto un uniforme?", "¿Dónde veo stock bajo?"),
    ),
    GuiaSistema(
        "Cursos Extra",
        "/cursos-extra",
        ("curso extra", "taller", "instructor", "alumno externo", "ganancia curso", "balance curso"),
        "Gestiona cursos, participantes internos o externos, cobros, costos y balance independiente.",
        (
            "Abre Cursos Extra y selecciona o crea el curso.",
            "Registra participantes y posteriormente sus cobros o costos.",
            "Revisa ingresos, costos y balance antes de cerrar o distribuir resultados.",
        ),
        ("Las finanzas de Cursos Extra no se mezclan con las mensualidades del módulo Finanzas.",),
        ("¿Cómo inscribo un alumno externo?", "¿Cómo registro un costo?", "¿Cómo consulto el balance?"),
    ),
    GuiaSistema(
        "Usuarios",
        "/usuarios",
        ("usuario", "rol", "permiso", "cuenta", "contrasena", "profesor", "asignacion"),
        "Administra cuentas, roles, estado, asignaciones y restablecimiento de contraseña.",
        (
            "Abre Usuarios y busca por nombre, usuario o correo.",
            "Crea o edita la cuenta y asigna sólo el rol necesario.",
            "Verifica sede, estado y asignaciones antes de guardar.",
        ),
        (
            "El administrador puede generar una contraseña temporal aleatoria.",
            "Después del restablecimiento, el usuario debe cambiar la contraseña al iniciar sesión.",
            "Los permisos efectivos dependen del rol y la sede.",
        ),
        ("¿Cómo restablezco una contraseña?", "¿Cómo asigno una profesora?", "¿Cómo reviso permisos?"),
    ),
    GuiaSistema(
        "Portal de acceso",
        "/registro",
        ("registro tutor", "registro profesora", "codigo de acceso", "olvide contrasena", "portal tutor", "portal profesora"),
        "Unifica el acceso y el registro por código para tutores y profesoras.",
        (
            "Desde el login selecciona completar registro con código.",
            "Elige el tipo de cuenta e ingresa el código entregado por administración.",
            "Completa el formulario y crea las credenciales.",
        ),
        ("Si se olvidó la contraseña, debe contactarse con administración para un restablecimiento seguro.",),
        ("¿Cómo uso mi código de acceso?", "Olvidé mi contraseña", "¿Cómo registro una cuenta de tutor?"),
    ),
)


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in texto if not unicodedata.combining(c))


def buscar_guias(consulta: str, limite: int = 2) -> list[GuiaSistema]:
    consulta_normalizada = normalizar(consulta)
    palabras = set(re.findall(r"[a-z0-9]+", consulta_normalizada))
    puntuadas: list[tuple[int, GuiaSistema]] = []
    for guia in GUIAS_SISTEMA:
        puntaje = 0
        for clave in guia.palabras_clave:
            clave_normalizada = normalizar(clave)
            if clave_normalizada in consulta_normalizada:
                puntaje += 4 if " " in clave_normalizada else 2
            elif clave_normalizada in palabras:
                puntaje += 1
        if puntaje:
            puntuadas.append((puntaje, guia))
    return [guia for _, guia in sorted(puntuadas, key=lambda item: item[0], reverse=True)[:limite]]


def respuesta_guia(guia: GuiaSistema) -> str:
    pasos = "\n".join(f"{indice}. {paso}" for indice, paso in enumerate(guia.pasos, 1))
    reglas = ""
    if guia.reglas:
        reglas = "\n\n**Reglas importantes**\n" + "\n".join(f"- {regla}" for regla in guia.reglas)
    return f"**{guia.modulo}**\n{guia.descripcion}\n\n{pasos}{reglas}"


def construir_contexto_asistente(roles: list[str] | None = None) -> str:
    """Genera el catálogo controlado que recibe el proveedor generativo."""
    rol_texto = ", ".join(roles or []) or "rol autenticado sin nombre disponible"
    bloques = [f"Rol o roles de la sesión: {rol_texto}."]
    for guia in GUIAS_SISTEMA:
        reglas = " ".join(guia.reglas) if guia.reglas else "Sin reglas adicionales documentadas."
        bloques.append(
            f"- {guia.modulo} ({guia.ruta}): {guia.descripcion} Reglas: {reglas}"
        )
    bloques.append(
        "Automatizaciones disponibles: crear un recordatorio personal con fecha y hora, siempre con confirmación; "
        "descargar reportes financieros CSV; abrir módulos. No puede registrar, modificar ni anular pagos automáticamente."
    )
    return "\n".join(bloques)

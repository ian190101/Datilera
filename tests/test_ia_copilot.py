import asyncio
from datetime import date, datetime, timedelta

import jwt

from app.kernel.application.services.datilera_knowledge import buscar_guias, construir_contexto_asistente
from app.kernel.application.services.ia_chat_service import IAChatService, ResultadoChat
from app.kernel.application.services.ia_financial_analytics import AnaliticaFinancieraIA


def test_recupera_guia_financiera_para_pregunta_operativa():
    guias = buscar_guias("¿Cómo registro un pago y obtengo el recibo?")
    assert guias
    assert guias[0].modulo == "Finanzas & Pagos"
    assert guias[0].ruta == "/finanzas"


def test_interpreta_recordatorio_de_manana():
    programada = IAChatService._extraer_fecha_hora("Recuérdame mañana a las 09:30 revisar caja")
    assert programada is not None
    assert programada.date() == date.today() + timedelta(days=1)
    assert (programada.hour, programada.minute) == (9, 30)


def test_periodo_financiero_nunca_incluye_fechas_futuras():
    inicio, fin, _ = IAChatService._resolver_periodo("reporte financiero de este mes")
    assert inicio == date.today().replace(day=1)
    assert fin == date.today()


def test_token_de_accion_esta_vinculado_a_usuario_y_sede():
    service = IAChatService(db=None)  # La firma no necesita una sesión de base de datos.
    programada = datetime.now() + timedelta(days=1)
    token = service._crear_token_accion(7, 3, "Revisar caja", programada)
    payload = jwt.decode(token, service.settings.jwt_secret, algorithms=[service.settings.jwt_algorithm])
    assert payload["type"] == "ia_action"
    assert payload["action"] == "create_reminder"
    assert payload["sub"] == "7"
    assert payload["sede"] == "3"


def test_respuesta_chat_transporta_graficos_y_sugerencias():
    resultado = ResultadoChat(
        reply="Reporte",
        intent="finanzas",
        confidence=1.0,
        visualizations=[{"type": "bar", "labels": ["Ingreso"], "datasets": []}],
        suggestions=["Compara con el mes anterior"],
    ).to_dict()

    assert resultado["visualizations"][0]["type"] == "bar"
    assert resultado["suggestions"] == ["Compara con el mes anterior"]


def test_graficos_financieros_no_inventan_series_vacias():
    datos = {
        "ingresos": 1200.0,
        "egresos": 400.0,
        "saldo": 800.0,
        "tendencia": [],
        "categorias_ingreso": [],
        "categorias_egreso": [],
    }

    graficos = AnaliticaFinancieraIA.construir_graficos(datos)

    assert len(graficos) == 1
    assert graficos[0]["type"] == "bar"
    assert graficos[0]["datasets"][0]["data"] == [1200.0, 400.0, 800.0]


def test_periodo_ultimos_seis_meses_termina_hoy():
    inicio, fin, etiqueta = IAChatService._resolver_periodo("grafica de los ultimos 6 meses")

    assert inicio.day == 1
    assert fin == date.today()
    assert etiqueta == "últimos 6 meses"


def test_reconoce_resumen_financiero_como_consulta_de_datos():
    consulta = "genera un resumen financiero de este mes"

    assert any(clave in consulta for clave in IAChatService.FINANZAS)


def test_enruta_resumen_financiero_al_motor_seguro_y_no_a_gemini():
    class ServicioPrueba(IAChatService):
        async def _responder_finanzas(self, prompt, sede_id, permitido):
            return ResultadoChat("Reporte verificado", "finanzas", 1.0, visualizations=[{"type": "bar"}])

        async def _registrar_auditoria(self, *args, **kwargs):
            return None

    resultado = asyncio.run(
        ServicioPrueba(db=None).procesar_consulta(
            prompt="Genera un resumen financiero de este mes",
            usuario_id=1,
            sede_id=1,
            puede_ver_finanzas=True,
        )
    )

    assert resultado.intent == "finanzas"
    assert resultado.reply == "Reporte verificado"
    assert resultado.visualizations


def test_contexto_del_modelo_incluye_reglas_y_automatizaciones_reales():
    contexto = construir_contexto_asistente(["ADMINISTRADOR"])

    assert "20 días hábiles" in contexto
    assert "crear un recordatorio personal" in contexto
    assert "No puede registrar, modificar ni anular pagos automáticamente" in contexto

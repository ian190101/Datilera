from app.interfaces.web.preinscripcion import extraer_datos_tutor_preinscripcion
from app.kernel.application.acceso.generar_codigo import GenerarCodigoRequest


def test_extrae_tutor_de_preinscripcion_legacy():
    datos = extraer_datos_tutor_preinscripcion(
        entregado_a=None,
        whatsapp_numero="",
        observaciones="Tutor: María Pérez (MADRE) - Tel: 70123456 - Grupo Pre-seleccionado ID: 4",
    )

    assert datos == {
        "nombre": "María Pérez",
        "parentesco": "MADRE",
        "telefono": "70123456",
    }


def test_prioriza_campos_estructurados_del_codigo():
    datos = extraer_datos_tutor_preinscripcion(
        entregado_a="Juan López",
        whatsapp_numero="76543210",
        observaciones="Tutor: Nombre anterior (PADRE) - Tel: 70000000",
    )

    assert datos["nombre"] == "Juan López"
    assert datos["parentesco"] == "PADRE"
    assert datos["telefono"] == "76543210"


def test_solicitud_de_codigo_conserva_datos_del_tutor():
    solicitud = GenerarCodigoRequest(
        sede_id=1,
        rol_id=2,
        alumno_id=3,
        whatsapp_numero="70123456",
        entregado_a="María Pérez",
    )

    assert solicitud.whatsapp_numero == "70123456"
    assert solicitud.entregado_a == "María Pérez"

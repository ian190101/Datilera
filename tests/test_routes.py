from collections import Counter

from app.main import app


def test_no_hay_rutas_http_duplicadas():
    operations = [
        (method, route.path) for route in app.routes for method in (getattr(route, "methods", None) or set())
    ]
    assert [operation for operation, count in Counter(operations).items() if count > 1] == []


def test_no_hay_prefijos_api_duplicados():
    assert all("/api/v1/api/v1" not in route.path for route in app.routes)


def test_media_y_pdf_son_endpoints_protegidos_no_montajes_publicos():
    protected_paths = {route.path for route in app.routes}
    assert "/media/{relative_path:path}" in protected_paths
    assert "/pdf/{relative_path:path}" in protected_paths


def test_comunicaciones_conserva_controladores_compatibles_con_la_interfaz():
    endpoints = {
        (method, route.path): route.endpoint.__name__
        for route in app.routes
        for method in (getattr(route, "methods", None) or set())
    }

    assert endpoints[("GET", "/api/v1/comunicaciones/conversaciones")] == "listar_conversaciones_real"
    assert endpoints[("GET", "/api/v1/comunicaciones/mensajes")] == "listar_mensajes_inbox"
    assert endpoints[("POST", "/api/v1/comunicaciones/mensajes")] == "crear_conversacion_mensaje"


def test_detalle_conversacion_resuelve_primero_el_controlador_de_la_interfaz():
    endpoint = next(
        route.endpoint.__name__
        for route in app.routes
        if "GET" in (getattr(route, "methods", None) or set())
        and getattr(route, "path_regex", None)
        and route.path_regex.fullmatch("/api/v1/comunicaciones/conversaciones/2")
    )

    assert endpoint == "get_conversacion_detalle"


def test_inscripciones_expone_asignacion_de_tutor_existente():
    endpoints = {
        (method, route.path): route.endpoint.__name__
        for route in app.routes
        for method in (getattr(route, "methods", None) or set())
    }

    assert endpoints[("GET", "/api/v1/tutores/existentes")] == "buscar_tutores_existentes"
    assert endpoints[("POST", "/api/v1/inscripciones/asignar-tutor-existente")] == "asignar_tutor_existente"

from app.middleware.api_auth import AuthPrincipal, _puede_usar_ruta_operativa


def test_administrador_puede_acceder_a_modulos_sin_permiso_explicito():
    principal = AuthPrincipal(
        usuario_id=1,
        sede_id=1,
        permisos=frozenset({"Usuarios:Ver"}),
        roles=frozenset({"ADMINISTRADOR"}),
    )

    assert principal.puede_acceder_modulo("Cursos Extra", "CursosExtra")


def test_usuario_regular_necesita_permiso_del_modulo():
    principal = AuthPrincipal(
        usuario_id=2,
        sede_id=1,
        permisos=frozenset({"Academico:Ver"}),
        roles=frozenset({"PROFESORA"}),
    )

    assert not principal.puede_acceder_modulo("Cursos Extra", "CursosExtra")


def test_profesora_puede_consultar_grupos_y_registrar_seguimiento():
    principal = AuthPrincipal(
        usuario_id=2,
        sede_id=1,
        permisos=frozenset(),
        roles=frozenset({"PROFESORA"}),
    )

    assert _puede_usar_ruta_operativa(principal, "/api/v1/grupos", "GET")
    assert _puede_usar_ruta_operativa(principal, "/api/v1/academico/asistencia", "POST")


def test_profesora_no_administra_grupos_por_excepcion_operativa():
    principal = AuthPrincipal(
        usuario_id=2,
        sede_id=1,
        permisos=frozenset(),
        roles=frozenset({"PROFESORA"}),
    )

    assert not _puede_usar_ruta_operativa(principal, "/api/v1/grupos", "POST")
    assert not _puede_usar_ruta_operativa(principal, "/api/v1/paralelos/3", "PUT")


def test_tutor_solo_consulta_academico_y_gestiona_sus_notificaciones():
    principal = AuthPrincipal(
        usuario_id=3,
        sede_id=1,
        permisos=frozenset(),
        roles=frozenset({"TUTOR"}),
    )

    assert _puede_usar_ruta_operativa(principal, "/api/v1/academico/diario", "GET")
    assert not _puede_usar_ruta_operativa(principal, "/api/v1/academico/asistencia", "POST")
    assert _puede_usar_ruta_operativa(principal, "/api/v1/notificaciones/7/leer", "PATCH")


def test_profesora_y_tutor_pueden_usar_su_perfil_y_comunicaciones():
    for rol in ("PROFESORA", "TUTOR"):
        principal = AuthPrincipal(
            usuario_id=4,
            sede_id=1,
            permisos=frozenset(),
            roles=frozenset({rol}),
        )

        assert _puede_usar_ruta_operativa(principal, "/api/v1/usuarios/me", "GET")
        assert _puede_usar_ruta_operativa(
            principal,
            "/api/v1/comunicaciones/conversaciones",
            "GET",
        )


def test_tutor_no_crea_notificaciones_y_profesora_si_puede():
    profesora = AuthPrincipal(2, 1, frozenset(), frozenset({"PROFESORA"}))
    tutor = AuthPrincipal(3, 1, frozenset(), frozenset({"TUTOR"}))

    assert _puede_usar_ruta_operativa(profesora, "/api/v1/notificaciones/enviar", "POST")
    assert not _puede_usar_ruta_operativa(tutor, "/api/v1/notificaciones/enviar", "POST")

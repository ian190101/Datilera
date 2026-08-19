import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.kernel.application.seguridad.usuario.listar_usuarios import (
    ListarUsuarios,
    ListarUsuariosDTO,
)
from app.kernel.domain.seguridad.rol_entidad import Rol
from app.kernel.domain.seguridad.user_entidad import Usuario


def test_listar_usuarios_serializa_roles_y_contacto():
    usuario = Usuario(
        id=1,
        nombre_usuario="ian",
        nombres="Ian",
        apellidos="Vera",
        email="ian@example.com",
        telefono="70000000",
        contrasena="hash-seguro",
        roles=[Rol(id=1, nombre="ADMINISTRADOR")],
        sede_id=1,
    )
    repositorio = SimpleNamespace(
        list_paginated=AsyncMock(return_value=([usuario], 1)),
    )

    resultado = asyncio.run(ListarUsuarios(repositorio).execute(ListarUsuariosDTO(q=" Ian ")))

    assert resultado["total"] == 1
    assert resultado["items"][0]["rol"] == "ADMINISTRADOR"
    assert resultado["items"][0]["telefono"] == "70000000"
    repositorio.list_paginated.assert_awaited_once_with(
        page=1,
        per_page=20,
        sede_id=None,
        rol_nombre=None,
        activo=None,
        q="Ian",
    )

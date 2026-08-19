import string

import pytest
from pydantic import ValidationError

from app.interfaces.api.v1.seguridad import CambiarPasswordObligatorioRequest
from app.interfaces.api.v1.usuarios import generar_password_temporal


def test_password_temporal_es_aleatoria_y_compleja():
    passwords = {generar_password_temporal() for _ in range(50)}
    assert len(passwords) == 50
    for password in passwords:
        assert len(password) == 14
        assert any(char in string.ascii_uppercase for char in password)
        assert any(char in string.ascii_lowercase for char in password)
        assert any(char in string.digits for char in password)
        assert any(char in "!@#$%*-_" for char in password)


def test_cambio_obligatorio_rechaza_confirmacion_distinta():
    with pytest.raises(ValidationError, match="no coinciden"):
        CambiarPasswordObligatorioRequest(
            password_actual="Temporal123!",
            password_nueva="NuevaSegura123!",
            password_confirmacion="Diferente123!",
        )


def test_cambio_obligatorio_rechaza_reutilizar_password_temporal():
    with pytest.raises(ValidationError, match="diferente"):
        CambiarPasswordObligatorioRequest(
            password_actual="MismaPassword123!",
            password_nueva="MismaPassword123!",
            password_confirmacion="MismaPassword123!",
        )

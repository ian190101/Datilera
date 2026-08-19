from app.config.settings import get_settings
from app.infrastructure.auth.auth_utils import PyJWTTokenService


def test_access_token_contiene_identidad_sede_permisos_y_roles():
    service = PyJWTTokenService(get_settings())
    token = service.create_access_token(7, 3, ["Finanzas:Ver"], ["ADMINISTRADOR"])
    payload = service.decode_token(token)

    assert payload["sub"] == "7"
    assert payload["sede"] == "3"
    assert payload["type"] == "access"
    assert payload["pms"] == ["Finanzas:Ver"]
    assert payload["roles"] == ["ADMINISTRADOR"]


def test_refresh_token_tiene_jti_y_tipo_correcto():
    service = PyJWTTokenService(get_settings())
    payload = service.decode_token(service.create_refresh_token(7, "jti-unico"))

    assert payload["sub"] == "7"
    assert payload["jti"] == "jti-unico"
    assert payload["type"] == "refresh"

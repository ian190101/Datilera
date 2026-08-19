import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.infrastructure.services.secure_storage import SecureStorageService


def test_guarda_imagen_con_nombre_generado(tmp_path):
    service = SecureStorageService(tmp_path)
    upload = UploadFile(filename="../../ataque.jpg", file=BytesIO(b"\xff\xd8\xff" + b"x" * 20))

    result = asyncio.run(service.save_upload(upload, "perfiles", allowed_mime_types={"image/jpeg"}))

    assert "ataque" not in result.relative_path
    assert service.resolve_for_read(result.relative_path).is_file()


def test_rechaza_contenido_que_no_coincide_con_tipo_permitido(tmp_path):
    service = SecureStorageService(tmp_path)
    upload = UploadFile(filename="falso.jpg", file=BytesIO(b"contenido no reconocido"))

    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.save_upload(upload, "perfiles", allowed_mime_types={"image/jpeg"}))
    assert exc.value.status_code == 415


def test_impide_lectura_fuera_del_directorio(tmp_path):
    service = SecureStorageService(tmp_path)
    with pytest.raises(HTTPException):
        service.resolve_for_read("../../secreto.txt")

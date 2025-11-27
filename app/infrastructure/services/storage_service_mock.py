# app/infrastructure/services/storage_service_mock.py

from app.kernel.domain.comunicaciones import TipoAdjunto, ArchivoStorageServicePort


class StorageServiceMock(ArchivoStorageServicePort):
    """Mock del servicio de almacenamiento para desarrollo."""

    async def subir_adjunto(
        self,
        archivo_bytes: bytes,
        nombre_archivo: str,
        mime_type: str,
        carpeta: str = "mensajes",
    ) -> str:
        """Mock: Retorna URL ficticia."""
        return f"https://storage.example.com/{carpeta}/{nombre_archivo}"

    async def eliminar_adjunto(self, url: str) -> bool:
        """Mock: Siempre retorna True."""
        print(f"[Storage Mock] Eliminando archivo: {url}")
        return True

    async def validar_mime_type(self, mime_type: str) -> bool:
        """Mock: Permite todos los tipos."""
        tipos_permitidos = [
            "image/jpeg", "image/png", "image/gif",
            "application/pdf",
            "video/mp4",
            "audio/mpeg",
        ]
        return mime_type in tipos_permitidos

    async def obtener_tamano_maximo(self, tipo_adjunto: TipoAdjunto) -> int:
        """Mock: Retorna límites ficticios."""
        limites = {
            TipoAdjunto.IMAGEN: 5 * 1024 * 1024,      # 5MB
            TipoAdjunto.VIDEO: 50 * 1024 * 1024,      # 50MB
            TipoAdjunto.AUDIO: 10 * 1024 * 1024,      # 10MB
            TipoAdjunto.DOCUMENTO: 10 * 1024 * 1024,  # 10MB
        }
        return limites.get(tipo_adjunto, 5 * 1024 * 1024)

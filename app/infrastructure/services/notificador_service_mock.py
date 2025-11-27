# app/infrastructure/services/notificador_service_mock.py

from app.kernel.domain.comunicaciones import Notificacion, NotificadorServicePort


class NotificadorServiceMock(NotificadorServicePort):
    """Mock del servicio notificador para desarrollo."""

    async def enviar_in_app(self, notificacion: Notificacion) -> bool:
        """Mock: Simula envío in-app."""
        print(f"[Notificador Mock] IN_APP - {notificacion.titulo}")
        return True

    async def enviar_email(
        self, notificacion: Notificacion, destinatario_email: str
    ) -> bool:
        """Mock: Simula envío por email."""
        print(f"[Notificador Mock] EMAIL a {destinatario_email} - {notificacion.titulo}")
        return True

    async def enviar_push(
        self, notificacion: Notificacion, dispositivo_token: str
    ) -> bool:
        """Mock: Simula envío push."""
        print(f"[Notificador Mock] PUSH a {dispositivo_token} - {notificacion.titulo}")
        return True

    async def enviar_sms(
        self, notificacion: Notificacion, numero_telefono: str
    ) -> bool:
        """Mock: Simula envío SMS."""
        print(f"[Notificador Mock] SMS a {numero_telefono} - {notificacion.titulo}")
        return True

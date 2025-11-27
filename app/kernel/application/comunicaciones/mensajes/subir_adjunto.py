# app/kernel/application/comunicaciones/mensajes/subir_adjunto.py

from app.kernel.domain.comunicaciones import (
    MensajeAdjunto,
    TipoAdjunto,
    MensajeRepositoryPort,
    ParticipanteRepositoryPort,
    MensajeAdjuntoRepositoryPort,
    ArchivoStorageServicePort,
    MensajeNoEncontrado,
    ParticipanteNoAutorizado,
    ArchivoTamanoExcedido,
    TipoArchivoNoPermitido,
)


class SubirAdjuntoUseCase:
    """Caso de uso: Subir archivo adjunto a mensaje.
    
    Reglas:
    - Solo participantes pueden adjuntar
    - Validar tipo y tamaño según configuración
    - Subir a storage externo (S3, etc.)
    """

    def __init__(
        self,
        mensaje_repo: MensajeRepositoryPort,
        participante_repo: ParticipanteRepositoryPort,
        adjunto_repo: MensajeAdjuntoRepositoryPort,
        storage_service: ArchivoStorageServicePort,
    ):
        self.mensaje_repo = mensaje_repo
        self.participante_repo = participante_repo
        self.adjunto_repo = adjunto_repo
        self.storage_service = storage_service

    async def ejecutar(
        self,
        mensaje_id: int,
        usuario_id: int,
        archivo_bytes: bytes,
        nombre_archivo: str,
        mime_type: str,
        tipo: TipoAdjunto,
    ) -> MensajeAdjunto:
        """Sube un adjunto a un mensaje.
        
        Args:
            mensaje_id: ID del mensaje
            usuario_id: Usuario que sube
            archivo_bytes: Contenido del archivo
            nombre_archivo: Nombre original
            mime_type: Tipo MIME
            tipo: Tipo de adjunto
            
        Returns:
            Adjunto creado
            
        Raises:
            MensajeNoEncontrado: Si no existe
            ParticipanteNoAutorizado: Si no es participante
            TipoArchivoNoPermitido: Si MIME no permitido
            ArchivoTamanoExcedido: Si excede límite
        """
        # Verificar mensaje existe
        mensaje = await self.mensaje_repo.obtener_por_id(mensaje_id)
        if not mensaje:
            raise MensajeNoEncontrado(mensaje_id)

        # Verificar que es participante
        es_participante = await self.participante_repo.es_participante(
            mensaje.conversacion_id, usuario_id
        )
        if not es_participante:
            raise ParticipanteNoAutorizado(usuario_id, mensaje.conversacion_id)

        # Validar tipo MIME
        mime_permitido = await self.storage_service.validar_mime_type(mime_type)
        if not mime_permitido:
            raise TipoArchivoNoPermitido(mime_type)

        # Validar tamaño
        tamano_bytes = len(archivo_bytes)
        tamano_maximo = await self.storage_service.obtener_tamano_maximo(tipo)
        if tamano_bytes > tamano_maximo:
            raise ArchivoTamanoExcedido(tamano_bytes, tamano_maximo)

        # Subir archivo
        url = await self.storage_service.subir_adjunto(
            archivo_bytes=archivo_bytes,
            nombre_archivo=nombre_archivo,
            mime_type=mime_type,
            carpeta="mensajes",
        )

        # Crear adjunto
        adjunto = await self.adjunto_repo.crear(
            mensaje_id=mensaje_id,
            tipo=tipo,
            url=url,
            nombre_archivo=nombre_archivo,
            tamano_bytes=tamano_bytes,
            mime_type=mime_type,
        )

        return adjunto

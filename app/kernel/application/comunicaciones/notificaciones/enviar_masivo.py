# app/kernel/application/comunicaciones/notificaciones/enviar_masivo.py

from __future__ import annotations

from typing import Dict, List, Optional
from datetime import datetime

# --- Dominio ---
from app.kernel.domain.comunicaciones import (
    CanalNotificacion,
    NotificacionRepositoryPort,
    NotificadorServicePort,
)
from app.kernel.domain.comunicaciones.notificacion_entidad import Notificacion

# --- Seguridad ---
from app.kernel.domain.seguridad.user_entidad import Usuario
from app.kernel.domain.seguridad.ports import AbstractUserRepository

# --- Excepciones ---
from app.kernel.domain.exceptions import PermisoDenegadoError

# NUEVO: helper para WS
from app.infrastructure.notificaciones.service import publicar_notificacion_nueva


class EnviarNotificacionMasivaUseCase:
    """Caso de uso: Enviar notificación masiva (US-COM-009)."""

    def __init__(
        self,
        notificacion_repo: NotificacionRepositoryPort,
        notificador_service: NotificadorServicePort,
        usuario_repo: AbstractUserRepository,
    ):
        self.notificacion_repo = notificacion_repo
        self.notificador_service = notificador_service
        self.usuario_repo = usuario_repo

    async def ejecutar(
        self,
        emisor_id: int,
        titulo: str,
        cuerpo: str,
        tipo: str,
        sede_ids: Optional[List[int]] = None,
        rol_destinatarios: Optional[str] = None,
        canal: CanalNotificacion = CanalNotificacion.IN_APP,
        prioridad: str = "media",
        programada_para: Optional[datetime] = None,
        metadatos: Optional[Dict] = None,
    ) -> Dict[str, object]:
        """Envía notificación masiva a múltiples usuarios."""
        # 1. Validar permisos del emisor
        emisor = await self.usuario_repo.get_by_id(emisor_id)
        if emisor is None:
            raise PermisoDenegadoError("Emisor no encontrado")

        rol_nombre = emisor.rol.nombre if hasattr(emisor.rol, "nombre") else str(emisor.rol)
        if rol_nombre not in {"directora", "admin", "superadmin"}:
            raise PermisoDenegadoError(
                "Solo directora, admin o superadmin pueden enviar notificaciones masivas"
            )

        # 2. Obtener destinatarios
        destinatarios: List[Usuario] = await self._obtener_destinatarios(
            sede_ids=sede_ids,
            rol_destinatarios=rol_destinatarios,
            emisor=emisor,
        )
        usuario_ids = [u.id for u in destinatarios]

        # 3. Si son muchos → encolar en Celery
        if len(destinatarios) > 50:
            from app.infrastructure.services.notificaciones import enviar_notificacion_masiva_task

            tarea = enviar_notificacion_masiva_task.delay(
                destinatarios=usuario_ids,
                titulo=titulo,
                cuerpo=cuerpo,
                tipo=tipo,
                canal=canal.value,
                prioridad=prioridad,
                programada_para=programada_para.isoformat() if programada_para else None,
                metadatos=metadatos,
            )

            return {
                "notificaciones_creadas": len(destinatarios),
                "destinatarios": usuario_ids,
                "tarea_id": tarea.id,
                "mensaje": f"Notificación encolada para {len(destinatarios)} usuarios",
            }

        # 4. Si son pocos → crear directamente
        notificaciones_creadas: List[Notificacion] = []
        for usuario in destinatarios:
            notif = await self.notificacion_repo.crear(
                usuario_id=usuario.id,
                titulo=titulo,
                cuerpo=cuerpo,
                tipo=tipo,
                canal=canal,
                prioridad=prioridad,
                programada_para=programada_para,
                metadatos=metadatos,
            )
            notificaciones_creadas.append(notif)

            # NUEVO: disparo WebSocket inmediato para IN_APP sin programar
            if canal == CanalNotificacion.IN_APP and not programada_para:
                await publicar_notificacion_nueva(
                    usuario_ids_destino=[usuario.id],
                    notificacion_id=notif.id,
                    titulo=notif.titulo,
                    mensaje=notif.cuerpo,
                    tipo=notif.tipo,
                    creado_en=notif.creado_en.isoformat(),
                    sede_id=notif.sede_id,
                )

        return {
            "notificaciones_creadas": len(notificaciones_creadas),
            "destinatarios": usuario_ids,
            "mensaje": f"Notificación enviada a {len(notificaciones_creadas)} usuarios",
        }

    async def _obtener_destinatarios(
        self,
        sede_ids: Optional[List[int]],
        rol_destinatarios: Optional[str],
        emisor: Usuario,
    ) -> List[Usuario]:
        """Filtra usuarios según permisos y filtros aplicados."""
        filtros = {
            "page": 1,
            "per_page": 10_000,
            "activo": True,
        }

        if emisor.rol.nombre != "superadmin":
            if emisor.sede_id is None:
                raise PermisoDenegadoError("El emisor no tiene sede asignada")
            filtros["sede_id"] = emisor.sede_id
        elif sede_ids:
            pass

        if rol_destinatarios:
            filtros["rol_nombre"] = rol_destinatarios

        usuarios, _total = await self.usuario_repo.list_paginated(**filtros)

        if emisor.rol.nombre == "superadmin" and sede_ids:
            usuarios = [u for u in usuarios if u.sede_id in sede_ids]

        return usuarios

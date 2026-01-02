"""
Caso de Uso: Enviar Recordatorio de Pago a Tutores
Endpoint: POST /api/v1/finanzas/estado-cuenta/{alumno_id}/recordatorio
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Recordatorio se envía 1, 3 y 5 días ANTES del vencimiento (día 10 del mes)
2. Horarios: 11:00, 14:00 y 17:00 horas
3. Canal: Notificación persistente en sistema + Email (opcional)
4. Contenido: Nombre alumno, monto cuota, fecha vencimiento, mensaje personalizado
5. NO enviar si cuota ya está pagada
6. NO enviar si alumno tiene suspensión de notificaciones
7. Registrar envío en auditoría
"""

from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List

from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort
from app.kernel.domain.finanzas.ports import (
    IEstadoCuentaNinoRepository,
    IPlanCuotaRepository,
)
from app.kernel.domain.comunicaciones.ports import NotificacionRepositoryPort
from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort
from app.kernel.domain.alumnos.errors import AlumnoNoEncontradoError
from app.kernel.domain.finanzas.errors import EstadoCuentaNoEncontradoError


class RecordatorioEnviadoDTO:
    """DTO de respuesta para recordatorio enviado"""
    
    def __init__(
        self,
        alumno_id: int,
        alumno_nombre_completo: str,
        cuota_id: int,
        monto_cuota: Decimal,
        fecha_vencimiento: date,
        tutores_notificados: int,
        notificacion_id: int,
        fecha_envio: datetime,
    ) -> None:
        self.alumno_id = alumno_id
        self.alumno_nombre_completo = alumno_nombre_completo
        self.cuota_id = cuota_id
        self.monto_cuota = monto_cuota
        self.fecha_vencimiento = fecha_vencimiento
        self.tutores_notificados = tutores_notificados
        self.notificacion_id = notificacion_id
        self.fecha_envio = fecha_envio


class EnviarRecordatorioPagoCU:
    """
    Caso de Uso: Enviar recordatorio de pago próximo a vencer
    
    Adaptado para usar ports.py actual:
    - IEstadoCuentaNinoRepository.obtener_por_alumno(alumno_id)
    - IPlanCuotaRepository.obtener_proxima_pendiente(plan_pago_id)
    - INotificacionRepository.crear(notificacion_data)
    - IAuditoriaAccionesRepository.registrar(auditoria_data)
    
    NOTA: Este CU se ejecuta desde una tarea programada (Celery/RQ)
    que verifica fechas 1/3/5 días antes del día 10 a las 11/14/17 horas.
    """
    
    def __init__(
        self,
        alumno_repo: AlumnoRepositoryPort,
        estado_cuenta_repo: IEstadoCuentaNinoRepository,
        cuota_repo: IPlanCuotaRepository,
        notificacion_repo: NotificacionRepositoryPort,
        auditoria_repo: AuditoriaAccionRepositoryPort,
    ) -> None:
        self.alumno_repo = alumno_repo
        self.estado_cuenta_repo = estado_cuenta_repo
        self.cuota_repo = cuota_repo
        self.notificacion_repo = notificacion_repo
        self.auditoria_repo = auditoria_repo
    
    async def execute(
        self,
        alumno_id: int,
        sede_id: int,
        usuario_sistema_id: int,  # ID del usuario "Sistema" para auditoría
    ) -> RecordatorioEnviadoDTO:
        """
        Envía recordatorio de pago a tutores de un alumno
        
        Args:
            alumno_id: ID del alumno
            sede_id: ID de la sede (validación RBAC)
            usuario_sistema_id: ID del usuario "Sistema" para auditoría
        
        Returns:
            RecordatorioEnviadoDTO con información del recordatorio enviado
        
        Raises:
            AlumnoNoEncontradoError: Si el alumno no existe
            EstadoCuentaNoEncontradoError: Si no tiene estado de cuenta
            ValueError: Si no tiene cuotas pendientes próximas a vencer
        """
        # 1. Validar alumno
        alumno_dict: Dict[str, Any] = await self._validar_alumno(alumno_id, sede_id)
        
        # 2. Verificar si tiene suspensión de notificaciones
        if alumno_dict.get("suspender_notificaciones", False):
            raise ValueError(
                f"Alumno {alumno_id} tiene suspendidas las notificaciones"
            )
        
        # 3. Obtener estado de cuenta
        estado_cuenta: Dict[str, Any] = await self._obtener_estado_cuenta(alumno_id)
        
        # 4. Obtener plan_pago_id
        plan_pago_id: Optional[int] = estado_cuenta.get("plan_pago_id")
        
        if not plan_pago_id:
            raise ValueError(f"Alumno {alumno_id} no tiene plan de pago activo")
        
        # 5. Obtener próxima cuota pendiente
        cuota_proxima: Optional[Dict[str, Any]] = await self.cuota_repo.obtener_proxima_pendiente(
            plan_pago_id=plan_pago_id
        )
        
        if not cuota_proxima:
            raise ValueError(f"Alumno {alumno_id} no tiene cuotas pendientes")
        
        # 6. Verificar si cuota está próxima a vencer (1/3/5 días antes)
        fecha_vencimiento: date = cuota_proxima["fecha_vencimiento"]
        dias_hasta_vencimiento: int = (fecha_vencimiento - date.today()).days
        
        if dias_hasta_vencimiento not in [1, 3, 5]:
            raise ValueError(
                f"Cuota no está en ventana de recordatorio (días hasta vencimiento: {dias_hasta_vencimiento})"
            )
        
        # 7. Verificar si cuota ya está pagada
        monto_pagado: Decimal = Decimal(str(cuota_proxima.get("monto_pagado", 0)))
        monto_cuota: Decimal = Decimal(str(cuota_proxima["monto"]))
        
        if monto_pagado >= monto_cuota:
            raise ValueError(f"Cuota {cuota_proxima['id']} ya está pagada completamente")
        
        # 8. Construir mensaje de recordatorio
        mensaje: str = self._construir_mensaje_recordatorio(
            alumno_nombre=f"{alumno_dict['nombre']} {alumno_dict['apellidos']}",
            monto_cuota=monto_cuota - monto_pagado,
            fecha_vencimiento=fecha_vencimiento,
            dias_restantes=dias_hasta_vencimiento,
        )
        
        # 9. Obtener IDs de tutores (asumiendo que están en alumno_dict)
        tutores_ids: List[int] = alumno_dict.get("tutores_ids", [])
        
        if not tutores_ids:
            raise ValueError(f"Alumno {alumno_id} no tiene tutores registrados")
        
        # 10. Crear notificación persistente para cada tutor
        notificacion_id: int = await self.notificacion_repo.crear({
            "tipo": "RECORDATORIO_PAGO",
            "titulo": "Recordatorio de Pago Próximo a Vencer",
            "mensaje": mensaje,
            "destinatarios_ids": tutores_ids,
            "alumno_id": alumno_id,
            "sede_id": sede_id,
            "prioridad": "ALTA" if dias_hasta_vencimiento == 1 else "MEDIA",
            "enviado_por_id": usuario_sistema_id,
            "fecha_envio": datetime.now(),
            "metadata": {
                "cuota_id": cuota_proxima["id"],
                "monto_cuota": str(monto_cuota),
                "fecha_vencimiento": fecha_vencimiento.isoformat(),
                "dias_restantes": dias_hasta_vencimiento,
            }
        })
        
        # 11. Registrar acción en auditoría
        await self.auditoria_repo.registrar({
            "accion": "ENVIO_RECORDATORIO_PAGO",
            "modulo": "FINANZAS",
            "entidad": "CUOTA_PLAN_PAGO",
            "entidad_id": cuota_proxima["id"],
            "usuario_id": usuario_sistema_id,
            "sede_id": sede_id,
            "detalles": {
                "alumno_id": alumno_id,
                "cuota_id": cuota_proxima["id"],
                "notificacion_id": notificacion_id,
                "tutores_notificados": len(tutores_ids),
                "dias_hasta_vencimiento": dias_hasta_vencimiento,
            },
            "fecha": datetime.now(),
        })
        
        # 12. Construir DTO de respuesta
        return RecordatorioEnviadoDTO(
            alumno_id=alumno_id,
            alumno_nombre_completo=f"{alumno_dict['nombre']} {alumno_dict['apellidos']}",
            cuota_id=cuota_proxima["id"],
            monto_cuota=monto_cuota - monto_pagado,
            fecha_vencimiento=fecha_vencimiento,
            tutores_notificados=len(tutores_ids),
            notificacion_id=notificacion_id,
            fecha_envio=datetime.now(),
        )
    
    async def _validar_alumno(self, alumno_id: int, sede_id: int) -> Dict[str, Any]:
        """Valida que el alumno existe y pertenece a la sede"""
        alumno: Optional[Dict[str, Any]] = await self.alumno_repo.obtener_por_id(alumno_id)
        
        if not alumno:
            raise AlumnoNoEncontradoError(f"Alumno {alumno_id} no encontrado")
        
        if alumno.get("sede_id") != sede_id:
            raise AlumnoNoEncontradoError(
                f"Alumno {alumno_id} no pertenece a la sede {sede_id}"
            )
        
        return alumno
    
    async def _obtener_estado_cuenta(self, alumno_id: int) -> Dict[str, Any]:
        """Obtiene el estado de cuenta del alumno"""
        estado: Optional[Dict[str, Any]] = await self.estado_cuenta_repo.obtener_por_alumno(alumno_id)
        
        if not estado:
            raise EstadoCuentaNoEncontradoError(
                f"Estado de cuenta no encontrado para alumno {alumno_id}"
            )
        
        return estado
    
    def _construir_mensaje_recordatorio(
        self,
        alumno_nombre: str,
        monto_cuota: Decimal,
        fecha_vencimiento: date,
        dias_restantes: int,
    ) -> str:
        """Construye el mensaje personalizado de recordatorio"""
        mensaje: str = (
            f"🔔 **Recordatorio de Pago - Centro Datilera**\n\n"
            f"Estimado(a) tutor(a),\n\n"
            f"Le recordamos que tiene un pago pendiente:\n\n"
            f"📌 **Alumno:** {alumno_nombre}\n"
            f"💵 **Monto:** Bs. {monto_cuota:.2f}\n"
            f"📅 **Fecha de vencimiento:** {fecha_vencimiento.strftime('%d/%m/%Y')}\n"
            f"⏰ **Días restantes:** {dias_restantes} día(s)\n\n"
        )
        
        if dias_restantes == 1:
            mensaje += (
                "⚠️ **ATENCIÓN:** El vencimiento es mañana. "
                "Por favor, realice su pago a la brevedad para evitar recargos.\n\n"
            )
        elif dias_restantes == 3:
            mensaje += (
                "ℹ️ Recuerde realizar su pago antes de la fecha de vencimiento "
                "para evitar inconvenientes.\n\n"
            )
        else:  # 5 días
            mensaje += (
                "ℹ️ Le recordamos con anticipación para su comodidad.\n\n"
            )
        
        mensaje += (
            "**Medios de pago:**\n"
            "- Efectivo en recepción\n"
            "- Transferencia bancaria\n"
            "- QR (solicitar en recepción)\n\n"
            "Gracias por su confianza.\n"
            "**Centro de Estimulación Infantil Datilera**"
        )
        
        return mensaje

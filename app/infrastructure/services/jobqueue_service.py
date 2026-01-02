# app/infrastructure/services/jobqueue_service.py
from __future__ import annotations

from datetime import date, datetime, time, timedelta

from app.infrastructure.queues.broker import broker


class JobQueueService:
    """Servicio de orquestación de jobs asíncronos."""

    # ---------- Multimedia ----------
    def enqueue_watermark_media(self, media_id: int) -> str:
        # Tarea definida en app.infrastructure.tasks.multimediatasks
        return broker.enqueue(
            "app.infrastructure.tasks.multimediatasks.procesar_watermark_media",
            args=[media_id],
            queue_name="default",
        )

    # ---------- Reportes ----------
    def programar_arqueo_mensual(self, sede_id: int, anio: int, mes: int) -> str:
        # Ejecutar el día 6 a las 06:00
        run_at = datetime(anio, mes, 6, 6, 0, 0)
        return broker.enqueue_at(
            "app.infrastructure.tasks.reportestasks.generar_reporte_arqueo_mensual",
            run_at=run_at,
            args=[sede_id, anio, mes],
            queue_name="high",
        )

    def enqueue_exportacion_masiva(self, exportacion_id: int) -> str:
        return broker.enqueue(
            "app.infrastructure.tasks.reportestasks.generar_exportacion_masiva",
            args=[exportacion_id],
            queue_name="low",
        )

    # ---------- Recordatorios de pagos ----------
    def programar_recordatorios_pagos_sede(
        self,
        sede_id: int,
        anio: int,
        mes: int,
    ) -> list[str]:
        """Programa jobs para 1/3/5 días antes del 10, a las 11, 14 y 17 hs."""
        job_ids: list[str] = []
        dia_10 = date(anio, mes, 10)
        offsets = [1, 3, 5]
        horas = [time(11, 0), time(14, 0), time(17, 0)]

        for dias in offsets:
            dia = dia_10 - timedelta(days=dias)
            for h in horas:
                run_at = datetime.combine(dia, h)
                job_ids.append(
                    broker.enqueue_at(
                        "app.infrastructure.tasks.recordatoriostasks.enviar_recordatorios_pagos_sede",
                        run_at=run_at,
                        args=[sede_id, dia_10.isoformat()],
                        queue_name="default",
                    )
                )
        return job_ids

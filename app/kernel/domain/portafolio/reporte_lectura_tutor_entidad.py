# app/kernel/domain/portafolio/reporte_lectura_tutor_entidad.py
from __future__ import annotations
from datetime import datetime


class ReporteLecturaTutor:
    """
    Entidad **ReporteLecturaTutor**.
    - Registra la primera lectura de un tutor sobre un reporte diario.
    - Único por (reporte_diario_id, tutor_id) a nivel de infraestructura.
    """
    def __init__(
        self,
        id: int,
        reporte_diario_id: int,
        tutor_id: int,
        leido_en: datetime | None = None,
    ):
        self.id = id
        self.reporte_diario_id = reporte_diario_id
        self.tutor_id = tutor_id
        self.leido_en = leido_en

    def marcar_leido(self, cuando: datetime | None = None) -> None:
        if self.leido_en is not None:
            return
        self.leido_en = cuando or datetime.utcnow()
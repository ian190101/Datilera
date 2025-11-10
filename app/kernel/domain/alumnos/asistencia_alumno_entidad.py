from datetime import date
from typing import Optional

class AsistenciaAlumno:
    def __init__(self, id: int, alumno_id: int, fecha: date, estado: str,
                 hora_retraso: Optional[str] = None):
        self.id = id
        self.alumno_id = alumno_id
        self.fecha = fecha
        self.estado = estado
        self.hora_retraso = hora_retraso

    def marcar_presente(self):
        self.estado = "presente"
        self.hora_retraso = None

    def marcar_falta(self):
        self.estado = "falta"
        self.hora_retraso = None

    def marcar_retraso(self, hora: str):
        self.estado = "retraso"
        self.hora_retraso = hora
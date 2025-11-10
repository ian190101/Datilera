from datetime import date
from typing import Optional

class AsistenciaPersonal:
    def __init__(self, id: int, usuario_id: int, fecha: date, estado: str,
                 hora_retraso: Optional[str] = None):
        self.id = id
        self.usuario_id = usuario_id
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
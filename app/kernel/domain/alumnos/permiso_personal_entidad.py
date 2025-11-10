from datetime import datetime
from typing import Optional

class PermisoPersonal:
    def __init__(self, id: int, usuario_id: int, titulo: str, descripcion: str,
                 archivo_url: Optional[str], estado: str, creado_en: datetime):
        self.id = id
        self.usuario_id = usuario_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.archivo_url = archivo_url
        self.estado = estado
        self.creado_en = creado_en

    def aprobar(self):
        self.estado = "aprobado"

    def rechazar(self):
        self.estado = "rechazado"

    def marcar_pendiente(self):
        self.estado = "pendiente"
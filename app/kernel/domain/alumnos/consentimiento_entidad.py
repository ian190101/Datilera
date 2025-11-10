from datetime import datetime

class Consentimiento:
    def __init__(self, id: int, alumno_id: int, tipo: str, aceptado: bool,
                 creado_en: datetime):
        self.id = id
        self.alumno_id = alumno_id
        self.tipo = tipo
        self.aceptado = aceptado
        self.creado_en = creado_en

    def revocar(self):
        """Revoca el consentimiento."""
        self.aceptado = False
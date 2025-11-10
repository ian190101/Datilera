from datetime import date
from typing import Optional

class Alumno:
    def __init__(self, id: int, nombre: str, fecha_nacimiento: date, codigo: str,
                 sede_id: int, gestion: int, creado_en: date, actualizado_en: date,
                 activo: bool = True):
        self.id = id
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        self.codigo = codigo
        self.sede_id = sede_id
        self.gestion = gestion
        self.creado_en = creado_en
        self.actualizado_en = actualizado_en
        self.activo = activo

    def calcular_edad(self) -> str:
        """Devuelve la edad en años y meses según la fecha actual."""
        hoy = date.today()
        años = hoy.year - self.fecha_nacimiento.year
        meses = hoy.month - self.fecha_nacimiento.month
        if hoy.day < self.fecha_nacimiento.day:
            meses -= 1
        if meses < 0:
            años -= 1
            meses += 12
        return f"{años} años {meses} meses" if años > 0 else f"{meses} meses"

    def activar(self):
        self.activo = True

    def desactivar(self):
        self.activo = False
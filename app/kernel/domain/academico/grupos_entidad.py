class Grupo:
    def __init__(self, id: int, nombre: str, edad_min_meses: int, edad_max_meses: int, sede_id: int, activo: bool = True):
        self.id = id
        self.nombre = nombre
        self.edad_min_meses = edad_min_meses
        self.edad_max_meses = edad_max_meses
        self.sede_id = sede_id
        self.activo = activo

    def desactivar(self):
        self.activo = False

    def activar(self):
        self.activo = True
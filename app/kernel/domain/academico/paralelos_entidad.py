class Paralelo:
    def __init__(self, id: int, grupo_id: int, nombre: str, sede_id: int, cupo_maximo: int, activo: bool = True):
        self.id = id
        self.grupo_id = grupo_id
        self.nombre = nombre
        self.sede_id = sede_id
        self.cupo_maximo = cupo_maximo
        self.activo = activo

    def actualizar_cupo(self, nuevo_cupo: int):
        self.cupo_maximo = nuevo_cupo

    def desactivar(self):
        self.activo = False

    def activar(self):
        self.activo = True
class Horario:
    def __init__(self, id: int, nombre: str, hora_inicio: str, hora_fin: str, precio: float, sede_id: int, activo: bool = True):
        self.id = id
        self.nombre = nombre
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.precio = precio
        self.sede_id = sede_id
        self.activo = activo

    def actualizar_precio(self, nuevo_precio: float):
        self.precio = nuevo_precio

    def desactivar(self):
        self.activo = False

    def activar(self):
        self.activo = True
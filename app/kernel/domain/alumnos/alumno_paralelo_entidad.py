class AlumnoParalelo:
    def __init__(self, id: int, alumno_id: int, paralelo_id: int):
        self.id = id
        self.alumno_id = alumno_id
        self.paralelo_id = paralelo_id

    def asociar(self, nuevo_paralelo_id: int):
        """Asocia el alumno a un nuevo paralelo."""
        self.paralelo_id = nuevo_paralelo_id

    def desasociar(self):
        """Elimina la asociación del alumno con el paralelo."""
        self.paralelo_id = None
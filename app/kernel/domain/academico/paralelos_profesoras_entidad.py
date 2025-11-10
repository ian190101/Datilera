class ParaleloProfesora:
    def __init__(self, id: int, paralelo_id: int, profesora_id: int, cargo: str):
        self.id = id
        self.paralelo_id = paralelo_id
        self.profesora_id = profesora_id
        self.cargo = cargo  # "titular" o "auxiliar"

    def cambiar_cargo(self, nuevo_cargo: str):
        if nuevo_cargo not in ["titular", "auxiliar"]:
            raise ValueError("Cargo inválido")
        self.cargo = nuevo_cargo

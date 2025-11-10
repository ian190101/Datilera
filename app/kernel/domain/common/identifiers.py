import uuid
import random
import string

class Identifier:
    def __init__(self, value: str):
        if not value or not isinstance(value, str):
            raise ValueError("El identificador debe ser una cadena no vacía.")
        self.value = value

    @classmethod
    def generar_uuid(cls) -> "Identifier":
        """Genera un UUID único."""
        return cls(str(uuid.uuid4()))

    @classmethod
    def generar_codigo_alfanumerico(cls, longitud: int = 6) -> "Identifier":
        """Genera un código alfanumérico único de longitud dada."""
        caracteres = string.ascii_uppercase + string.digits
        codigo = ''.join(random.choices(caracteres, k=longitud))
        return cls(codigo)

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return isinstance(other, Identifier) and self.value == other.value

    def __hash__(self):
        return hash(self.value)
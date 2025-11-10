import enum

class EstadoCodigo(enum.Enum):
    pendiente = "pendiente"
    enviado = "enviado"
    consumido = "consumido"
    expirado = "expirado"
    revocado = "revocado"
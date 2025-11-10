class Pagination:
    def __init__(self, total: int, limit: int, offset: int):
        if total < 0 or limit <= 0 or offset < 0:
            raise ValueError("Valores inválidos para paginación.")
        self.total = total
        self.limit = limit
        self.offset = offset

    def siguiente_offset(self) -> int:
        return self.offset + self.limit

    def tiene_mas(self) -> bool:
        return self.offset + self.limit < self.total

    def pagina_actual(self) -> int:
        return (self.offset // self.limit) + 1

    def total_paginas(self) -> int:
        return (self.total + self.limit - 1) // self.limit

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "limit": self.limit,
            "offset": self.offset,
            "pagina_actual": self.pagina_actual(),
            "total_paginas": self.total_paginas(),
            "tiene_mas": self.tiene_mas()
        }
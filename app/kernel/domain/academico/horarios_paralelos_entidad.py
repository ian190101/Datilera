# app/kernel/domain/academico/horario_paralelo_entidad.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, date

class HorarioParalelo(BaseModel):
    """
    Entidad de dominio que vincula un horario con un paralelo.
    
    Define qué horario se usa en qué paralelo, y en qué periodo (desde/hasta).
    
    Atributos:
        id: Identificador único
        paralelo_id: ID del paralelo
        horario_id: ID del horario
        desde: Fecha de inicio del periodo
        hasta: Fecha de fin del periodo
        creado_en: Fecha de creación
    """
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    paralelo_id: int = Field(..., gt=0, description="ID del paralelo")
    horario_id: int = Field(..., gt=0, description="ID del horario")
    desde: date = Field(..., description="Fecha de inicio")
    hasta: date = Field(..., description="Fecha de fin")
    creado_en: datetime | None = Field(default=None, description="Fecha de creación")

    @field_validator('hasta')
    @classmethod
    def validar_periodo(cls, v: date, info) -> date:
        """Valida que 'hasta' sea posterior a 'desde'."""
        desde = info.data.get('desde')
        if desde and v < desde:
            raise ValueError("La fecha 'hasta' debe ser posterior a 'desde'")
        return v

    def esta_vigente(self, fecha: date | None = None) -> bool:
        """Verifica si el horario está vigente en la fecha indicada."""
        if fecha is None:
            fecha = date.today()
        return self.desde <= fecha <= self.hasta

    def __str__(self) -> str:
        return f"HorarioParalelo (Paralelo {self.paralelo_id}, Horario {self.horario_id}, {self.desde} - {self.hasta})"

    def __repr__(self) -> str:
        return (
            f"HorarioParalelo(id={self.id}, paralelo_id={self.paralelo_id}, "
            f"horario_id={self.horario_id}, desde={self.desde}, hasta={self.hasta})"
        )

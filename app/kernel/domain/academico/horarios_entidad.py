# app/kernel/domain/academico/horario_entidad.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, time

class Horario(BaseModel):
    """
    Entidad de dominio que representa un horario (franja horaria global).
    
    Los horarios definen rangos de tiempo reutilizables.
    Ejemplos: "Matutino 08:00-12:00", "Vespertino 14:00-18:00"
    
    Atributos:
        id: Identificador único
        nombre: Nombre descriptivo del horario
        hora_inicio: Hora de inicio (HH:MM)
        hora_fin: Hora de fin (HH:MM)
        creado_en: Fecha de creación
    """
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    nombre: str = Field(..., max_length=50, description="Nombre del horario")
    hora_inicio: str = Field(..., description="Hora de inicio (HH:MM)")
    hora_fin: str = Field(..., description="Hora de fin (HH:MM)")
    creado_en: datetime | None = Field(default=None, description="Fecha de creación")

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("El nombre del horario no puede estar vacío")
        return v.strip()

    @field_validator('hora_inicio', 'hora_fin')
    @classmethod
    def validar_formato_hora(cls, v: str) -> str:
        if not v:
            raise ValueError("La hora no puede estar vacía")
        
        try:
            partes = v.split(":")
            if len(partes) != 2:
                raise ValueError
            
            hora, minuto = int(partes[0]), int(partes[1])
            
            if not (0 <= hora <= 23):
                raise ValueError("La hora debe estar entre 00 y 23")
            if not (0 <= minuto <= 59):
                raise ValueError("Los minutos deben estar entre 00 y 59")
            
            return f"{hora:02d}:{minuto:02d}"
        except (ValueError, IndexError):
            raise ValueError("Formato de hora inválido. Use HH:MM (ej: 08:00)")

    def obtener_duracion_horas(self) -> float:
        """Calcula la duración del horario en horas."""
        inicio = time.fromisoformat(self.hora_inicio)
        fin = time.fromisoformat(self.hora_fin)
        
        inicio_min = inicio.hour * 60 + inicio.minute
        fin_min = fin.hour * 60 + fin.minute
        
        if fin_min < inicio_min:
            fin_min += 24 * 60
        
        duracion_min = fin_min - inicio_min
        return duracion_min / 60.0

    def actualizar_horario(self, hora_inicio: str, hora_fin: str) -> None:
        """Actualiza las horas del horario."""
        self.hora_inicio = self.validar_formato_hora(hora_inicio)
        self.hora_fin = self.validar_formato_hora(hora_fin)

    def __str__(self) -> str:
        return f"{self.nombre} ({self.hora_inicio} - {self.hora_fin})"

    def __repr__(self) -> str:
        return f"Horario(id={self.id}, nombre='{self.nombre}', horario='{self.hora_inicio}-{self.hora_fin}')"

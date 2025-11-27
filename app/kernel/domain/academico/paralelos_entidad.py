from pydantic import BaseModel, ConfigDict, Field

class Paralelo(BaseModel):
    """
    Entidad de dominio que representa un paralelo (turno dentro de un grupo).
    
    Los paralelos son las instancias de turnos dentro de un grupo específico.
    Ejemplo: Grupo A puede tener Paralelo Mañana y Paralelo Tarde.
    
    Atributos:
        id: Identificador único
        grupo_id: ID del grupo al que pertenece
        nombre: Nombre del paralelo (e.g., Mañana, Tarde)
        sede_id: ID de la sede asociada
        cupo_maximo: Cupo máximo de estudiantes
        activo: Estado activo del paralelo
    """
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    id: int = Field(..., description="Identificador único")
    grupo_id: int = Field(..., gt=0, description="ID del grupo")
    nombre: str = Field(..., min_length=1, description="Nombre del paralelo")
    sede_id: int = Field(..., gt=0, description="ID de la sede")
    cupo_maximo: int = Field(..., gt=0, description="Cupo máximo")
    activo: bool = Field(default=True, description="Estado activo")
    
    def actualizar_cupo(self, nuevo_cupo: int) -> None:
        if nuevo_cupo <= 0:
            raise ValueError("El cupo máximo debe ser mayor que 0")
        self.cupo_maximo = nuevo_cupo
    
    def desactivar(self) -> None:
        self.activo = False
    
    def activar(self) -> None:
        self.activo = True
    
    def __str__(self) -> str:
        return f"Paralelo {self.id} (Grupo {self.grupo_id}, Nombre: {self.nombre})"
    
    def __repr__(self) -> str:
        return (f"Paralelo(id={self.id}, grupo_id={self.grupo_id}, nombre='{self.nombre}', "
                f"sede_id={self.sede_id}, cupo_maximo={self.cupo_maximo}, activo={self.activo})")
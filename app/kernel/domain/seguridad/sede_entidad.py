# app/kernel/domain/seguridad/sede_entidad.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Sede(BaseModel):
    """
    Entidad de dominio que representa una sede/sucursal del sistema.
    
    Atributos:
        id: Identificador único de la sede
        codigo: Código corto y único de la sede (ej: CBBA, SCRZ)
        nombre: Nombre completo de la sede
        direccion: Dirección física (antes 'ubicacion')
        activo: Estado de la sede (soft delete)
        config_alerta_vencimiento_dias: Días para alertas de vencimiento (formato: "5,3,1")
    """
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    codigo: str = Field(..., max_length=10, description="Código único de la sede")
    nombre: str = Field(..., max_length=120, description="Nombre de la sede")
    direccion: str | None = Field(None, max_length=250, description="Dirección física de la sede")
    activo: bool = Field(default=True, description="Indica si la sede está activa")
    config_alerta_vencimiento_dias: str | None = Field(
        default="5,3,1",
        max_length=15,
        description="Días de alerta separados por coma (ej: 5,3,1)"
    )

    # Validadores
    @field_validator('codigo')
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        """Valida y normaliza el código de sede."""
        if not v or len(v.strip()) == 0:
            raise ValueError("El código de sede no puede estar vacío")
        return v.strip().upper()

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        """Valida que el nombre no esté vacío."""
        if not v or len(v.strip()) == 0:
            raise ValueError("El nombre de sede no puede estar vacío")
        return v.strip()

    @field_validator('config_alerta_vencimiento_dias')
    @classmethod
    def validar_config_alertas(cls, v: str | None) -> str | None:
        """Valida el formato de configuración de alertas."""
        if v is None:
            return "5,3,1"  # Valor por defecto
        
        v = v.strip()
        if not v:
            return "5,3,1"
        
        # Validar que sean números separados por comas
        try:
            dias = [int(d.strip()) for d in v.split(",") if d.strip()]
            if not dias:
                raise ValueError
            if any(d <= 0 for d in dias):
                raise ValueError("Los días deben ser positivos")
        except ValueError:
            raise ValueError(
                "Formato inválido. Use números positivos separados por comas (ej: 5,3,1)"
            )
        
        return v

    # Métodos de dominio
    def desactivar(self) -> None:
        """Desactiva la sede (soft delete)."""
        self.activo = False

    def activar(self) -> None:
        """Activa la sede."""
        self.activo = True

    def obtener_dias_alerta(self) -> list[int]:
        """
        Retorna la lista de días de alerta como enteros ordenados de mayor a menor.
        
        Returns:
            Lista de enteros representando los días de alerta.
        
        Ejemplo:
            >>> sede.config_alerta_vencimiento_dias = "5,3,1"
            >>> sede.obtener_dias_alerta()
            [5, 3, 1]
        """
        if not self.config_alerta_vencimiento_dias:
            return [5, 3, 1]
        
        dias = [int(d.strip()) for d in self.config_alerta_vencimiento_dias.split(",") if d.strip()]
        return sorted(dias, reverse=True)

    def actualizar_dias_alerta(self, dias: list[int]) -> None:
        """
        Actualiza la configuración de días de alerta.
        
        Args:
            dias: Lista de enteros positivos representando días de alerta.
        
        Raises:
            ValueError: Si algún día es negativo o cero.
        
        Ejemplo:
            >>> sede.actualizar_dias_alerta([10, 5, 2])
            >>> sede.config_alerta_vencimiento_dias
            "10,5,2"
        """
        if not dias:
            raise ValueError("Debe proporcionar al menos un día de alerta")
        
        if any(d <= 0 for d in dias):
            raise ValueError("Todos los días deben ser positivos")
        
        # Ordenar de mayor a menor y eliminar duplicados
        dias_unicos = sorted(set(dias), reverse=True)
        self.config_alerta_vencimiento_dias = ",".join(map(str, dias_unicos))

    def es_activa(self) -> bool:
        """Retorna True si la sede está activa."""
        return self.activo

    def __str__(self) -> str:
        """Representación en string de la sede."""
        return f"Sede({self.codigo} - {self.nombre})"

    def __repr__(self) -> str:
        """Representación técnica de la sede."""
        return (
            f"Sede(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}', "
            f"activo={self.activo})"
        )

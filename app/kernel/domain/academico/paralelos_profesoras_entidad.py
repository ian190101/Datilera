# app/kernel/domain/academico/paralelos_profesoras_entidad.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, date

class ParaleloProfesora(BaseModel):
    """
    Entidad de dominio que vincula un profesor con un paralelo en un periodo.
    
    Representa la asignación de un profesor a un paralelo para una gestión y
    periodo específico (desde/hasta). Permite cambios de profesores sin perder
    histórico.
    
    Atributos:
        id: Identificador único
        paralelo_id: ID del paralelo
        profesor_id: ID del profesor
        gestion: Año de gestión (ej: 2024)
        desde: Fecha de inicio de la asignación
        hasta: Fecha de fin de la asignación
        creado_en: Fecha de creación del registro
    
    Ejemplo:
        Paralelo 5 (Grupo A Mañana) + Profesor 1 (María García) 
        + Gestión 2024 + Desde 2024-01-01 + Hasta 2024-12-31
    """
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    paralelo_id: int = Field(..., gt=0, description="ID del paralelo")
    profesor_id: int = Field(..., gt=0, description="ID del profesor")
    gestion: int = Field(..., ge=2020, le=2100, description="Año de gestión")
    desde: date = Field(..., description="Fecha de inicio de la asignación")
    hasta: date = Field(..., description="Fecha de fin de la asignación")
    creado_en: datetime | None = Field(default=None, description="Fecha de creación")

    # Validadores
    @field_validator('hasta')
    @classmethod
    def validar_periodo(cls, v: date, info) -> date:
        """Valida que 'hasta' sea posterior a 'desde'."""
        desde = info.data.get('desde')
        if desde and v < desde:
            raise ValueError("La fecha 'hasta' debe ser posterior a 'desde'")
        return v

    @field_validator('gestion')
    @classmethod
    def validar_gestion(cls, v: int) -> int:
        """Valida que la gestión esté en rango válido."""
        if v < 2020 or v > 2100:
            raise ValueError("La gestión debe estar entre 2020 y 2100")
        return v

    # Métodos de dominio
    def esta_vigente(self, fecha: date | None = None) -> bool:
        """
        Verifica si la asignación está vigente en la fecha indicada.
        
        Args:
            fecha: Fecha a verificar. Si es None, usa la fecha actual.
        
        Returns:
            True si la fecha está dentro del periodo desde/hasta.
        
        Ejemplo:
            >>> asignacion.esta_vigente(date(2024, 06, 15))
            True
        """
        if fecha is None:
            fecha = date.today()
        return self.desde <= fecha <= self.hasta

    def es_pasado(self) -> bool:
        """Retorna True si la asignación ya terminó."""
        return date.today() > self.hasta

    def es_futuro(self) -> bool:
        """Retorna True si la asignación aún no ha comenzado."""
        return date.today() < self.desde

    def es_actual(self) -> bool:
        """Retorna True si la asignación está en curso."""
        return self.esta_vigente()

    def obtener_duracion_dias(self) -> int:
        """
        Calcula la duración de la asignación en días.
        
        Returns:
            Número de días entre desde y hasta (inclusive).
        
        Ejemplo:
            >>> asignacion.obtener_duracion_dias()
            365
        """
        delta = self.hasta - self.desde
        return delta.days + 1  # +1 para incluir el día final

    def actualizar_periodo(self, desde: date, hasta: date) -> None:
        """
        Actualiza el periodo de asignación.
        
        Args:
            desde: Nueva fecha de inicio
            hasta: Nueva fecha de fin
        
        Raises:
            ValueError: Si 'hasta' es anterior a 'desde'
        
        Ejemplo:
            >>> asignacion.actualizar_periodo(date(2024, 1, 1), date(2024, 6, 30))
        """
        if hasta < desde:
            raise ValueError("La fecha 'hasta' debe ser posterior a 'desde'")
        self.desde = desde
        self.hasta = hasta

    def extender_hasta(self, nueva_fecha: date) -> None:
        """
        Extiende la fecha de finalización de la asignación.
        
        Args:
            nueva_fecha: Nueva fecha de fin (debe ser posterior a la actual)
        
        Raises:
            ValueError: Si la nueva fecha es anterior a la actual.
        
        Ejemplo:
            >>> asignacion.extender_hasta(date(2024, 12, 31))
        """
        if nueva_fecha <= self.hasta:
            raise ValueError("La nueva fecha debe ser posterior a la fecha de fin actual")
        self.hasta = nueva_fecha

    def truncar_hasta(self, nueva_fecha: date) -> None:
        """
        Acorta la fecha de finalización de la asignación.
        
        Args:
            nueva_fecha: Nueva fecha de fin (debe ser posterior a 'desde')
        
        Raises:
            ValueError: Si la nueva fecha es anterior a 'desde' o posterior a 'hasta'.
        
        Ejemplo:
            >>> asignacion.truncar_hasta(date(2024, 06, 15))
        """
        if nueva_fecha < self.desde:
            raise ValueError("La nueva fecha debe ser posterior a la fecha de inicio")
        if nueva_fecha > self.hasta:
            raise ValueError("La nueva fecha debe ser anterior o igual a la fecha de fin actual")
        self.hasta = nueva_fecha

    def cambiar_profesor(self, nuevo_profesor_id: int) -> None:
        """
        Cambia el profesor de la asignación.
        
        Args:
            nuevo_profesor_id: ID del nuevo profesor
        
        Raises:
            ValueError: Si el ID es inválido.
        
        Ejemplo:
            >>> asignacion.cambiar_profesor(2)
        """
        if nuevo_profesor_id <= 0:
            raise ValueError("El ID del profesor debe ser positivo")
        self.profesor_id = nuevo_profesor_id

    def cambiar_paralelo(self, nuevo_paralelo_id: int) -> None:
        """
        Cambia el paralelo de la asignación.
        
        Args:
            nuevo_paralelo_id: ID del nuevo paralelo
        
        Raises:
            ValueError: Si el ID es inválido.
        """
        if nuevo_paralelo_id <= 0:
            raise ValueError("El ID del paralelo debe ser positivo")
        self.paralelo_id = nuevo_paralelo_id

    def cambiar_gestion(self, nueva_gestion: int) -> None:
        """
        Cambia la gestión de la asignación.
        
        Args:
            nueva_gestion: Año de gestión
        
        Raises:
            ValueError: Si la gestión está fuera de rango.
        """
        if nueva_gestion < 2020 or nueva_gestion > 2100:
            raise ValueError("La gestión debe estar entre 2020 y 2100")
        self.gestion = nueva_gestion

    def __str__(self) -> str:
        """Representación en string del paralelo-profesor."""
        estado = "vigente" if self.es_actual() else ("pasado" if self.es_pasado() else "futuro")
        return (
            f"ParaleloProfesor: Profesor {self.profesor_id} → "
            f"Paralelo {self.paralelo_id} ({self.desde} a {self.hasta}) [{estado}]"
        )

    def __repr__(self) -> str:
        """Representación técnica del paralelo-profesor."""
        return (
            f"ParaleloProfesor(id={self.id}, paralelo_id={self.paralelo_id}, "
            f"profesor_id={self.profesor_id}, gestion={self.gestion}, "
            f"desde={self.desde}, hasta={self.hasta})"
        )

# app/kernel/domain/cursos_extra/curso_extra_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from decimal import Decimal, InvalidOperation
from typing import Optional, Union


class EstadoCurso(str, Enum):
    BORRADOR = 'borrador'
    PUBLICADO = 'publicado'
    EN_CURSO = 'en_curso'
    FINALIZADO = 'finalizado'
    CANCELADO = 'cancelado'


class CupoLlenoError(Exception):
    """Se intentó sobrepasar el cupo del curso (sin lista de espera)."""


class CursoCerradoError(Exception):
    """Operación no válida cuando el curso está FINALIZADO o CANCELADO."""


@dataclass(frozen=True)
class PrecioDiferenciado:
    """VO para precios por tipo de participante (inscrito vs externo)."""
    inscritos: Decimal
    no_inscritos: Decimal

    def __post_init__(self):
        for nombre, val in (('inscritos', self.inscritos), ('no_inscritos', self.no_inscritos)):
            try:
                v = Decimal(val)
            except (InvalidOperation, TypeError):
                raise ValueError(f'Precio {nombre} inválido')
            if v < 0:
                raise ValueError(f'Precio {nombre} no puede ser negativo')


class CursoExtra:
    """Entidad CursoExtra (cursos/eventos por sede).

    Reglas del documento:
    - Diferencia de precio para niños INSCRITOS vs NO INSCRITOS al centro.
    - Cupo máximo configurable por curso y sede (sin lista de espera).
    - Profesor se referencia como empleado registrado sin acceso al sistema.
    - Balance por curso = suma pagos confirmados – suma costos.
    """

    def __init__(
        self,
        id: int,
        sede_id: int,
        nombre: str,
        descripcion: Optional[str],
        precio: PrecioDiferenciado,
        cupo_maximo: int,
        fecha_inicio: date,
        fecha_fin: Optional[date],
        profesor_empleado_id: Optional[int],
        estado: EstadoCurso = EstadoCurso.BORRADOR,
        creado_en: Optional[datetime] = None,
        actualizado_en: Optional[datetime] = None,
        inscritos_actuales: int = 0,
        ingresos_acumulados: Union[Decimal, int] = 0,
        costos_acumulados: Union[Decimal, int] = 0,
    ):
        nom = (nombre or '').strip()
        if not nom:
            raise ValueError('El nombre del curso extra es obligatorio.')
        if cupo_maximo <= 0:
            raise ValueError('El cupo máximo debe ser positivo.')
        if fecha_fin and fecha_fin < fecha_inicio:
            raise ValueError('La fecha fin no puede ser anterior a la fecha inicio.')

        self.id = id
        self.sede_id = sede_id
        self.nombre = nom
        self.descripcion = (descripcion or '').strip() or None
        self.precio = precio
        self.cupo_maximo = cupo_maximo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.profesor_empleado_id = profesor_empleado_id
        self.estado = estado
        self.creado_en = creado_en or datetime.utcnow()
        self.actualizado_en = actualizado_en or self.creado_en
        self.inscritos_actuales = max(0, int(inscritos_actuales))
        self.ingresos_acumulados = Decimal(ingresos_acumulados)
        self.costos_acumulados = Decimal(costos_acumulados)

    # --- Reglas/consultas ---
    def hay_cupo(self) -> bool:
        return self.inscritos_actuales < self.cupo_maximo

    def precio_para(self, es_inscrito_centro: bool) -> Decimal:
        return self.precio.inscritos if es_inscrito_centro else self.precio.no_inscritos

    # --- Comportamiento ---
    def registrar_inscripcion(self, es_inscrito_centro: bool) -> Decimal:
        """Incrementa el contador de inscritos si hay cupo y retorna el precio aplicable."""
        if self.estado in {EstadoCurso.FINALIZADO, EstadoCurso.CANCELADO}:
            raise CursoCerradoError('El curso no admite más inscripciones.')
        if not self.hay_cupo():
            raise CupoLlenoError('No hay cupo disponible para este curso (sin lista de espera).')
        self.inscritos_actuales += 1
        self.actualizado_en = datetime.utcnow()
        return self.precio_para(es_inscrito_centro)

    def revertir_inscripcion(self) -> None:
        if self.inscritos_actuales > 0:
            self.inscritos_actuales -= 1
            self.actualizado_en = datetime.utcnow()

    def acumular_pago(self, monto: Union[Decimal, int]) -> None:
        self.ingresos_acumulados += Decimal(monto)
        self.actualizado_en = datetime.utcnow()

    def acumular_costo(self, monto: Union[Decimal, int]) -> None:
        self.costos_acumulados += Decimal(monto)
        self.actualizado_en = datetime.utcnow()

    def balance(self) -> Decimal:
        return self.ingresos_acumulados - self.costos_acumulados
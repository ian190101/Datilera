# app/kernel/domain/academico/errors.py
"""
Excepciones de dominio del módulo académico.

Todas las excepciones heredan de BaseDominioError para mantener
consistencia en el manejo de errores de negocio.
"""
from __future__ import annotations
from app.kernel.domain.common.excepciones import BaseDominioError


# ========== Horarios ==========

class HorarioNoEncontrado(BaseDominioError):
    """Se lanza cuando un horario no existe."""
    status_code = 404
    code = "HORARIO_NOT_FOUND"


class HorarioNombreDuplicado(BaseDominioError):
    """Se lanza cuando se intenta crear un horario con nombre duplicado."""
    status_code = 409
    code = "HORARIO_NAME_DUPLICATED"


class HorarioEnUso(BaseDominioError):
    """Se lanza cuando se intenta eliminar un horario que está en uso."""
    status_code = 409
    code = "HORARIO_IN_USE"


# ========== Grupos ==========

class GrupoNoEncontrado(BaseDominioError):
    """Se lanza cuando un grupo no existe."""
    status_code = 404
    code = "GRUPO_NOT_FOUND"


class GrupoLetraDuplicada(BaseDominioError):
    """Se lanza cuando se intenta crear un grupo con letra duplicada en la misma sede/gestión."""
    status_code = 409
    code = "GRUPO_LETTER_DUPLICATED"


class GrupoCapacidadExcedida(BaseDominioError):
    """Se lanza cuando se intenta exceder la capacidad del grupo."""
    status_code = 409
    code = "GRUPO_CAPACITY_EXCEEDED"


class GrupoEnUso(BaseDominioError):
    """Se lanza cuando se intenta eliminar un grupo que tiene paralelos asociados."""
    status_code = 409
    code = "GRUPO_IN_USE"

class GrupoNombreDuplicado(BaseDominioError):
    """"Se lanza cuando el nombre del grupo es duplicado"""
    status_code = 409
    code = "GRUPO_LETRA_DUPLICATED"

# ========== Paralelos ==========

class ParaleloNoEncontrado(BaseDominioError):
    """Se lanza cuando un paralelo no existe."""
    status_code = 404
    code = "PARALELO_NOT_FOUND"


class ParaleloEnUso(BaseDominioError):
    """Se lanza cuando se intenta eliminar un paralelo que tiene asignaciones."""
    status_code = 409
    code = "PARALELO_IN_USE"

class ParaleloDuplicado(BaseDominioError):
    """"Se lanza cuando el paralelo ya existe"""
    status_code = 409
    code = "PARALELO_DUPLICATED"


# ========== Horario-Paralelo ==========

class HorarioParaleloNoEncontrado(BaseDominioError):
    """Se lanza cuando una asignación horario-paralelo no existe."""
    status_code = 404
    code = "HORARIO_PARALELO_NOT_FOUND"


class HorarioParaleloSolapado(BaseDominioError):
    """Se lanza cuando un horario se solapa con otro existente en el mismo paralelo."""
    status_code = 409
    code = "HORARIO_PARALELO_OVERLAPPED"


class HorarioParaleloPeriodoInvalido(BaseDominioError):
    """Se lanza cuando el periodo desde/hasta es inválido."""
    status_code = 422
    code = "HORARIO_PARALELO_INVALID_PERIOD"


# ========== Paralelo-Profesor ==========

class ParaleloProfesorNoEncontrado(BaseDominioError):
    """Se lanza cuando una asignación paralelo-profesor no existe."""
    status_code = 404
    code = "PARALELO_PROFESOR_NOT_FOUND"


class ParaleloProfesorSolapado(BaseDominioError):
    """Se lanza cuando un profesor ya está asignado en el mismo periodo."""
    status_code = 409
    code = "PARALELO_PROFESOR_OVERLAPPED"


class ProfesorNoDisponible(BaseDominioError):
    """Se lanza cuando un profesor no está disponible para la asignación."""
    status_code = 409
    code = "PROFESOR_NOT_AVAILABLE"


class ParaleloProfesorPeriodoInvalido(BaseDominioError):
    """Se lanza cuando el periodo desde/hasta es inválido."""
    status_code = 422
    code = "PARALELO_PROFESOR_INVALID_PERIOD"


class ProfesorNoEncontrado(BaseDominioError):
    """Se lanza cuando un profesor no existe."""
    status_code = 404
    code = "PROFESOR_NOT_FOUND"


# ========== Gestión ==========

class GestionInvalida(BaseDominioError):
    """Se lanza cuando la gestión es inválida."""
    status_code = 422
    code = "INVALID_GESTION"


class GestionNoEncontrada(BaseDominioError):
    """Se lanza cuando una gestión no existe."""
    status_code = 404
    code = "GESTION_NOT_FOUND"
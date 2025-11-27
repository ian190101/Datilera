# app/kernel/application/academico/__init__.py
"""Casos de uso del módulo académico."""

# Horarios
from .horarios.crear_horario import CrearHorario, CrearHorarioDTO
from .horarios.obtener_horario import ObtenerHorario
from .horarios.listar_horarios import ListarHorarios
from .horarios.actualizar_horario import ActualizarHorario, ActualizarHorarioDTO
from .horarios.eliminar_horario import EliminarHorario

# Grupos
from .grupos.crear_grupo import CrearGrupo, CrearGrupoDTO
from .grupos.listar_grupo_por_sede import ListarGruposPorSede
from .grupos.eliminar_grupo import EliminarGrupo

# Paralelos
from .paralelos.crear_paralelo import CrearParalelo, CrearParaleloDTO
from .paralelos.listar_paralelos_por_grupo import ListarParalelosPorGrupo

# Horarios-Paralelos
#from .horarios_paralelos.asignar_horario_paralelo import (
    #AsignarHorarioParalelo,
    #AsignarHorarioParaleloDTO
#)

# Paralelos-Profesores
from .paralelos_profesoras.asignar_paralelo_profesora import (
    AsignarProfesoraParalelo
)

__all__ = [
    # Horarios
    "CrearHorario",
    "CrearHorarioDTO",
    "ObtenerHorario",
    "ListarHorarios",
    "ActualizarHorario",
    "ActualizarHorarioDTO",
    "EliminarHorario",
    # Grupos
    "CrearGrupo",
    "CrearGrupoDTO",
    "ListarGruposPorSede",
    "EliminarGrupo",
    # Paralelos
    "CrearParalelo",
    "CrearParaleloDTO",
    "ListarParalelosPorGrupo",
    # Horarios-Paralelos
    "AsignarHorarioParalelo",
    "AsignarHorarioParaleloDTO",
    # Paralelos-Profesores
    "AsignarProfesoraParalelo",
    "AsignarProfesorParaleloDTO",
]
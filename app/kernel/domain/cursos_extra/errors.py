# app/kernel/domain/cursosextra/errors.py

"""
Excepciones de dominio para Cursos Extra.
"""


class CursosExtraError(Exception):
    """Base de errores de Cursos Extra."""
    pass


# ==========================================
# Cursos Extra
# ==========================================

class CursoExtraNoEncontrado(CursosExtraError):
    def __init__(self, curso_id: int):
        super().__init__(f"Curso extra {curso_id} no encontrado")


class CursoExtraInactivo(CursosExtraError):
    def __init__(self, curso_id: int):
        super().__init__(f"Curso extra {curso_id} está inactivo")


class CuposAgotados(CursosExtraError):
    def __init__(self, curso_id: int, nombre_curso: str):
        super().__init__(
            f"El curso '{nombre_curso}' (ID: {curso_id}) no tiene cupos disponibles"
        )


class NombreCursoInvalido(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Nombre de curso inválido: {razon}")


class InstructorInvalido(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Instructor inválido: {razon}")


class FechasInvalidas(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Fechas inválidas: {razon}")


class PorcentajeInvalido(CursosExtraError):
    def __init__(self, porcentaje: float):
        super().__init__(
            f"Porcentaje inválido: {porcentaje}. Debe estar entre 0 y 100."
        )


class CupoMaximoInvalido(CursosExtraError):
    def __init__(self, cupo: int):
        super().__init__(f"Cupo máximo inválido: {cupo}. Debe ser mayor a 0.")


class PrecioInvalido(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Precio inválido: {razon}")


# ==========================================
# Inscripciones
# ==========================================

class InscripcionNoEncontrada(CursosExtraError):
    def __init__(self, inscripcion_id: int):
        super().__init__(f"Inscripción {inscripcion_id} no encontrada")


class InscripcionDuplicada(CursosExtraError):
    def __init__(self, alumno_tipo: str, alumno_id: int, curso_id: int):
        super().__init__(
            f"El alumno {alumno_tipo} (ID: {alumno_id}) ya está inscrito "
            f"activamente en el curso {curso_id}"
        )


class InscripcionYaCompletada(CursosExtraError):
    def __init__(self, inscripcion_id: int):
        super().__init__(f"La inscripción {inscripcion_id} ya está completada")


class InscripcionYaRetirada(CursosExtraError):
    def __init__(self, inscripcion_id: int):
        super().__init__(f"La inscripción {inscripcion_id} ya está retirada")


class TipoAlumnoInvalido(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Tipo de alumno inválido: {razon}")


class DatosAlumnoIncompletos(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Datos del alumno incompletos: {razon}")


# ==========================================
# Alumnos Externos
# ==========================================

class AlumnoExternoNoEncontrado(CursosExtraError):
    def __init__(self, alumno_id: int):
        super().__init__(f"Alumno externo {alumno_id} no encontrado")


class AlumnoExternoDuplicado(CursosExtraError):
    def __init__(self, nombre: str, tutor_celular: str, sede_id: int):
        super().__init__(
            f"Ya existe un alumno externo '{nombre}' con tutor celular "
            f"'{tutor_celular}' en la sede {sede_id}"
        )


class NombreAlumnoInvalido(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Nombre del alumno inválido: {razon}")


class DatosTutorInvalidos(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Datos del tutor inválidos: {razon}")


# ==========================================
# Balance
# ==========================================

class BalanceNoEncontrado(CursosExtraError):
    def __init__(self, balance_id: int):
        super().__init__(f"Balance {balance_id} no encontrado")


class BalanceYaPagado(CursosExtraError):
    def __init__(self, balance_id: int):
        super().__init__(
            f"El balance {balance_id} ya está completamente pagado"
        )


class MontoInvalido(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Monto inválido: {razon}")


class PagoExcedeSaldo(CursosExtraError):
    def __init__(self, monto_pago: float, saldo_actual: float):
        super().__init__(
            f"El pago de {monto_pago} Bs excede el saldo pendiente de {saldo_actual} Bs"
        )


class MontosPagoIncoherentes(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Montos de pago incoherentes: {razon}")


# ==========================================
# Pagos
# ==========================================

class PagoNoEncontrado(CursosExtraError):
    def __init__(self, pago_id: int):
        super().__init__(f"Pago {pago_id} no encontrado")


class PagoInmutable(CursosExtraError):
    def __init__(self, pago_id: int):
        super().__init__(
            f"Los pagos son inmutables: no se puede modificar el pago {pago_id}"
        )


class MetodoPagoInvalido(CursosExtraError):
    def __init__(self, metodo: str):
        super().__init__(f"Método de pago inválido: {metodo}")


class ComprobanteRequerido(CursosExtraError):
    def __init__(self, metodo_pago: str):
        super().__init__(
            f"Se requiere comprobante para pagos con método '{metodo_pago}'"
        )


# ==========================================
# Costos
# ==========================================

class CostoNoEncontrado(CursosExtraError):
    def __init__(self, costo_id: int):
        super().__init__(f"Costo {costo_id} no encontrado")


class CategoriaNoEncontrada(CursosExtraError):
    def __init__(self, categoria_id: int):
        super().__init__(f"Categoría de costo {categoria_id} no encontrada")


class CategoriaDuplicada(CursosExtraError):
    def __init__(self, nombre: str, curso_id: int):
        super().__init__(
            f"Ya existe una categoría '{nombre}' en el curso {curso_id}"
        )


class CategoriaInactiva(CursosExtraError):
    def __init__(self, categoria_id: int):
        super().__init__(f"La categoría {categoria_id} está inactiva")


class CategoriaConCostos(CursosExtraError):
    def __init__(self, categoria_id: int, cantidad_costos: int):
        super().__init__(
            f"No se puede eliminar la categoría {categoria_id} porque tiene "
            f"{cantidad_costos} costos asociados"
        )


class DescripcionCostoInvalida(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Descripción del costo inválida: {razon}")


# ==========================================
# Ingresos/Balance Consolidado
# ==========================================

class IngresoNoEncontrado(CursosExtraError):
    def __init__(self, curso_id: int):
        super().__init__(
            f"No se encontró registro de ingresos para el curso {curso_id}"
        )


class CalculoGananciasError(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Error al calcular ganancias: {razon}")


class DatosFinancierosInconsistentes(CursosExtraError):
    def __init__(self, razon: str):
        super().__init__(f"Datos financieros inconsistentes: {razon}")


# ==========================================
# Validaciones de Sede
# ==========================================

class SedeNoCoincide(CursosExtraError):
    def __init__(self, recurso: str, sede_esperada: int, sede_recurso: int):
        super().__init__(
            f"La sede del {recurso} ({sede_recurso}) no coincide con la esperada ({sede_esperada})"
        )


class SedeInvalida(CursosExtraError):
    def __init__(self, sede_id: int):
        super().__init__(f"Sede {sede_id} inválida o no existe")

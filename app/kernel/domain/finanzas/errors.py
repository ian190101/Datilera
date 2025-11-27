# app/kernel/domain/finanzas/errors.py
"""
Excepciones de dominio para el módulo de Finanzas.
"""


class FinanzasError(Exception):
    """Excepción base para errores del dominio de finanzas"""
    pass


# ==========================================
# Categorías de Pago
# ==========================================
class CategoriaPagoNoEncontrada(FinanzasError):
    """Categoría de pago no encontrada"""
    def __init__(self, categoria_id: int):
        super().__init__(f"Categoría de pago con ID {categoria_id} no encontrada")


class CategoriaPagoDuplicada(FinanzasError):
    """Categoría de pago con nombre duplicado en la sede"""
    def __init__(self, nombre: str, sede_id: int):
        super().__init__(f"Ya existe una categoría de pago '{nombre}' en la sede {sede_id}")


class CategoriaPagoEnUso(FinanzasError):
    """No se puede eliminar categoría de pago en uso"""
    def __init__(self, categoria_id: int):
        super().__init__(f"La categoría de pago {categoria_id} está en uso y no puede eliminarse")


# ==========================================
# Categorías de Egreso
# ==========================================
class CategoriaEgresoNoEncontrada(FinanzasError):
    """Categoría de egreso no encontrada"""
    def __init__(self, categoria_id: int):
        super().__init__(f"Categoría de egreso con ID {categoria_id} no encontrada")


class CategoriaEgresoDuplicada(FinanzasError):
    """Categoría de egreso con nombre duplicado en la sede"""
    def __init__(self, nombre: str, sede_id: int):
        super().__init__(f"Ya existe una categoría de egreso '{nombre}' en la sede {sede_id}")


class CategoriaEgresoEnUso(FinanzasError):
    """No se puede eliminar categoría de egreso en uso"""
    def __init__(self, categoria_id: int):
        super().__init__(f"La categoría de egreso {categoria_id} está en uso y no puede eliminarse")


# ==========================================
# Libro de Caja
# ==========================================
class LibroCajaError(FinanzasError):
    """Error genérico en operaciones de libro de caja"""
    pass


class MovimientoInvalido(LibroCajaError):
    """Movimiento de libro de caja inválido"""
    pass


class CategoriaTipoIncorrecto(LibroCajaError):
    """Categoría no corresponde al tipo de movimiento"""
    def __init__(self, tipo_movimiento: str, categoria_tipo: str):
        super().__init__(
            f"Tipo de movimiento '{tipo_movimiento}' requiere una categoría de "
            f"{'pago' if tipo_movimiento == 'ingreso' else 'egreso'}, "
            f"pero se proporcionó una categoría de {categoria_tipo}"
        )


class SaldoNegativo(LibroCajaError):
    """Operación resultaría en saldo negativo"""
    def __init__(self, saldo_actual: float, monto_egreso: float):
        super().__init__(
            f"El egreso de {monto_egreso} excede el saldo disponible {saldo_actual}"
        )


# ==========================================
# Pagos
# ==========================================
class PagoNoEncontrado(FinanzasError):
    """Pago no encontrado"""
    def __init__(self, pago_id: int):
        super().__init__(f"Pago con ID {pago_id} no encontrado")


class ComprobanteInvalido(FinanzasError):
    """Comprobante inválido o duplicado"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje)


class MontoPagoIncorrecto(FinanzasError):
    """Monto de pago no coincide con el esperado"""
    def __init__(self, monto_recibido: float, monto_esperado: float):
        super().__init__(
            f"El monto recibido {monto_recibido} no coincide con el esperado {monto_esperado}"
        )


# ==========================================
# Arqueos
# ==========================================
class ArqueoNoEncontrado(FinanzasError):
    """Arqueo no encontrado"""
    def __init__(self, arqueo_id: int):
        super().__init__(f"Arqueo con ID {arqueo_id} no encontrado")


class ArqueoPeriodoInvalido(FinanzasError):
    """Período de arqueo inválido"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje)


class ArqueoYaExiste(FinanzasError):
    """Ya existe un arqueo para el período"""
    def __init__(self, sede_id: int, periodo: str):
        super().__init__(f"Ya existe un arqueo para la sede {sede_id} en el período {periodo}")


# ==========================================
# Conciliaciones
# ==========================================
class ConciliacionError(FinanzasError):
    """Error en conciliación bancaria"""
    pass


class ConciliacionNoEncontrada(FinanzasError):
    """Conciliación no encontrada"""
    def __init__(self, conciliacion_id: int):
        super().__init__(f"Conciliación con ID {conciliacion_id} no encontrada")


# ==========================================
# Permisos y Acceso
# ==========================================
class AccesoFinanzasDenegado(FinanzasError):
    """Usuario no tiene permisos para operación financiera"""
    def __init__(self, usuario_id: int, operacion: str):
        super().__init__(f"Usuario {usuario_id} no autorizado para {operacion}")


class AccesoSedeFinanzasDenegado(FinanzasError):
    """Usuario no tiene acceso a finanzas de esta sede"""
    def __init__(self, usuario_id: int, sede_id: int):
        super().__init__(f"Usuario {usuario_id} no tiene acceso a finanzas de sede {sede_id}")

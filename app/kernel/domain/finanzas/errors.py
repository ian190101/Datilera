# app/kernel/domain/finanzas/errors.py
"""
Excepciones personalizadas del dominio de finanzas.
Organizadas por entidad para facilitar mantenimiento.
"""


# ==================== EXCEPCIONES BASE ====================

class FinanzasError(Exception):
    """Excepción base para errores de finanzas."""
    pass


# ==================== PAGOS ====================

class PagoError(FinanzasError):
    """Excepción base para errores relacionados con pagos."""
    pass


class PagoNoEncontradoError(PagoError):
    """El pago solicitado no existe."""
    pass


class PagoYaAnuladoError(PagoError):
    """El pago ya está anulado."""
    pass


class MontoPagoInvalidoError(PagoError):
    """El monto del pago es inválido (debe ser mayor a cero)."""
    pass


class MetodoPagoInvalidoError(PagoError):
    """El método de pago no es válido (solo efectivo o qr)."""
    pass


class ComprobantePagoYaExisteError(PagoError):
    """El comprobante de pago ya existe en el sistema."""
    pass


class AlumnoSinDeudaError(PagoError):
    """El alumno no tiene deuda registrada."""
    pass


class PagoExcedeMoraError(PagoError):
    """El monto del pago excede la mora del alumno."""
    pass


class PagoSinAlumnoError(PagoError):
    """El pago no tiene un alumno asignado."""
    pass


class PagoSinCategoriaError(PagoError):
    """El pago no tiene una categoría asignada."""
    pass


# ==================== EGRESOS ====================

class EgresoError(FinanzasError):
    """Excepción base para errores relacionados con egresos."""
    pass


class EgresoNoEncontradoError(EgresoError):
    """El egreso solicitado no existe."""
    pass


class EgresoYaAnuladoError(EgresoError):
    """El egreso ya está anulado."""
    pass


class MontoEgresoInvalidoError(EgresoError):
    """El monto del egreso es inválido (debe ser mayor a cero)."""
    pass


class DescripcionInvalidaError(EgresoError):
    """La descripción del egreso es inválida (muy corta o vacía)."""
    pass


class ComprobanteEgresoYaExisteError(EgresoError):
    """El comprobante del egreso ya existe en el sistema."""
    pass


class MotivoAnulacionInvalidoError(EgresoError):
    """El motivo de anulación es inválido (muy corto o vacío)."""
    pass


class EgresoSinSedeError(EgresoError):
    """El egreso no tiene una sede asignada."""
    pass


class EgresoSinCategoriaError(EgresoError):
    """El egreso no tiene una categoría asignada."""
    pass


# ==================== CATEGORÍAS DE PAGO ====================

class CategoriaPagoError(FinanzasError):
    """Excepción base para errores relacionados con categorías de pago."""
    pass


class CategoriaPagoNoEncontradaError(CategoriaPagoError):
    """La categoría de pago solicitada no existe."""
    pass


class CategoriaPagoYaExisteError(CategoriaPagoError):
    """Ya existe una categoría de pago con ese nombre en la sede."""
    pass


class CategoriaPagoInactivaError(CategoriaPagoError):
    """La categoría de pago está inactiva."""
    pass


class CategoriaPagoEnUsoError(CategoriaPagoError):
    """La categoría de pago no puede eliminarse porque está en uso."""
    pass


class NombreCategoriaPagoInvalidoError(CategoriaPagoError):
    """El nombre de la categoría de pago es inválido."""
    pass


# ==================== CATEGORÍAS DE EGRESO ====================

class CategoriaEgresoError(FinanzasError):
    """Excepción base para errores relacionados con categorías de egreso."""
    pass


class CategoriaEgresoNoEncontradaError(CategoriaEgresoError):
    """La categoría de egreso solicitada no existe."""
    pass


class CategoriaEgresoYaExisteError(CategoriaEgresoError):
    """Ya existe una categoría de egreso con ese nombre en la sede."""
    pass


class CategoriaEgresoInactivaError(CategoriaEgresoError):
    """La categoría de egreso está inactiva."""
    pass


class CategoriaEgresoEnUsoError(CategoriaEgresoError):
    """La categoría de egreso no puede eliminarse porque está en uso."""
    pass


class NombreCategoriaEgresoInvalidoError(CategoriaEgresoError):
    """El nombre de la categoría de egreso es inválido."""
    pass


# ==================== DESCUENTOS ====================

class DescuentoError(FinanzasError):
    """Excepción base para errores relacionados con descuentos."""
    pass


class DescuentoNoEncontradoError(DescuentoError):
    """El descuento solicitado no existe."""
    pass


class DescuentoYaAplicadoError(DescuentoError):
    """El descuento ya fue aplicado al alumno."""
    pass


class DescuentoExcedeLimiteError(DescuentoError):
    """El monto del descuento excede el límite permitido."""
    pass


class TipoDescuentoInvalidoError(DescuentoError):
    """El tipo de descuento no es válido."""
    pass


class DescuentoVencidoError(DescuentoError):
    """El descuento ha vencido."""
    pass


class AlumnoSinDescuentoDisponibleError(DescuentoError):
    """El alumno no tiene descuentos disponibles."""
    pass


# ==================== PLANES DE PAGO ====================

class PlanPagoError(FinanzasError):
    """Excepción base para errores relacionados con planes de pago."""
    pass


class PlanPagoNoEncontradoError(PlanPagoError):
    """El plan de pago solicitado no existe."""
    pass


class PlanPagoYaExisteError(PlanPagoError):
    """El alumno ya tiene un plan de pago activo."""
    pass


class MontoTotalInvalidoError(PlanPagoError):
    """El monto total del plan de pago es inválido."""
    pass


class NumeroCuotasInvalidoError(PlanPagoError):
    """El número de cuotas es inválido."""
    pass


class CuotaNoEncontradaError(PlanPagoError):
    """La cuota solicitada no existe."""
    pass


class CuotaYaPagadaError(PlanPagoError):
    """La cuota ya está pagada."""
    pass


class PlanPagoCanceladoError(PlanPagoError):
    """El plan de pago está cancelado."""
    pass


class FechaInicioInvalidaError(PlanPagoError):
    """La fecha de inicio del plan de pago es inválida."""
    pass


# ==================== ESTADO DE CUENTA ====================

class EstadoCuentaError(FinanzasError):
    """Excepción base para errores relacionados con estado de cuenta."""
    pass


class EstadoCuentaNoEncontradoError(EstadoCuentaError):
    """El estado de cuenta del alumno no existe."""
    pass


class SaldoInsuficienteError(EstadoCuentaError):
    """El saldo del alumno es insuficiente."""
    pass


class OperacionEstadoCuentaError(EstadoCuentaError):
    """Error al realizar operación en el estado de cuenta."""
    pass


class AlumnoNoTieneEstadoCuentaError(EstadoCuentaError):
    """El alumno no tiene estado de cuenta registrado."""
    pass


# ==================== LIBRO DE CAJA ====================

class LibroCajaError(FinanzasError):
    """Excepción base para errores relacionados con libro de caja."""
    pass


class MovimientoNoEncontradoError(LibroCajaError):
    """El movimiento de caja no existe."""
    pass


class SaldoCajaInvalidoError(LibroCajaError):
    """El saldo de caja es inválido."""
    pass


class FechaCierreInvalidaError(LibroCajaError):
    """La fecha de cierre es inválida."""
    pass


class CajaYaCerradaError(LibroCajaError):
    """La caja ya está cerrada para esa fecha."""
    pass


class ObservacionesRequeridaError(LibroCajaError):
    """Las observaciones son requeridas para este tipo de movimiento."""
    pass


# ==================== ARQUEOS ====================

class ArqueoError(FinanzasError):
    """Excepción base para errores relacionados con arqueos."""
    pass


class ArqueoNoEncontradoError(ArqueoError):
    """El arqueo solicitado no existe."""
    pass


class ArqueoYaCerradoError(ArqueoError):
    """El arqueo ya está cerrado."""
    pass


class DiferenciaArqueoExcedeLimiteError(ArqueoError):
    """La diferencia del arqueo excede el límite permitido."""
    pass


class ArqueoFechaInvalidaError(ArqueoError):
    """La fecha del arqueo es inválida."""
    pass


# ==================== COMPROBANTES ====================

class ComprobanteError(FinanzasError):
    """Excepción base para errores relacionados con comprobantes."""
    pass


class ComprobanteNoEncontradoError(ComprobanteError):
    """El comprobante solicitado no existe."""
    pass


class ComprobanteYaGeneradoError(ComprobanteError):
    """El comprobante ya fue generado."""
    pass


class TipoComprobanteInvalidoError(ComprobanteError):
    """El tipo de comprobante no es válido."""
    pass


class NumeroComprobanteInvalidoError(ComprobanteError):
    """El número de comprobante es inválido."""
    pass


# ==================== CONCILIACIONES ====================

class ConciliacionError(FinanzasError):
    """Excepción base para errores relacionadas con conciliaciones."""
    pass


class ConciliacionNoEncontradaError(ConciliacionError):
    """La conciliación solicitada no existe."""
    pass


class ConciliacionYaProcesadaError(ConciliacionError):
    """La conciliación ya fue procesada."""
    pass


class MontoConciliacionInvalidoError(ConciliacionError):
    """El monto de la conciliación es inválido."""
    pass


class ConciliacionYaReversadaError(ConciliacionError):
    """La conciliación ya está reversada."""
    pass


# ==================== PRORRATEO ====================

class ProrrateoError(FinanzasError):
    """Excepción base para errores relacionados con prorrateo."""
    pass


class FechaInicioMayorFinError(ProrrateoError):
    """La fecha de inicio no puede ser mayor que la fecha de fin."""
    pass


class PeriodoProrrateoInvalidoError(ProrrateoError):
    """El período de prorrateo es inválido."""
    pass


class TipoProrrateoInvalidoError(ProrrateoError):
    """El tipo de prorrateo no es válido."""
    pass

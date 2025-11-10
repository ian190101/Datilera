from decimal import Decimal, ROUND_HALF_UP

class Money:
    def __init__(self, amount: Decimal, currency: str = "BOB"):
        if amount < 0:
            raise ValueError("El monto no puede ser negativo.")
        self.amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.currency = currency

    def aplicar_descuento(self, porcentaje: float) -> "Money":
        """Aplica un descuento porcentual al monto."""
        descuento = (self.amount * Decimal(porcentaje / 100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Money(self.amount - descuento, self.currency)

    def prorratear(self, dias_utilizados: int, total_dias: int = 20) -> "Money":
        """Calcula el monto prorrateado según días utilizados."""
        if dias_utilizados <= 0 or dias_utilizados > total_dias:
            raise ValueError("Cantidad de días inválida para prorrateo.")
        monto_diario = (self.amount / Decimal(total_dias)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        monto_total = monto_diario * Decimal(dias_utilizados)
        return Money(monto_total, self.currency)

    def redondear_bolivianos(self) -> "Money":
        """Redondea el monto según reglas bolivianas (0.50 o entero)."""
        entero = int(self.amount)
        centavos = (self.amount - Decimal(entero)).quantize(Decimal("0.01"))
        if centavos <= Decimal("0.49"):
            redondeado = Decimal(entero) + Decimal("0.50") if centavos > 0 else Decimal(entero)
        else:
            redondeado = Decimal(entero + 1)
        return Money(redondeado, self.currency)

    def __str__(self):
        return f"{self.amount} {self.currency}"

    def __add__(self, other):
        if not isinstance(other, Money) or self.currency != other.currency:
            raise ValueError("No se puede sumar montos con diferentes monedas.")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        if not isinstance(other, Money) or self.currency != other.currency:
            raise ValueError("No se puede restar montos con diferentes monedas.")
        return Money(self.amount - other.amount, self.currency)
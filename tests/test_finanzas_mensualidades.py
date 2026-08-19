from datetime import date
from decimal import Decimal
from pathlib import Path

from app.infrastructure.db.models import Base
from app.kernel.domain.finanzas.calculos_mensualidad import (
    calcular_prorrateo_mensualidad,
    fecha_vencimiento_primera_cuota,
    redondear_a_medio_boliviano,
)
from app.main import app


def test_redondeo_no_agrega_cincuenta_centavos_a_un_entero() -> None:
    assert redondear_a_medio_boliviano(Decimal("475.00")) == Decimal("475.00")


def test_redondeo_solo_utiliza_medios_o_enteros() -> None:
    assert redondear_a_medio_boliviano(Decimal("475.10")) == Decimal("475.50")
    assert redondear_a_medio_boliviano(Decimal("475.50")) == Decimal("475.50")
    assert redondear_a_medio_boliviano(Decimal("475.51")) == Decimal("476.00")


def test_prorrateo_real_de_enero_no_suma_cincuenta_centavos() -> None:
    resultado = calcular_prorrateo_mensualidad(date(2026, 1, 6), Decimal("500.00"))
    assert resultado.dias_habiles_cobrados == 19
    assert resultado.monto == Decimal("475.00")
    assert resultado.diferido is False


def test_ingreso_al_cierre_difiere_el_cobro_sin_cuota_cero() -> None:
    resultado = calcular_prorrateo_mensualidad(date(2026, 1, 29), Decimal("500.00"))
    assert resultado.diferido is True
    assert resultado.fecha_inicio_cobro == date(2026, 2, 1)
    assert resultado.monto == Decimal("500.00")


def test_diferimiento_de_diciembre_cambia_de_anio() -> None:
    resultado = calcular_prorrateo_mensualidad(date(2026, 12, 29), Decimal("500.00"))
    assert resultado.fecha_inicio_cobro == date(2027, 1, 1)


def test_primera_cuota_nunca_vence_antes_del_ingreso() -> None:
    assert fecha_vencimiento_primera_cuota(date(2026, 2, 5)) == date(2026, 2, 10)
    assert fecha_vencimiento_primera_cuota(date(2026, 2, 20)) == date(2026, 2, 20)


def test_rutas_visibles_usan_controladores_financieros_consistentes() -> None:
    endpoints = {
        (method, route.path): route.endpoint.__name__
        for route in app.routes
        for method in (getattr(route, "methods", None) or set())
    }
    assert endpoints[("POST", "/api/v1/finanzas/planes-pago/generar")] == ("generar_plan_pago_consistente")
    assert endpoints[("POST", "/api/v1/ingresos/cobrar")] == "registrar_cobro_consistente"
    assert endpoints[("GET", "/api/v1/finanzas/planes-pago/gestion/alumno/{alumno_id}")] == (
        "obtener_detalle_plan_alumno"
    )


def test_formulario_envia_los_nombres_esperados_por_el_backend() -> None:
    html = Path("app/interfaces/web/templates/finanzas/index.html").read_text(encoding="utf-8")
    for nombre in ("pagometodo", "pagofecha", "pagoreferencia", "pagocomprobante"):
        assert f'name="{nombre}"' in html


def test_metadata_incluye_historial_de_asignaciones_pago_cuota() -> None:
    tabla = Base.metadata.tables["pagos_cuotas"]
    assert {"pago_id", "cuota_id", "monto_aplicado"}.issubset(tabla.columns.keys())

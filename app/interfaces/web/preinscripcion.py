from __future__ import annotations

import re


_PATRON_TUTOR_LEGACY = re.compile(
    r"Tutor:\s*(?P<nombre>.*?)\s*\((?P<parentesco>[^)]+)\)\s*-\s*Tel:\s*(?P<telefono>[^-]+)",
    re.IGNORECASE,
)


def extraer_datos_tutor_preinscripcion(
    *,
    entregado_a: str | None,
    whatsapp_numero: str | None,
    observaciones: str | None,
) -> dict[str, str]:
    """Recupera los datos del tutor y conserva compatibilidad con códigos antiguos."""
    coincidencia = _PATRON_TUTOR_LEGACY.search(observaciones or "")

    nombre_legacy = coincidencia.group("nombre").strip() if coincidencia else ""
    parentesco = coincidencia.group("parentesco").strip().upper() if coincidencia else ""
    telefono_legacy = coincidencia.group("telefono").strip() if coincidencia else ""

    return {
        "nombre": (entregado_a or nombre_legacy).strip(),
        "parentesco": parentesco,
        "telefono": (whatsapp_numero or telefono_legacy).strip(),
    }

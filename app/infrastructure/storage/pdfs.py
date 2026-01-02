# app/infrastructure/storage/pdfs.py
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.infrastructure.storage.local_fs import LocalFileStorage


class PDFReportStorage:
    """
    Servicio para generar PDFs de reportes (por ahora, arqueo mensual).
    Usa ReportLab y LocalFileStorage.
    """

    def __init__(self, storage: LocalFileStorage | None = None) -> None:
        self.storage = storage or LocalFileStorage()
        self.styles = getSampleStyleSheet()

    # ---------- Arqueo mensual ----------

    def generar_arqueo_mensual_pdf(
        self,
        sede_id: int,
        anio: int,
        mes: int,
        datos: list[dict[str, Any]],
    ) -> str:
        """
        Genera un PDF con un resumen tabular del arqueo mensual.
        Retorna ruta relativa del archivo generado.
        """
        relative_path = f"reportes/arqueos/sede_{sede_id}/{anio}_{mes:02d}.pdf"
        self.storage.ensure_dir_for(relative_path)
        full_path: Path = self.storage.get_full_path(relative_path)

        doc = SimpleDocTemplate(
            str(full_path),
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=30,
            bottomMargin=30,
        )

        elementos: list[Any] = []

        # Título
        titulo = f"Arqueo mensual - Sede {sede_id} - {anio}-{mes:02d}"
        elementos.append(Paragraph(titulo, self.styles["Title"]))
        elementos.append(Spacer(1, 12))

        if not datos:
            elementos.append(Paragraph("Sin datos para el período.", self.styles["Normal"]))
        else:
            headers = list(datos[0].keys())
            tabla_data = [headers]
            for fila in datos:
                tabla_data.append([fila.get(col, "") for col in headers])

            tabla = Table(tabla_data, repeatRows=1)
            tabla.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ]
                )
            )

            elementos.append(tabla)

        doc.build(elementos)

        return full_path.relative_to(self.storage.base_path).as_posix()

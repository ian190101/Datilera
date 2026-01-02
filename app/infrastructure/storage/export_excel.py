# app/infrastructure/storage/export_excel.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from openpyxl import Workbook

from app.infrastructure.storage.local_fs import LocalFileStorage


class ExcelExportStorage:
    """
    Servicio para generar archivos Excel (XLSX) de exportaciones y reportes.
    Usa LocalFileStorage para persistir el archivo y retorna rutas relativas.
    """

    def __init__(self, storage: LocalFileStorage | None = None) -> None:
        self.storage = storage or LocalFileStorage()

    # ---------- Arqueo mensual ----------

    def generar_arqueo_mensual_excel(
        self,
        sede_id: int,
        anio: int,
        mes: int,
        datos: list[dict[str, Any]],
    ) -> str:
        """
        Genera un XLSX con los datos de arqueo mensual.
        'datos' es una lista de dicts homogéneos.
        Retorna ruta relativa donde se guardó el archivo.
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Arqueo"

        if not datos:
            # Fila de encabezado mínima
            ws.append(["Mensaje"])
            ws.append(["Sin datos para el período"])
        else:
            # Encabezados desde las claves del primer registro
            headers = list(datos[0].keys())
            ws.append(headers)
            for fila in datos:
                ws.append([fila.get(col) for col in headers])

        relative_path = f"reportes/arqueos/sede_{sede_id}/{anio}_{mes:02d}.xlsx"
        self.storage.ensure_dir_for(relative_path)
        full_path: Path = self.storage.get_full_path(relative_path)
        wb.save(full_path)

        return full_path.relative_to(self.storage.base_path).as_posix()

    # ---------- Exportaciones genéricas ----------

    def generar_exportacion_excel(
        self,
        exportacion_id: int,
        filas: Iterable[Mapping[str, Any]],
        definicion: Mapping[str, Any],
    ) -> str:
        """
        Genera un XLSX genérico para una exportación masiva.
        - 'filas': iterable de dicts con datos.
        - 'definicion': puede contener 'columnas' para ordenar/filtrar columnas.
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Exportación"

        filas = list(filas)
        if not filas:
            ws.append(["Mensaje"])
            ws.append(["Sin datos para exportar"])
        else:
            # Determinar columnas
            columnas_def = definicion.get("columnas")
            if columnas_def:
                headers = columnas_def
            else:
                headers = list(filas[0].keys())

            ws.append(headers)
            for fila in filas:
                ws.append([fila.get(col) for col in headers])

        relative_path = f"exportaciones/{exportacion_id}.xlsx"
        self.storage.ensure_dir_for(relative_path)
        full_path = self.storage.get_full_path(relative_path)
        wb.save(full_path)

        return full_path.relative_to(self.storage.base_path).as_posix()

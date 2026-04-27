"""Exportacion de resultados normalizados."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class ExporterError(Exception):
    """Error al exportar archivos de salida."""


class MatrixExporter:
    """Exporta la matriz normalizada en formatos operativos."""

    def export(self, df: pd.DataFrame, output_excel: Path, output_csv: Path) -> None:
        try:
            output_excel.parent.mkdir(parents=True, exist_ok=True)
            output_csv.parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(output_excel, index=False, engine="openpyxl")
            df.to_csv(output_csv, index=False, encoding="utf-8-sig")
        except Exception as exc:
            raise ExporterError(f"No fue posible exportar los archivos normalizados: {exc}") from exc

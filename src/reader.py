"""Lectura de matrices Excel de produccion grafica."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class ReaderError(Exception):
    """Error al leer el archivo de entrada."""


class ExcelReader:
    """Lee Excel como datos crudos para permitir normalizacion flexible."""

    def __init__(self, sheet_name: str | int = 0) -> None:
        self.sheet_name = sheet_name

    def read(self, input_path: Path) -> pd.DataFrame:
        if not input_path.exists():
            raise ReaderError(f"No se encontro el Excel de entrada: {input_path}")

        if input_path.suffix.lower() not in {".xlsx", ".xlsm", ".xls"}:
            raise ReaderError(f"El archivo de entrada debe ser Excel, no: {input_path.suffix}")

        try:
            return pd.read_excel(input_path, sheet_name=self.sheet_name, header=None, dtype=object, engine="openpyxl")
        except Exception as exc:
            raise ReaderError(f"No fue posible leer el Excel {input_path}: {exc}") from exc

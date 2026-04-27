"""Punto de entrada para normalizar matrices Excel de produccion grafica."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import ConfigLoader
from exporter import MatrixExporter
from logger import setup_logger
from normalizer import MatrixNormalizer
from reader import ExcelReader
from validators import MatrixValidator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normaliza matriz Excel de produccion grafica.")
    parser.add_argument("--config", default=None, help="Ruta al archivo config.yaml")
    parser.add_argument("--input", default=None, help="Ruta al Excel original de entrada")
    parser.add_argument("--output-excel", default=None, help="Ruta al Excel normalizado de salida")
    parser.add_argument("--output-csv", default=None, help="Ruta al CSV normalizado de salida")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        app_config = ConfigLoader().load(args.config)
        input_excel = _resolve_override(args.input, app_config.input_excel, app_config.project_root)
        output_excel = _resolve_override(args.output_excel, app_config.output_excel, app_config.project_root)
        output_csv = _resolve_override(args.output_csv, app_config.output_csv, app_config.project_root)

        logger, log_path = setup_logger(app_config.logs_dir)
        logger.info("Inicio de normalizacion de matriz Excel")
        logger.info("Config: %s", app_config.config_path)
        logger.info("Input: %s", input_excel)
        logger.info("Output Excel: %s", output_excel)
        logger.info("Output CSV: %s", output_csv)

        reader = ExcelReader(sheet_name=app_config.excel.get("sheet_name", 0))
        raw_df = reader.read(input_excel)
        logger.info("Filas crudas leidas: %s | Columnas crudas: %s", raw_df.shape[0], raw_df.shape[1])

        normalizer_config = dict(app_config.normalization)
        normalizer_config["header_scan_rows"] = app_config.excel.get("header_scan_rows", 25)
        normalizer = MatrixNormalizer(normalizer_config)
        normalized_df, normalization_report = normalizer.normalize(raw_df)

        validator = MatrixValidator(app_config.normalization)
        validation_summary = validator.validate(normalized_df)

        exporter = MatrixExporter()
        exporter.export(normalized_df, output_excel, output_csv)

        logger.info("Filas normalizadas exportadas: %s", len(normalized_df))
        logger.info("Filas vacias omitidas: %s", normalization_report.empty_rows_removed)
        logger.info("Encabezados repetidos omitidos: %s", normalization_report.repeated_headers_removed)
        logger.info("Fila de encabezado detectada: %s", normalization_report.header_row_index)
        logger.info("Columnas detectadas: %s", normalization_report.detected_columns)
        _log_validation_summary(logger, validation_summary.as_dict())
        logger.info("Log generado: %s", log_path)
        logger.info("Fin de normalizacion")

        print("Normalizacion finalizada correctamente.")
        print(f"Filas normalizadas: {len(normalized_df)}")
        print(f"Excel: {output_excel}")
        print(f"CSV: {output_csv}")
        print(f"Log: {log_path}")
        return 0
    except Exception as exc:
        print(f"Error en normalizacion: {exc}")
        return 1


def _resolve_override(raw_value: str | None, default_path: Path, project_root: Path) -> Path:
    if not raw_value:
        return default_path
    path = Path(raw_value)
    return path if path.is_absolute() else project_root / path


def _log_validation_summary(logger, summary: dict[str, list[str]]) -> None:
    for validation_name, piece_ids in summary.items():
        if piece_ids:
            logger.warning("%s: %s", validation_name, ", ".join(piece_ids))
        else:
            logger.info("%s: sin hallazgos", validation_name)


if __name__ == "__main__":
    raise SystemExit(main())

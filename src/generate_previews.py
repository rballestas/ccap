"""CLI experimental para generar previews graficos desde piezas normalizadas."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from config import ConfigLoader
from logger import setup_logger
from piece_generator import PiecePreviewGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera previews comparativos desde matriz normalizada y KVS.")
    parser.add_argument("--config", default=None, help="Ruta a config.yaml")
    parser.add_argument("--input", default=None, help="CSV normalizado de entrada")
    parser.add_argument("--output", default=None, help="Carpeta de previews generados")
    parser.add_argument("--limit", type=int, default=None, help="Cantidad maxima de piezas a generar")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        app_config = ConfigLoader().load(args.config)
        input_csv = _resolve(args.input, app_config.output_csv, app_config.project_root)
        output_dir = _resolve(args.output, app_config.generated_dir, app_config.project_root)
        logger, log_path = setup_logger(app_config.logs_dir, prefix="generacion_preview")

        logger.info("Inicio de generacion experimental de previews")
        logger.info("Input normalizado: %s", input_csv)
        logger.info("Output previews: %s", output_dir)
        logger.info("KVS root: %s", app_config.generation.get("kvs_root"))

        df = pd.read_csv(input_csv, encoding="utf-8-sig")
        generator = PiecePreviewGenerator(app_config.generation, output_dir)
        output_paths = generator.generate_from_dataframe(df, limit=args.limit)

        for path in output_paths:
            logger.info("Preview generado: %s", path)

        logger.info("Previews generados: %s", len(output_paths))
        logger.info("Log generado: %s", log_path)
        print("Generacion experimental finalizada.")
        print(f"Previews generados: {len(output_paths)}")
        print(f"Salida: {output_dir}")
        print(f"Log: {log_path}")
        return 0
    except Exception as exc:
        print(f"Error generando previews: {exc}")
        return 1


def _resolve(raw_value: str | None, default_path: Path, project_root: Path) -> Path:
    if not raw_value:
        return default_path
    path = Path(raw_value)
    return path if path.is_absolute() else project_root / path


if __name__ == "__main__":
    raise SystemExit(main())

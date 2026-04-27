"""Command-line entry point for Cheil Creative Automation Platform."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from config_manager import ConfigManager
from generator import Generator
from input_handler import InputHandler
from output_manager import OutputManager
from template_engine import TemplateEngine
from validator import ValidationError, Validator


LOGGER = logging.getLogger("cheil_automation")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automatizacion de Produccion Grafica")
    parser.add_argument("--input", required=True, help="Archivo de datos de entrada CSV o Excel")
    parser.add_argument("--output", help="Directorio base de salida")
    parser.add_argument("--validate-only", action="store_true", help="Solo validar sin generar piezas")
    return parser.parse_args()


def setup_logging(logs_dir: Path, timestamp: str, level_name: str) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"automation_{timestamp}.log"
    level = getattr(logging, level_name.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_path


def resolve_input_path(raw_path: str, project_root: Path) -> Path:
    input_path = Path(raw_path)
    if input_path.is_absolute():
        return input_path
    return project_root / input_path


def run() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    config = ConfigManager().load()
    log_path = setup_logging(
        config.logs_dir,
        timestamp,
        config.settings["logging"].get("level", "INFO"),
    )

    input_path = resolve_input_path(args.input, config.project_root)
    output_base = Path(args.output) if args.output else config.output_dir
    if not output_base.is_absolute():
        output_base = config.project_root / output_base

    LOGGER.info("Inicio de ejecucion")
    LOGGER.info("Archivo de entrada: %s", input_path)
    LOGGER.info("Archivo de log: %s", log_path)

    input_handler = InputHandler(config.supported_input_formats)
    validator = Validator(config)
    template_engine = TemplateEngine(config.templates_dir)
    generator = Generator(config)
    output_manager = OutputManager(output_base, timestamp)

    try:
        records = input_handler.load_data(input_path)
        validator.validate_dataset(records)
    except Exception as exc:
        LOGGER.exception("No fue posible iniciar el procesamiento: %s", exc)
        print(f"Error inicial: {exc}")
        return 1

    LOGGER.info("Registros leidos: %s", len(records))
    LOGGER.info("Carpeta de salida de la ejecucion: %s", output_manager.run_dir)

    manifest: dict[str, Any] = {
        "run_timestamp": timestamp,
        "input_file": str(input_path),
        "output_dir": str(output_manager.run_dir),
        "log_file": str(log_path),
        "validate_only": args.validate_only,
        "total_records": len(records),
        "successful": [],
        "failed": [],
    }

    for index, record in enumerate(records, start=1):
        piece_id = str(record.get("id", f"fila_{index}"))
        template_name = str(record.get("template_name", ""))
        template_rules = config.templates.get(template_name, {})

        try:
            validator.validate_record(record)
            output_format = validator.get_output_format(record, template_rules)

            if args.validate_only:
                LOGGER.info("Pieza %s validada correctamente", piece_id)
                manifest["successful"].append({"id": piece_id, "status": "validated"})
                continue

            processed_template = template_engine.render(template_name, record)
            generated_piece = generator.generate(processed_template, record, output_format)
            output_path = output_manager.save_piece(generated_piece, record, output_format)

            LOGGER.info("Pieza %s generada: %s", piece_id, output_path)
            manifest["successful"].append(
                {
                    "id": piece_id,
                    "template": template_name,
                    "format": output_format,
                    "output_path": str(output_path),
                    "status": "generated",
                }
            )
        except ValidationError as exc:
            LOGGER.error("Pieza %s rechazada por validacion: %s", piece_id, exc)
            manifest["failed"].append({"id": piece_id, "template": template_name, "error": str(exc)})
        except Exception as exc:
            LOGGER.exception("Error inesperado procesando pieza %s: %s", piece_id, exc)
            manifest["failed"].append({"id": piece_id, "template": template_name, "error": str(exc)})

    manifest["successful_count"] = len(manifest["successful"])
    manifest["failed_count"] = len(manifest["failed"])
    manifest_path = output_manager.save_manifest(manifest)

    LOGGER.info("Fin de ejecucion. Exitosas: %s | Fallidas: %s", manifest["successful_count"], manifest["failed_count"])
    LOGGER.info("Manifest: %s", manifest_path)

    print(f"Ejecucion finalizada. Exitosas: {manifest['successful_count']} | Fallidas: {manifest['failed_count']}")
    print(f"Salida: {output_manager.run_dir}")
    print(f"Log: {log_path}")
    print(f"Manifest: {manifest_path}")

    return 0 if manifest["failed_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(run())

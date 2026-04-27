"""Validation rules for input records, templates and assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config_manager import AppConfig


class ValidationError(Exception):
    """Raised when a piece cannot be safely generated."""


class Validator:
    """Validates data before any graphic piece is generated."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def validate_dataset(self, records: list[dict[str, Any]]) -> None:
        if not records:
            raise ValidationError("El archivo de entrada no contiene registros para procesar.")

        seen_ids: set[str] = set()
        for index, record in enumerate(records, start=1):
            piece_id = str(record.get("id", "")).strip()
            if not piece_id:
                raise ValidationError(f"La fila {index} no tiene un id valido.")
            if piece_id in seen_ids:
                raise ValidationError(f"El id '{piece_id}' esta duplicado en el archivo de entrada.")
            seen_ids.add(piece_id)

    def validate_record(self, record: dict[str, Any]) -> None:
        self._validate_required_fields(record, self.config.required_fields, "globales")

        template_name = str(record.get("template_name", "")).strip()
        template_path = self.config.templates_dir / template_name
        if not template_path.exists():
            raise ValidationError(f"No existe el template '{template_name}' en {self.config.templates_dir}.")

        template_rules = self.config.templates.get(template_name, {})
        self._validate_required_fields(record, template_rules.get("required_fields", []), f"del template {template_name}")
        self._validate_output_format(record, template_rules)
        self._validate_assets(record, template_rules)

    def _validate_required_fields(self, record: dict[str, Any], required_fields: list[str], context: str) -> None:
        missing = [field for field in required_fields if not str(record.get(field, "")).strip()]
        if missing:
            piece_id = record.get("id", "sin_id")
            raise ValidationError(f"La pieza {piece_id} no tiene campos obligatorios {context}: {', '.join(missing)}")

    def _validate_output_format(self, record: dict[str, Any], template_rules: dict[str, Any]) -> None:
        output_format = self.get_output_format(record, template_rules)
        if output_format not in self.config.supported_output_formats:
            allowed = ", ".join(sorted(self.config.supported_output_formats))
            raise ValidationError(f"Formato de salida no soportado '{output_format}'. Permitidos: {allowed}")

    def _validate_assets(self, record: dict[str, Any], template_rules: dict[str, Any]) -> None:
        asset_fields = set(self.config.asset_fields) | set(template_rules.get("asset_fields", []))
        missing_assets: list[str] = []

        for field in sorted(asset_fields):
            raw_value = str(record.get(field, "")).strip()
            if not raw_value:
                continue

            asset_path = Path(raw_value)
            if not asset_path.is_absolute():
                asset_path = self.config.project_root / asset_path

            if not asset_path.exists():
                missing_assets.append(f"{field}={raw_value}")

        if missing_assets:
            piece_id = record.get("id", "sin_id")
            raise ValidationError(f"La pieza {piece_id} referencia assets inexistentes: {', '.join(missing_assets)}")

    def get_output_format(self, record: dict[str, Any], template_rules: dict[str, Any]) -> str:
        configured_field = self.config.output_format_field
        output_format = str(record.get(configured_field, "")).strip().lower()
        if output_format:
            return output_format

        if template_rules.get("default_output_format"):
            return str(template_rules["default_output_format"]).lower()

        template_name = str(record.get("template_name", ""))
        template_suffix = Path(template_name).suffix.replace(".", "").lower()
        return template_suffix or str(self.config.settings["generation"]["default_format"]).lower()

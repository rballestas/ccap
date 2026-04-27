"""Configuration loading utilities for the automation pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigurationError(Exception):
    """Raised when project configuration is missing or invalid."""


@dataclass(frozen=True)
class AppConfig:
    """Normalized application configuration."""

    project_root: Path
    settings: dict[str, Any]
    templates: dict[str, Any]

    @property
    def input_dir(self) -> Path:
        return self.project_root / self.settings["paths"]["input_dir"]

    @property
    def output_dir(self) -> Path:
        return self.project_root / self.settings["paths"]["output_dir"]

    @property
    def logs_dir(self) -> Path:
        return self.project_root / self.settings["paths"]["logs_dir"]

    @property
    def templates_dir(self) -> Path:
        return self.project_root / self.settings["paths"]["templates_dir"]

    @property
    def assets_dir(self) -> Path:
        return self.project_root / self.settings["paths"]["assets_dir"]

    @property
    def supported_input_formats(self) -> set[str]:
        return set(self.settings["generation"]["supported_input_formats"])

    @property
    def supported_output_formats(self) -> set[str]:
        return set(self.settings["generation"]["supported_output_formats"])

    @property
    def required_fields(self) -> list[str]:
        return list(self.settings["validation"]["required_fields"])

    @property
    def asset_fields(self) -> list[str]:
        return list(self.settings["validation"].get("asset_fields", []))

    @property
    def output_format_field(self) -> str:
        return self.settings["validation"].get("output_format_field", "formato_salida")


class ConfigManager:
    """Loads JSON configuration files and exposes normalized paths."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[1]

    def load(self) -> AppConfig:
        settings = self._load_json(self.project_root / "config" / "settings.json")
        templates = self._load_json(self.project_root / "config" / "templates_config.json")
        self._validate_settings(settings)
        return AppConfig(project_root=self.project_root, settings=settings, templates=templates)

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise ConfigurationError(f"No se encontro el archivo de configuracion: {path}")

        try:
            with path.open("r", encoding="utf-8-sig") as file:
                return json.load(file)
        except json.JSONDecodeError as exc:
            raise ConfigurationError(f"El archivo {path} no contiene JSON valido: {exc}") from exc

    def _validate_settings(self, settings: dict[str, Any]) -> None:
        required_sections = ["paths", "generation", "validation", "logging"]
        missing = [section for section in required_sections if section not in settings]
        if missing:
            raise ConfigurationError(f"Faltan secciones de configuracion: {', '.join(missing)}")

        required_paths = ["input_dir", "output_dir", "logs_dir", "templates_dir", "assets_dir"]
        missing_paths = [key for key in required_paths if key not in settings["paths"]]
        if missing_paths:
            raise ConfigurationError(f"Faltan rutas de configuracion: {', '.join(missing_paths)}")


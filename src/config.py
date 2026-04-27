"""Configuracion centralizada para la fase de normalizacion."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


class ConfigError(Exception):
    """Error de configuracion del proyecto."""


@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    raw: dict[str, Any]
    config_path: Path

    @property
    def input_excel(self) -> Path:
        return self._resolve_env_path("CCAP_INPUT_EXCEL", self.raw["paths"]["input_excel"])

    @property
    def output_excel(self) -> Path:
        return self._resolve_env_path("CCAP_OUTPUT_EXCEL", self.raw["paths"]["output_excel"])

    @property
    def output_csv(self) -> Path:
        return self._resolve_env_path("CCAP_OUTPUT_CSV", self.raw["paths"]["output_csv"])

    @property
    def logs_dir(self) -> Path:
        return self._resolve_env_path("CCAP_LOGS_DIR", self.raw["paths"]["logs_dir"])

    @property
    def generated_dir(self) -> Path:
        return self._resolve_env_path("CCAP_GENERATED_DIR", self.raw["paths"]["generated_dir"])

    @property
    def excel(self) -> dict[str, Any]:
        return self.raw.get("excel", {})

    @property
    def normalization(self) -> dict[str, Any]:
        return self.raw.get("normalization", {})

    @property
    def generation(self) -> dict[str, Any]:
        generation = dict(self.raw.get("generation", {}))
        if os.getenv("CCAP_KVS_ROOT"):
            generation["kvs_root"] = os.getenv("CCAP_KVS_ROOT")
        return generation

    def _resolve_env_path(self, env_name: str, configured_path: str) -> Path:
        value = os.getenv(env_name, configured_path)
        path = Path(value)
        return path if path.is_absolute() else self.project_root / path


class ConfigLoader:
    """Carga config.yaml y variables opcionales desde .env."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[1]

    def load(self, config_path: str | Path | None = None) -> AppConfig:
        load_dotenv(self.project_root / ".env")
        selected_config = Path(config_path or os.getenv("CCAP_CONFIG_PATH", "config.yaml"))
        if not selected_config.is_absolute():
            selected_config = self.project_root / selected_config

        if not selected_config.exists():
            raise ConfigError(f"No se encontro el archivo de configuracion: {selected_config}")

        with selected_config.open("r", encoding="utf-8-sig") as file:
            raw = yaml.safe_load(file) or {}

        self._validate(raw)
        return AppConfig(project_root=self.project_root, raw=raw, config_path=selected_config)

    def _validate(self, raw: dict[str, Any]) -> None:
        for section in ["paths", "normalization"]:
            if section not in raw:
                raise ConfigError(f"Falta la seccion requerida en config.yaml: {section}")

        expected_paths = ["input_excel", "output_excel", "output_csv", "logs_dir", "generated_dir"]
        missing_paths = [key for key in expected_paths if key not in raw["paths"]]
        if missing_paths:
            raise ConfigError(f"Faltan rutas en config.yaml: {', '.join(missing_paths)}")

        if "expected_columns" not in raw["normalization"]:
            raise ConfigError("Falta normalization.expected_columns en config.yaml")

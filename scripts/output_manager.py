"""Output folder management and manifest creation."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class OutputManager:
    """Creates organized output folders and saves generated pieces."""

    def __init__(self, base_output_dir: Path, run_timestamp: str) -> None:
        self.base_output_dir = base_output_dir
        self.run_timestamp = run_timestamp
        self.run_dir = base_output_dir / f"run_{run_timestamp}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def save_piece(self, piece: bytes | str, record: dict[str, Any], output_format: str) -> Path:
        filename = self._build_filename(record, output_format)
        output_path = self.run_dir / filename

        if isinstance(piece, bytes):
            output_path.write_bytes(piece)
        else:
            output_path.write_text(piece, encoding="utf-8")

        return output_path

    def save_manifest(self, manifest: dict[str, Any]) -> Path:
        manifest_path = self.run_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest_path

    def _build_filename(self, record: dict[str, Any], output_format: str) -> str:
        piece_id = self._slugify(str(record.get("id", "pieza")))
        raw_name = str(record.get("nombre_archivo") or record.get("titulo") or record.get("nombre_producto") or "pieza")
        slug = self._slugify(raw_name)
        return f"{piece_id}_{slug}.{output_format.lower()}"

    def _slugify(self, value: str) -> str:
        normalized = value.strip().lower()
        normalized = re.sub(r"[^a-z0-9áéíóúñü]+", "_", normalized, flags=re.IGNORECASE)
        normalized = normalized.strip("_")
        return normalized or "pieza"

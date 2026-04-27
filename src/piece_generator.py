"""Generador experimental de previews desde KVS y matriz normalizada."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from kv_catalog import KVCatalog

Image.MAX_IMAGE_PIXELS = None


class PreviewGenerationError(Exception):
    """Error al generar previews."""


class PiecePreviewGenerator:
    """Crea previews comparativos; no produce artes finales de impresion."""

    def __init__(self, generation_config: dict[str, Any], output_dir: Path) -> None:
        self.config = generation_config
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.catalog = KVCatalog(Path(generation_config["kvs_root"]))

    def generate_from_dataframe(self, df: pd.DataFrame, limit: int | None = None) -> list[Path]:
        generated: list[Path] = []
        records = df.head(limit).to_dict("records") if limit else df.to_dict("records")
        for record in records:
            generated.append(self.generate_piece(record))
        return generated

    def generate_piece(self, record: dict[str, Any]) -> Path:
        width_cm = self._to_float(record.get("ancho_cm"))
        height_cm = self._to_float(record.get("alto_cm"))
        if not width_cm or not height_cm:
            raise PreviewGenerationError(f"La pieza {record.get('id_pieza')} no tiene medidas validas.")

        target_size = self._target_size(width_cm, height_cm)
        kv_asset = self.catalog.select_for_dimensions(width_cm, height_cm)

        with Image.open(kv_asset.path) as source:
            source = source.convert("RGB")
            canvas = self._cover_resize(source, target_size)

        self._draw_overlays(canvas, record, width_cm, height_cm, kv_asset.name)

        filename = self._build_filename(record)
        output_path = self.output_dir / filename
        canvas.save(output_path, format="PNG", optimize=True)
        return output_path

    def _target_size(self, width_cm: float, height_cm: float) -> tuple[int, int]:
        preview = self.config.get("preview", {})
        px_per_cm = int(preview.get("px_per_cm", 8))
        width_px = max(320, int(width_cm * px_per_cm))
        height_px = max(320, int(height_cm * px_per_cm))
        max_width = int(preview.get("max_width_px", 1800))
        max_height = int(preview.get("max_height_px", 1800))
        scale = min(max_width / width_px, max_height / height_px, 1.0)
        return max(1, int(width_px * scale)), max(1, int(height_px * scale))

    def _cover_resize(self, image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
        target_w, target_h = target_size
        source_ratio = image.width / image.height
        target_ratio = target_w / target_h

        if source_ratio > target_ratio:
            new_h = target_h
            new_w = int(new_h * source_ratio)
        else:
            new_w = target_w
            new_h = int(new_w / source_ratio)

        resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = max(0, (new_w - target_w) // 2)
        top = max(0, (new_h - target_h) // 2)
        return resized.crop((left, top, left + target_w, top + target_h))

    def _draw_overlays(
        self,
        image: Image.Image,
        record: dict[str, Any],
        width_cm: float,
        height_cm: float,
        kv_name: str,
    ) -> None:
        draw = ImageDraw.Draw(image, "RGBA")
        text_config = self.config.get("text", {})
        safe_margin = int(min(image.size) * float(text_config.get("safe_margin_ratio", 0.055)))
        title_size = max(18, int(min(image.size) * float(text_config.get("font_size_title_ratio", 0.045))))
        body_size = max(12, int(min(image.size) * float(text_config.get("font_size_body_ratio", 0.022))))
        title_font = ImageFont.load_default(size=title_size)
        body_font = ImageFont.load_default(size=body_size)

        panel_h = max(int(image.height * 0.18), safe_margin * 3)
        draw.rectangle((0, image.height - panel_h, image.width, image.height), fill=(255, 255, 255, 215))

        title = self._clean_text(str(record.get("tienda") or "Tienda sin definir"))
        subtitle = self._clean_text(str(record.get("tipo_grafica") or "Tipo sin definir"))
        measure = f"{width_cm:g} x {height_cm:g} cm"
        flags = self._build_flags(record)

        x = safe_margin
        y = image.height - panel_h + safe_margin // 2
        draw.text((x, y), title, fill=(0, 0, 0, 255), font=title_font)
        draw.text((x, y + title_size + 6), f"{subtitle} | {measure}", fill=(35, 35, 35, 255), font=body_font)
        if flags:
            draw.text((x, y + title_size + body_size + 14), flags, fill=(35, 35, 35, 255), font=body_font)

        badge = "PREVIEW MVP"
        bbox = draw.textbbox((0, 0), badge, font=body_font)
        badge_w = bbox[2] - bbox[0] + 24
        badge_h = bbox[3] - bbox[1] + 18
        draw.rounded_rectangle((safe_margin, safe_margin, safe_margin + badge_w, safe_margin + badge_h), radius=10, fill=(0, 0, 0, 185))
        draw.text((safe_margin + 12, safe_margin + 8), badge, fill=(255, 255, 255, 255), font=body_font)

        footer = f"KV: {kv_name}"
        draw.text((safe_margin, safe_margin + badge_h + 8), footer[:90], fill=(255, 255, 255, 230), font=body_font)

    def _build_flags(self, record: dict[str, Any]) -> str:
        labels = []
        if self._is_true(record.get("requiere_logo_samsung")):
            labels.append("Samsung")
        if self._is_true(record.get("requiere_otro_logo")):
            labels.append(str(record.get("otro_logo")))
        if self._is_true(record.get("requiere_logo_subtel")):
            labels.append("Subtel")
        if self._is_true(record.get("requiere_legal")):
            labels.append("Legal")
        if self._is_true(record.get("requiere_troquelado")):
            labels.append("Troquelado")
        return " | ".join(label for label in labels if label)

    def _build_filename(self, record: dict[str, Any]) -> str:
        piece_id = self._slugify(str(record.get("id_pieza") or "pieza"))
        tienda = self._slugify(str(record.get("tienda") or "sin_tienda"))
        return f"{piece_id}_{tienda}.png"

    def _slugify(self, value: str) -> str:
        value = unicodedata.normalize("NFKD", value.lower().strip())
        value = value.encode("ascii", "ignore").decode("ascii")
        value = re.sub(r"[^a-z0-9]+", "_", value, flags=re.IGNORECASE)
        return (value.strip("_") or "pieza")[:90]

    def _to_float(self, value: Any) -> float | None:
        try:
            if pd.isna(value):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _is_true(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"true", "1", "si", "sí"}

    def _clean_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

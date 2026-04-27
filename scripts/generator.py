"""Graphic generation strategies for the MVP pipeline."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from config_manager import AppConfig


class Generator:
    """Generates output payloads from processed templates and source data."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def generate(self, processed_template: str, data: dict[str, Any], output_format: str) -> bytes | str:
        output_format = output_format.lower()

        if output_format in {"svg", "html"}:
            return processed_template

        if output_format in {"png", "jpg", "jpeg"}:
            return self._generate_raster_preview(data, output_format)

        raise ValueError(f"No existe estrategia de generacion para el formato: {output_format}")

    def _generate_raster_preview(self, data: dict[str, Any], output_format: str) -> bytes:
        canvas = self.config.settings["generation"].get("default_canvas", {})
        width = int(canvas.get("width", 1200))
        height = int(canvas.get("height", 628))
        background_color = str(data.get("color_fondo") or canvas.get("background_color", "#FFFFFF"))

        image = Image.new("RGB", (width, height), color=background_color)
        draw = ImageDraw.Draw(image)
        font_title = ImageFont.load_default(size=36)
        font_body = ImageFont.load_default(size=22)

        title = str(data.get("titulo") or data.get("nombre_producto") or "Pieza sin titulo")
        description = str(data.get("descripcion") or data.get("promocion") or data.get("texto") or "")
        cta = str(data.get("cta") or "")

        draw.text((60, 80), title, fill="#111111", font=font_title)
        if description:
            draw.text((60, 150), description, fill="#333333", font=font_body)
        if cta:
            draw.rounded_rectangle((60, 230, 360, 290), radius=18, fill="#111111")
            draw.text((90, 248), cta, fill="#FFFFFF", font=font_body)

        buffer = BytesIO()
        pil_format = "JPEG" if output_format in {"jpg", "jpeg"} else "PNG"
        image.save(buffer, format=pil_format)
        return buffer.getvalue()

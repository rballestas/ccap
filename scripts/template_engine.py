"""Template loading and rendering utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound


class TemplateEngineError(Exception):
    """Raised when a template cannot be loaded or rendered."""


class TemplateEngine:
    """Loads templates from disk and renders them with piece data."""

    def __init__(self, templates_dir: Path) -> None:
        self.templates_dir = templates_dir
        self.environment = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            undefined=StrictUndefined,
            autoescape=False,
        )

    def render(self, template_name: str, data: dict[str, Any]) -> str:
        try:
            template = self.environment.get_template(template_name)
            return template.render(**data)
        except TemplateNotFound as exc:
            raise TemplateEngineError(f"No se encontro el template: {template_name}") from exc
        except Exception as exc:
            raise TemplateEngineError(f"No se pudo procesar el template {template_name}: {exc}") from exc

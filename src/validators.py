"""Validaciones de calidad para piezas normalizadas."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class ValidationSummary:
    medidas_faltantes: list[str] = field(default_factory=list)
    medidas_invalidas: list[str] = field(default_factory=list)
    tienda_faltante: list[str] = field(default_factory=list)
    observaciones_criticas: list[str] = field(default_factory=list)
    piezas_con_troquelado: list[str] = field(default_factory=list)
    piezas_con_composicion_especial: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, list[str]]:
        return {
            "medidas_faltantes": self.medidas_faltantes,
            "medidas_invalidas": self.medidas_invalidas,
            "tienda_faltante": self.tienda_faltante,
            "observaciones_criticas": self.observaciones_criticas,
            "piezas_con_troquelado": self.piezas_con_troquelado,
            "piezas_con_composicion_especial": self.piezas_con_composicion_especial,
        }


class MatrixValidator:
    """Aplica validaciones de datos y alertas productivas."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.critical_keywords = [self._normalize(value) for value in config.get("critical_observation_keywords", [])]

    def validate(self, df: pd.DataFrame) -> ValidationSummary:
        summary = ValidationSummary()

        for _, row in df.iterrows():
            piece_id = str(row.get("id_pieza", "sin_id"))
            medidas = str(row.get("medidas_original", "")).strip()
            ancho = row.get("ancho_cm")
            alto = row.get("alto_cm")
            tienda = str(row.get("tienda", "")).strip()
            observaciones = str(row.get("observaciones", "")).strip()

            if not medidas:
                summary.medidas_faltantes.append(piece_id)
            elif pd.isna(ancho) or pd.isna(alto) or ancho is None or alto is None:
                summary.medidas_invalidas.append(piece_id)

            if not tienda:
                summary.tienda_faltante.append(piece_id)

            if self._has_critical_observation(observaciones):
                summary.observaciones_criticas.append(piece_id)

            if bool(row.get("requiere_troquelado")):
                summary.piezas_con_troquelado.append(piece_id)

            if bool(row.get("requiere_composicion_especial")):
                summary.piezas_con_composicion_especial.append(piece_id)

        return summary

    def _has_critical_observation(self, value: str) -> bool:
        normalized = self._normalize(value)
        return any(keyword and keyword in normalized for keyword in self.critical_keywords)

    def _normalize(self, value: str) -> str:
        return value.lower().strip()

"""Normalizacion de matrices Excel irregulares."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class NormalizationReport:
    empty_rows_removed: int = 0
    repeated_headers_removed: int = 0
    header_row_index: int | None = None
    detected_columns: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class MatrixNormalizer:
    """Convierte una matriz operacional a una estructura tecnica estandar."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.expected_columns = config["expected_columns"]
        self.output_columns = config["output_columns"]
        self.truthy_keywords = self._normalize_keyword_list(config.get("truthy_keywords", []))
        self.troquelado_keywords = self._normalize_keyword_list(config.get("troquelado_keywords", []))
        self.special_keywords = self._normalize_keyword_list(config.get("special_composition_keywords", []))

    def normalize(self, raw_df: pd.DataFrame) -> tuple[pd.DataFrame, NormalizationReport]:
        report = NormalizationReport()
        cleaned = self._drop_empty_rows(raw_df, report)
        if cleaned.empty:
            return pd.DataFrame(columns=self.output_columns), report

        header_index = self._detect_header_row(cleaned)
        report.header_row_index = int(header_index)

        headers = [self._cell_to_text(value) for value in cleaned.loc[header_index].tolist()]
        data = cleaned.loc[header_index + 1 :].copy()
        data.columns = self._dedupe_headers(headers)
        data = self._drop_empty_rows(data, report)

        canonical_map = self._build_canonical_map(data.columns)
        report.detected_columns = canonical_map.copy()
        data = self._remove_repeated_headers(data, canonical_map, report)

        normalized_records = []
        for index, row in data.iterrows():
            record = self._normalize_row(row, canonical_map, len(normalized_records) + 1)
            if self._is_effectively_empty_record(record):
                report.empty_rows_removed += 1
                continue
            normalized_records.append(record)

        normalized_df = pd.DataFrame(normalized_records, columns=self.output_columns)
        return normalized_df, report

    def _drop_empty_rows(self, df: pd.DataFrame, report: NormalizationReport) -> pd.DataFrame:
        before = len(df)
        cleaned = df.dropna(how="all").copy()
        cleaned = cleaned[~cleaned.apply(lambda row: all(not self._cell_to_text(value) for value in row), axis=1)]
        report.empty_rows_removed += before - len(cleaned)
        return cleaned.reset_index(drop=True)

    def _detect_header_row(self, df: pd.DataFrame) -> int:
        best_index = 0
        best_score = -1
        scan_limit = int(self.config.get("header_scan_rows", 25))

        for index, row in df.head(scan_limit).iterrows():
            normalized_values = [self._normalize_label(value) for value in row.tolist()]
            score = sum(1 for value in normalized_values if self._canonical_for_label(value))
            if score > best_score:
                best_score = score
                best_index = int(index)

        return best_index

    def _dedupe_headers(self, headers: list[str]) -> list[str]:
        seen: dict[str, int] = {}
        result = []
        for position, header in enumerate(headers):
            base = header or f"columna_{position + 1}"
            key = base
            seen[key] = seen.get(key, 0) + 1
            result.append(base if seen[key] == 1 else f"{base}_{seen[key]}")
        return result

    def _build_canonical_map(self, columns: list[str] | pd.Index) -> dict[str, str]:
        canonical_map: dict[str, str] = {}
        for column in columns:
            canonical = self._canonical_for_label(self._normalize_label(column))
            if canonical and canonical not in canonical_map:
                canonical_map[canonical] = str(column)
        return canonical_map

    def _remove_repeated_headers(
        self,
        data: pd.DataFrame,
        canonical_map: dict[str, str],
        report: NormalizationReport,
    ) -> pd.DataFrame:
        if not canonical_map:
            return data

        def is_repeated_header(row: pd.Series) -> bool:
            matches = 0
            for canonical, source_column in canonical_map.items():
                value = self._normalize_label(row.get(source_column, ""))
                if value and self._canonical_for_label(value) == canonical:
                    matches += 1
            return matches >= max(2, min(4, len(canonical_map)))

        mask = data.apply(is_repeated_header, axis=1)
        report.repeated_headers_removed += int(mask.sum())
        return data.loc[~mask].copy().reset_index(drop=True)

    def _normalize_row(self, row: pd.Series, canonical_map: dict[str, str], sequence: int) -> dict[str, Any]:
        categoria = self._get_value(row, canonical_map, "categoria_grafica")
        medidas = self._get_value(row, canonical_map, "medidas")
        ancho, alto = self._parse_dimensions(medidas)
        logo_samsung = self._get_value(row, canonical_map, "logo_samsung")
        otro_logo = self._get_value(row, canonical_map, "otro_logo")
        logo_subtel = self._get_value(row, canonical_map, "logo_subtel_posicion")
        legal = self._get_value(row, canonical_map, "legal_posicion")
        margen = self._get_value(row, canonical_map, "margen_excedente")
        observaciones = self._get_value(row, canonical_map, "observaciones")

        return {
            "id_pieza": f"PZ-{sequence:04d}",
            "tipo_grafica": categoria,
            "canal": self._infer_channel(categoria),
            "tienda": self._get_value(row, canonical_map, "tienda"),
            "imagen_referencial": self._get_value(row, canonical_map, "imagen_referencial"),
            "medidas_original": medidas,
            "ancho_cm": ancho,
            "alto_cm": alto,
            "logo_samsung": logo_samsung,
            "otro_logo": otro_logo,
            "logo_subtel_posicion": logo_subtel,
            "legal_posicion": legal,
            "margen_excedente": margen,
            "observaciones": observaciones,
            "requiere_troquelado": self._contains_any(f"{margen} {observaciones} {categoria}", self.troquelado_keywords),
            "requiere_logo_samsung": self._is_truthy_requirement(logo_samsung),
            "requiere_otro_logo": bool(otro_logo.strip()),
            "requiere_logo_subtel": bool(logo_subtel.strip()) and not self._is_negative(logo_subtel),
            "requiere_legal": bool(legal.strip()) and not self._is_negative(legal),
            "requiere_composicion_especial": self._contains_any(observaciones, self.special_keywords),
        }

    def _get_value(self, row: pd.Series, canonical_map: dict[str, str], canonical_name: str) -> str:
        source_column = canonical_map.get(canonical_name)
        if not source_column:
            return ""
        return self._cell_to_text(row.get(source_column, ""))

    def _parse_dimensions(self, value: str) -> tuple[float | None, float | None]:
        normalized = self._normalize_dimension_text(value)
        match = re.search(r"(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)", normalized)
        if not match:
            return None, None
        return round(float(match.group(1)), 2), round(float(match.group(2)), 2)

    def _normalize_dimension_text(self, value: str) -> str:
        text = value.lower().replace(",", ".")
        text = text.replace("×", "x").replace("*", "x")
        text = re.sub(r"\b(cms|cm|centimetros|centímetros|mm|mts|m)\b", "", text)
        return re.sub(r"\s+", "", text)

    def _infer_channel(self, categoria: str) -> str:
        normalized = self._normalize_label(categoria)
        if "carrier" in normalized or "operador" in normalized:
            return "carrier"
        if "retail" in normalized or "tienda" in normalized:
            return "retail"
        return "sin_clasificar"

    def _is_effectively_empty_record(self, record: dict[str, Any]) -> bool:
        business_values = [record.get("tipo_grafica"), record.get("tienda"), record.get("medidas_original"), record.get("observaciones")]
        return all(not str(value or "").strip() for value in business_values)

    def _canonical_for_label(self, normalized_label: str) -> str | None:
        for canonical, aliases in self.expected_columns.items():
            normalized_aliases = {self._normalize_label(alias) for alias in aliases}
            if normalized_label in normalized_aliases:
                return canonical
        return None

    def _normalize_label(self, value: Any) -> str:
        text = self._cell_to_text(value).lower()
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^a-z0-9]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _cell_to_text(self, value: Any) -> str:
        if pd.isna(value):
            return ""
        return str(value).strip()

    def _normalize_keyword_list(self, values: list[str]) -> list[str]:
        return [self._normalize_label(value) for value in values]

    def _contains_any(self, value: str, keywords: list[str]) -> bool:
        normalized = self._normalize_label(value)
        return any(keyword and keyword in normalized for keyword in keywords)

    def _is_truthy_requirement(self, value: str) -> bool:
        normalized = self._normalize_label(value)
        return bool(normalized) and not self._is_negative(value) and any(keyword in normalized for keyword in self.truthy_keywords)

    def _is_negative(self, value: str) -> bool:
        normalized = self._normalize_label(value)
        return normalized in {"no", "sin", "n/a", "na", "no aplica", "sin logo"}

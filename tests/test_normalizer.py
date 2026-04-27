"""Tests de normalizacion de matrices Excel."""

from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import ConfigLoader
from normalizer import MatrixNormalizer


class TestMatrixNormalizer(unittest.TestCase):
    def setUp(self):
        config = ConfigLoader(Path(__file__).resolve().parents[1]).load()
        normalizer_config = dict(config.normalization)
        normalizer_config["header_scan_rows"] = 25
        self.normalizer = MatrixNormalizer(normalizer_config)

    def test_normalize_removes_empty_rows_and_repeated_headers(self):
        raw = pd.DataFrame(
            [
                ["Titulo", None, None, None, None, None, None, None, None, None],
                ["Categoria de grafica", "Nombre de la tienda", "Imagen referencial", "Medidas horizontal x vertical", "Con o sin logo Samsung", "Otro logo", "Logo Subtel", "Legal", "MARGEN", "OBSERVACION"],
                ["Retail POP", "Falabella", "ref.jpg", "97,8x169 cms", "Con logo", "", "Inferior", "Abajo", "5 cm", "Troquelado con composicion especial"],
                [None, None, None, None, None, None, None, None, None, None],
                ["Categoria de grafica", "Nombre de la tienda", "Imagen referencial", "Medidas horizontal x vertical", "Con o sin logo Samsung", "Otro logo", "Logo Subtel", "Legal", "EXCEDENTE", "OBSERVACIONES"],
                ["Carrier", "Entel", "ref2.jpg", "120 x 80 cm", "Si", "Logo Entel", "Superior", "", "2 cm", "Confirmar"],
            ]
        )

        normalized, report = self.normalizer.normalize(raw)

        self.assertEqual(len(normalized), 2)
        self.assertEqual(report.repeated_headers_removed, 1)
        self.assertEqual(normalized.loc[0, "ancho_cm"], 97.8)
        self.assertEqual(normalized.loc[0, "alto_cm"], 169.0)
        self.assertTrue(bool(normalized.loc[0, "requiere_troquelado"]))
        self.assertTrue(bool(normalized.loc[0, "requiere_composicion_especial"]))


if __name__ == "__main__":
    unittest.main()

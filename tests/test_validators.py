"""Tests de validaciones de matriz normalizada."""

from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import ConfigLoader
from validators import MatrixValidator


class TestMatrixValidator(unittest.TestCase):
    def setUp(self):
        config = ConfigLoader(Path(__file__).resolve().parents[1]).load()
        self.validator = MatrixValidator(config.normalization)

    def test_validate_flags_missing_and_invalid_data(self):
        data = pd.DataFrame(
            [
                {"id_pieza": "PZ-0001", "medidas_original": "", "ancho_cm": None, "alto_cm": None, "tienda": "Entel", "observaciones": "Urgente revisar", "requiere_troquelado": False, "requiere_composicion_especial": False},
                {"id_pieza": "PZ-0002", "medidas_original": "abc", "ancho_cm": None, "alto_cm": None, "tienda": "", "observaciones": "", "requiere_troquelado": True, "requiere_composicion_especial": True},
            ]
        )

        summary = self.validator.validate(data)

        self.assertEqual(summary.medidas_faltantes, ["PZ-0001"])
        self.assertEqual(summary.medidas_invalidas, ["PZ-0002"])
        self.assertEqual(summary.tienda_faltante, ["PZ-0002"])
        self.assertEqual(summary.observaciones_criticas, ["PZ-0001"])
        self.assertEqual(summary.piezas_con_troquelado, ["PZ-0002"])
        self.assertEqual(summary.piezas_con_composicion_especial, ["PZ-0002"])


if __name__ == "__main__":
    unittest.main()

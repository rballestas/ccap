"""Tests for validation rules."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from config_manager import ConfigManager
from validator import Validator


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.config = ConfigManager(Path(__file__).resolve().parents[1]).load()
        self.validator = Validator(self.config)

    def test_validate_record_accepts_valid_banner(self):
        record = {
            "id": "1",
            "template_name": "banner_template.svg",
            "titulo": "Test",
            "descripcion": "Descripcion",
            "imagen": "",
            "formato_salida": "svg",
        }
        self.validator.validate_record(record)


if __name__ == "__main__":
    unittest.main()

"""Tests for the generator module."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from config_manager import ConfigManager
from generator import Generator


class TestGenerator(unittest.TestCase):
    def setUp(self):
        config = ConfigManager(Path(__file__).resolve().parents[1]).load()
        self.generator = Generator(config)

    def test_generate_svg_returns_processed_template(self):
        result = self.generator.generate("<svg>Test</svg>", {"titulo": "Test"}, "svg")
        self.assertEqual(result, "<svg>Test</svg>")

    def test_generate_png_returns_bytes(self):
        result = self.generator.generate("ignored", {"titulo": "Test"}, "png")
        self.assertIsInstance(result, bytes)


if __name__ == "__main__":
    unittest.main()

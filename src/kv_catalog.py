"""Catalogo de KVS disponibles para previews graficos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


@dataclass(frozen=True)
class KVAsset:
    path: Path
    width: int
    height: int
    orientation: str
    name: str

    @property
    def ratio(self) -> float:
        return self.width / self.height if self.height else 1.0


class KVCatalogError(Exception):
    """Error al construir catalogo de KVS."""


class KVCatalog:
    """Indexa JPGs de KVS y selecciona el mas cercano por proporcion."""

    def __init__(self, kvs_root: Path) -> None:
        self.kvs_root = kvs_root
        self.assets = self._load_assets()

    def select_for_dimensions(self, width_cm: float, height_cm: float) -> KVAsset:
        if not self.assets:
            raise KVCatalogError(f"No hay JPGs de KV disponibles en {self.kvs_root}")

        target_ratio = width_cm / height_cm if height_cm else 1.0
        target_orientation = "horizontal" if target_ratio >= 1 else "vertical"
        candidates = [asset for asset in self.assets if asset.orientation == target_orientation] or self.assets
        return min(candidates, key=lambda asset: abs(asset.ratio - target_ratio))

    def _load_assets(self) -> list[KVAsset]:
        if not self.kvs_root.exists():
            raise KVCatalogError(f"No existe la carpeta KVS configurada: {self.kvs_root}")

        assets: list[KVAsset] = []
        for path in self.kvs_root.rglob("*.jpg"):
            try:
                with Image.open(path) as image:
                    width, height = image.size
            except Exception:
                continue

            orientation = "horizontal" if width >= height else "vertical"
            assets.append(KVAsset(path=path, width=width, height=height, orientation=orientation, name=path.stem))

        return assets

# Guia de Usuario

Esta guia explica como usar el MVP de Cheil Creative Automation Platform.

## Requisitos

- Python 3.8 o superior.
- Dependencias instaladas con `pip install -r requirements.txt`.

## Preparar una ejecucion

1. Coloca los templates en `templates/`.
2. Configura reglas de templates en `config/templates_config.json`.
3. Coloca assets locales en `assets/`.
4. Completa el archivo de entrada en `data/input_data.csv`.

## Validar sin generar

```bash
python scripts/main.py --input data/input_data.csv --validate-only
```

## Generar piezas

```bash
python scripts/main.py --input data/input_data.csv
```

## Revisar resultados

Cada ejecucion crea una carpeta en `output/generated_pieces/run_YYYYMMDD_HHMMSS/`.

Tambien se genera:

- Un log en `output/logs/`.
- Un `manifest.json` dentro de la carpeta de salida.

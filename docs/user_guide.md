# Guia de Usuario

Esta guia describe la Fase 1 del proyecto: normalizacion de matrices Excel de produccion grafica.

## Preparacion

1. Instala dependencias con `pip install -r requirements.txt`.
2. Copia tu matriz original a `input/matriz_piezas.xlsx` o define otra ruta en `config.yaml`.
3. Si necesitas rutas locales distintas, copia `.env.example` como `.env` y ajusta las variables.

## Ejecutar normalizacion

```bash
python src/main.py
```

## Usar el Excel real de trabajo

```bash
python src/main.py --input "C:\Users\roberto.ballestas\Desktop\grafic\INFORMACION GRAFICAS_GALAXY S26.xlsx"
```

## Insumos reales detectados

La carpeta `C:\Users\roberto.ballestas\Desktop\grafic` contiene:

- PDFs: referencias visuales de las piezas finales esperadas.
- `KVS`: paquetes base para armado futuro, con archivos `.ai`, fuentes y links JPG.
- Excel: matriz de requerimientos usada como input principal de Fase 1.

Los PDFs y KVS no se copian al repositorio porque son archivos pesados de produccion. Deben tratarse como insumos externos configurables.

## Salidas

El proceso genera:

- `output/piezas_normalizadas.xlsx`
- `output/piezas_normalizadas.csv`
- `output/logs/normalizacion_YYYYMMDD_HHMMSS.log`

## Importante

Esta fase no genera piezas graficas finales. Solo limpia, estructura y valida la informacion para preparar una segunda fase de automatizacion grafica.

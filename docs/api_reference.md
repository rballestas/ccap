# Referencia de Modulos

## `src/config.py`

Carga `config.yaml`, lee variables desde `.env` y expone rutas normalizadas.

## `src/logger.py`

Configura logs de consola y archivo por ejecucion.

## `src/reader.py`

Lee matrices Excel con `pandas` y `openpyxl` en formato crudo para permitir deteccion flexible de encabezados.

## `src/normalizer.py`

Normaliza columnas, omite filas vacias, omite encabezados repetidos, unifica campos equivalentes, extrae medidas y genera campos tecnicos.

## `src/validators.py`

Genera resumen de validaciones: medidas faltantes, medidas invalidas, tienda faltante, observaciones criticas, troquelado y composicion especial.

## `src/exporter.py`

Exporta la matriz limpia a Excel y CSV.

## `src/main.py`

Orquesta la fase completa de normalizacion.

# Cheil Creative Automation Platform - Normalizacion de Matrices de Produccion Grafica

## 1. Proposito del proyecto

Cheil Creative Automation Platform busca industrializar la produccion de piezas graficas para retail y carrier. La plataforma partira desde una matriz Excel operativa, limpiara y estructurara los requerimientos, validara riesgos de produccion y dejara datos tecnicos listos para una segunda fase de generacion grafica con Illustrator, Photoshop, HTML/CSS renderer o Adobe API.

La primera fase no genera piezas graficas finales. Su objetivo es transformar un Excel irregular en una base confiable, normalizada y trazable.

## 2. Objetivo del MVP - Fase 1

1. Leer el Excel original de requerimientos.
2. Detectar y omitir filas vacias.
3. Detectar encabezados repetidos o titulos intermedios.
4. Normalizar nombres de columnas aunque vengan con pequenas variaciones.
5. Unificar `MARGEN` y `EXCEDENTE` en `margen_excedente`.
6. Unificar `OBSERVACION` y `OBSERVACIONES` en `observaciones`.
7. Extraer `ancho_cm` y `alto_cm` desde el campo de medidas.
8. Convertir medidas con coma decimal, por ejemplo `97,8x169 cms`.
9. Crear campos tecnicos estandarizados.
10. Exportar archivos limpios en Excel y CSV.
11. Generar logs de validacion para riesgos de produccion.
12. Dejar arquitectura preparada para conectar motores graficos en fases posteriores.

## 3. Columnas base esperadas del Excel

El Excel original puede venir con nombres de columnas ligeramente distintos, secciones repetidas, titulos intermedios y filas vacias.

Columnas de negocio esperadas:

- `Categoria de grafica`
- `Nombre de la tienda`
- `Imagen referencial`
- `Medidas horizontal x vertical`
- `Con o sin logo Samsung`
- `Otro logo`
- `Logo Subtel`
- `Legal`
- `Margen o excedente`
- `Observaciones`

Variantes soportadas en el MVP:

- `MARGEN`
- `EXCEDENTE`
- `OBSERVACION`
- `OBSERVACIONES`
- Variantes con tildes, mayusculas, minusculas, espacios dobles y signos simples.

## 4. Campos tecnicos generados

La salida normalizada debe contener:

- `id_pieza`
- `tipo_grafica`
- `canal`
- `tienda`
- `imagen_referencial`
- `medidas_original`
- `ancho_cm`
- `alto_cm`
- `logo_samsung`
- `otro_logo`
- `logo_subtel_posicion`
- `legal_posicion`
- `margen_excedente`
- `observaciones`
- `requiere_troquelado`
- `requiere_logo_samsung`
- `requiere_otro_logo`
- `requiere_logo_subtel`
- `requiere_legal`
- `requiere_composicion_especial`

## 5. Validaciones del MVP

El sistema debe registrar en logs y resumen de validaciones:

- Medidas faltantes.
- Medidas invalidas.
- Tienda faltante.
- Observaciones criticas.
- Piezas con troquelado.
- Piezas con composicion especial.
- Encabezados repetidos omitidos.
- Filas vacias omitidas.

## 6. Estructura del proyecto

```text
creative_automation/
|-- README_AUTOMATIZACION_GRAFICA.md
|-- config.yaml
|-- requirements.txt
|-- .env.example
|-- input/
|   |-- matriz_piezas.xlsx
|   `-- .gitkeep
|-- output/
|   |-- piezas_normalizadas.xlsx
|   |-- piezas_normalizadas.csv
|   `-- logs/
|       `-- normalizacion_YYYYMMDD_HHMMSS.log
|-- assets/
|   |-- logos/
|   |-- productos/
|   |-- referencias/
|   `-- fondos/
|-- src/
|   |-- main.py
|   |-- config.py
|   |-- reader.py
|   |-- normalizer.py
|   |-- validators.py
|   |-- exporter.py
|   `-- logger.py
|-- tests/
`-- docs/
```

## 7. Responsabilidades por modulo

### `src/config.py`

Carga configuracion desde `config.yaml` y permite sobreescribir rutas con variables de entorno.

### `src/logger.py`

Configura logging a consola y archivo por ejecucion.

### `src/reader.py`

Lee el Excel con `pandas` y `openpyxl`, sin asumir que el archivo viene perfectamente estructurado.

### `src/normalizer.py`

Normaliza columnas, elimina filas vacias, omite encabezados repetidos, unifica campos equivalentes y construye los campos tecnicos.

### `src/validators.py`

Evalua reglas de calidad de datos y riesgos productivos.

### `src/exporter.py`

Exporta la matriz normalizada a Excel y CSV.

### `src/main.py`

Orquesta la fase 1 completa: configuracion, lectura, normalizacion, validacion, exportacion y resumen.

## 8. Configuracion

El archivo `config.yaml` define rutas, columnas esperadas, sinonimos, reglas de deteccion y nombres de salida.

No deben quedar rutas quemadas en el codigo. Las rutas pueden cambiarse desde `config.yaml` o variables de entorno documentadas en `.env.example`.

## 9. Salidas esperadas

La fase 1 genera:

```text
output/piezas_normalizadas.xlsx
output/piezas_normalizadas.csv
output/logs/normalizacion_YYYYMMDD_HHMMSS.log
```

## 10. Comandos de uso

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar normalizacion:

```bash
python src/main.py
```

Usar un Excel especifico:

```bash
python src/main.py --input input/matriz_piezas.xlsx
```

Usar una configuracion especifica:

```bash
python src/main.py --config config.yaml
```

## 11. Preparacion para fases futuras

La salida normalizada sera la entrada para etapas posteriores:

- Mapeo contra templates graficos.
- Validacion de assets locales o cloud.
- Render HTML/CSS.
- Automatizacion Illustrator o Photoshop.
- Integracion Adobe API.
- Azure Blob Storage.
- SQL Server.
- Aplicacion web para carga, revision y aprobacion.

## 12. Registro de cambios

### 2026-04-27

- Se redefine el MVP como Fase 1 de normalizacion de matrices Excel de produccion grafica.
- Se documentan columnas base, variantes esperadas, campos tecnicos de salida y validaciones requeridas.
- Se establece nueva estructura modular en `src/` separando configuracion, lectura, normalizacion, validacion, exportacion y logging.
- Se declara que esta fase no genera piezas graficas finales y queda preparada para integraciones futuras con Illustrator, Photoshop, HTML/CSS renderer o Adobe API.

### 2026-04-27

- Se preparo el proyecto para control de versiones con Git.
- Se definio una politica inicial de versionado: incluir codigo fuente, configuracion, documentacion, templates y datos de ejemplo; excluir logs, piezas generadas, caches y entornos locales.
- Se agrego `.gitignore` para evitar subir artefactos de ejecucion y archivos temporales.

### 2026-04-27

- Se identifico la carpeta real de insumos `C:\Users\roberto.ballestas\Desktop\grafic` como fuente de trabajo externa.
- Se clasificaron los PDFs como referencias visuales objetivo de salida y la carpeta `KVS` como fuente base para armado futuro de piezas finales.
- Se detecto que el Excel real contiene secciones `GRAFICAS CARRIER` y `GRAFICAS DE RETAIL`, encabezados repetidos y cambios de nombres como `MARGEN`, `EXCEDENTE`, `OBSERVACIONES` y `OBSERVACION`.
- Se define que la Fase 1 debe normalizar ese Excel real preservando el canal por seccion antes de cualquier automatizacion grafica final.

### 2026-04-27

- Se habilita una Fase 2 experimental para generar previews comparativos desde la matriz normalizada y los JPG base de `KVS`.
- Los previews no son artes finales ni reemplazan Illustrator/Photoshop; sirven para validar aproximacion visual contra los PDFs de ejemplo.
- Se define seleccion automatica de KV horizontal o vertical segun proporcion de la pieza.
- Se limita la resolucion de salida para evitar procesar archivos gigantes de impresion durante pruebas locales.

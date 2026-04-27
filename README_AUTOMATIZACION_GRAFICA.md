# Cheil Creative Automation Platform - Automatizacion de Produccion Grafica

## 1. Proposito del proyecto

Cheil Creative Automation Platform busca industrializar la produccion de piezas graficas a partir de templates preparados por disenadores, datos estructurados y assets locales. El objetivo es reducir trabajo manual repetitivo, disminuir errores operativos y dejar una base tecnica mantenible que pueda crecer hacia integraciones con Adobe, almacenamiento cloud, bases de datos y una futura aplicacion web.

El primer MVP se enfoca en un flujo confiable y trazable:

1. Leer un archivo de entrada CSV o Excel.
2. Validar campos obligatorios por pieza.
3. Validar existencia de templates y assets.
4. Reemplazar placeholders en el template.
5. Generar una salida organizada por ejecucion.
6. Registrar logs, errores y resumen de procesamiento.

## 2. Flujo funcional esperado

1. El disenador crea un template base en la carpeta `templates/`.
2. El equipo define campos dinamicos como `nombre_producto`, `precio`, `promocion`, `disclaimer`, `cta`, `logo`, `imagen_principal`, `fondo` y `formato_salida`.
3. El usuario completa un archivo de entrada en `data/` con una fila por pieza.
4. El sistema lee la informacion del archivo.
5. El sistema valida que los campos obligatorios esten presentes.
6. El sistema valida que existan los assets indicados.
7. El sistema procesa el template con los datos de cada pieza.
8. El sistema genera los archivos finales.
9. El sistema exporta los resultados en una carpeta ordenada.
10. El sistema registra logs de ejecucion, advertencias y errores.

## 3. Alcance del MVP

### Incluido

- Lectura de archivos `.csv`, `.xlsx` y `.xls`.
- Configuracion central en `config/settings.json`.
- Configuracion de templates en `config/templates_config.json`.
- Validacion previa de datos, templates y assets.
- Procesamiento de templates con Jinja2.
- Generacion inicial de salidas `.svg`, `.html` y raster basico con Pillow para `.png`/`.jpg`.
- Carpeta de salida por ejecucion con timestamp.
- Logs en archivo y consola.
- Resumen final de piezas exitosas y fallidas.
- Separacion entre entrada, configuracion, validacion, templates, generacion y salida.

### No incluido todavia

- Renderizado fiel de SVG/HTML a imagen final mediante motor dedicado.
- Integracion directa con Illustrator, Photoshop o Adobe APIs.
- Azure Blob Storage.
- SQL Server.
- Interfaz web.
- Colaboracion o edicion en tiempo real.

## 4. Principios tecnicos

- Documentar antes de avanzar con implementacion.
- Mantener modulos pequenos y con responsabilidades claras.
- Evitar valores quemados: rutas, formatos, campos y patrones deben vivir en archivos de configuracion cuando corresponda.
- Fallar temprano cuando falten datos criticos.
- Continuar procesando piezas validas aunque una pieza falle.
- Registrar trazabilidad suficiente para auditar una ejecucion.
- Preparar interfaces simples para poder reemplazar generadores locales por integraciones futuras.

## 5. Estructura propuesta del proyecto

```text
Cheil Creative Automation Platform/
|-- README_AUTOMATIZACION_GRAFICA.md
|-- requirements.txt
|-- config/
|   |-- settings.json
|   `-- templates_config.json
|-- data/
|   |-- input_data.csv
|   `-- sample_data.json
|-- assets/
|   |-- images/
|   |-- fonts/
|   `-- colors/
|-- templates/
|   |-- banner_template.svg
|   `-- social_post_template.html
|-- scripts/
|   |-- main.py
|   |-- config_manager.py
|   |-- input_handler.py
|   |-- validator.py
|   |-- template_engine.py
|   |-- generator.py
|   `-- output_manager.py
|-- output/
|   |-- generated_pieces/
|   `-- logs/
|-- tests/
|   |-- test_generator.py
|   `-- test_validator.py
`-- docs/
    |-- user_guide.md
    `-- api_reference.md
```

## 6. Responsabilidades por modulo

### `scripts/main.py`

Punto de entrada de la automatizacion. Orquesta configuracion, logging, carga de datos, validaciones, generacion y reporte final.

### `scripts/config_manager.py`

Carga y normaliza configuraciones desde archivos JSON. Centraliza rutas, formatos permitidos, campos obligatorios y parametros de ejecucion.

### `scripts/input_handler.py`

Lee archivos de entrada CSV o Excel y devuelve registros normalizados para el pipeline.

### `scripts/validator.py`

Valida estructura del input, campos obligatorios, existencia de templates, existencia de assets y consistencia basica de cada pieza antes de generar.

### `scripts/template_engine.py`

Carga templates desde `templates/` y reemplaza placeholders usando Jinja2.

### `scripts/generator.py`

Genera la pieza final segun el formato solicitado. En el MVP puede guardar contenido procesado como SVG/HTML o crear una imagen raster basica cuando se solicite PNG/JPG. La clase queda preparada para incorporar renderers especializados despues.

### `scripts/output_manager.py`

Crea carpetas ordenadas por ejecucion, construye nombres de archivo seguros y guarda piezas generadas.

## 7. Configuracion

### `config/settings.json`

Define rutas, formatos soportados, formato por defecto, campos obligatorios globales, campos considerados assets y opciones de logging.

Ejemplo conceptual:

```json
{
  "paths": {
    "input_dir": "data",
    "output_dir": "output/generated_pieces",
    "logs_dir": "output/logs",
    "templates_dir": "templates",
    "assets_dir": "assets"
  },
  "generation": {
    "default_format": "svg",
    "supported_output_formats": ["svg", "html", "png", "jpg", "jpeg"]
  },
  "validation": {
    "required_fields": ["id", "template_name"],
    "asset_fields": ["logo", "imagen_principal", "fondo", "imagen"]
  }
}
```

### `config/templates_config.json`

Define reglas especificas por template: dimensiones, placeholders esperados, campos obligatorios y campos de assets.

## 8. Formato de entrada

El archivo de entrada debe tener una fila por pieza.

Campos minimos:

- `id`: identificador unico de la pieza.
- `template_name`: nombre del archivo de template, por ejemplo `banner_template.svg`.

Campos recomendados:

- `nombre_producto`
- `precio`
- `promocion`
- `disclaimer`
- `cta`
- `logo`
- `imagen_principal`
- `fondo`
- `formato_salida`
- `nombre_archivo`

Tambien se soportan campos heredados del prototipo inicial, como `titulo`, `descripcion`, `imagen` y `color_fondo`.

## 9. Reglas de validacion

Antes de generar una pieza, el sistema debe validar:

- El archivo de entrada existe.
- El archivo de entrada tiene extension soportada.
- Cada registro contiene los campos obligatorios globales.
- El `template_name` existe en `templates/`.
- Los placeholders obligatorios configurados para el template estan disponibles.
- Los assets indicados existen en disco cuando el campo tiene valor.
- El formato de salida solicitado esta soportado.
- El identificador de pieza permite construir un nombre de archivo seguro.

## 10. Logs y trazabilidad

Cada ejecucion genera logs en `output/logs/automation_YYYYMMDD_HHMMSS.log`.

Los logs deben registrar:

- Inicio y fin de ejecucion.
- Archivo de entrada utilizado.
- Carpeta de salida creada.
- Cantidad de registros leidos.
- Piezas generadas correctamente.
- Piezas fallidas y motivo del fallo.
- Errores inesperados con stack trace cuando aplique.

## 11. Estrategia de salida

Cada ejecucion crea una carpeta unica dentro de `output/generated_pieces/` con formato `run_YYYYMMDD_HHMMSS`.

Ejemplo:

```text
output/generated_pieces/run_20260427_093000/
|-- 001_banner_verano.svg
|-- 002_social_post_promocion.html
`-- manifest.json
```

El archivo `manifest.json` resume resultados, rutas de salida, errores y fecha de ejecucion.

## 12. Preparacion para crecimiento futuro

La base debe permitir incorporar sin reescribir todo:

- Renderers para Illustrator, Photoshop, HTML/CSS, SVG avanzado o Adobe API.
- Conectores de almacenamiento como Azure Blob Storage.
- Conectores de datos como SQL Server.
- API backend para exponer la generacion como servicio.
- Interfaz web para cargar datos, seleccionar templates y monitorear ejecuciones.
- Sistema de colas para procesamiento masivo.
- Validaciones por marca, cliente, campana o formato.

## 13. Comandos de uso

Validar sin generar:

```bash
python scripts/main.py --input data/input_data.csv --validate-only
```

Generar piezas:

```bash
python scripts/main.py --input data/input_data.csv
```

Indicar salida manual:

```bash
python scripts/main.py --input data/input_data.csv --output output/generated_pieces
```

## 14. Registro de cambios

### 2026-04-27

- Se corrigio la codificacion del documento maestro para evitar caracteres corruptos.
- Se redefinio el README como documento rector del MVP.
- Se establecieron reglas obligatorias de arquitectura, validacion, configuracion, logging y crecimiento futuro.
- Se propuso una estructura modular alineada con una base profesional y escalable.

### 2026-04-27

- Se preparo el proyecto para control de versiones con Git.
- Se definio una politica inicial de versionado: incluir codigo fuente, configuracion, documentacion, templates y datos de ejemplo; excluir logs, piezas generadas, caches y entornos locales.
- Se agrego `.gitignore` para evitar subir artefactos de ejecucion y archivos temporales.

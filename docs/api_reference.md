# Referencia de API

## `ConfigManager`

Carga `config/settings.json` y `config/templates_config.json`, valida secciones minimas y expone rutas normalizadas del proyecto.

## `InputHandler`

Lee archivos CSV o Excel y devuelve una lista de registros normalizados.

## `Validator`

Valida dataset completo, campos obligatorios, templates, formatos de salida y existencia de assets.

## `TemplateEngine`

Carga templates desde `templates/` y procesa placeholders con Jinja2.

## `Generator`

Genera el payload final. En el MVP guarda SVG/HTML procesado y puede crear una previsualizacion raster basica para PNG/JPG.

## `OutputManager`

Crea carpetas por ejecucion, guarda piezas y escribe `manifest.json`.

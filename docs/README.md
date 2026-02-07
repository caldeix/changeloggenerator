# Changelogger - Documentación Técnica

## Overview

Changelogger es una herramienta CLI para generar changelogs automáticos desde repositorios Git. Esta documentación describe la arquitectura del sistema, módulos y flujo de trabajo.

## Arquitectura del Sistema

### Estructura de Módulos

```
src/changelogger/
├── __init__.py           # Definición de versión
├── __main__.py          # Punto de entrada principal
├── git_operations.py    # Operaciones Git
├── ui_interface.py      # Interfaz de usuario TUI
├── file_operations.py  # Operaciones de archivos
├── markdown_formatter.py # Formato Markdown
└── utils.py             # Utilidades generales
```

### Flujo de Trabajo

1. **Detección de repositorio** - `git_operations.detect_repository()`
2. **Listado de commits** - `git_operations.list_recent_commits()`
3. **Selección interactiva** - `ui_interface.select_commit()`
4. **Confirmación** - `ui_interface.confirm_action()`
5. **Generación de diff** - `file_operations.generate_diff()`
6. **Procesamiento de archivos** - `git_operations.analyze_changes()`
7. **Formateo Markdown** - `markdown_formatter.format_changelog()`
8. **Escritura de archivos** - `file_operations.write_output()`

## Módulos Detallados

### git_operations.py
Responsable de toda la interacción con GitPython:
- Detección y validación de repositorios
- Obtención de commits y análisis de cambios
- Clasificación de archivos por estado
- Generación de diffs

### ui_interface.py
Maneja toda la interacción con el usuario:
- Diálogos TUI con prompt_toolkit
- Paginación y navegación de commits
- Confirmaciones y validaciones de input
- Fallback a modo texto cuando no hay TTY

### file_operations.py
Operaciones de sistema de archivos:
- Creación de estructura de directorios
- Generación y escritura de archivos diff
- Gestión de rutas y nombres de archivo
- Operaciones I/O con codificación UTF-8

### markdown_formatter.py
Formateo y generación de contenido Markdown:
- Estructuración del changelog
- Formato de fechas y metadatos
- Listas de archivos afectados
- Detalles por commit

### utils.py
Funciones utilitarias reutilizables:
- Validación de dependencias
- Formato de texto (slugify)
- Utilidades de consola
- Funciones de ayuda

## Dependencias

- **GitPython**: Interacción con repositorios Git
- **prompt_toolkit**: Interfaz de usuario TUI moderna
- **datetime**: Manejo de fechas y timestamps
- **re**: Expresiones regulares para slugify
- **os**: Operaciones de sistema de archivos

## Configuración

La herramienta se configura principalmente a través de:
- Constantes definidas en cada módulo
- Parámetros por defecto en funciones
- Estructura de directorios `.changelogger/`

## Extensibilidad

El diseño modular permite:
- Agregar nuevos formatos de salida
- Modificar la interfaz de usuario
- Extender el análisis de cambios
- Personalizar el formato Markdown

## Testing

Cada módulo está diseñado para ser testeable independientemente:
- Funciones puras sin efectos secundarios
- Inyección de dependencias donde es posible
- Manejo de errores y casos límite
- Fallbacks para entornos sin dependencias opcionales

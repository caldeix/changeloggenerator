# API Reference - Changelogger

## Módulo: git_operations

### Funciones Principales

#### `detect_repository() -> git.Repo`
Detecta y abre el repositorio Git en la ruta actual o directorios padre.

**Returns:** Objeto Repo de GitPython
**Raises:** SystemExit si no se encuentra repositorio

#### `list_recent_commits(repo: git.Repo, max_commits: int = 50) -> List[git.objects.Commit]`
Obtiene los últimos N commits del HEAD.

**Parameters:**
- `repo`: Repositorio Git
- `max_commits`: Número máximo de commits a obtener

**Returns:** Lista de objetos Commit

#### `analyze_commit_changes(repo: git.Repo, commit: git.objects.Commit) -> List[Tuple[str, str]]`
Analiza los archivos cambiados en un commit específico.

**Parameters:**
- `repo`: Repositorio Git
- `commit`: Commit a analizar

**Returns:** Lista de tuplas (tipo_archivo, ruta_archivo)

#### `classify_files_by_status(repo: git.Repo, origin: git.objects.Commit, target: git.objects.Commit) -> Dict[str, List[str]]`
Clasifica archivos afectados por tipo de cambio.

**Parameters:**
- `repo`: Repositorio Git
- `origin`: Commit de origen
- `target`: Commit de destino

**Returns:** Diccionario con claves 'creados', 'modificados', 'eliminados'

#### `get_commits_in_range(repo: git.Repo, origin: git.objects.Commit, target: git.objects.Commit) -> List[git.objects.Commit]`
Obtiene commits entre dos puntos (inclusive).

**Parameters:**
- `repo`: Repositorio Git
- `origin`: Commit de origen (inclusive)
- `target`: Commit de destino (inclusive)

**Returns:** Lista ordenada de commits

#### `generate_diff(repo: git.Repo, origin: git.objects.Commit, target: git.objects.Commit) -> str`
Genera el diff completo entre dos commits.

**Parameters:**
- `repo`: Repositorio Git
- `origin`: Commit de origen
- `target`: Commit de destino

**Returns:** String con el diff en formato Git

## Módulo: ui_interface

### Funciones Principales

#### `select_commit(commits: List[git.objects.Commit], per_page: int = 10) -> int`
Interfaz TUI para seleccionar un commit de la lista.

**Parameters:**
- `commits`: Lista de commits disponibles
- `per_page`: Commits por página

**Returns:** Índice del commit seleccionado
**Raises:** SystemExit si el usuario cancela

#### `confirm_action(question: str) -> bool`
Diálogo de confirmación Sí/No con TUI.

**Parameters:**
- `question`: Pregunta a mostrar al usuario

**Returns:** True si confirma, False si cancela

#### `paginate_commits_fallback(commits: List[git.objects.Commit], per_page: int = 10) -> int`
Fallback modo texto para selección de commits.

**Parameters:**
- `commits`: Lista de commits
- `per_page`: Commits por página

**Returns:** Índice del commit seleccionado

#### `get_numeric_input(prompt: str, min_val: int, max_val: int) -> int`
Obtiene y valida input numérico del usuario.

**Parameters:**
- `prompt`: Mensaje a mostrar
- `min_val`: Valor mínimo aceptado
- `max_val`: Valor máximo aceptado

**Returns:** Entero validado

## Módulo: file_operations

### Funciones Principales

#### `ensure_output_structure(base_path: str) -> Tuple[str, str]`
Crea estructura de directorios .changelogger.

**Parameters:**
- `base_path`: Ruta base del repositorio

**Returns:** Tupla (diff_dir, md_dir) con rutas absolutas

#### `write_diff_file(diff_path: str, content: str) -> None`
Escribe archivo diff con codificación UTF-8.

**Parameters:**
- `diff_path`: Ruta del archivo a crear
- `content`: Contenido del diff

#### `write_markdown_file(md_path: str, content: str) -> None`
Escribe archivo Markdown con codificación UTF-8.

**Parameters:**
- `md_path`: Ruta del archivo a crear
- `content`: Contenido Markdown

#### `generate_filenames(origin_hash: str, target_hash: str, target_message: str, timestamp: str) -> Tuple[str, str]`
Genera nombres de archivo para diff y markdown.

**Parameters:**
- `origin_hash`: Hash del commit origen
- `target_hash`: Hash del commit destino
- `target_message`: Mensaje del commit destino
- `timestamp`: Timestamp formateado YYYYMMDD-HHMM

**Returns:** Tupla (diff_filename, md_filename)

## Módulo: markdown_formatter

### Funciones Principales

#### `format_changelog(origin: git.objects.Commit, target: git.objects.Commit, files_by_status: Dict[str, List[str]], commits: List[git.objects.Commit], files_by_commit: Dict[str, List[Tuple[str, str]]]) -> str`
Genera contenido Markdown completo del changelog.

**Parameters:**
- `origin`: Commit de origen
- `target`: Commit de destino
- `files_by_status`: Diccionario de archivos por estado
- `commits`: Lista de commits en el rango
- `files_by_commit`: Archivos cambiados por commit

**Returns:** String con contenido Markdown

#### `format_file_list(title: str, files: List[str]) -> str`
Formatea lista de archivos en Markdown.

**Parameters:**
- `title`: Título de la sección
- `files`: Lista de archivos

**Returns:** String con formato Markdown

#### `format_commit_info(commit: git.objects.Commit, files: List[Tuple[str, str]]) -> str`
Formatea información de un commit individual.

**Parameters:**
- `commit`: Commit a formatear
- `files`: Lista de archivos cambiados

**Returns:** String con formato Markdown

## Módulo: utils

### Funciones Principales

#### `ensure_gitpython() -> None`
Verifica que GitPython esté instalado.

**Raises:** SystemExit si no está disponible

#### `format_timestamp(timestamp: float) -> str`
Formatea timestamp a formato legible.

**Parameters:**
- `timestamp`: Timestamp Unix

**Returns:** String formato "YYYY-MM-DD HH:MM"

#### `slugify(text: str) -> str`
Convierte texto a slug válido para nombres de archivo.

**Parameters:**
- `text`: Texto a convertir

**Returns:** Slug sanitizado

#### `print_title(text: str) -> None`
Imprime título con separadores para consola.

**Parameters:**
- `text`: Texto del título

## Constantes y Configuración

### Formatos de Fecha
- **Timestamp:** `%Y%m%d-%H%M`
- **Legible:** `%Y-%m-%d %H:%M`

### Límites y Valores por Defecto
- **Commits máximos:** 50
- **Commits por página:** 10
- **Longitud máxima slug:** 80 caracteres
- **Longitud hash:** 7 caracteres

### Estructura de Directorios
```
.changelogger/
├── .diff/     # Archivos diff
└── .md/       # Archivos Markdown
```

## Manejo de Errores

### Excepciones Comunes
- `SystemExit`: Salida controlada del programa
- `RuntimeError`: Dependencias no disponibles
- `git.InvalidGitRepositoryError`: Repositorio no encontrado
- `git.GitCommandError`: Error en comandos Git

### Validaciones
- Verificación de dependencias al inicio
- Validación de inputs numéricos
- Comprobación de rutas de archivos
- Manejo de commits vacíos

## Extensibilidad

### Puntos de Extensión
- **Formatos de salida:** Nuevos formatters además de Markdown
- **Interfaces:** Alternativas a prompt_toolkit
- **Análisis:** Métricas adicionales de commits
- **Integraciones:** Hooks con otros sistemas

### Patrones de Diseño
- **Inyección de dependencias:** Para testing
- **Strategy pattern:** Para diferentes formatos
- **Factory pattern:** Para crear interfaces
- **Observer pattern:** Para eventos del sistema

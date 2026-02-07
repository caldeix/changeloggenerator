![version](https://img.shields.io/badge/version-v3.0.0-yellow.svg) ![python](https://img.shields.io/badge/python-3.9%2B-blue.svg) ![platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg) ![author](https://img.shields.io/badge/author-caldeix-blue.svg)

# changelogger

Herramienta CLI para generar:

- Un archivo `.diff` con todos los cambios entre un commit seleccionado y `HEAD`.
- Un archivo `.md` (Markdown) con un resumen estructurado en español.

Autor: `caldeix`

Última actualización: `2026-02-07`

## Requisitos

- Python `3.9+`
- Git instalado y accesible en el `PATH`
- Acceso a un repositorio Git con commits

## Instalación (modo editable)

Desde la raíz del proyecto (carpeta que contiene `pyproject.toml`):

```bash
python -m pip install -e .
```

Notas (Windows / Python de Microsoft Store):

- `pip` puede instalar en modo usuario y mostrar un aviso de que el directorio `Scripts` no está en `PATH`.
- Si luego **no existe** el comando `changelogger`, revisa la sección **Troubleshooting**.

### Configuración de OpenAI (opcional)
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tu API key
nano .env
```

Añade tu API key de OpenAI al archivo `.env`:
```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
```

## 🤖 Integración con ChatGPT

Cuando se configura una API key de OpenAI, Changelogger añade automáticamente:

1. **Análisis ejecutivo** de los cambios principales
2. **Impacto funcional** detectado
3. **Riesgos potenciales** identificados
4. **Recomendaciones** para testing/despliegue

El análisis se incluye en la sección **"🤖 Información"** del Markdown generado.

## Verificación de instalación

Comprueba que el paquete está instalado:

```bash
python -m pip show changelogger
```

Comprueba si el comando está disponible:

Windows (PowerShell):

```bash
where changelogger
```

Linux/macOS:

```bash
which changelogger
```

Si no aparece, igualmente puedes ejecutar:

```bash
python -m changelogger
```

## Uso (flujo normal)

Ejecuta el comando dentro de un repositorio Git (o una subcarpeta del mismo):

```bash
changelogger
```

Controles (modo interactivo moderno):

- **↑ / ↓**: mover selección
- **← / →**: cambiar de página
- **Enter / Espacio**: seleccionar commit
- **q / Esc**: salir

La herramienta:

- Lista los últimos commits de forma paginada.
- Permite seleccionar un commit de origen por índice.
- Pide confirmación.
- Genera los archivos en la raíz del repo (si no existe, lo crea):
  - `.changelogger/.diff/`
  - `.changelogger/.md/`

## Salida esperada

Al confirmar la generación se crean dos archivos en la raíz del repositorio:

- Diff (texto plano, UTF-8):
  - Carpeta: `.changelogger/.diff/`
  - Nombre: `YYYYMMDD-HHMM_HASHORIGEN-HASHDESTINO.diff`

- Markdown (UTF-8):
  - Carpeta: `.changelogger/.md/`
  - Nombre: `YYYYMMDD-HHMM_slug-del-ultimo-commit.md`

## Test en un repo de ejemplo (opcional)

Si quieres comprobarlo rápido en una carpeta vacía:

```bash
mkdir repo-prueba
cd repo-prueba
git init
echo hola > demo.txt
git add .
git commit -m "feat: commit inicial"
echo mundo >> demo.txt
git add .
git commit -m "fix: ajustar demo"
changelogger
```

Al seleccionar el primer commit como origen, el diff debería contener cambios y se generarán los dos archivos.

## Smoke test (probar que funciona en 2 minutos)

1. Abre una terminal dentro de un repositorio Git que tenga commits.
2. Ejecuta:

   ```bash
   changelogger
   ```

3. En la pantalla de commits:

   - Usa `x` para elegir por índice.
   - Elige un commit que NO sea `HEAD` (para que el diff tenga contenido).
   - Confirma con `s`.

4. Verifica que se han generado archivos:

   - Debe existir la carpeta `.changelogger/`.
   - Debe existir al menos un archivo en:
     - `.changelogger/.diff/`
     - `.changelogger/.md/`

5. Comprueba rápidamente el contenido:

   - El `.diff` debe contener un diff unificado de Git.
   - El `.md` debe contener las secciones:
     - `## Archivos afectados`
     - `## Commits`

## Casos de prueba recomendados

- Ejecutar en una carpeta que **no** es repo Git.
  - Esperado: mensaje de error indicando que no se encontró repositorio.

- Ejecutar en un repo sin commits.
  - Esperado: `No hay commits en este repositorio.`

## Troubleshooting

### El comando `changelogger` no se encuentra

Si `python -m pip install -e .` mostró un aviso del estilo “Scripts is not on PATH”, añade al `PATH` el directorio de scripts de tu instalación de usuario.

En tu caso suele ser algo como:

```text
C:\Users\<tu_usuario>\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.xx_*\LocalCache\local-packages\Python3xx\Scripts
```

Para obtener la ruta exacta de forma automática:

```bash
python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
```

Alternativa inmediata (sin tocar PATH):

```bash
python -m changelogger
```

### Git no está disponible

- Verifica que `git --version` funciona.
- Si no, instala Git y asegúrate de que esté en el `PATH`.


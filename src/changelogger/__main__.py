from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple

try:
    import git
except ModuleNotFoundError:  # pragma: no cover
    git = None  # type: ignore[assignment]


def _asegurar_gitpython() -> None:
    """Verifica que GitPython esté instalado antes de ejecutar lógica que lo requiera."""

    if git is None:
        print(
            "Error: no se ha encontrado la dependencia GitPython. Instala el paquete con 'pip install -e .' o 'pip install GitPython'."
        )
        raise SystemExit(1)


def imprimir_titulo(texto: str) -> None:
    """Imprime un título con separadores para la interfaz de consola."""

    print("=" * 35)
    print(texto)
    print("=" * 35)
    print("")


def obtener_repo_actual() -> git.Repo:
    """Detecta y abre el repositorio Git en la ruta actual o sus directorios padre."""

    _asegurar_gitpython()
    try:
        return git.Repo(os.getcwd(), search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        print(
            "Error: no se ha encontrado un repositorio Git en esta ruta ni en sus padres."
        )
        raise SystemExit(1)


def listar_ultimos_commits(repo: git.Repo, max_commits: int = 50) -> List[git.objects.Commit]:
    """Obtiene los últimos N commits del HEAD."""

    _asegurar_gitpython()
    try:
        return list(repo.iter_commits(max_count=max_commits))
    except git.GitCommandError:
        return []


def _formatear_fecha(commit: git.objects.Commit) -> str:
    return datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d %H:%M")


def _paginar_commits_tui(commits: List[git.objects.Commit], por_pagina: int = 10) -> int:
    """UI interactiva (TUI) para seleccionar un commit con teclas de flecha.

    Controles:
    - Arriba/abajo: mover selección
    - Izquierda/derecha: cambiar de página
    - Enter/Espacio: seleccionar
    - q/Esc: salir
    """

    _asegurar_gitpython()
    try:
        from prompt_toolkit.application import Application
        from prompt_toolkit.formatted_text import FormattedText
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.layout import HSplit, Layout
        from prompt_toolkit.layout.controls import FormattedTextControl
        from prompt_toolkit.layout.dimension import Dimension
        from prompt_toolkit.layout.containers import Window
        from prompt_toolkit.styles import Style
    except ModuleNotFoundError:
        raise RuntimeError("prompt_toolkit no está instalado")

    total = len(commits)
    pagina = 0
    seleccionado_en_pagina = 0
    resultado: List[int] = []

    def _rango_pagina() -> tuple[int, int]:
        inicio = pagina * por_pagina
        fin = min(inicio + por_pagina, total)
        return inicio, fin

    def _titulo() -> str:
        inicio, fin = _rango_pagina()
        paginas_total = max(1, (total + por_pagina - 1) // por_pagina)
        return (
            f"Últimos {total} commits (página {pagina + 1}/{paginas_total})  "
            f"[{inicio}-{fin - 1}]"
        )

    def _render() -> FormattedText:
        inicio, fin = _rango_pagina()
        lineas: List[tuple[str, str]] = []

        lineas.append(("class:title", "=" * 70 + "\n"))
        lineas.append(("class:title", _titulo() + "\n"))
        lineas.append(("class:title", "=" * 70 + "\n\n"))

        for idx, i in enumerate(range(inicio, fin)):
            c = commits[i]
            texto = (
                f"[{i}] {c.hexsha[:7]} | {_formatear_fecha(c)} | {c.author.name} | {c.summary}"
            )
            if idx == seleccionado_en_pagina:
                lineas.append(("class:cursor", "> " + texto + "\n"))
            else:
                lineas.append(("", "  " + texto + "\n"))

        lineas.append(("", "\n"))
        lineas.append(
            (
                "class:help",
                "↑/↓ mover  ←/→ página  Enter/Espacio seleccionar  q/Esc salir\n",
            )
        )
        return FormattedText(lineas)

    control = FormattedTextControl(_render, focusable=True, show_cursor=False)
    window = Window(
        content=control,
        always_hide_cursor=True,
        height=Dimension(min=10),
    )

    kb = KeyBindings()

    @kb.add("up")
    def _up(event) -> None:  # type: ignore[no-untyped-def]
        nonlocal seleccionado_en_pagina
        if seleccionado_en_pagina > 0:
            seleccionado_en_pagina -= 1

    @kb.add("down")
    def _down(event) -> None:  # type: ignore[no-untyped-def]
        nonlocal seleccionado_en_pagina
        inicio, fin = _rango_pagina()
        if inicio + seleccionado_en_pagina + 1 < fin:
            seleccionado_en_pagina += 1

    @kb.add("left")
    def _left(event) -> None:  # type: ignore[no-untyped-def]
        nonlocal pagina, seleccionado_en_pagina
        if pagina > 0:
            pagina -= 1
            seleccionado_en_pagina = 0

    @kb.add("right")
    def _right(event) -> None:  # type: ignore[no-untyped-def]
        nonlocal pagina, seleccionado_en_pagina
        paginas_total = max(1, (total + por_pagina - 1) // por_pagina)
        if pagina + 1 < paginas_total:
            pagina += 1
            seleccionado_en_pagina = 0

    @kb.add("enter")
    @kb.add(" ")
    def _select(event) -> None:  # type: ignore[no-untyped-def]
        inicio, fin = _rango_pagina()
        idx = inicio + seleccionado_en_pagina
        if idx >= fin:
            return
        resultado.append(idx)
        event.app.exit()

    @kb.add("q")
    @kb.add("escape")
    def _quit(event) -> None:  # type: ignore[no-untyped-def]
        event.app.exit()

    style = Style.from_dict(
        {
            "title": "bold",
            "cursor": "reverse",
            "help": "italic",
        }
    )

    app = Application(
        layout=Layout(HSplit([window]), focused_element=window),
        key_bindings=kb,
        style=style,
        full_screen=True,
    )

    app.run()

    if not resultado:
        print("Saliendo.")
        raise SystemExit(0)

    return resultado[0]


def confirmar_si_no(pregunta: str) -> bool:
    """Pide confirmación Sí/No.

    Si hay TTY y prompt_toolkit está disponible, muestra una UI interactiva.
    En caso contrario, usa input clásico (s/n).
    """

    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            from prompt_toolkit.shortcuts import radiolist_dialog
        except ModuleNotFoundError:
            radiolist_dialog = None  # type: ignore[assignment]

        if radiolist_dialog is not None:
            resultado = radiolist_dialog(
                title="Confirmación",
                text=pregunta,
                values=[(True, "Sí"), (False, "No")],
            ).run()

            if resultado is None:
                return False

            return bool(resultado)

    respuesta = input(f"{pregunta} (s/n): ").strip().lower()
    return respuesta == "s"


def paginar_commits(commits: List[git.objects.Commit], por_pagina: int = 10) -> int:
    """Muestra commits paginados y maneja navegación hasta seleccionar un índice."""

    if not commits:
        print("No hay commits en este repositorio.")
        raise SystemExit(0)

    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            return _paginar_commits_tui(commits, por_pagina=por_pagina)
        except Exception:
            pass

    total = len(commits)
    pagina = 0

    while True:
        inicio = pagina * por_pagina
        fin = min(inicio + por_pagina, total)

        imprimir_titulo(f"Últimos {total} commits (página {pagina + 1})")

        for i in range(inicio, fin):
            c = commits[i]
            print(
                f"[{i}] {c.hexsha[:7]} | {_formatear_fecha(c)} | {c.author.name} | {c.summary}"
            )

        print("")
        print("Opciones:")
        print("  n - siguiente página")
        print("  p - página anterior")
        print("  x - elegir commit por índice")
        print("  q - salir")
        print("")

        opcion = input("Selecciona opción (n/p/x/q): ").strip().lower()

        if opcion == "n":
            if fin >= total:
                print("Ya estás en la última página.")
            else:
                pagina += 1
            continue

        if opcion == "p":
            if pagina == 0:
                print("Ya estás en la primera página.")
            else:
                pagina -= 1
            continue

        if opcion == "q":
            print("Saliendo.")
            raise SystemExit(0)

        if opcion == "x":
            return pedir_opcion_int(
                f"Introduce índice de commit (0 - {total - 1}): ", 0, total - 1
            )

        print("Opción no válida.")


def pedir_opcion_int(prompt: str, minimo: int, maximo: int) -> int:
    """Pide input numérico al usuario con validación."""

    while True:
        valor = input(prompt).strip()
        try:
            n = int(valor)
        except ValueError:
            print(f"Introduce un número entre {minimo} y {maximo}.")
            continue

        if n < minimo or n > maximo:
            print(f"El valor debe estar entre {minimo} y {maximo}.")
            continue

        return n


def slugify(texto: str) -> str:
    """Convierte texto en slug válido para nombres de archivo."""

    texto = texto.strip().lower()

    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
        "ü": "u",
    }

    for origen, destino in reemplazos.items():
        texto = texto.replace(origen, destino)

    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    texto = re.sub(r"-+", "-", texto).strip("-")

    if not texto:
        return "sin-mensaje"

    return texto[:80]


def asegurar_directorios(base: str) -> Tuple[str, str]:
    """Crea la estructura de salida en .changelogger y retorna rutas diff/md."""

    root = os.path.join(base, ".changelogger")
    diff_dir = os.path.join(root, ".diff")
    md_dir = os.path.join(root, ".md")

    os.makedirs(diff_dir, exist_ok=True)
    os.makedirs(md_dir, exist_ok=True)

    return diff_dir, md_dir


def generar_diff_rango(
    repo: git.Repo, commit_origen: git.objects.Commit, commit_destino: git.objects.Commit
) -> str:
    """Genera el texto diff completo entre dos commits."""

    _asegurar_gitpython()
    return repo.git.diff(f"{commit_origen.hexsha}..{commit_destino.hexsha}")


def clasificar_archivos_por_estado(
    repo: git.Repo, commit_origen: git.objects.Commit, commit_destino: git.objects.Commit
) -> Dict[str, List[str]]:
    """Clasifica archivos afectados por tipo de cambio: creados/modificados/eliminados."""

    _asegurar_gitpython()
    creados: set[str] = set()
    modificados: set[str] = set()
    eliminados: set[str] = set()

    for d in commit_destino.diff(commit_origen):
        if d.change_type == "A":
            if d.b_path:
                creados.add(d.b_path)
        elif d.change_type == "M":
            if d.b_path:
                modificados.add(d.b_path)
        elif d.change_type == "D":
            if d.a_path:
                eliminados.add(d.a_path)
        else:
            path = d.b_path or d.a_path
            if path:
                modificados.add(path)

    return {
        "creados": sorted(creados),
        "modificados": sorted(modificados),
        "eliminados": sorted(eliminados),
    }


def obtener_commits_en_rango(
    repo: git.Repo, commit_origen: git.objects.Commit, commit_destino: git.objects.Commit
) -> List[git.objects.Commit]:
    """Obtiene lista de commits entre origen (inclusivo) y destino (inclusivo)."""

    _asegurar_gitpython()
    commits = list(repo.iter_commits(f"{commit_origen.hexsha}..{commit_destino.hexsha}"))
    if not commits or commits[-1].hexsha != commit_origen.hexsha:
        commits.append(commit_origen)
    return commits


def _normalizar_estado_archivo(codigo_estado: str) -> str:
    """Convierte el código de estado de Git (A/M/D/...) a un tipo en español."""

    if codigo_estado.startswith("A"):
        return "Creado"
    if codigo_estado.startswith("D"):
        return "Eliminado"
    return "Modificado"


def obtener_archivos_por_commit(
    repo: git.Repo, commit: git.objects.Commit
) -> List[Tuple[str, str]]:
    """Obtiene los archivos implicados en un commit con su tipo (Creado/Modificado/Eliminado)."""

    _asegurar_gitpython()

    salida = repo.git.show(commit.hexsha, "--name-status", "--pretty=format:")
    cambios: List[Tuple[str, str]] = []

    for linea in salida.splitlines():
        linea = linea.strip()
        if not linea:
            continue

        partes = linea.split("\t")
        estado = partes[0]
        tipo = _normalizar_estado_archivo(estado)

        path = ""
        if estado.startswith("R") or estado.startswith("C"):
            if len(partes) >= 3:
                path = partes[2]
            elif len(partes) >= 2:
                path = partes[1]
        else:
            if len(partes) >= 2:
                path = partes[1]

        if path:
            cambios.append((tipo, path))

    cambios.sort(key=lambda x: x[1])
    return cambios


def _formatear_lista_archivos(titulo: str, archivos: List[str]) -> str:
    out: List[str] = []
    out.append(f"- **{titulo}**")
    if archivos:
        for a in archivos:
            out.append(f"  - {a}")
    else:
        out.append("  - Ninguno")
    return "\n".join(out)


def formatear_markdown(
    commit_origen: git.objects.Commit,
    commit_destino: git.objects.Commit,
    archivos_por_estado: Dict[str, List[str]],
    commits_rango: List[git.objects.Commit],
    archivos_por_commit: Dict[str, List[Tuple[str, str]]],
) -> str:
    """Genera el contenido Markdown estructurado en español."""

    fecha_destino = _formatear_fecha(commit_destino)

    out: List[str] = []
    out.append(
        f"# Cambios desde {commit_origen.hexsha[:7]} hasta {commit_destino.hexsha[:7]} ({fecha_destino})"
    )
    out.append("")
    out.append("## Archivos afectados")
    out.append("")

    out.append(_formatear_lista_archivos("Creados", archivos_por_estado.get("creados", [])))
    out.append(_formatear_lista_archivos("Modificados", archivos_por_estado.get("modificados", [])))
    out.append(_formatear_lista_archivos("Eliminados", archivos_por_estado.get("eliminados", [])))
    out.append("")

    out.append("## Commits")
    out.append("")

    for c in reversed(commits_rango):
        out.append(f"- `{c.hexsha[:7]}` | {_formatear_fecha(c)} | {c.author.name}")
        out.append(f"  - Mensaje: {c.summary}")

        archivos_commit = archivos_por_commit.get(c.hexsha, [])
        out.append("  - Archivos:")
        if archivos_commit:
            for tipo, path in archivos_commit:
                out.append(f"    - {tipo}: {path}")
        else:
            out.append("    - Ninguno")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main() -> None:
    """Punto de entrada principal del comando changelogger."""

    _asegurar_gitpython()
    repo = obtener_repo_actual()

    commits = listar_ultimos_commits(repo, max_commits=50)
    if not commits:
        print("No hay commits en este repositorio.")
        raise SystemExit(0)

    indice = paginar_commits(commits, por_pagina=10)

    commit_origen = commits[indice]
    commit_destino = repo.head.commit

    print("")
    print(
        f"Has seleccionado como origen: {commit_origen.hexsha[:7]} - {commit_origen.summary}"
    )
    print(
        f"Destino (HEAD actual): {commit_destino.hexsha[:7]} - {commit_destino.summary}"
    )
    print("")

    if not confirmar_si_no("¿Continuar generando diff y markdown para este rango?"):
        print("Operación cancelada.")
        raise SystemExit(0)

    base_repo = repo.working_tree_dir
    if not base_repo:
        print("Error: no se ha podido determinar la ruta del repositorio.")
        raise SystemExit(1)

    diff_dir, md_dir = asegurar_directorios(base_repo)

    ts = datetime.fromtimestamp(commit_destino.committed_date).strftime("%Y%m%d-%H%M")

    diff_filename = (
        f"{ts}_{commit_origen.hexsha[:7]}-{commit_destino.hexsha[:7]}.diff"
    )
    md_filename = f"{ts}_{slugify(commit_destino.summary)}.md"

    diff_path = os.path.join(diff_dir, diff_filename)
    md_path = os.path.join(md_dir, md_filename)

    diff_texto = generar_diff_rango(repo, commit_origen, commit_destino)
    with open(diff_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(diff_texto)

    archivos_por_estado = clasificar_archivos_por_estado(repo, commit_origen, commit_destino)
    commits_rango = obtener_commits_en_rango(repo, commit_origen, commit_destino)

    archivos_por_commit: Dict[str, List[Tuple[str, str]]] = {}
    for c in commits_rango:
        archivos_por_commit[c.hexsha] = obtener_archivos_por_commit(repo, c)

    markdown = formatear_markdown(
        commit_origen,
        commit_destino,
        archivos_por_estado,
        commits_rango,
        archivos_por_commit,
    )

    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(markdown)

    print("")
    print("Archivos generados:")
    print(f"- Diff: {diff_path}")
    print(f"- Markdown: {md_path}")
    print("")
    print("Ahora puedes pasar el archivo .diff a Claude Code para que te explique los cambios.")


if __name__ == "__main__":
    main()

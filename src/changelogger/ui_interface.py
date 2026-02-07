"""Interfaz de usuario para Changelogger."""

from __future__ import annotations

import sys
from typing import List

try:
    import git
except ModuleNotFoundError:  # pragma: no cover
    git = None  # type: ignore[assignment]

from .utils import ensure_gitpython, format_timestamp, get_numeric_input, is_tty_available, print_title
from .git_operations import format_commit_info


def select_commit_tui(commits: List[git.objects.Commit], per_page: int = 10) -> int:
    """UI interactiva (TUI) para seleccionar un commit con teclas de flecha.

    Usa radiolist_dialog para el mismo estilo visual que la confirmación Sí/No.
    """
    ensure_gitpython()
    try:
        from prompt_toolkit.shortcuts import radiolist_dialog
    except ModuleNotFoundError:
        raise RuntimeError("prompt_toolkit no está instalado")

    total = len(commits)
    paginas_total = max(1, (total + per_page - 1) // per_page)
    pagina = 0

    while True:
        inicio = pagina * per_page
        fin = min(inicio + per_page, total)
        
        # Preparar valores para el diálogo
        valores = []
        for i in range(inicio, fin):
            c = commits[i]
            texto = f"[{i}] {format_commit_info(c)} | {c.summary}"
            valores.append((i, texto))
        
        # Título del diálogo con información de paginación
        titulo = f"Seleccionar commit (página {pagina + 1}/{paginas_total})"
        texto = f"Mostrando commits {inicio}-{fin - 1} de {total} commits totales"
        
        # Mostrar diálogo de selección
        resultado = radiolist_dialog(
            title=titulo,
            text=texto,
            values=valores,
        ).run()
        
        # Si el usuario cancela (Esc), salir
        if resultado is None:
            print("Saliendo.")
            raise SystemExit(0)
        
        # Si el usuario seleccionó un commit, devolver el índice
        if isinstance(resultado, int):
            return resultado
        
        # Navegación de páginas - ciclo simple
        if pagina + 1 >= paginas_total:
            pagina = 0
        else:
            pagina += 1


def select_commit_fallback(commits: List[git.objects.Commit], per_page: int = 10) -> int:
    """Fallback modo texto para selección de commits."""
    if not commits:
        print("No hay commits en este repositorio.")
        raise SystemExit(0)

    total = len(commits)
    pagina = 0

    while True:
        inicio = pagina * per_page
        fin = min(inicio + per_page, total)

        print_title(f"Últimos {total} commits (página {pagina + 1})")

        for i in range(inicio, fin):
            c = commits[i]
            print(f"[{i}] {format_commit_info(c)} | {c.summary}")

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
            return get_numeric_input(
                f"Introduce índice de commit (0 - {total - 1}): ", 0, total - 1
            )

        print("Opción no válida.")


def select_commit(commits: List[git.objects.Commit], per_page: int = 10) -> int:
    """Selecciona un commit usando TUI si está disponible, sino fallback texto."""
    if not commits:
        print("No hay commits en este repositorio.")
        raise SystemExit(0)

    if is_tty_available():
        try:
            return select_commit_tui(commits, per_page=per_page)
        except Exception:
            # Si falla la TUI, usar fallback
            pass

    return select_commit_fallback(commits, per_page=per_page)


def confirm_action(question: str) -> bool:
    """Pide confirmación Sí/No.

    Si hay TTY y prompt_toolkit está disponible, muestra una UI interactiva.
    En caso contrario, usa input clásico (s/n).
    """
    if is_tty_available():
        try:
            from prompt_toolkit.shortcuts import radiolist_dialog
        except ModuleNotFoundError:
            radiolist_dialog = None  # type: ignore[assignment]

        if radiolist_dialog is not None:
            resultado = radiolist_dialog(
                title="Confirmación",
                text=question,
                values=[(True, "Sí"), (False, "No")],
            ).run()

            if resultado is None:
                return False

            return bool(resultado)

    respuesta = input(f"{question} (s/n): ").strip().lower()
    return respuesta == "s"

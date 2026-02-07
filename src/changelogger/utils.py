"""Utilidades generales para Changelogger."""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from typing import List, Tuple

try:
    import git
except ModuleNotFoundError:  # pragma: no cover
    git = None  # type: ignore[assignment]


def ensure_gitpython() -> None:
    """Verifica que GitPython esté instalado antes de ejecutar lógica que lo requiera."""
    if git is None:
        print(
            "Error: no se ha encontrado la dependencia GitPython. "
            "Instala el paquete con 'pip install -e .' o 'pip install GitPython'."
        )
        raise SystemExit(1)


def print_title(text: str) -> None:
    """Imprime un título con separadores para la interfaz de consola."""
    print("=" * 35)
    print(text)
    print("=" * 35)
    print("")


def format_timestamp(timestamp: float) -> str:
    """Formatea timestamp Unix a formato legible."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


def slugify(text: str) -> str:
    """Convierte texto en slug válido para nombres de archivo."""
    text = text.strip().lower()

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
        text = text.replace(origen, destino)

    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")

    if not text:
        return "sin-mensaje"

    return text[:80]


def get_numeric_input(prompt: str, min_val: int, max_val: int) -> int:
    """Pide input numérico al usuario con validación."""
    while True:
        valor = input(prompt).strip()
        try:
            n = int(valor)
        except ValueError:
            print(f"Introduce un número entre {min_val} y {max_val}.")
            continue

        if n < min_val or n > max_val:
            print(f"El valor debe estar entre {min_val} y {max_val}.")
            continue

        return n


def is_tty_available() -> bool:
    """Verifica si hay una terminal TTY disponible para interfaces interactivas."""
    return sys.stdin.isatty() and sys.stdout.isatty()


def ensure_directory_exists(path: str) -> None:
    """Asegura que un directorio exista, creándolo si es necesario."""
    os.makedirs(path, exist_ok=True)


def normalize_file_status(status_code: str) -> str:
    """Convierte el código de estado de Git (A/M/D/...) a un tipo en español."""
    if status_code.startswith("A"):
        return "Creado"
    if status_code.startswith("D"):
        return "Eliminado"
    return "Modificado"

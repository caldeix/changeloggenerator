"""Operaciones de archivos para Changelogger."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Tuple

from .utils import ensure_directory_exists, format_timestamp, slugify


def ensure_output_structure(base_path: str) -> Tuple[str, str]:
    """Crea la estructura de salida en .changelogger y retorna rutas diff/md."""
    root = os.path.join(base_path, ".changelogger")
    diff_dir = os.path.join(root, ".diff")
    md_dir = os.path.join(root, ".md")

    ensure_directory_exists(diff_dir)
    ensure_directory_exists(md_dir)

    return diff_dir, md_dir


def generate_filenames(
    origin_hash: str, target_hash: str, target_message: str, timestamp: datetime
) -> Tuple[str, str]:
    """Genera nombres de archivo para diff y markdown."""
    ts = timestamp.strftime("%Y%m%d-%H%M")
    
    diff_filename = f"{ts}_{origin_hash[:7]}-{target_hash[:7]}.diff"
    md_filename = f"{ts}_{slugify(target_message)}.md"

    return diff_filename, md_filename


def write_diff_file(diff_path: str, content: str) -> None:
    """Escribe archivo diff con codificación UTF-8."""
    with open(diff_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def write_markdown_file(md_path: str, content: str) -> None:
    """Escribe archivo Markdown con codificación UTF-8."""
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def get_repository_working_path(repo) -> str:
    """Obtiene la ruta del directorio de trabajo del repositorio."""
    base_repo = repo.working_tree_dir
    if not base_repo:
        print("Error: no se ha podido determinar la ruta del repositorio.")
        raise SystemExit(1)
    return base_repo


def create_output_files(
    diff_dir: str,
    md_dir: str,
    origin_hash: str,
    target_hash: str,
    target_message: str,
    target_timestamp: datetime,
    diff_content: str,
    markdown_content: str,
) -> Tuple[str, str]:
    """Crea los archivos de salida y retorna sus rutas."""
    diff_filename, md_filename = generate_filenames(
        origin_hash, target_hash, target_message, target_timestamp
    )

    diff_path = os.path.join(diff_dir, diff_filename)
    md_path = os.path.join(md_dir, md_filename)

    write_diff_file(diff_path, diff_content)
    write_markdown_file(md_path, markdown_content)

    return diff_path, md_path


def print_output_summary(diff_path: str, md_path: str) -> None:
    """Imprime resumen de archivos generados."""
    print("")
    print("Archivos generados:")
    print(f"- Diff: {diff_path}")
    print(f"- Markdown: {md_path}")
    print("")
    print("Ahora puedes pasar el archivo .diff a Claude Code para que te explique los cambios.")

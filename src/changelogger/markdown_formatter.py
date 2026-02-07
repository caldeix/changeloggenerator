"""Formateo Markdown para Changelogger."""

from __future__ import annotations

from typing import Dict, List, Tuple

from .utils import format_timestamp


def format_file_list(title: str, files: List[str]) -> str:
    """Formatea lista de archivos en Markdown."""
    out: List[str] = []
    out.append(f"- **{title}**")
    if files:
        for f in files:
            out.append(f"  - {f}")
    else:
        out.append("  - Ninguno")
    return "\n".join(out)


def format_commit_section(commit, files: List[Tuple[str, str]]) -> List[str]:
    """Formatea la sección de un commit individual."""
    lines: List[str] = []
    lines.append(f"- `{commit.hexsha[:7]}` | {format_timestamp(commit.committed_date)} | {commit.author.name}")
    lines.append(f"  - Mensaje: {commit.summary}")
    lines.append("  - Archivos:")
    
    if files:
        for file_type, path in files:
            lines.append(f"    - {file_type}: {path}")
    else:
        lines.append("    - Ninguno")
    
    lines.append("")
    return lines


def format_changelog(
    origin_commit,
    target_commit,
    files_by_status: Dict[str, List[str]],
    commits_in_range: List,
    files_by_commit: Dict[str, List[Tuple[str, str]]],
) -> str:
    """Genera el contenido Markdown estructurado en español."""
    fecha_destino = format_timestamp(target_commit.committed_date)

    out: List[str] = []
    
    # Título principal
    out.append(
        f"# Cambios desde {origin_commit.hexsha[:7]} hasta {target_commit.hexsha[:7]} ({fecha_destino})"
    )
    out.append("")
    
    # Sección de archivos afectados
    out.append("## Archivos afectados")
    out.append("")
    
    out.append(format_file_list("Creados", files_by_status.get("creados", [])))
    out.append(format_file_list("Modificados", files_by_status.get("modificados", [])))
    out.append(format_file_list("Eliminados", files_by_status.get("eliminados", [])))
    out.append("")
    
    # Sección de commits
    out.append("## Commits")
    out.append("")
    
    # Commits en orden cronológico inverso (más reciente primero)
    for commit in reversed(commits_in_range):
        commit_files = files_by_commit.get(commit.hexsha, [])
        commit_lines = format_commit_section(commit, commit_files)
        out.extend(commit_lines)
    
    return "\n".join(out).rstrip() + "\n"


def format_commit_selection_summary(origin_commit, target_commit) -> List[str]:
    """Formatea el resumen de selección de commits."""
    lines: List[str] = []
    lines.append("")
    lines.append(f"Has seleccionado como origen: {origin_commit.hexsha[:7]} - {origin_commit.summary}")
    lines.append(f"Destino (HEAD actual): {target_commit.hexsha[:7]} - {target_commit.summary}")
    lines.append("")
    return lines

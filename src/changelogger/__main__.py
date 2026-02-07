"""Punto de entrada principal para Changelogger."""

from __future__ import annotations

from datetime import datetime

from .file_operations import (
    create_output_files,
    ensure_output_structure,
    get_repository_working_path,
    print_output_summary,
)
from .git_operations import (
    analyze_commit_changes,
    classify_files_by_status,
    detect_repository,
    generate_diff,
    get_commits_in_range,
    list_recent_commits,
)
from .markdown_formatter import format_changelog, format_commit_selection_summary
from .ui_interface import confirm_action, select_commit
from .utils import ensure_gitpython


def main() -> None:
    """Punto de entrada principal del comando changelogger."""
    ensure_gitpython()
    
    # Detectar repositorio y obtener commits
    repo = detect_repository()
    commits = list_recent_commits(repo, max_commits=50)
    
    if not commits:
        print("No hay commits en este repositorio.")
        raise SystemExit(0)

    # Selección interactiva de commit
    indice = select_commit(commits, per_page=10)
    commit_origen = commits[indice]
    commit_destino = repo.head.commit

    # Mostrar resumen de selección
    summary_lines = format_commit_selection_summary(commit_origen, commit_destino)
    print("\n".join(summary_lines))

    # Confirmación del usuario
    if not confirm_action("¿Continuar generando diff y markdown para este rango?"):
        print("Operación cancelada.")
        raise SystemExit(0)

    # Preparar estructura de salida
    base_repo = get_repository_working_path(repo)
    diff_dir, md_dir = ensure_output_structure(base_repo)

    # Generar contenido
    diff_texto = generate_diff(repo, commit_origen, commit_destino)
    archivos_por_estado = classify_files_by_status(repo, commit_origen, commit_destino)
    commits_rango = get_commits_in_range(repo, commit_origen, commit_destino)

    # Analizar archivos por commit
    archivos_por_commit = {}
    for commit in commits_rango:
        archivos_por_commit[commit.hexsha] = analyze_commit_changes(repo, commit)

    # Generar Markdown
    markdown = format_changelog(
        commit_origen,
        commit_destino,
        archivos_por_estado,
        commits_rango,
        archivos_por_commit,
    )

    # Crear archivos de salida
    diff_path, md_path = create_output_files(
        diff_dir,
        md_dir,
        commit_origen.hexsha,
        commit_destino.hexsha,
        commit_destino.summary,
        datetime.fromtimestamp(commit_destino.committed_date),
        diff_texto,
        markdown,
    )

    # Mostrar resumen final
    print_output_summary(diff_path, md_path)


if __name__ == "__main__":
    main()

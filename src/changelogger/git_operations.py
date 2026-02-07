"""Operaciones Git para Changelogger."""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

try:
    import git
except ModuleNotFoundError:  # pragma: no cover
    git = None  # type: ignore[assignment]

from .utils import ensure_gitpython, format_timestamp, normalize_file_status


def detect_repository() -> git.Repo:
    """Detecta y abre el repositorio Git en la ruta actual o sus directorios padre."""
    ensure_gitpython()
    try:
        return git.Repo(os.getcwd(), search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        print(
            "Error: no se ha encontrado un repositorio Git en esta ruta ni en sus padres."
        )
        raise SystemExit(1)


def list_recent_commits(repo: git.Repo, max_commits: int = 50) -> List[git.objects.Commit]:
    """Obtiene los últimos N commits del HEAD."""
    ensure_gitpython()
    try:
        return list(repo.iter_commits(max_count=max_commits))
    except git.GitCommandError:
        return []


def analyze_commit_changes(repo: git.Repo, commit: git.objects.Commit) -> List[Tuple[str, str]]:
    """Obtiene los archivos implicados en un commit con su tipo (Creado/Modificado/Eliminado)."""
    ensure_gitpython()
    
    salida = repo.git.show(commit.hexsha, "--name-status", "--pretty=format:")
    cambios: List[Tuple[str, str]] = []

    for linea in salida.splitlines():
        linea = linea.strip()
        if not linea:
            continue

        partes = linea.split("\t")
        estado = partes[0]
        tipo = normalize_file_status(estado)

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


def classify_files_by_status(
    repo: git.Repo, origin: git.objects.Commit, target: git.objects.Commit
) -> Dict[str, List[str]]:
    """Clasifica archivos afectados por tipo de cambio: creados/modificados/eliminados."""
    ensure_gitpython()
    creados: set[str] = set()
    modificados: set[str] = set()
    eliminados: set[str] = set()

    # Si origin y target son el mismo commit, mostrar los cambios de ese commit
    if origin.hexsha == target.hexsha:
        # Obtener los archivos cambiados en este commit específico
        for d in origin.diff(origin.parents[0] if origin.parents else None):
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
    else:
        # Usar origin.diff(target) para mostrar cambios desde origin hacia target
        # "A" = archivos agregados en target (CREADOS)
        # "D" = archivos eliminados en target (ELIMINADOS)
        diffs = list(origin.diff(target))
        
        for d in diffs:
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


def get_commits_in_range(
    repo: git.Repo, origin: git.objects.Commit, target: git.objects.Commit
) -> List[git.objects.Commit]:
    """Obtiene lista de commits entre origen (inclusivo) y destino (inclusivo)."""
    ensure_gitpython()
    commits = list(repo.iter_commits(f"{origin.hexsha}..{target.hexsha}"))
    if not commits or commits[-1].hexsha != origin.hexsha:
        commits.append(origin)
    return commits


def generate_diff(repo: git.Repo, origin: git.objects.Commit, target: git.objects.Commit) -> str:
    """Genera el texto diff completo entre dos commits."""
    ensure_gitpython()
    return repo.git.diff(f"{origin.hexsha}..{target.hexsha}")


def get_commit_short_hash(commit: git.objects.Commit) -> str:
    """Obtiene el hash corto de un commit (7 caracteres)."""
    return commit.hexsha[:7]


def format_commit_info(commit: git.objects.Commit) -> str:
    """Formatea información básica de un commit."""
    return f"{get_commit_short_hash(commit)} | {format_timestamp(commit.committed_date)} | {commit.author.name}"

"""Integración con ChatGPT para análisis automático de cambios."""

from __future__ import annotations

import os
from typing import Dict, List

try:
    import openai
except ModuleNotFoundError:
    openai = None

from .utils import ensure_gitpython


def load_openai_config() -> tuple[str, str, int]:
    """Carga configuración de OpenAI desde variables de entorno."""
    # Cargar variables de entorno desde .env si existe
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        # Si python-dotenv no está instalado, continuar sin cargar .env
        pass
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "gpt-4")
    max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
    
    return api_key, model, max_tokens


def is_openai_available() -> bool:
    """Verifica si OpenAI está disponible y configurado."""
    if openai is None:
        print("🔍 DEBUG: OpenAI no está instalado")
        return False
    
    api_key, _, _ = load_openai_config()
    if not api_key.strip():
        print("🔍 DEBUG: OPENAI_API_KEY no está configurada")
        return False
    
    print(f"🔍 DEBUG: OpenAI disponible - Model: {load_openai_config()[1]}, Tokens: {load_openai_config()[2]}")
    return True


def analyze_changes_with_gpt(
    diff_content: str, 
    commits_summary: str, 
    files_affected: Dict[str, List[str]]
) -> str:
    """Analiza cambios usando ChatGPT y genera resumen inteligente."""
    
    print("🤖 DEBUG: Iniciando análisis con ChatGPT...")
    print(f"🔍 DEBUG: Longitud del diff: {len(diff_content)} caracteres")
    print(f"🔍 DEBUG: Número de commits: {len(commits_summary.split(chr(10)))}")
    print(f"🔍 DEBUG: Archivos afectados - Creados: {len(files_affected.get('creados', []))}, Modificados: {len(files_affected.get('modificados', []))}, Eliminados: {len(files_affected.get('eliminados', []))}")
    
    if not is_openai_available():
        print("❌ ERROR: OpenAI no configurado. Añade OPENAI_API_KEY a tu archivo .env")
        return "⚠️ OpenAI no configurado. Añade OPENAI_API_KEY a tu archivo .env"
    
    api_key, model, max_tokens = load_openai_config()
    
    try:
        print(f"🔍 DEBUG: Creando cliente OpenAI con modelo {model}")
        client = openai.OpenAI(api_key=api_key)
        
        # Preparar el prompt para el análisis
        prompt = f"""Analiza los siguientes cambios de Git y proporciona un resumen ejecutivo:

COMMITS INVOLUCRADOS:
{commits_summary}

ARCHIVOS AFECTADOS:
- Creados: {len(files_affected.get('creados', []))}
- Modificados: {len(files_affected.get('modificados', []))}
- Eliminados: {len(files_affected.get('eliminados', []))}

DIFF COMPLETO:
{diff_content[:3000]}...

Proporciona un análisis conciso que incluya:
1. Resumen ejecutivo de los cambios principales
2. Impacto funcional (qué funcionalidades se ven afectadas)
3. Riesgos potenciales o áreas críticas modificadas
4. Recomendaciones para testing/despliegue

Responde en español, de forma técnica pero clara. Máximo 300 palabras.
"""
        
        print("🔍 DEBUG: Enviando solicitud a OpenAI...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de código y cambios de software."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ DEBUG: Análisis recibido de OpenAI ({len(result)} caracteres)")
        return result
        
    except Exception as e:
        print(f"❌ ERROR: Excepción al analizar con ChatGPT: {str(e)}")
        return f"❌ Error al analizar con ChatGPT: {str(e)}"


def format_ai_section(ai_analysis: str) -> str:
    """Formatea la sección de análisis de IA en el Markdown."""
    lines = [
        "## 🤖 Información (Análisis con IA)",
        "",
        ai_analysis,
        "",
        "---",
        ""
    ]
    return "\n".join(lines)

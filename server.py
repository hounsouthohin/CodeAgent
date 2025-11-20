"""
Serveur MCP - 2 Super-Outils pour Gemini CLI
Basé sur votre structure qui fonctionne.
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append('/app')

from fastmcp import FastMCP
from utils import Config, setup_logger
from mcp_tools import intelligent_assist, build_project_context

# === Configuration ===
logger = setup_logger(__name__)
mcp = FastMCP(name="CodeAgent-Ollama")

# === Statistiques ===
stats = {
    "code_assists": 0,
    "project_analyses": 0
}

# === Outils MCP ===

@mcp.tool()
def code_assist(
    filepath: str,
    task: str = "fix",
    verify: bool = False,
    use_tools: bool = True
) -> dict:
    """
    🚀 Assistant de code intelligent multi-langage.
    
    **Langages supportés:** Python, JavaScript, TypeScript, React, Java, Go, Rust
    
    **Tâches disponibles:**
    - "fix" : Corriger bugs (recommandé: verify=True)
    - "review" : Code review expert
    - "optimize" : Optimiser performances
    - "explain" : Expliquer le code
    
    Args:
        filepath: Fichier à traiter (ex: "test.py", "App.jsx")
        task: Type de tâche (fix/review/optimize/explain)
        verify: Vérifier avec exécution
        use_tools: Utiliser les 3 outils disponibles
    
    Returns:
        Résultat complet
    
    Examples:
        code_assist("test.py", task="fix", verify=True)
        code_assist("Button.jsx", task="review")
    """
    stats["code_assists"] += 1
    logger.info(f"🤖 Code assist #{stats['code_assists']}: {filepath} | {task}")
    
    result = intelligent_assist(filepath, task, verify, use_tools)
    result["total_assists_today"] = stats["code_assists"]
    
    return result


@mcp.tool()
def analyze_project(
    project_path: str = ".",
    generate_summary: bool = True
) -> dict:
    """
    🚀 Analyse complète d'un projet.
    
    Args:
        project_path: Chemin du projet (défaut: ".")
        generate_summary: Générer résumé IA
    
    Returns:
        Context complet du projet
    
    Examples:
        analyze_project("./my-app")
        analyze_project(".", generate_summary=False)
    """
    stats["project_analyses"] += 1
    logger.info(f"🔍 Project analysis #{stats['project_analyses']}: {project_path}")
    
    result = build_project_context(project_path, generate_summary)
    result["total_analyses_today"] = stats["project_analyses"]
    
    return result


@mcp.tool()
def get_server_stats() -> dict:
    """
    📊 Statistiques d'utilisation du serveur.
    """
    from tools import AVAILABLE_TOOLS
    
    return {
        "status": "✅ Server running",
        "usage_today": {
            "code_assists": stats["code_assists"],
            "project_analyses": stats["project_analyses"],
            "total": stats["code_assists"] + stats["project_analyses"]
        },
        "configuration": {
            "ollama_model": Config.OLLAMA_MODEL,
            "ollama_url": Config.OLLAMA_BASE_URL,
            "cache_enabled": Config.CACHE_ENABLED,
            "code_execution": Config.CODE_EXECUTION_ENABLED
        },
        "tools_available": len(AVAILABLE_TOOLS),
        "cost": "0€ (Ollama local)"
    }


# === Démarrage ===

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Code Agent MCP Server - Powered by Ollama")
    logger.info("=" * 60)
    logger.info(f"   Modèle Ollama: {Config.OLLAMA_MODEL}")
    logger.info(f"   URL Ollama: {Config.OLLAMA_BASE_URL}")
    logger.info(f"   Port MCP: 8080")
    logger.info(f"   Cache activé: {Config.CACHE_ENABLED}")
    logger.info(f"   Exécution code: {Config.CODE_EXECUTION_ENABLED}")
    logger.info("=" * 60)
    
    # Lister les outils disponibles
    from tools import AVAILABLE_TOOLS
    logger.info(f"   Outils internes: {len(AVAILABLE_TOOLS)}")
    for tool_class in AVAILABLE_TOOLS:
        tool_def = tool_class.get_tool_definition()
        logger.info(f"      - {tool_def['name']}")
    
    logger.info("=" * 60)
    logger.info("✅ Serveur prêt!")
    logger.info("=" * 60)
    
    # Démarrer le serveur MCP en mode STDIO
    # C'est le mode standard pour MCP
    mcp.run()
"""
Serveur MCP Code-Assist - Version Finale
Avec boucle infinie pour rester actif
"""
import sys
from pathlib import Path

sys.path.append('/app')

from fastmcp import FastMCP
from utils import Config, setup_logger
from mcp_tools import intelligent_assist, build_project_context

# === Configuration ===
logger = setup_logger(__name__)
mcp = FastMCP(name="CodeAssistMCP")

# === Stats ===
stats = {"code_assists": 0, "project_analyses": 0}

# === OUTILS MCP ===

@mcp.tool()
def code_assist_tool(filepath: str, task: str = "fix", verify: bool = False) -> dict:
    """
    🚀 Assistant de code intelligent multi-langage.
    
    Langages supportés: Python, JavaScript, TypeScript, React, Java, Go, Rust
    
    Tâches disponibles:
    - "fix": Corriger les bugs
    - "review": Code review expert
    - "optimize": Optimiser performances
    - "explain": Expliquer le code
    
    Args:
        filepath: Fichier à traiter (ex: "test.py", "App.jsx")
        task: Type de tâche (fix/review/optimize/explain)
        verify: Vérifier avec exécution (True/False)
    
    Returns:
        Résultat complet avec code corrigé/analysé
    """
    stats["code_assists"] += 1
    logger.info(f"🤖 code_assist called: {filepath} | {task}")
    return intelligent_assist(filepath, task, verify, use_tools=True)

@mcp.tool()
def analyze_project_tool(project_path: str = ".", generate_summary: bool = True) -> dict:
    """
    🔍 Analyse complète d'un projet.
    
    Scanne tout le projet, détecte les langages, trouve les points d'entrée,
    et génère un résumé intelligent avec Ollama.
    
    Args:
        project_path: Chemin du projet (défaut: ".")
        generate_summary: Générer résumé IA (True/False)
    
    Returns:
        Context complet du projet
    """
    stats["project_analyses"] += 1
    logger.info(f"🔍 analyze_project called: {project_path}")
    return build_project_context(project_path, generate_summary)

@mcp.tool()
def get_stats_tool() -> dict:
    """
    📊 Statistiques d'utilisation du serveur.
    
    Returns:
        Statistiques complètes (usage, config, outils)
    """
    from tools import AVAILABLE_TOOLS
    return {
        "status": "✅ Server running",
        "usage": {
            "code_assists": stats["code_assists"],
            "project_analyses": stats["project_analyses"],
            "total": stats["code_assists"] + stats["project_analyses"]
        },
        "config": {
            "model": Config.OLLAMA_MODEL,
            "url": Config.OLLAMA_BASE_URL,
        },
        "tools_available": len(AVAILABLE_TOOLS),
        "cost": "0€ (Ollama local)"
    }

# === Démarrage ===
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Démarrage du serveur MCP Code-Assist (FastMCP 2.13.1 - FINAL NOV 2025)")
    logger.info("=" * 60)
    logger.info(f"   Modèle Ollama : {Config.OLLAMA_MODEL}")
    logger.info(f"   URL Ollama    : {Config.OLLAMA_BASE_URL}")
    logger.info("   Port MCP      : 8080")
    logger.info("   Transport     : HTTP (streamable-http)")
    logger.info("✅ Serveur prêt !")
    logger.info("=" * 60)

    # === MÉTHODE OFFICIELLE QUI MARCHE EN 2.13.1 (20 novembre 2025) ===
    mcp.run(
        transport="http",          # ou "streamable-http" → les deux marchent maintenant
        host="0.0.0.0",
        port=8080,
        path="/mcp"                # optionnel, mais recommandé pour compat Gemini/Cursor
    )
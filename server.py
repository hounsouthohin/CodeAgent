"""
Serveur MCP Code-Assist - Architecture Modulaire
Point d'entrée principal de l'application.
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append('/app')

from fastmcp import FastMCP
from utils import Config, setup_logger
from mcp_tools import (
    analyze_and_fix,
    analyze_and_fix_advanced,
    expert_review,
    expert_review_advanced,
    generate_tests,
    quick_explain,
    list_files
)

# === Configuration ===
logger = setup_logger(__name__)
mcp = FastMCP(name="CodeAssistMCP")

# === Outils MCP ===

@mcp.tool()
def analyze_and_fix_tool(fichier: str) -> dict:
    """
    Analyse et corrige automatiquement un fichier Python (rapide).
    
    Args:
        fichier: Nom du fichier à analyser (ex: "test.py")
    
    Returns:
        Dict avec le statut, le code corrigé et le chemin de sauvegarde
    """
    logger.info(f"analyze_and_fix called for: {fichier}")
    return analyze_and_fix(fichier)

@mcp.tool()
def analyze_and_fix_advanced_tool(fichier: str) -> dict:
    """
    Analyse et corrige avec vérification par outils (précis mais plus lent).
    L'IA peut exécuter et tester le code pour garantir qu'il fonctionne!
    
    Args:
        fichier: Nom du fichier à analyser (ex: "test.py")
    
    Returns:
        Dict avec le statut, le code corrigé vérifié
    """
    logger.info(f"analyze_and_fix_advanced called for: {fichier}")
    return analyze_and_fix_advanced(fichier)

@mcp.tool()
def expert_review_tool(fichier: str) -> dict:
    """
    Code review rapide: bugs, style, performance (rapide).
    
    Args:
        fichier: Nom du fichier à analyser
    
    Returns:
        Dict avec l'analyse complète
    """
    logger.info(f"expert_review called for: {fichier}")
    return expert_review(fichier)

@mcp.tool()
def expert_review_advanced_tool(fichier: str) -> dict:
    """
    Code review approfondie avec analyse statique et tests (précis).
    L'IA utilise des outils d'analyse avancée (radon, bandit, etc.)
    
    Args:
        fichier: Nom du fichier à analyser
    
    Returns:
        Dict avec l'analyse approfondie
    """
    logger.info(f"expert_review_advanced called for: {fichier}")
    return expert_review_advanced(fichier)

@mcp.tool()
def generate_tests_tool(fichier: str) -> dict:
    """
    Génère des tests unitaires complets avec pytest.
    
    Args:
        fichier: Nom du fichier à tester (ex: "main.py")
    
    Returns:
        Dict avec le chemin du fichier de tests et le contenu
    """
    logger.info(f"generate_tests called for: {fichier}")
    return generate_tests(fichier)

@mcp.tool()
def quick_explain_tool(fichier: str) -> dict:
    """
    Explication rapide et concise de ce que fait le code.
    
    Args:
        fichier: Nom du fichier à expliquer
    
    Returns:
        Dict avec l'explication
    """
    logger.info(f"quick_explain called for: {fichier}")
    return quick_explain(fichier)

@mcp.tool()
def list_files_tool(pattern: str = "*.py") -> dict:
    """
    Liste les fichiers dans le projet.
    
    Args:
        pattern: Pattern de recherche (défaut: *.py)
    
    Returns:
        Dict avec la liste des fichiers
    """
    logger.info(f"list_files called with pattern: {pattern}")
    return list_files(pattern)

# === Démarrage ===

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Démarrage du serveur MCP Code-Assist (Modulaire)")
    logger.info("=" * 60)
    logger.info(f"   Modèle Ollama: {Config.OLLAMA_MODEL}")
    logger.info(f"   URL Ollama: {Config.OLLAMA_BASE_URL}")
    logger.info(f"   Port MCP: 8080")
    logger.info(f"   Cache activé: {Config.CACHE_ENABLED}")
    logger.info(f"   Exécution code: {Config.CODE_EXECUTION_ENABLED}")
    logger.info(f"   Recherche web: {Config.WEB_SEARCH_ENABLED}")
    logger.info("=" * 60)
    
    # Lister les outils disponibles
    from tools import AVAILABLE_TOOLS
    logger.info(f"   Outils disponibles pour Ollama: {len(AVAILABLE_TOOLS)}")
    for tool_class in AVAILABLE_TOOLS:
        tool_def = tool_class.get_tool_definition()
        logger.info(f"      - {tool_def['name']}")
    
    logger.info("=" * 60)
    logger.info("✅ Serveur prêt!")
    logger.info("=" * 60)
    
    # Démarrer le serveur MCP
    mcp.run(transport="http", port=8080, host="0.0.0.0")
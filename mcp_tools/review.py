"""
Outil MCP pour code review.
"""
from pathlib import Path
from typing import Dict

import sys
sys.path.append('/app')
from utils.config import Config
from utils.logger import setup_logger
from agents import OllamaAgent, PromptTemplates

logger = setup_logger(__name__)
agent = OllamaAgent()

def expert_review(fichier: str) -> Dict:
    """
    Code review rapide (version simple).
    
    Args:
        fichier: Nom du fichier à analyser
    
    Returns:
        Dict avec l'analyse
    """
    path = Config.APP_PATH / fichier
    if not path.exists():
        return {"error": f"Fichier '{fichier}' non trouvé"}
    
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible de lire le fichier : {e}"}
    
    code_truncated = code[:3000]
    
    prompt = PromptTemplates.CODE_REVIEW_PROMPT.format(code=code_truncated)
    analysis = agent.ask_simple(prompt)
    
    return {
        "fichier": str(path),
        "analyse": analysis,
        "lignes_analysées": len(code.splitlines()),
        "status": "✅ Analyse terminée"
    }

def expert_review_advanced(fichier: str) -> Dict:
    """
    Code review approfondie avec outils (version avancée).
    Ollama peut exécuter et tester le code!
    
    Args:
        fichier: Nom du fichier à analyser
    
    Returns:
        Dict avec l'analyse
    """
    path = Config.APP_PATH / fichier
    if not path.exists():
        return {"error": f"Fichier '{fichier}' non trouvé"}
    
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible de lire le fichier : {e}"}
    
    code_truncated = code[:3000]
    
    prompt = PromptTemplates.CODE_REVIEW_PROMPT.format(code=code_truncated)
    analysis = agent.ask_with_tools(prompt, task_type="review")
    
    return {
        "fichier": str(path),
        "analyse": analysis,
        "lignes_analysées": len(code.splitlines()),
        "status": "✅ Analyse approfondie terminée (avec tests)"
    }
"""
Outil MCP pour analyser et corriger du code AVEC VÉRIFICATION.
"""
from pathlib import Path
from typing import Dict

import sys
sys.path.append('/app')
from utils.config import Config
from utils.logger import setup_logger
from agents import OllamaAgent, PromptTemplates
from agents.code_verify import IterativeFixRunner

logger = setup_logger(__name__)
agent = OllamaAgent()

def clean_code_response(response: str) -> str:
    """Nettoie la réponse pour extraire uniquement le code."""
    response = response.replace("```python", "").replace("```", "").strip()
    return response

def analyze_and_fix(fichier: str) -> Dict:
    """
    Analyse et corrige automatiquement un fichier Python (version simple, rapide).
    
    Args:
        fichier: Nom du fichier à analyser
    
    Returns:
        Dict avec le statut et le code corrigé
    """
    path = Config.APP_PATH / fichier
    if not path.exists():
        return {"error": f"Fichier '{fichier}' non trouvé dans {Config.APP_PATH}"}
    
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible de lire le fichier : {e}"}
    
    code_truncated = code[:Config.MAX_CODE_LENGTH]
    
    # Utiliser l'agent simple (plus rapide, sans outils)
    prompt = PromptTemplates.CODE_FIX_PROMPT.format(code=code_truncated)
    fixed_code = agent.ask_simple(prompt)
    fixed_code = clean_code_response(fixed_code)
    
    if fixed_code.startswith("❌") or fixed_code.startswith("⏱️"):
        return {
            "fichier": str(path),
            "status": "Échec",
            "erreur": fixed_code
        }
    
    # Sauvegarde
    backup_path = path.with_suffix(".py.bak")
    if not backup_path.exists():
        backup_path.write_text(code, encoding="utf-8")
    
    # Écrire le code corrigé
    path.write_text(fixed_code, encoding="utf-8")
    
    return {
        "fichier": str(path),
        "status": "✅ Corrigé par IA",
        "lignes_avant": len(code.splitlines()),
        "lignes_après": len(fixed_code.splitlines()),
        "sauvegarde": str(backup_path),
        "code_corrigé": fixed_code[:500] + "..." if len(fixed_code) > 500 else fixed_code
    }

def analyze_and_fix_advanced(fichier: str) -> Dict:
    """
    Analyse et corrige avec outils ET VÉRIFICATION (version avancée).
    Ollama peut tester et vérifier ses corrections!
    Boucle itérative jusqu'à ce que le code soit correct.
    
    Args:
        fichier: Nom du fichier à analyser
    
    Returns:
        Dict avec le statut, le code corrigé vérifié, et score de qualité
    """
    path = Config.APP_PATH / fichier
    if not path.exists():
        return {"error": f"Fichier '{fichier}' non trouvé dans {Config.APP_PATH}"}
    
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible de lire le fichier : {e}"}
    
    code_truncated = code[:Config.MAX_CODE_LENGTH]
    
    # Utiliser le runner itératif avec vérification
    logger.info(f"Starting advanced fix with verification for {fichier}")
    runner = IterativeFixRunner(agent)
    result = runner.fix_with_verification(code_truncated, task_type="fix")
    
    fixed_code = result['code']
    verification = result['verification']
    
    if not result['success']:
        logger.warning(f"Fix completed with issues. Score: {verification['score']}/100")
    
    # Sauvegarde
    backup_path = path.with_suffix(".py.bak")
    if not backup_path.exists():
        backup_path.write_text(code, encoding="utf-8")
    
    # Écrire le code corrigé
    path.write_text(fixed_code, encoding="utf-8")
    
    # Préparer le statut
    if verification['score'] >= 85:
        status = f"✅ Corrigé et vérifié (score: {verification['score']}/100)"
    elif verification['score'] >= 50:
        status = f"⚠️ Corrigé avec avertissements (score: {verification['score']}/100)"
    else:
        status = f"❌ Correction partielle (score: {verification['score']}/100)"
    
    return {
        "fichier": str(path),
        "status": status,
        "lignes_avant": len(code.splitlines()),
        "lignes_après": len(fixed_code.splitlines()),
        "sauvegarde": str(backup_path),
        "iterations": result['iterations'],
        "verification_score": verification['score'],
        "issues": verification.get('issues', []),
        "syntax_valid": verification['syntax_valid'],
        "can_import": verification['can_import'],
        "code_corrigé": fixed_code[:500] + "..." if len(fixed_code) > 500 else fixed_code
    }
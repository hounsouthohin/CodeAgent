"""
Super-Outil 1: Assistant de code intelligent multi-langage.
Complète Gemini CLI avec exécution et vérification.
"""
from pathlib import Path
from typing import Dict
import sys
sys.path.append('/app')
from utils import Config, setup_logger
from agents import OllamaAgent, PromptTemplates

logger = setup_logger(__name__)

# ============================================================================
# DÉTECTION DE LANGAGE
# ============================================================================

LANGUAGE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'react',
    '.ts': 'typescript',
    '.tsx': 'react-typescript',
    '.java': 'java',
    '.go': 'go',
    '.rs': 'rust',
    '.cpp': 'cpp',
    '.c': 'c',
}

def detect_language(filepath: str) -> str:
    """Détecte le langage du fichier."""
    ext = Path(filepath).suffix.lower()
    return LANGUAGE_MAP.get(ext, 'unknown')

def clean_code_response(response: str) -> str:
    """Nettoie la réponse pour extraire le code."""
    # Enlever les markdown code blocks
    for lang in ['python', 'javascript', 'typescript', 'java', 'go', 'rust']:
        response = response.replace(f"```{lang}", "")
    response = response.replace("```", "").strip()
    return response

# ============================================================================
# ASSISTANT INTELLIGENT
# ============================================================================

def intelligent_assist(
    filepath: str,
    task: str = "fix",
    verify: bool = False,
    use_tools: bool = True
) -> Dict:
    """
    🚀 SUPER-OUTIL 1: Assistant de code intelligent multi-langage.
    
    Ce que Gemini CLI NE PEUT PAS faire:
    - Exécuter du code dans un environnement isolé
    - Utiliser des outils spécialisés (linters, tests, profilers)
    - Accès gratuit illimité à Ollama local
    
    Args:
        filepath: Chemin du fichier (ex: "test.py", "App.jsx")
        task: Type de tâche:
            - "fix": Corriger les bugs
            - "review": Code review expert
            - "optimize": Optimiser performances
            - "explain": Expliquer le code
        verify: Si True, vérifie avec exécution
        use_tools: Si True, utilise les 3 outils disponibles
    
    Returns:
        Dict avec résultat complet
    
    Examples:
        # Corriger bugs Python
        intelligent_assist("test.py", task="fix", verify=True)
        
        # Review React component
        intelligent_assist("Button.jsx", task="review")
        
        # Optimiser code TypeScript
        intelligent_assist("utils.ts", task="optimize")
    """
    path = Config.APP_PATH / filepath
    if not path.exists():
        return {"error": f"❌ File '{filepath}' not found"}
    
    # Détection du langage
    language = detect_language(filepath)
    if language == 'unknown':
        return {"error": f"❌ Language not supported for {filepath}"}
    
    logger.info(f"🔍 Language detected: {language}")
    logger.info(f"🎯 Task: {task}")
    
    # Lire le code
    try:
        code = path.read_text(encoding='utf-8')
    except Exception as e:
        return {"error": f"❌ Cannot read file: {e}"}
    
    # Tronquer si trop long
    code_truncated = code[:Config.MAX_CODE_LENGTH]
    
    # Construire le prompt adapté
    prompt = PromptTemplates.get_language_prompt(language, code_truncated, task)
    
    # Initialiser l'agent
    agent = OllamaAgent()
    
    # Exécuter
    if use_tools:
        logger.info("🔧 Using tools (ReAct mode)")
        result = agent.ask_with_tools(prompt, max_iterations=3)
    else:
        logger.info("⚡ Fast mode (no tools)")
        result = agent.ask_simple(prompt)
    
    # Nettoyer la réponse
    cleaned_result = clean_code_response(result)
    
    # Vérification optionnelle
    verification = None
    if verify and task == "fix":
        logger.info("✅ Verifying with execution...")
        verification = _verify_code(cleaned_result, language)
    
    # Sauvegarder si c'est une correction
    if task in ["fix", "optimize"]:
        # Backup
        backup_path = path.with_suffix(path.suffix + '.bak')
        if not backup_path.exists():
            backup_path.write_text(code, encoding='utf-8')
        
        # Écrire
        path.write_text(cleaned_result, encoding='utf-8')
        
        return {
            "status": "✅ Completed",
            "language": language,
            "task": task,
            "filepath": str(path),
            "backup": str(backup_path),
            "lines_before": len(code.splitlines()),
            "lines_after": len(cleaned_result.splitlines()),
            "verification": verification,
            "tools_used": 3 if use_tools else 0,
            "cost": "0€ (Ollama local)",
            "result": cleaned_result[:500] + "..." if len(cleaned_result) > 500 else cleaned_result
        }
    else:
        # Pour review/explain, pas de sauvegarde
        return {
            "status": "✅ Completed",
            "language": language,
            "task": task,
            "filepath": str(path),
            "result": cleaned_result,
            "cost": "0€ (Ollama local)"
        }

def _verify_code(code: str, language: str) -> Dict:
    """Vérifie le code avec exécution."""
    from agents.tool_executor import ToolExecutor
    
    executor = ToolExecutor()
    
    # 1. Vérifier syntaxe
    syntax_result = executor.execute_tool('check_syntax', {
        'code': code,
        'language': language
    })
    
    # 2. Exécuter si Python/JS
    execution_result = None
    if language in ['python', 'javascript']:
        execution_result = executor.execute_tool('run_code', {
            'code': code,
            'language': language
        })
    
    return {
        'syntax': syntax_result,
        'execution': execution_result
    }
"""
Outils MCP pour génération de tests et explications.
"""
from pathlib import Path
from typing import Dict

import sys
sys.path.append('/app')
from utils.config import Config
from utils.logger import setup_logger
from agents import OllamaAgent

logger = setup_logger(__name__)
agent = OllamaAgent()

def generate_tests(fichier: str) -> Dict:
    """Génère des tests unitaires avec pytest."""
    path = Config.APP_PATH / fichier
    if not path.exists():
        return {"error": f"Fichier '{fichier}' non trouvé"}
    
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible de lire le fichier : {e}"}
    
    code_truncated = code[:4000]
    
    prompt = f"""Generate pytest tests for this code. Return ONLY the test code.

Code:
```python
{code_truncated}
```

Test code:"""
    
    tests = agent.ask_simple(prompt)
    tests = tests.replace("```python", "").replace("```", "").strip()
    
    if tests.startswith("❌"):
        return {"status": "Échec", "erreur": tests}
    
    test_file = path.parent / f"test_{path.name}"
    test_file.write_text(tests, encoding="utf-8")
    
    return {
        "test_file": str(test_file),
        "status": "✅ Tests générés",
        "nombre_lignes": len(tests.splitlines()),
        "tests": tests[:500] + "..." if len(tests) > 500 else tests
    }

def quick_explain(fichier: str) -> Dict:
    """Explication rapide du code."""
    path = Config.APP_PATH / fichier
    if not path.exists():
        return {"error": f"Fichier '{fichier}' non trouvé"}
    
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible de lire le fichier : {e}"}
    
    code_truncated = code[:2000]
    
    prompt = f"""Explain this code in 3-4 sentences. What does it do?

```python
{code_truncated}
```

Explanation:"""
    
    explanation = agent.ask_simple(prompt, max_tokens=500)
    
    return {
        "fichier": str(path),
        "explication": explanation,
        "status": "✅ Explication générée"
    }

def list_files(pattern: str = "*.py") -> Dict:
    """Liste les fichiers dans le projet."""
    try:
        files = list(Config.APP_PATH.glob(pattern))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
        
        return {
            "status": "✅ Fichiers trouvés",
            "nombre": len(files),
            "fichiers": [f.name for f in sorted(files)],
            "chemin": str(Config.APP_PATH)
        }
    except Exception as e:
        return {"error": f"❌ Erreur : {e}"}
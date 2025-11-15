import os
import json
import requests
from pathlib import Path
from typing import Dict
from fastmcp import FastMCP

# === Configuration FastMCP ===
mcp = FastMCP(name="CodeAssistMCP")

# Configuration Ollama avec modèle optimisé
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"
MODEL = "qwen2.5-coder:1.5b"  # ← Modèle rapide et optimisé pour le code

def ask_ollama(prompt: str, max_tokens: int = 2000, timeout: int = 60) -> str:
    """
    Appel à Ollama avec streaming pour éviter les timeouts.
    
    Args:
        prompt: Le prompt à envoyer
        max_tokens: Nombre maximum de tokens à générer
        timeout: Timeout en secondes (par chunk, pas total)
    """
    try:
        # Vérification santé Ollama
        health_check = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags", 
            timeout=5
        )
        health_check.raise_for_status()
        
        # Requête avec streaming
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": True,  # ← Streaming activé
                "options": {
                    "temperature": 0.2,
                    "num_predict": max_tokens,
                    "top_p": 0.9
                }
            },
            stream=True,
            timeout=timeout
        )
        response.raise_for_status()
        
        # Collecter la réponse en streaming
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    full_response += chunk.get("response", "")
                    
                    # Arrêter si la génération est terminée
                    if chunk.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
        
        return full_response.strip() or "Pas de réponse générée"
        
    except requests.exceptions.ConnectionError:
        return "❌ Impossible de se connecter à Ollama. Le service est-il démarré ?"
    except requests.exceptions.Timeout:
        return f"⏱️ Timeout après {timeout}s. Le modèle prend trop de temps."
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"❌ Modèle '{MODEL}' non trouvé. Installez-le : docker-compose exec ollama ollama pull {MODEL}"
        return f"❌ Erreur HTTP {e.response.status_code}: {e}"
    except Exception as e:
        return f"❌ Erreur inattendue : {str(e)}"

def clean_code_response(response: str) -> str:
    """Nettoie la réponse pour extraire uniquement le code."""
    # Supprimer les balises markdown si présentes
    response = response.replace("```python", "").replace("```", "").strip()
    return response

@mcp.tool()
def analyze_and_fix(fichier: str) -> Dict:
    """
    Analyse et corrige automatiquement un fichier Python avec IA locale.
    
    Args:
        fichier: Nom du fichier à analyser (ex: "test.py")
    
    Returns:
        Dict avec le statut, le code corrigé et le chemin de sauvegarde
    """
    path = Path("/app") / fichier
    if not path.exists():
        return {"error": f"Fichier '{fichier}' non trouvé dans /app"}
    
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible de lire le fichier : {e}"}
    
    # Limiter la taille du code pour éviter les timeouts
    code_truncated = code[:5000] if len(code) > 5000 else code
    
    prompt = f"""Fix all bugs in this Python code. Return ONLY the corrected code, no explanations.

Fixes needed:
- Syntax errors
- Missing imports
- Undefined variables
- Logic errors
- Indentation

Code:
```python
{code_truncated}
```

Corrected code:"""
    
    fixed_code = ask_ollama(prompt, max_tokens=3000, timeout=90)
    
    # Nettoyer la réponse
    fixed_code = clean_code_response(fixed_code)
    
    # Vérifier si c'est une erreur
    if fixed_code.startswith("❌") or fixed_code.startswith("⏱️"):
        return {
            "fichier": str(path),
            "status": "Échec",
            "erreur": fixed_code
        }
    
    # Créer une sauvegarde
    backup_path = path.with_suffix(".py.bak")
    if not backup_path.exists():
        try:
            backup_path.write_text(code, encoding="utf-8")
        except Exception as e:
            return {"error": f"Impossible de créer la sauvegarde : {e}"}
    
    # Écrire le code corrigé
    try:
        path.write_text(fixed_code, encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible d'écrire le fichier corrigé : {e}"}
    
    return {
        "fichier": str(path),
        "status": "✅ Corrigé par IA",
        "lignes_avant": len(code.splitlines()),
        "lignes_après": len(fixed_code.splitlines()),
        "sauvegarde": str(backup_path),
        "code_corrigé": fixed_code[:500] + "..." if len(fixed_code) > 500 else fixed_code
    }

@mcp.tool()
def generate_tests(fichier: str) -> Dict:
    """
    Génère des tests unitaires complets avec pytest.
    
    Args:
        fichier: Nom du fichier à tester (ex: "main.py")
    
    Returns:
        Dict avec le chemin du fichier de tests et le contenu
    """
    path = Path("/app") / fichier
    if not path.exists():
        return {"error": f"Fichier '{fichier}' non trouvé"}
    
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible de lire le fichier : {e}"}
    
    code_truncated = code[:4000] if len(code) > 4000 else code
    
    prompt = f"""Generate pytest unit tests for this code. Return ONLY the test code.

Requirements:
- Use pytest fixtures
- Test normal cases
- Test edge cases
- Test error handling
- Use descriptive test names

Code to test:
```python
{code_truncated}
```

Test code:"""
    
    tests = ask_ollama(prompt, max_tokens=2500, timeout=90)
    tests = clean_code_response(tests)
    
    if tests.startswith("❌") or tests.startswith("⏱️"):
        return {
            "status": "Échec",
            "erreur": tests
        }
    
    test_file = path.parent / f"test_{path.name}"
    
    try:
        test_file.write_text(tests, encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible d'écrire les tests : {e}"}
    
    return {
        "test_file": str(test_file),
        "status": "✅ Tests générés",
        "nombre_lignes": len(tests.splitlines()),
        "tests": tests[:500] + "..." if len(tests) > 500 else tests
    }

@mcp.tool()
def expert_review(fichier: str) -> Dict:
    """
    Analyse experte rapide : bugs, style, performance, sécurité.
    
    Args:
        fichier: Nom du fichier à analyser
    
    Returns:
        Dict avec l'analyse complète
    """
    path = Path("/app") / fichier
    if not path.exists():
        return {"error": f"Fichier '{fichier}' non trouvé"}
    
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible de lire le fichier : {e}"}
    
    # Limiter pour analyse rapide
    code_truncated = code[:3000] if len(code) > 3000 else code
    
    prompt = f"""Code review - Be concise:

1. Critical bugs?
2. Security issues?
3. Style problems?
4. Top 3 improvements?

Code:
```python
{code_truncated}
```

Review:"""
    
    analysis = ask_ollama(prompt, max_tokens=1500, timeout=60)
    
    return {
        "fichier": str(path),
        "analyse": analysis,
        "lignes_analysées": len(code.splitlines()),
        "taille_fichier": f"{len(code)} caractères",
        "status": "✅ Analyse terminée" if not analysis.startswith("❌") else "❌ Échec"
    }

@mcp.tool()
def quick_explain(fichier: str) -> Dict:
    """
    Explication rapide et concise de ce que fait le code.
    
    Args:
        fichier: Nom du fichier à expliquer
    
    Returns:
        Dict avec l'explication
    """
    path = Path("/app") / fichier
    if not path.exists():
        return {"error": f"Fichier '{fichier}' non trouvé"}
    
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Impossible de lire le fichier : {e}"}
    
    code_truncated = code[:2000] if len(code) > 2000 else code
    
    prompt = f"""Explain this code in 3-4 sentences. What does it do?

```python
{code_truncated}
```

Explanation:"""
    
    explanation = ask_ollama(prompt, max_tokens=500, timeout=30)
    
    return {
        "fichier": str(path),
        "explication": explanation,
        "status": "✅ Explication générée"
    }

@mcp.tool()
def list_files(pattern: str = "*.py") -> Dict:
    """
    Liste les fichiers Python dans /app.
    
    Args:
        pattern: Pattern de recherche (défaut: *.py)
    
    Returns:
        Dict avec la liste des fichiers
    """
    app_path = Path("/app")
    
    try:
        files = list(app_path.glob(pattern))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
        
        return {
            "status": "✅ Fichiers trouvés",
            "nombre": len(files),
            "fichiers": [f.name for f in sorted(files)],
            "chemin": str(app_path)
        }
    except Exception as e:
        return {"error": f"❌ Erreur : {e}"}

if __name__ == "__main__":
    print(f"🚀 Démarrage du serveur MCP optimisé")
    print(f"   Modèle: {MODEL}")
    print(f"   URL Ollama: {OLLAMA_BASE_URL}")
    print(f"   Port: 8080")
    mcp.run(transport="http", port=8080, host="0.0.0.0")
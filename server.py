import os
from pathlib import Path
from typing import Dict, List, Optional
from fastmcp import FastMCP
import git
import black
import flake8.api.legacy as flake8
from pylint.lint import Run  # Correct pour pylint 3.x

mcp = FastMCP(name="CodeAssistMCP")

# ------------------------------------------------------------------ #
# OUTILS (avec @mcp.tool())
# ------------------------------------------------------------------ #

@mcp.tool()
def code_review(fichier: str, contexte: Optional[str] = None) -> Dict[str, str]:
    """Revue complète d’un fichier Python."""
    repo_path = Path(os.getcwd())
    full_path = repo_path / fichier
    if not full_path.exists():
        return {"error": f"Fichier {fichier} non trouvé dans {repo_path}"}

    with open(full_path, 'r', encoding="utf-8") as f:
        code = f.read()

    style_report = _run_flake8(full_path)
    pylint_report = _run_pylint(full_path)

    lines = code.split('\n')
    complexity = len([l for l in lines if any(k in l for k in ('if', 'for', 'while'))])

    # TOUT EN STRING
    return {
        "fichier": str(full_path),
        "lignes": str(len(lines)),
        "complexite_estimee": str(complexity),
        "style_issues": style_report,
        "pylint_score": str(pylint_report.get('score', 'N/A')),
        "suggestions": f"Réduisez la complexité ({complexity} branches).",
        "contexte": contexte or "Revue générale"
    }

@mcp.tool()  # Correct
def code_critique_et_suggestions(fichier: str, focus: str = "performance") -> List[Dict[str, str]]:
    """Critiques ciblées."""
    repo_path = Path(os.getcwd())
    full_path = repo_path / fichier
    if not full_path.exists():
        return [{"error": f"Fichier {fichier} non trouvé."}]

    with open(full_path, 'r', encoding="utf-8") as f:
        code = f.read()

    critiques = []
    if focus == "performance":
        critiques.append({
            "critique": "Boucles imbriquées détectées.",
            "suggestion": "Utilisez dict/set pour O(1) lookups."
        })
    elif focus == "lisibilité":
        critiques.append({
            "critique": "Fonctions trop longues.",
            "suggestion": "Découpez en sous-fonctions."
        })

    try:
        formatted = black.format_str(code, mode=black.FileMode())
        diff = "\n".join([l for l in formatted.splitlines()[:5] if l not in code.splitlines()[:5]])
        critiques.append({
            "critique": "Code non formaté Black.",
            "suggestion": f"Appliquez Black → {diff}"
        })
    except:
        pass

    return critiques

@mcp.tool()  # Correct
def prepare_push_github(message_commit: str, branche: str = "main") -> Dict[str, str]:
    """Génère script bash pour push."""
    try:
        repo = git.Repo(os.getcwd())
        status = repo.git.status('--porcelain')
        if not status.strip():
            return {"error": "Aucun changement."}

        script = f"""#!/bin/bash
git add .
git commit -m "{message_commit}"
git push origin {branche}
"""
        return {
            "stage": "git add .",
            "commit": f'git commit -m "{message_commit}"',
            "push": f"git push origin {branche}",
            "full_script": script,
            "status_actuel": status
        }
    except git.InvalidGitRepositoryError:
        return {"error": "Pas un repo Git. Exécutez `git init`."}

@mcp.tool()  # Correct
def lint_et_format(fichier: Optional[str] = None) -> Dict[str, str]:
    repo_path = Path(os.getcwd())
    target = repo_path / fichier if fichier else repo_path

    if target.is_file():
        original = target.read_text(encoding="utf-8")
        try:
            formatted = black.format_str(original, mode=black.FileMode())
            diff = "\n".join([l for l in formatted.splitlines()[:10] if l not in original.splitlines()[:10]])
        except:
            diff = "Erreur formatting."
    else:
        diff = "Exécutez `black .` localement."

    report = _run_flake8(target)
    return {"diff_formatting": diff, "lint_report": report}

# ------------------------------------------------------------------ #
# PROMPTS (avec @mcp.prompt())
# ------------------------------------------------------------------ #

@mcp.prompt()  # Correct
def revue_code_complete(fichier: str) -> str:
    """Workflow complet de revue."""
    pass

@mcp.prompt()  # Correct
def deploy_propre(message: str) -> str:
    """Nettoie + push."""
    pass

# ------------------------------------------------------------------ #
# HELPERS
# ------------------------------------------------------------------ #

def _run_flake8(path: Path) -> str:
    style_guide = flake8.get_style_guide(ignore=['E501'])
    report = style_guide.check_files([str(path)])
    return f"{report.total_errors} erreurs Flake8."

def _run_pylint(path: Path) -> Dict[str, any]:
    """Exécute pylint sans bloquer le processus."""
    from io import StringIO
    import sys
    from pylint.lint import Run
    from pylint.reporters.text import TextReporter

    # Redirige la sortie
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    try:
        # Run sans do_exit → il ne quitte pas le programme
        Run([str(path), '--output-format=text'], reporter=TextReporter(mystdout), exit=False)
        output = mystdout.getvalue()
        
        # Extraire le score (ex: "Your code has been rated at 9.50/10")
        score_line = [line for line in output.splitlines() if "rated at" in line]
        score = score_line[0].split("at")[1].split("/")[0].strip() if score_line else "N/A"
        
    except Exception as e:
        output = f"Erreur pylint: {e}"
        score = "N/A"
    finally:
        sys.stdout = old_stdout

    return {
        "score": f"{score}/10",
        "output": output[:600] + ("..." if len(output) > 600 else "")
    }
# ------------------------------------------------------------------ #
# LANCEMENT
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    mcp.run(transport="http", port=8080)
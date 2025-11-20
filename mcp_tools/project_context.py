"""
Super-Outil 2: Analyse complète de projet.
Ce que Gemini CLI fait mal (vision globale).
"""
from pathlib import Path
from typing import Dict, List
import sys
sys.path.append('/app')
from utils import Config, setup_logger
from agents import OllamaAgent, PromptTemplates

logger = setup_logger(__name__)

# ============================================================================
# PROJECT CONTEXT BUILDER
# ============================================================================

def build_project_context(
    project_path: str = ".",
    generate_summary: bool = True
) -> Dict:
    """
    🚀 SUPER-OUTIL 2: Construit le contexte complet d'un projet.
    
    Ce que Gemini CLI FAIT MAL:
    - Vision globale (il ne voit qu'un fichier à la fois)
    - Comprendre l'architecture complète
    - Analyser les dépendances
    
    Cette fonction:
    - Scanne TOUT le projet
    - Détecte langages et frameworks
    - Trouve les points d'entrée
    - Génère un résumé intelligent avec Ollama
    
    Args:
        project_path: Chemin du projet (défaut: ".")
        generate_summary: Générer un résumé IA de l'architecture
    
    Returns:
        Context complet du projet
    
    Examples:
        # Analyser projet Next.js
        build_project_context("./my-nextjs-app")
        
        # Context rapide sans IA
        build_project_context(".", generate_summary=False)
    """
    project = Path(project_path).resolve()
    if not project.exists():
        return {"error": f"❌ Project '{project_path}' not found"}
    
    logger.info(f"🔍 Analyzing project: {project}")
    
    # 1. Scanner avec l'outil
    from agents.tool_executor import ToolExecutor
    executor = ToolExecutor()
    
    scan_result = executor.execute_tool('scan_project', {
        'project_path': str(project)
    })
    
    # 2. Analyser la structure
    structure = _analyze_structure(project)
    
    # 3. Détecter le type de projet
    project_type = _detect_project_type(structure)
    
    # 4. Trouver les points d'entrée
    entry_points = _find_entry_points(structure)
    
    # 5. Générer résumé IA (optionnel)
    ai_summary = None
    if generate_summary:
        ai_summary = _generate_ai_summary(structure, project_type)
    
    return {
        "status": "✅ Context built",
        "project_path": str(project),
        "project_type": project_type,
        "scan_result": scan_result,
        "entry_points": entry_points,
        "structure": structure,
        "ai_summary": ai_summary,
        "cost": "0€ (Ollama local)"
    }

def _analyze_structure(project: Path) -> Dict:
    """Analyse la structure du projet."""
    IGNORE_DIRS = {
        'node_modules', '__pycache__', '.git', 'venv', 'env',
        'dist', 'build', '.next', '.vscode', 'target'
    }
    
    files = []
    languages = {}
    directories = set()
    
    for file in project.rglob('*'):
        # Ignorer
        if any(ignored in file.parts for ignored in IGNORE_DIRS):
            continue
        
        if file.is_file():
            rel_path = str(file.relative_to(project))
            files.append(rel_path)
            
            # Langage
            ext = file.suffix
            if ext:
                lang = _ext_to_language(ext)
                languages[lang] = languages.get(lang, 0) + 1
            
            # Dossiers
            parts = Path(rel_path).parts
            if len(parts) > 1:
                directories.add(parts[0])
    
    return {
        'total_files': len(files),
        'files_sample': files[:20],  # 20 premiers fichiers
        'languages': languages,
        'directories': sorted(directories)
    }

def _ext_to_language(ext: str) -> str:
    """Convertit extension en langage."""
    map_lang = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'React',
        '.ts': 'TypeScript',
        '.tsx': 'React',
        '.java': 'Java',
        '.go': 'Go',
        '.rs': 'Rust',
        '.cpp': 'C++',
        '.c': 'C',
        '.html': 'HTML',
        '.css': 'CSS',
        '.json': 'JSON',
        '.md': 'Markdown'
    }
    return map_lang.get(ext, f'Other ({ext})')

def _detect_project_type(structure: Dict) -> str:
    """Détecte le type de projet."""
    files = structure['files_sample']
    languages = structure['languages']
    
    # Next.js
    if 'next.config.js' in files or 'next.config.ts' in files:
        return "Next.js Application"
    
    # React
    if any('React' in lang for lang in languages.keys()):
        return "React Application"
    
    # Python
    if 'Python' in languages:
        if 'requirements.txt' in files or 'pyproject.toml' in files:
            if 'app.py' in files or 'main.py' in files:
                return "Python Web Application"
            return "Python Project"
    
    # Node.js
    if 'package.json' in files:
        return "Node.js Project"
    
    # Java
    if 'Java' in languages:
        if 'pom.xml' in files:
            return "Java Maven Project"
        if 'build.gradle' in files:
            return "Java Gradle Project"
        return "Java Project"
    
    return "Unknown Project Type"

def _find_entry_points(structure: Dict) -> List[str]:
    """Trouve les points d'entrée."""
    files = structure['files_sample']
    
    entry_patterns = [
        'main.py', 'app.py', '__main__.py',
        'index.js', 'index.ts', 'main.js',
        'server.py', 'server.js',
        'Main.java', 'main.go', 'main.rs',
        'pages/index.tsx', 'src/index.tsx'
    ]
    
    entry_points = []
    for file in files:
        if any(pattern in file for pattern in entry_patterns):
            entry_points.append(file)
    
    return entry_points[:5]  # Max 5

def _generate_ai_summary(structure: Dict, project_type: str) -> str:
    """Génère un résumé avec Ollama."""
    try:
        agent = OllamaAgent()
        
        prompt = PromptTemplates.PROJECT_ANALYSIS_PROMPT.format(
            file_count=structure['total_files'],
            languages=', '.join(structure['languages'].keys()),
            directories=', '.join(structure['directories'][:5]),
            files_sample='\n'.join(structure['files_sample'][:10])
        )
        
        prompt = f"Project Type: {project_type}\n\n{prompt}"
        
        summary = agent.ask_simple(prompt)
        return summary
    except Exception as e:
        logger.error(f"AI summary generation failed: {e}")
        return "AI summary generation failed"
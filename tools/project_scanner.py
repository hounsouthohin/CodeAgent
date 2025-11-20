"""
Outil de scan et analyse de projet complet.
"""
from pathlib import Path
from typing import Dict
from .base_tool import BaseTool
import sys
sys.path.append('/app')
from utils import setup_logger

logger = setup_logger(__name__)

class ProjectScannerTool(BaseTool):
    """Scanne un projet complet."""
    
    IGNORE_DIRS = {
        'node_modules', '__pycache__', '.git', 'venv', 'env',
        'dist', 'build', '.next', '.vscode', 'target', 'bin'
    }
    
    @staticmethod
    def get_tool_definition() -> Dict:
        return {
            'name': 'scan_project',
            'description': 'Scan entire project structure and analyze files',
            'parameters': {
                'project_path': 'Path to project root (default: ".")'
            }
        }
    
    @staticmethod
    def execute(project_path: str = '.') -> str:
        """
        Scanne un projet complet.
        
        Args:
            project_path: Chemin du projet
            
        Returns:
            Résumé du projet
        """
        try:
            project = Path(project_path).resolve()
            if not project.exists():
                return f"❌ Project path '{project_path}' not found"
            
            logger.info(f"🔍 Scanning project: {project}")
            
            # Scan des fichiers
            files = []
            for file in project.rglob('*'):
                # Ignorer certains dossiers
                if any(ignored in file.parts for ignored in ProjectScannerTool.IGNORE_DIRS):
                    continue
                
                if file.is_file():
                    files.append({
                        'path': str(file.relative_to(project)),
                        'size': file.stat().st_size,
                        'ext': file.suffix
                    })
            
            # Analyser
            total_files = len(files)
            total_size = sum(f['size'] for f in files)
            
            # Extensions
            extensions = {}
            for f in files:
                ext = f['ext'] or 'no_ext'
                extensions[ext] = extensions.get(ext, 0) + 1
            
            # Top extensions
            top_exts = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Dossiers principaux
            top_dirs = set()
            for f in files:
                parts = Path(f['path']).parts
                if len(parts) > 1:
                    top_dirs.add(parts[0])
            
            # Résumé
            summary = f"""✅ Project scan complete

📊 Statistics:
- Total files: {total_files}
- Total size: {total_size / 1024:.1f} KB
- Directories: {len(top_dirs)}

📁 Top file types:
{chr(10).join(f'- {ext}: {count} files' for ext, count in top_exts)}

📂 Main directories:
{chr(10).join(f'- {d}/' for d in sorted(top_dirs)[:10])}"""
            
            return summary
            
        except Exception as e:
            logger.error(f"Project scan error: {e}")
            return f"❌ Error scanning project: {str(e)}"
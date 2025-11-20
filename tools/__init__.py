"""
Outils disponibles pour l'agent Ollama.
"""
from .code_execution import CodeExecutionTool, SyntaxCheckTool
from .project_scanner import ProjectScannerTool

# Liste de TOUS les outils disponibles
AVAILABLE_TOOLS = [
    CodeExecutionTool,
    SyntaxCheckTool,
    ProjectScannerTool,
]

__all__ = [
    'AVAILABLE_TOOLS',
    'CodeExecutionTool',
    'SyntaxCheckTool',
    'ProjectScannerTool',
]
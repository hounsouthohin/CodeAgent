"""
Outils exposés à Gemini CLI via MCP.
Seulement 2 super-outils optimisés.
"""
from .intelligent_assist import intelligent_assist
from .project_context import build_project_context

__all__ = [
    'intelligent_assist',
    'build_project_context',
]
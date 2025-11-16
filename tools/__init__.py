"""
Outils disponibles pour l'agent Ollama.
"""
from .code_execution import CodeExecutionTool, SyntaxCheckTool, TestRunnerTool
from .code_analysis import CodeAnalysisTool, LintingTool
from .documentation import DocumentationSearchTool, ErrorExplainerTool, CodeExampleFinder
from .git_operations import GitDiffTool, GitHistoryTool, GitStatusTool
from .performance import ProfilerTool, MemoryProfilerTool

__all__ = [
    # Code Execution
    'CodeExecutionTool',
    'SyntaxCheckTool', 
    'TestRunnerTool',
    
    # Code Analysis
    'CodeAnalysisTool',
    'LintingTool',
    
    # Documentation
    'DocumentationSearchTool',
    'ErrorExplainerTool',
    'CodeExampleFinder',
    
    # Git
    'GitDiffTool',
    'GitHistoryTool',
    'GitStatusTool',
    
    # Performance
    'ProfilerTool',
    'MemoryProfilerTool',
]

# Liste de tous les outils disponibles
AVAILABLE_TOOLS = [
    CodeExecutionTool,
    SyntaxCheckTool,
    TestRunnerTool,
    CodeAnalysisTool,
    LintingTool,
    DocumentationSearchTool,
    ErrorExplainerTool,
    CodeExampleFinder,
    GitDiffTool,
    GitHistoryTool,
    GitStatusTool,
    ProfilerTool,
    MemoryProfilerTool,
]
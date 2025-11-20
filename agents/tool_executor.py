"""
Exécuteur d'outils pour l'agent Ollama.
"""
import sys
sys.path.append('/app')
from utils import setup_logger

logger = setup_logger(__name__)

class ToolExecutor:
    """Exécute les outils demandés par l'agent."""
    
    def __init__(self):
        # Importer tous les outils disponibles
        from tools import AVAILABLE_TOOLS
        self.tools = {
            tool.get_tool_definition()['name']: tool
            for tool in AVAILABLE_TOOLS
        }
        logger.info(f"ToolExecutor initialized with {len(self.tools)} tools")
    
    def execute_tool(self, tool_name: str, parameters: dict) -> str:
        """
        Exécute un outil avec les paramètres donnés.
        
        Args:
            tool_name: Nom de l'outil
            parameters: Paramètres de l'outil
            
        Returns:
            Résultat de l'exécution
        """
        if tool_name not in self.tools:
            available = ", ".join(self.tools.keys())
            return f"❌ Tool '{tool_name}' not found. Available: {available}"
        
        try:
            tool_class = self.tools[tool_name]
            result = tool_class.execute(**parameters)
            return result
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return f"❌ Error: {str(e)}"
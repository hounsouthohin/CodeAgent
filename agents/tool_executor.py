"""
Exécuteur d'outils pour l'agent Ollama.
"""
import json
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ToolExecutor:
    """Exécute les outils demandés par Ollama."""
    
    def __init__(self):
        """Initialise l'exécuteur avec les outils disponibles."""
        # Import dynamique pour éviter l'import circulaire
        from tools import AVAILABLE_TOOLS
        
        self.tools_map = {
            tool.get_tool_definition()['name']: tool
            for tool in AVAILABLE_TOOLS
        }
        logger.info(f"ToolExecutor initialized with {len(self.tools_map)} tools")
    
    def get_tools_definitions(self) -> List[Dict[str, Any]]:
        """Retourne les définitions de tous les outils."""
        from tools import AVAILABLE_TOOLS
        return [tool.get_tool_definition() for tool in AVAILABLE_TOOLS]
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        Exécute un outil avec les paramètres donnés.
        
        Args:
            tool_name: Nom de l'outil
            parameters: Paramètres de l'outil
            
        Returns:
            Résultat de l'exécution
        """
        logger.info(f"Executing tool: {tool_name} with params: {parameters}")
        
        # Vérifier que l'outil existe
        if tool_name not in self.tools_map:
            available = ', '.join(self.tools_map.keys())
            return f"❌ Unknown tool '{tool_name}'. Available tools: {available}"
        
        try:
            # Récupérer la classe de l'outil
            tool_class = self.tools_map[tool_name]
            
            # Exécuter l'outil
            result = tool_class.execute(**parameters)
            
            logger.info(f"Tool {tool_name} executed successfully")
            return result
            
        except TypeError as e:
            # Erreur de paramètres
            logger.error(f"Invalid parameters for {tool_name}: {e}")
            return f"❌ Invalid parameters for '{tool_name}': {str(e)}"
        except Exception as e:
            # Erreur d'exécution
            logger.error(f"Tool execution error for {tool_name}: {e}", exc_info=True)
            return f"❌ Tool execution failed: {str(e)}"
    
    def parse_tool_call(self, text: str) -> tuple:
        """
        Parse un appel d'outil du format: TOOL_CALL: {"name": "...", "parameters": {...}}
        
        Args:
            text: Texte contenant l'appel d'outil
            
        Returns:
            (tool_name, parameters) ou (None, None) si parsing échoue
        """
        try:
            # Extraire le JSON après "TOOL_CALL:"
            if "TOOL_CALL:" not in text:
                return None, None
            
            json_str = text.split("TOOL_CALL:", 1)[1].strip()
            
            # Prendre juste la première ligne si multiligne
            if '\n' in json_str:
                json_str = json_str.split('\n')[0].strip()
            
            # Parser le JSON
            tool_call = json.loads(json_str)
            
            tool_name = tool_call.get('name')
            parameters = tool_call.get('parameters', {})
            
            if not tool_name:
                logger.error("Tool call missing 'name' field")
                return None, None
            
            return tool_name, parameters
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tool call JSON: {e}")
            logger.debug(f"Problematic text: {text}")
            return None, None
        except Exception as e:
            logger.error(f"Error parsing tool call: {e}")
            return None, None
    
    def is_tool_call(self, text: str) -> bool:
        """Vérifie si le texte contient un appel d'outil."""
        return "TOOL_CALL:" in text
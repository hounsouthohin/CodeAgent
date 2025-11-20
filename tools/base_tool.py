"""
Classe de base pour tous les outils.
"""
from abc import ABC, abstractmethod
from typing import Dict

class BaseTool(ABC):
    """Classe abstraite pour tous les outils."""
    
    @staticmethod
    @abstractmethod
    def get_tool_definition() -> Dict:
        """
        Retourne la définition de l'outil pour l'agent.
        
        Returns:
            Dict avec 'name', 'description', 'parameters'
        """
        pass
    
    @staticmethod
    @abstractmethod
    def execute(**kwargs) -> str:
        """
        Exécute l'outil avec les paramètres donnés.
        
        Returns:
            Résultat sous forme de string
        """
        pass
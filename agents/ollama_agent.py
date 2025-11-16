"""
Agent Ollama avec capacité d'utiliser des outils (ReAct pattern).
"""
import json
import requests
from typing import Optional

import sys
sys.path.append('/app')
from utils.config import Config
from utils.logger import setup_logger
from utils.cache import cache_result
from .tool_executor import ToolExecutor
from .prompts import PromptTemplates

logger = setup_logger(__name__)

class OllamaAgent:
    """Agent Ollama avec ReAct (Reasoning + Acting)."""
    
    def __init__(self):
        """Initialise l'agent."""
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
        self.tool_executor = ToolExecutor()
        
        logger.info(f"OllamaAgent initialized (model: {self.model})")
    
    def ask_with_tools(
        self,
        prompt: str,
        task_type: str = "general",
        max_iterations: int = None
    ) -> str:
        """
        Pose une question à Ollama avec possibilité d'utiliser des outils.
        
        Args:
            prompt: Question/tâche à accomplir
            task_type: Type de tâche (general, fix, review, test, debug)
            max_iterations: Nombre max d'itérations tool (default: Config.MAX_TOOL_ITERATIONS)
            
        Returns:
            Réponse finale
        """
        if max_iterations is None:
            max_iterations = Config.MAX_TOOL_ITERATIONS
        
        # Créer le prompt système avec les outils
        tools = self.tool_executor.get_tools_definitions()
        system_prompt = PromptTemplates.create_system_prompt(tools, task_type)
        
        # Combiner système + user prompt
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Boucle ReAct
        conversation_history = []
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"ReAct iteration {iteration}/{max_iterations}")
            
            # Obtenir la réponse d'Ollama
            if conversation_history:
                # Utiliser l'historique pour le contexte
                current_prompt = conversation_history[-1]
            else:
                current_prompt = full_prompt
            
            ollama_response = self._call_ollama(current_prompt)
            
            # Vérifier si Ollama veut utiliser un outil
            if self.tool_executor.is_tool_call(ollama_response):
                # Parser l'appel d'outil
                tool_name, parameters = self.tool_executor.parse_tool_call(ollama_response)
                
                if tool_name is None:
                    # Parsing échoué, retourner la réponse telle quelle
                    logger.warning("Failed to parse tool call, returning response as-is")
                    return ollama_response
                
                # Exécuter l'outil
                logger.info(f"Tool requested: {tool_name}")
                tool_result = self.tool_executor.execute_tool(tool_name, parameters)
                
                # Ajouter le résultat à l'historique
                feedback = f"Tool '{tool_name}' returned:\n{tool_result}\n\nNow provide your response based on this information."
                conversation_history.append(feedback)
                
            else:
                # Pas d'appel d'outil, c'est la réponse finale
                logger.info("Final answer received")
                return ollama_response
        
        # Max iterations atteintes
        logger.warning(f"Max iterations ({max_iterations}) reached")
        return ollama_response if ollama_response else "❌ Max iterations reached without final answer"
    
    @cache_result(ttl=3600)
    def ask_simple(self, prompt: str, max_tokens: int = None, timeout: int = None) -> str:
        """
        Appel simple à Ollama sans outils (avec cache).
        
        Args:
            prompt: Prompt à envoyer
            max_tokens: Nombre max de tokens
            timeout: Timeout en secondes
            
        Returns:
            Réponse d'Ollama
        """
        if max_tokens is None:
            max_tokens = Config.MAX_TOKENS
        if timeout is None:
            timeout = Config.OLLAMA_TIMEOUT
        
        return self._call_ollama(prompt, max_tokens, timeout, stream=True)
    
    def _call_ollama(
        self,
        prompt: str,
        max_tokens: int = None,
        timeout: int = None,
        stream: bool = False
    ) -> str:
        """
        Appel bas-niveau à l'API Ollama.
        
        Args:
            prompt: Prompt à envoyer
            max_tokens: Nombre max de tokens
            timeout: Timeout
            stream: Utiliser le streaming
            
        Returns:
            Réponse d'Ollama
        """
        if max_tokens is None:
            max_tokens = Config.MAX_TOKENS
        if timeout is None:
            timeout = Config.OLLAMA_TIMEOUT
        
        try:
            # Vérifier qu'Ollama est accessible
            health_check = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            health_check.raise_for_status()
            
            # Faire la requête
            url = f"{self.base_url}/api/generate"
            
            if stream:
                return self._call_ollama_stream(url, prompt, max_tokens, timeout)
            else:
                return self._call_ollama_simple(url, prompt, max_tokens, timeout)
                
        except requests.exceptions.ConnectionError:
            error_msg = f"❌ Cannot connect to Ollama at {self.base_url}"
            logger.error(error_msg)
            return error_msg
        except requests.exceptions.Timeout:
            error_msg = f"⏱️ Ollama request timed out after {timeout}s"
            logger.error(error_msg)
            return error_msg
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                error_msg = f"❌ Model '{self.model}' not found. Install: docker-compose exec ollama ollama pull {self.model}"
            else:
                error_msg = f"❌ HTTP {e.response.status_code}: {e}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg
    
    def _call_ollama_stream(self, url: str, prompt: str, max_tokens: int, timeout: int) -> str:
        """Appel avec streaming."""
        response = requests.post(
            url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
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
                    if chunk.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
        
        return full_response.strip() or "Pas de réponse générée"
    
    def _call_ollama_simple(self, url: str, prompt: str, max_tokens: int, timeout: int) -> str:
        """Appel simple sans streaming."""
        response = requests.post(
            url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": max_tokens
                }
            },
            timeout=timeout
        )
        response.raise_for_status()
        
        return response.json().get("response", "Pas de réponse générée")
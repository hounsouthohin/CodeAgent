"""
Agent Ollama avec pattern ReAct simplifié.
"""
import requests
import json
from typing import Dict, Optional
import sys
sys.path.append('/app')
from utils import Config, setup_logger, cache_result

logger = setup_logger(__name__)

class OllamaAgent:
    """Agent qui utilise Ollama avec pattern ReAct."""
    
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
        self.timeout = Config.OLLAMA_TIMEOUT
    
    @cache_result(ttl=3600)
    def ask_simple(self, prompt: str) -> str:
        """
        Requête simple à Ollama sans outils (rapide).
        
        Args:
            prompt: Prompt à envoyer
            
        Returns:
            Réponse de l'IA
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Déterministe pour corrections
                "num_predict": Config.MAX_TOKENS
            }
        }
        
        try:
            logger.info(f"🤖 Asking Ollama (simple): {prompt[:100]}...")
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            answer = result.get('response', '').strip()
            
            logger.info(f"✅ Got response ({len(answer)} chars)")
            return answer
            
        except requests.Timeout:
            logger.error(f"⏱️ Ollama timeout after {self.timeout}s")
            return "⏱️ Timeout: Requête trop longue"
        except Exception as e:
            logger.error(f"❌ Ollama error: {e}")
            return f"❌ Error: {str(e)}"
    
    def ask_with_tools(
        self,
        prompt: str,
        tools: Optional[list] = None,
        max_iterations: int = 5
    ) -> str:
        """
        Requête avec outils disponibles (pattern ReAct).
        
        Args:
            prompt: Prompt initial
            tools: Liste des outils disponibles (optionnel)
            max_iterations: Nombre max d'itérations ReAct
            
        Returns:
            Réponse finale après utilisation des outils
        """
        if tools is None:
            # Importer les outils par défaut
            from tools import AVAILABLE_TOOLS
            tools = [t.get_tool_definition() for t in AVAILABLE_TOOLS]
        
        logger.info(f"🤖 Starting ReAct loop ({len(tools)} tools available)")
        
        # Construire le prompt système avec les outils
        system_prompt = self._build_system_prompt(tools)
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        conversation_history = []
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"   ReAct iteration {iteration}/{max_iterations}")
            
            # Demander à Ollama
            response = self.ask_simple(full_prompt)
            conversation_history.append(response)
            
            # Vérifier si Ollama veut appeler un outil
            if "TOOL_CALL:" in response:
                # Extraire et exécuter l'appel d'outil
                tool_result = self._execute_tool_call(response, tools)
                
                # Ajouter le résultat à l'historique
                full_prompt = f"{full_prompt}\n\nTool result: {tool_result}\n\nContinue:"
                conversation_history.append(f"Tool result: {tool_result}")
            else:
                # Pas d'appel d'outil = réponse finale
                logger.info(f"✅ ReAct completed in {iteration} iterations")
                return response
        
        logger.warning(f"⚠️ Max iterations reached ({max_iterations})")
        return conversation_history[-1] if conversation_history else "No response"
    
    def _build_system_prompt(self, tools: list) -> str:
        """Construit le prompt système avec les outils."""
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in tools
        ])
        
        return f"""You are an AI coding assistant with access to tools.

AVAILABLE TOOLS:
{tools_desc}

TO USE A TOOL:
TOOL_CALL: {{"name": "tool_name", "parameters": {{"param": "value"}}}}

Think step-by-step and use tools when needed."""
    
    def _execute_tool_call(self, response: str, tools: list) -> str:
        """Extrait et exécute un appel d'outil depuis la réponse."""
        try:
            # Extraire le JSON après TOOL_CALL:
            tool_call_start = response.find("TOOL_CALL:")
            if tool_call_start == -1:
                return "Error: No TOOL_CALL found"
            
            json_start = response.find("{", tool_call_start)
            json_end = response.find("}", json_start) + 1
            
            if json_start == -1 or json_end == 0:
                return "Error: Invalid TOOL_CALL format"
            
            tool_call_json = response[json_start:json_end]
            tool_call = json.loads(tool_call_json)
            
            tool_name = tool_call.get('name')
            parameters = tool_call.get('parameters', {})
            
            logger.info(f"   🔧 Calling tool: {tool_name}")
            
            # Exécuter l'outil
            from agents.tool_executor import ToolExecutor
            executor = ToolExecutor()
            result = executor.execute_tool(tool_name, parameters)
            
            return result
            
        except Exception as e:
            logger.error(f"   ❌ Tool execution error: {e}")
            return f"Error executing tool: {str(e)}"
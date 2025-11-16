"""
Outils de recherche de documentation.
Utilise DuckDuckGo (gratuit, sans API key), BeautifulSoup pour parsing.
"""
import re
from typing import Dict, Any, List
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
from requests_cache import CachedSession

import sys
sys.path.append('/app')
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Session avec cache pour éviter les requêtes répétées
session = CachedSession(
    cache_name=str(Config.CACHE_DIR / 'http_cache'),
    expire_after=Config.CACHE_TTL
)

class DocumentationSearchTool:
    """Recherche dans la documentation Python et StackOverflow."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "search_documentation",
            "description": "Search Python documentation, StackOverflow, and programming resources. Use when you need examples, error explanations, or best practices. FREE and unlimited!",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'asyncio.run usage', 'fix TypeError in Python')"
                    },
                    "source": {
                        "type": "string",
                        "enum": ["python_docs", "stackoverflow", "general"],
                        "description": "Where to search",
                        "default": "general"
                    }
                },
                "required": ["query"]
            }
        }
    
    @staticmethod
    def execute(query: str, source: str = "general") -> str:
        """Recherche de documentation."""
        if not Config.WEB_SEARCH_ENABLED:
            return "❌ Web search is disabled in configuration"
        
        logger.info(f"Searching documentation: {query} (source: {source})")
        
        try:
            if source == "python_docs":
                return DocumentationSearchTool._search_python_docs(query)
            elif source == "stackoverflow":
                return DocumentationSearchTool._search_stackoverflow(query)
            else:
                return DocumentationSearchTool._search_general(query)
                
        except Exception as e:
            logger.error(f"Documentation search error: {e}")
            return f"❌ Search error: {str(e)}"
    
    @staticmethod
    def _search_python_docs(query: str) -> str:
        """Recherche dans la documentation Python officielle."""
        try:
            # Rechercher sur docs.python.org
            ddgs = DDGS()
            results = list(ddgs.text(
                f"site:docs.python.org {query}",
                max_results=3
            ))
            
            if not results:
                return f"❌ No Python documentation found for '{query}'"
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   URL: {result['href']}\n"
                    f"   {result['body'][:200]}..."
                )
            
            return "📚 Python Documentation Results:\n\n" + "\n\n".join(formatted_results)
            
        except Exception as e:
            return f"❌ Python docs search failed: {str(e)}"
    
    @staticmethod
    def _search_stackoverflow(query: str) -> str:
        """Recherche sur StackOverflow avec extraction de réponse."""
        try:
            # Rechercher sur StackOverflow
            ddgs = DDGS()
            results = list(ddgs.text(
                f"site:stackoverflow.com {query}",
                max_results=3
            ))
            
            if not results:
                return f"❌ No StackOverflow results for '{query}'"
            
            # Extraire le contenu de la meilleure réponse
            best_result = results[0]
            
            # Tenter de récupérer la page pour extraire la réponse acceptée
            try:
                response = session.get(best_result['href'], timeout=5)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Trouver la réponse acceptée
                accepted_answer = soup.find('div', class_='accepted-answer')
                if accepted_answer:
                    answer_text = accepted_answer.find('div', class_='s-prose').get_text()
                    # Nettoyer et limiter
                    answer_text = answer_text.strip()[:500]
                    
                    return (
                        f"✅ StackOverflow - Accepted Answer:\n\n"
                        f"Question: {best_result['title']}\n"
                        f"URL: {best_result['href']}\n\n"
                        f"Answer excerpt:\n{answer_text}...\n\n"
                        f"💡 Visit URL for complete code examples"
                    )
            except:
                pass
            
            # Fallback: retourner juste les liens
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   {result['href']}"
                )
            
            return "🔍 StackOverflow Results:\n\n" + "\n\n".join(formatted_results)
            
        except Exception as e:
            return f"❌ StackOverflow search failed: {str(e)}"
    
    @staticmethod
    def _search_general(query: str) -> str:
        """Recherche générale."""
        try:
            ddgs = DDGS()
            results = list(ddgs.text(
                f"python {query}",
                max_results=Config.MAX_SEARCH_RESULTS
            ))
            
            if not results:
                return f"❌ No results found for '{query}'"
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   URL: {result['href']}\n"
                    f"   {result['body'][:150]}..."
                )
            
            return "🔍 Search Results:\n\n" + "\n\n".join(formatted_results)
            
        except Exception as e:
            return f"❌ General search failed: {str(e)}"


class ErrorExplainerTool:
    """Explique les erreurs Python et suggère des solutions."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "explain_error",
            "description": "Explain Python errors/exceptions and find solutions. Searches StackOverflow for similar errors and provides fixes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "error_message": {
                        "type": "string",
                        "description": "The error message or exception"
                    },
                    "error_type": {
                        "type": "string",
                        "description": "Error type (e.g., 'TypeError', 'ValueError')",
                        "default": ""
                    }
                },
                "required": ["error_message"]
            }
        }
    
    @staticmethod
    def execute(error_message: str, error_type: str = "") -> str:
        """Explique une erreur et trouve des solutions."""
        try:
            # Nettoyer le message d'erreur
            clean_error = re.sub(r'File ".*",', '', error_message)
            clean_error = re.sub(r'line \d+', '', clean_error).strip()
            
            # Construire la requête
            query = f"{error_type} {clean_error}" if error_type else clean_error
            
            # Rechercher sur StackOverflow
            ddgs = DDGS()
            results = list(ddgs.text(
                f"site:stackoverflow.com python {query}",
                max_results=3
            ))
            
            if not results:
                return f"❌ No solutions found for this error"
            
            output = f"🔧 Solutions for: {error_type or 'Error'}\n\n"
            
            for i, result in enumerate(results, 1):
                output += f"{i}. {result['title']}\n   {result['href']}\n\n"
            
            output += "💡 Common fixes:\n"
            
            # Suggestions basées sur le type d'erreur
            if "NameError" in error_message or "not defined" in error_message:
                output += "- Check for typos in variable names\n"
                output += "- Verify variable is defined before use\n"
                output += "- Check import statements\n"
            elif "TypeError" in error_message:
                output += "- Check data types match expected types\n"
                output += "- Verify function arguments\n"
                output += "- Check if object supports the operation\n"
            elif "AttributeError" in error_message:
                output += "- Verify object has the attribute\n"
                output += "- Check object type\n"
                output += "- Ensure object is initialized\n"
            
            return output
            
        except Exception as e:
            return f"❌ Error explanation failed: {str(e)}"


class CodeExampleFinder:
    """Trouve des exemples de code."""
    
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "name": "find_code_examples",
            "description": "Find working code examples for a specific Python feature, library, or pattern. Returns real-world examples.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "What to find examples for (e.g., 'asyncio websocket', 'pandas groupby')"
                    }
                },
                "required": ["topic"]
            }
        }
    
    @staticmethod
    def execute(topic: str) -> str:
        """Trouve des exemples de code."""
        try:
            # Rechercher sur GitHub et docs
            ddgs = DDGS()
            results = list(ddgs.text(
                f"python {topic} example code",
                max_results=5
            ))
            
            if not results:
                return f"❌ No examples found for '{topic}'"
            
            # Filtrer pour garder sources de qualité
            quality_sources = ['github.com', 'docs.python.org', 'realpython.com', 'stackoverflow.com']
            filtered = [r for r in results if any(src in r['href'] for src in quality_sources)]
            
            if not filtered:
                filtered = results[:3]
            
            output = f"📝 Code Examples for '{topic}':\n\n"
            for i, result in enumerate(filtered, 1):
                output += f"{i}. {result['title']}\n   {result['href']}\n\n"
            
            return output
            
        except Exception as e:
            return f"❌ Example search failed: {str(e)}"